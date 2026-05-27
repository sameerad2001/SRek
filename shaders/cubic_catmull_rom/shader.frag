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

vec4 catmull_rom(vec4 p0, vec4 p1, vec4 p2, vec4 p3, float t)
{
    float t2 = t * t;
    float t3 = t2 * t;

    return 0.5 * (
        (2.0 * p1) +
        (-p0 + p2) * t +
        (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2 +
        (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
    );
}

vec4 sample_cubic_catmull_rom(vec2 uv)
{
    vec2 src_pos = uv * vec2(input_size) - vec2(0.5);

    ivec2 base = ivec2(floor(src_pos));
    vec2 f = fract(src_pos);

    vec4 row0 = catmull_rom(
        fetch_pixel(base + ivec2(-1, -1)),
        fetch_pixel(base + ivec2( 0, -1)),
        fetch_pixel(base + ivec2( 1, -1)),
        fetch_pixel(base + ivec2( 2, -1)),
        f.x
    );

    vec4 row1 = catmull_rom(
        fetch_pixel(base + ivec2(-1, 0)),
        fetch_pixel(base + ivec2( 0, 0)),
        fetch_pixel(base + ivec2( 1, 0)),
        fetch_pixel(base + ivec2( 2, 0)),
        f.x
    );

    vec4 row2 = catmull_rom(
        fetch_pixel(base + ivec2(-1, 1)),
        fetch_pixel(base + ivec2( 0, 1)),
        fetch_pixel(base + ivec2( 1, 1)),
        fetch_pixel(base + ivec2( 2, 1)),
        f.x
    );

    vec4 row3 = catmull_rom(
        fetch_pixel(base + ivec2(-1, 2)),
        fetch_pixel(base + ivec2( 0, 2)),
        fetch_pixel(base + ivec2( 1, 2)),
        fetch_pixel(base + ivec2( 2, 2)),
        f.x
    );

    vec4 color = catmull_rom(row0, row1, row2, row3, f.y);

    return clamp(color, 0.0, 1.0);
}

void main()
{
    ivec2 out_px = ivec2(gl_FragCoord.xy);

    if (out_px.x >= output_size.x || out_px.y >= output_size.y)
        discard;

    vec2 out_uv = (vec2(out_px) + vec2(0.5)) / vec2(output_size);

    frag_color = sample_cubic_catmull_rom(out_uv);
}