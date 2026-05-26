import moderngl
import numpy as np
from pathlib import Path


VERTEX_SHADER = """
#version 410 core

out vec2 uv;

vec2 positions[3] = vec2[](
    vec2(-1.0, -1.0),
    vec2( 3.0, -1.0),
    vec2(-1.0,  3.0)
);

void main()
{
    vec2 pos = positions[gl_VertexID];
    uv = pos * 0.5 + 0.5;
    gl_Position = vec4(pos, 0.0, 1.0);
}
"""


def apply_spatial_sr(image, sr_type, sr_ratio):
    ctx = moderngl.create_standalone_context(require=410)

    fragment_shader = _load_shader(sr_type)
    program = ctx.program(
        vertex_shader=VERTEX_SHADER,
        fragment_shader=fragment_shader,
    )

    vao = ctx.vertex_array(program, [])
    output_image = _run_fullscreen_pass(ctx, program, vao, image, sr_ratio)

    vao.release()
    program.release()
    ctx.release()

    return output_image


def _load_shader(sr_type):
    shader_path = Path("shaders") / sr_type / "shader.frag"
    return shader_path.read_text(encoding="utf-8")


def _run_fullscreen_pass(ctx, program, vao, input_image, sr_ratio):
    input_h, input_w, _ = input_image.shape

    output_w = int(input_w * sr_ratio)
    output_h = int(input_h * sr_ratio)

    input_tex = ctx.texture((input_w, input_h), 4, input_image.tobytes())
    output_tex = ctx.texture((output_w, output_h), 4)

    input_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
    output_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)

    framebuffer = ctx.framebuffer(color_attachments=[output_tex])
    framebuffer.use()
    ctx.viewport = (0, 0, output_w, output_h)

    input_tex.use(0)

    program["input_image"].value = 0
    program["input_size"].value = (input_w, input_h)
    program["output_size"].value = (output_w, output_h)

    vao.render(mode=moderngl.TRIANGLES, vertices=3)
    ctx.finish()

    result = np.frombuffer(framebuffer.read(components=4), dtype=np.uint8)
    result = result.reshape((output_h, output_w, 4))

    framebuffer.release()
    input_tex.release()
    output_tex.release()

    return result