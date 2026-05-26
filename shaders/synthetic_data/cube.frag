#version 410 core

in vec3 world_normal;

uniform vec3 base_color;
uniform vec3 light_dir;
uniform float ambient;

out vec4 frag_color;

void main()
{
    vec3 n = normalize(world_normal);
    vec3 l = normalize(-light_dir);

    float ndotl = max(dot(n, l), 0.0);
    vec3 color = base_color * (ambient + ndotl * (1.0 - ambient));

    frag_color = vec4(color, 1.0);
}