# SHREK - Super (Hackable) Resolution (Experimentation) (Kit)

## Setup

### Automatic (MacOS and Linux)
```bash
source setup.sh
```

### Manual (Windows)
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Running an experiment

1. Configure your experiment by modifying the `config_SR_experiment.json` file. <br> Example:
    ```json
    {
        "input_path": "./input/synthetic_data",
        "output_path": "./output",
        "test_name": "interpolation_x2",
        "sr_mode": "spatial",
        "sr_type": "interpolation",
        "sr_ratio": 2.0,
        "create_video": true,
        "fps": 30
    }
    ```
2. Run `run_SR_experiment.py`

### What does `run_SR_experiment` do?

1. Take each image in a sequence of inputs....
2. Downscale the image using lanczos based on the SR ratio
3. Upscale the image back to the original size
4. Compute PSNR by comparing the original and the upscaled image (Stores PSNR for each frame in a csv)
5. (Optional) Generates a video

## (Optional) Generating synthetic data

Renders a procedural scene and writes the G-Buffer data to the disk.

To use it simply configure `config_synthetic_data.json` and run `generate_synthetic_data.py`

This writes the generated data to: `<output_path>/color_<frameNum>.png`

## Potential questions?

Q: Why does the project use fragment shaders instead of compute shaders?
A: I have a MacBook Air M2 and it does not support OpenGL 4.3, nor could I get slangpy working. I can't be bothered to fix the issues with slangpy. (26 May 2026)