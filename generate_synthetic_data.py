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


def load_texture(ctx, path):
    image = Image.open(path).convert("RGBA")
    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    texture = ctx.texture(image.size, 4, image.tobytes())
    texture.filter = (moderngl.LINEAR, moderngl.LINEAR)
    return texture


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


def translate(v):
    x, y, z = v
    return np.array([
        [1.0, 0.0, 0.0, x],
        [0.0, 1.0, 0.0, y],
        [0.0, 0.0, 1.0, z],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def scale(v):
    x, y, z = v
    return np.array([
        [x, 0.0, 0.0, 0.0],
        [0.0, y, 0.0, 0.0],
        [0.0, 0.0, z, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)


def rotation_xyz(degrees):
    rx, ry, rz = [math.radians(v) for v in degrees]

    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)

    rot_x = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, cx, -sx, 0.0],
        [0.0, sx, cx, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

    rot_y = np.array([
        [cy, 0.0, sy, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [-sy, 0.0, cy, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

    rot_z = np.array([
        [cz, -sz, 0.0, 0.0],
        [sz, cz, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ], dtype=np.float32)

    return rot_z @ rot_y @ rot_x


def create_cube_mesh(ctx, program):
    vertices = np.array([
        -1, -1, -1,  0,  0, -1,  0, 0,
         1, -1, -1,  0,  0, -1,  1, 0,
         1,  1, -1,  0,  0, -1,  1, 1,
        -1,  1, -1,  0,  0, -1,  0, 1,

        -1, -1,  1,  0,  0,  1,  0, 0,
         1, -1,  1,  0,  0,  1,  1, 0,
         1,  1,  1,  0,  0,  1,  1, 1,
        -1,  1,  1,  0,  0,  1,  0, 1,

        -1, -1, -1, -1,  0,  0,  0, 0,
        -1,  1, -1, -1,  0,  0,  1, 0,
        -1,  1,  1, -1,  0,  0,  1, 1,
        -1, -1,  1, -1,  0,  0,  0, 1,

         1, -1, -1,  1,  0,  0,  0, 0,
         1,  1, -1,  1,  0,  0,  1, 0,
         1,  1,  1,  1,  0,  0,  1, 1,
         1, -1,  1,  1,  0,  0,  0, 1,

        -1,  1, -1,  0,  1,  0,  0, 0,
         1,  1, -1,  0,  1,  0,  1, 0,
         1,  1,  1,  0,  1,  0,  1, 1,
        -1,  1,  1,  0,  1,  0,  0, 1,

        -1, -1, -1,  0, -1,  0,  0, 0,
         1, -1, -1,  0, -1,  0,  1, 0,
         1, -1,  1,  0, -1,  0,  1, 1,
        -1, -1,  1,  0, -1,  0,  0, 1,
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
        [(vbo, "3f 3f 2f", "in_position", "in_normal", "in_uv")],
        index_buffer=ibo,
    )

    return vao, vbo, ibo


def create_solid_texture(ctx, color):
    rgba = np.array([
        int(color[0] * 255),
        int(color[1] * 255),
        int(color[2] * 255),
        255,
    ], dtype=np.uint8)

    texture = ctx.texture((1, 1), 4, rgba.tobytes())
    texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
    return texture


def resolve_texture(ctx, texture_name, fallback_color, texture_cache):
    if texture_name:
        texture_path = texture_name

        if texture_path not in texture_cache:
            texture_cache[texture_path] = load_texture(ctx, texture_path)

        return texture_cache[texture_path], True

    return create_solid_texture(ctx, fallback_color), False


def compute_entity_model(entity, frame_index):
    position = np.array(entity.get("position", [0, 0, 0]), dtype=np.float32)
    orientation = np.array(entity.get("orientation", [0, 0, 0]), dtype=np.float32)
    scale_value = np.array(entity.get("scale", [1, 1, 1]), dtype=np.float32)

    linear_velocity = np.array(entity.get("linear_velocity", [0, 0, 0]), dtype=np.float32)
    angular_velocity = np.array(entity.get("angular_velocity", [0, 0, 0]), dtype=np.float32)

    position = position + linear_velocity * frame_index
    orientation = orientation + angular_velocity * frame_index

    return translate(position) @ rotation_xyz(orientation) @ scale(scale_value)


def save_frame(path, data, width, height):
    image = np.frombuffer(data, dtype=np.uint8)
    image = image.reshape((height, width, 4))
    image = np.flipud(image)

    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(image, mode="RGBA").save(path)


def draw_background(ctx, scene):
    background = scene.get("background", {})
    color = background.get("color", [0.0, 0.0, 0.0, 1.0])
    ctx.clear(color[0], color[1], color[2], color[3], depth=1.0)


def main():
    config = load_config()

    output_path = Path(config.get("output_path", "input/synthetic_data"))
    frame_count = int(config.get("frame_count", 100))
    width = int(config.get("width", 1280))
    height = int(config.get("height", 720))

    scene = config["scene"]

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

    camera = scene.get("camera", {})
    eye = camera.get("eye", [0.0, 1.5, 6.0])
    target = camera.get("target", [0.0, 0.0, 0.0])
    up = camera.get("up", [0.0, 1.0, 0.0])
    fov_y = float(camera.get("fov_y", 60.0))

    proj = perspective(fov_y, width / height, 0.1, 100.0)
    view = look_at(eye, target, up)

    lighting = scene.get("lighting", {})
    light_dir = np.array(lighting.get("direction", [-0.4, -1.0, -0.6]), dtype=np.float32)
    light_dir /= np.linalg.norm(light_dir)

    program["light_dir"].value = tuple(light_dir)
    program["ambient"].value = float(lighting.get("ambient", 0.15))
    program["input_texture"].value = 0

    texture_cache = {}

    for frame in range(frame_count):
        framebuffer.use()
        ctx.viewport = (0, 0, width, height)
        draw_background(ctx, scene) # Clear screen color, texture not supported

        for entity in scene.get("entities", []):
            model = compute_entity_model(entity, frame)
            mvp = proj @ view @ model
            normal_matrix = np.linalg.inv(model[:3, :3]).T

            color = entity.get("color", [0.0, 0.15, 1.0])
            texture_name = entity.get("texture")

            texture, has_texture = resolve_texture(ctx, texture_name, color, texture_cache)
            texture.use(0)

            program["mvp"].write(mvp.T.astype(np.float32).tobytes())
            program["normal_matrix"].write(normal_matrix.T.astype(np.float32).tobytes())
            program["base_color"].value = tuple(color)
            program["has_texture"].value = has_texture

            vao.render(mode=moderngl.TRIANGLES)

            if not texture_name:
                texture.release()

        ctx.finish()

        frame_path = output_path / f"color_{frame:04d}.png"
        save_frame(frame_path, framebuffer.read(components=4), width, height)

    for texture in texture_cache.values():
        texture.release()

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