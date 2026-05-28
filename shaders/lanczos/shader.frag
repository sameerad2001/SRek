#version 410 core

uniform sampler2D input_image;
uniform ivec2 input_size;
uniform ivec2 output_size;

in vec2 uv;
out vec4 frag_color;

const float PI = 3.14159265358979323846;
const float LANCZOS_A = 3.0;

vec4 fetch_pixel(ivec2 p)
{
    p = clamp(p, ivec2(0), input_size - 1);
    return texelFetch(input_image, p, 0);
}

float sinc(float x)
{
    if (abs(x) < 1e-5)
        return 1.0;

    float pix = PI * x;
    return sin(pix) / pix;
}

float lanczos_weight(float x)
{
    x = abs(x);

    if (x >= LANCZOS_A)
        return 0.0;

    return sinc(x) * sinc(x / LANCZOS_A);
}

vec4 sample_lanczos(vec2 uv)
{
    vec2 src_pos = uv * vec2(input_size) - vec2(0.5);

    ivec2 base = ivec2(floor(src_pos));

    vec4 sum = vec4(0.0);
    float weight_sum = 0.0;

    for (int y = -2; y <= 3; ++y)
    {
        for (int x = -2; x <= 3; ++x)
        {
            ivec2 p = base + ivec2(x, y);

            float dx = src_pos.x - float(p.x);
            float dy = src_pos.y - float(p.y);

            float wx = lanczos_weight(dx);
            float wy = lanczos_weight(dy);
            float w = wx * wy;

            sum += fetch_pixel(p) * w;
            weight_sum += w;
        }
    }

    if (abs(weight_sum) < 1e-5) // Prevent vales from exploding
        return fetch_pixel(base);

    return clamp(sum / weight_sum, 0.0, 1.0);
}

void main()
{
    ivec2 out_px = ivec2(gl_FragCoord.xy);

    if (out_px.x >= output_size.x || out_px.y >= output_size.y)
        discard;

    vec2 out_uv = (vec2(out_px) + vec2(0.5)) / vec2(output_size);

    frag_color = sample_lanczos(out_uv);
}