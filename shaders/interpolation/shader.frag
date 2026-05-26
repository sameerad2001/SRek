#version 410 core

uniform sampler2D input_image;
uniform ivec2 input_size;
uniform ivec2 output_size;

in vec2 uv;
out vec4 frag_color;

vec4 fetch_pixel(ivec2 p)
{
    p = clamp(p, ivec2(0), input_size - 1);
    return texelFetch(input_image, p, 0);
}

vec4 sample_bilinear_manual(vec2 uv)
{
    vec2 src_pos = uv * vec2(input_size) - vec2(0.5);

    ivec2 base = ivec2(floor(src_pos));
    vec2 f = fract(src_pos);

    /*
        a ---- b
        |      |
        |      |
        c ---- d
    */
    vec4 a = fetch_pixel(base + ivec2(0, 0));
    vec4 b = fetch_pixel(base + ivec2(1, 0));
    vec4 c = fetch_pixel(base + ivec2(0, 1));
    vec4 d = fetch_pixel(base + ivec2(1, 1));

    vec4 x0 = mix(a, b, f.x);
    vec4 x1 = mix(c, d, f.x);

    return mix(x0, x1, f.y);
}

void main()
{
    ivec2 out_px = ivec2(gl_FragCoord.xy);

    if (out_px.x >= output_size.x || out_px.y >= output_size.y)
        discard;

    vec2 out_uv = (vec2(out_px) + vec2(0.5)) / vec2(output_size);

    frag_color = sample_bilinear_manual(out_uv);
}