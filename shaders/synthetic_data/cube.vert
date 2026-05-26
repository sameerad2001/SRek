#version 410 core

in vec3 in_position;
in vec3 in_normal;

uniform mat4 mvp;
uniform mat3 normal_matrix;

out vec3 world_normal;

void main()
{
    world_normal = normalize(normal_matrix * in_normal);
    gl_Position = mvp * vec4(in_position, 1.0);
}