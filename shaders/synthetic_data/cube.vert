#version 410 core

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

uniform mat4 mvp;
uniform mat3 normal_matrix;

out vec3 world_normal;
out vec2 uv;

void main()
{
    world_normal = normalize(normal_matrix * in_normal);
    uv = in_uv;
    gl_Position = mvp * vec4(in_position, 1.0);
}