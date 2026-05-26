#version 410 core

in vec3 world_normal;
in vec2 uv;

uniform vec3 base_color;
uniform vec3 light_dir;
uniform float ambient;

uniform sampler2D input_texture;
uniform bool has_texture;

out vec4 frag_color;

void main()
{
    vec3 n = normalize(world_normal);
    vec3 l = normalize(-light_dir);

    float ndotl = max(dot(n, l), 0.0);

    vec3 albedo = base_color;

    if (has_texture)
        albedo *= texture(input_texture, uv).rgb;

    vec3 color = albedo * (ambient + ndotl * (1.0 - ambient));

    frag_color = vec4(color, 1.0);
}