import json
import math
from pathlib import Path

import moderngl
import numpy as np
from PIL import Image


def load_config(path="config_synthetic_data.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_shader(path):
    return Path(path).read_text(encoding="utf-8")


def perspective(fov_y_degrees, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_y_degrees) * 0.5)

    return np.array([
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), (2.0 * far * near) / (near - far)],
        [0.0, 0.0, -1.0, 0.0],
    ], dtype=np.float32)


def look_at(eye, target, up):
    eye = np.array(eye, dtype=np.float32)
    target = np.array(target, dtype=np.float32)
    up = np.array(up, dtype=np.float32)

    z = eye - target
    z /= np.linalg.norm(z)

    x = np.cross(up, z)
    x /= np.linalg.norm(x)

    y = np.cross(z, x)

    return np.array([
        [x[0], x[1], x[2], -np.dot(x, eye)],
        [y[0], y[1], y[2], -np.dot(y, eye)],
        [z[0], z[1], z[2], -np.dot(z, eye)],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def rotation_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [c, 0.0, s, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-s, 0.0, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def rotation_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)

    return np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, c, -s, 0.0],
        [0.0, s, c, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def create_cube_mesh(ctx, program):
    vertices = np.array([
        -1, -1, -1,  0,  0, -1,
         1, -1, -1,  0,  0, -1,
         1,  1, -1,  0,  0, -1,
        -1,  1, -1,  0,  0, -1,

        -1, -1,  1,  0,  0,  1,
         1, -1,  1,  0,  0,  1,
         1,  1,  1,  0,  0,  1,
        -1,  1,  1,  0,  0,  1,

        -1, -1, -1, -1,  0,  0,
        -1,  1, -1, -1,  0,  0,
        -1,  1,  1, -1,  0,  0,
        -1, -1,  1, -1,  0,  0,

         1, -1, -1,  1,  0,  0,
         1,  1, -1,  1,  0,  0,
         1,  1,  1,  1,  0,  0,
         1, -1,  1,  1,  0,  0,

        -1,  1, -1,  0,  1,  0,
         1,  1, -1,  0,  1,  0,
         1,  1,  1,  0,  1,  0,
        -1,  1,  1,  0,  1,  0,

        -1, -1, -1,  0, -1,  0,
         1, -1, -1,  0, -1,  0,
         1, -1,  1,  0, -1,  0,
        -1, -1,  1,  0, -1,  0,
    ], dtype=np.float32)

    indices = np.array([
         0,  1,  2,  2,  3,  0,
         4,  5,  6,  6,  7,  4,
         8,  9, 10, 10, 11,  8,
        12, 13, 14, 14, 15, 12,
        16, 17, 18, 18, 19, 16,
        20, 21, 22, 22, 23, 20,
    ], dtype=np.uint32)

    vbo = ctx.buffer(vertices.tobytes())
    ibo = ctx.buffer(indices.tobytes())

    vao = ctx.vertex_array(
        program,
        [(vbo, "3f 3f", "in_position", "in_normal")],
        index_buffer=ibo,
    )

    return vao, vbo, ibo


def save_frame(path, data, width, height):
    image = np.frombuffer(data, dtype=np.uint8)
    image = image.reshape((height, width, 4))
    image = np.flipud(image)

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image, mode="RGBA").save(path)


def main():
    config = load_config()

    output_path = Path(config.get("output_path", "input/synthetic_data"))
    frame_count = int(config.get("frame_count", 100))
    width = int(config.get("width", 1280))
    height = int(config.get("height", 720))

    vertex_shader = load_shader(config.get("vertex_shader", "shaders/synthetic_data/cube.vert"))
    fragment_shader = load_shader(config.get("fragment_shader", "shaders/synthetic_data/cube.frag"))

    ctx = moderngl.create_standalone_context(require=410)
    ctx.enable(moderngl.DEPTH_TEST)

    program = ctx.program(
        vertex_shader=vertex_shader,
        fragment_shader=fragment_shader,
    )

    color_tex = ctx.texture((width, height), 4)
    depth_rb = ctx.depth_renderbuffer((width, height))
    framebuffer = ctx.framebuffer(
        color_attachments=[color_tex],
        depth_attachment=depth_rb,
    )

    vao, vbo, ibo = create_cube_mesh(ctx, program)

    proj = perspective(60.0, width / height, 0.1, 100.0)
    view = look_at(
        eye=[0.0, 1.5, 5.0],
        target=[0.0, 0.0, 0.0],
        up=[0.0, 1.0, 0.0],
    )

    light_dir = np.array([-0.4, -1.0, -0.6], dtype=np.float32)
    light_dir /= np.linalg.norm(light_dir)

    program["base_color"].value = (0.0, 0.15, 1.0)
    program["light_dir"].value = tuple(light_dir)
    program["ambient"].value = 0.15

    for frame in range(frame_count):
        t = frame / frame_count
        angle = t * math.tau

        model = rotation_y(angle) @ rotation_x(angle * 0.35)
        mvp = proj @ view @ model
        normal_matrix = np.linalg.inv(model[:3, :3]).T

        framebuffer.use()
        ctx.viewport = (0, 0, width, height)
        ctx.clear(0.0, 0.0, 0.0, 1.0, depth=1.0)

        program["mvp"].write(mvp.T.astype(np.float32).tobytes())
        program["normal_matrix"].write(normal_matrix.T.astype(np.float32).tobytes())

        vao.render(mode=moderngl.TRIANGLES)
        ctx.finish()

        frame_path = output_path / f"color_{frame:04d}.png"
        save_frame(frame_path, framebuffer.read(components=4), width, height)

    vao.release()
    vbo.release()
    ibo.release()
    framebuffer.release()
    color_tex.release()
    depth_rb.release()
    program.release()
    ctx.release()


if __name__ == "__main__":
    main()