import csv
import imageio.v3 as iio
import json
import math
import numpy as np
from pathlib import Path
from PIL import Image

from src.spatial_SR import apply_spatial_sr


def load_config(path="config_SR_experiment.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_input_images(input_path):
    path = Path(input_path)

    if path.is_file():
        return [path]

    extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tga", ".webp"}
    return sorted(p for p in path.iterdir() if p.suffix.lower() in extensions)


def load_image(path):
    image = Image.open(path).convert("RGBA")
    return np.array(image, dtype=np.uint8)


def downsample_image(image, sr_ratio):
    input_h, input_w, _ = image.shape

    down_w = max(1, int(round(input_w / sr_ratio)))
    down_h = max(1, int(round(input_h / sr_ratio)))

    pil_image = Image.fromarray(image, mode="RGBA")
    pil_image = pil_image.resize((down_w, down_h), Image.Resampling.LANCZOS)

    return np.array(pil_image, dtype=np.uint8)


def resize_to_match(image, target_shape):
    target_h, target_w, _ = target_shape

    if image.shape[:2] == (target_h, target_w):
        return image

    pil_image = Image.fromarray(image, mode="RGBA")
    pil_image = pil_image.resize((target_w, target_h), Image.Resampling.BICUBIC)

    return np.array(pil_image, dtype=np.uint8)


def compute_psnr(reference, test):
    reference = reference[:, :, :3].astype(np.float32)
    test = test[:, :, :3].astype(np.float32)

    mse = np.mean((reference - test) ** 2)

    if mse == 0.0:
        return math.inf

    return 20.0 * math.log10(255.0 / math.sqrt(mse))


def save_image(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    image = Image.fromarray(data, mode="RGBA")

    if path.suffix.lower() in {".jpg", ".jpeg"}:
        image = image.convert("RGB")

    image.save(path)


def stitch_video(image_paths, output_path, fps):
    if not image_paths:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    frames = []
    for path in image_paths:
        frame = iio.imread(path)
        if frame.shape[2] == 4:
            frame = frame[:, :, :3]
        frames.append(frame)

    iio.imwrite(output_path, frames, fps=fps)


def write_psnr_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["image", "psnr"])
        writer.writerows(rows)


def run_spatial_sr(config):
    input_path = config["input_path"]
    output_path = Path(config["output_path"])
    test_name = config["test_name"]
    sr_type = config["sr_type"]
    sr_ratio = float(config["sr_ratio"])
    fps = int(config.get("fps", 30))
    create_video = bool(config.get("create_video", False))

    test_output_path = output_path / test_name
    image_paths = list_input_images(input_path)

    written_images = []
    psnr_rows = []

    for image_path in image_paths:
        original_image = load_image(image_path)
        downsampled_image = downsample_image(original_image, sr_ratio)

        output_image = apply_spatial_sr(downsampled_image, sr_type, sr_ratio)
        output_image = resize_to_match(output_image, original_image.shape)

        psnr = compute_psnr(original_image, output_image)
        psnr_rows.append([image_path.name, psnr])

        output_file = test_output_path / image_path.name
        save_image(output_file, output_image)
        written_images.append(output_file)

    psnr_csv_path = test_output_path / f"PSNR_{test_name}.csv"
    write_psnr_csv(psnr_csv_path, psnr_rows)

    if create_video:
        video_path = test_output_path / f"{test_name}.mp4"
        stitch_video(written_images, video_path, fps)


def run_temporal_sr(config):
    raise NotImplementedError("Temporal SR is not supported yet.")


def run_sr_test(config):
    sr_mode = config.get("sr_mode", "spatial")

    match sr_mode:
        case "spatial":
            run_spatial_sr(config)
        case "temporal":
            run_temporal_sr(config)
        case _:
            raise ValueError(f"Unknown SR mode: {sr_mode}")


def main():
    config = load_config()
    run_sr_test(config)


if __name__ == "__main__":
    main()