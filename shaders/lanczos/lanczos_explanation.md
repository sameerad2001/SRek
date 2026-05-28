TODO: Add picture of sinc and lanczos (truncated sinc)

## 1D Lanczos

The ideal reconstruction filter for band limited signals is the sinc filter:

```txt
sinc(x) = sin(pi * x) / (pi * x)
```

with:

```txt
sinc(0) = 1
```

In theory, sinc interpolation uses infinitely many neighboring samples. This is not practical for image sampling, so Lanczos uses windowed sinc:

```txt
L(x) = sinc(x) * sinc(x / a), for |x| < a
L(x) = 0, otherwise
```

where `a` is the filter radius.

For Lanczos 3, samples farther than 3 texels from the source do not contribute.

<br>

## Lanczos weight function

The following:

```glsl
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
```

is equivalent to:
```txt
L(x) = sinc(x) * sinc(x / a)
```

<br>

## 1D Lanczos sampling

Given a fractional source position:

```cpp
src_pos = 10.25
base = 10
```

Lanczos 3 samples neighboring pixels within radius 3:

```txt
base - 2, base - 1, base, base + 1, base + 2, base + 3
=> 8, 9, 10, 11, 12, 13
```

Each sample gets a weight based on its distance from the fractional position:

```txt
distance_vector = src_pos - sample_position
weight   = Lanczos(distance_vector)
```

Continuing the example:
```txt
sample 10:
distance = 10.25 - 10 = 0.25
weight   = Lanczos(0.25)

sample 11:
distance = 10.25 - 11 = -0.75
weight   = Lanczos(-0.75)

sample 12:
distance = 10.25 - 12 = -1.75
weight   = Lanczos(-1.75)
```

The final result is a weighted average:

```txt
result =
    sample0 * weight0 +
    sample1 * weight1 +
    sample2 * weight2 +
    ...
```

Then normalize by the total weight:
```txt
result = weighted_sum / weight_sum
```

<br>

## 2D Lanczos

For images, Lanczos is applied as a separable filter. That means the 2D weight is:
```txt
weight_2d = L(dx) * L(dy)
```

where:
```txt
dx = horizontal distance from source position to source texel
dy = vertical distance from source position to source texel
```

For Lanczos 3, the shader samples a 6x6 neighborhood relative to the base.
```txt
(-2,-2)  (-1,-2)  (0,-2)  (1,-2)  (2,-2)  (3,-2)
(-2,-1)  (-1,-1)  (0,-1)  (1,-1)  (2,-1)  (3,-1)
(-2, 0)  (-1, 0)  (0, 0)  (1, 0)  (2, 0)  (3, 0)
(-2, 1)  (-1, 1)  (0, 1)  (1, 1)  (2, 1)  (3, 1)
(-2, 2)  (-1, 2)  (0, 2)  (1, 2)  (2, 2)  (3, 2)
(-2, 3)  (-1, 3)  (0, 3)  (1, 3)  (2, 3)  (3, 3)
```

Example:
```cpp
src_pos = (10.25, 20.75)
base = (10, 20)
```

For each texel in the 6x6 region:
```cpp
dx = src_pos.x - sample_x;
dy = src_pos.y - sample_y;

wx = lanczos_weight(dx);
wy = lanczos_weight(dy);

w = wx * wy;
```

Normalized weighted sum:
```cpp
sum += fetch_pixel(sample_position) * w;
weight_sum += w;
color = sum / weight_sum;
```

### High level overview

1. Map output pixel to fractional source position
2. Pick the 6x6 source neighborhood
3. Compute a Lanczos weight for every source texel
4. Comput the weighted sum of all 36 samples
5. Normalize by total weight
6. Clamp final color

<br>

## Practical behavior

Lanczos usually produces sharper results than bilinear and often sharper than Catmull-Rom.

But because it uses sinc-like negative lobes, it can overshoot near sharp edges.

That can cause:

```txt
ringing
halos
values below 0
values above 1
```

That is why the shader ends with:

```glsl
return clamp(sum / weight_sum, 0.0, 1.0);
```

The clamp keeps the final color valid, but it does not remove the underlying ringing behavior.
