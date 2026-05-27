## 1D Catmull-Rom

Given four neighboring samples:
```
p0, p1, p2, p3
```

Build a cubic curve between p1 and p2. The curve is given by the following polynomial:
```
f(t) = a t^3 + b t^2 + c t + d
```

where:
```
t = 0 gives p1
t = 1 gives p2
```

So the constraints are:
```
f(0) = p1
f(1) = p2
f'(0) = (p2 - p0) / 2
f'(1) = (p3 - p1) / 2
```
( `/ 2`: because samples are evenly spaced out at unit distances from each other)

The shader function:
```glsl
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
```
is just the solved polynomial form of those four constraints.

The shader returns:
```
f(t) = a t^3 + b t^2 + c t + d
```
where:
```
d = p1
c = 0.5 * (p2 - p0)
b = 0.5 * (2p0 - 5p1 + 4p2 - p3)
a = 0.5 * (-p0 + 3p1 - 3p2 + p3)
```

<br>

## 2D Catmull-Rom

Example:
```cpp
src_pos = (10.25, 20.75)
base = (10, 20)
f.x  = 0.25
f.y  = 0.75
```

The shader grabs a 4x4 neighborhood around the source relative to base:
```
(-1,-1)  (0,-1)  (1,-1)  (2,-1)
(-1, 0)  (0, 0)  (1, 0)  (2, 0)
(-1, 1)  (0, 1)  (1, 1)  (2, 1)
(-1, 2)  (0, 2)  (1, 2)  (2, 2)
```


For each row, the shader performs a 1D Catmull-Rom interpolation in x:
```cpp
vec4 row0 = catmull_rom(..., f.x);
vec4 row1 = catmull_rom(..., f.x);
vec4 row2 = catmull_rom(..., f.x);
vec4 row3 = catmull_rom(..., f.x);
```

The shader then does another 1D Catmull-Rom interpolation in y:
```cpp
vec4 color = catmull_rom(row0, row1, row2, row3, f.y);
```

So 2D cubic interpolation is:
```
4 horizontal cubic evaluations
1 vertical cubic evaluation
```