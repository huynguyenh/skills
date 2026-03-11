#!/usr/bin/env python3
"""
Optimize video files: convert GIF/MOV/MP4/AVI to compressed H.264 MP4.

Handles format conversion, compression, scaling, and trimming.
Reports before/after file sizes with reduction percentage.

Usage:
  python3 optimize_video.py input.gif --output output.mp4
  python3 optimize_video.py input.mov --crf 28 --max-width 1280
  python3 optimize_video.py input.mp4 --trim-start 2 --trim-end 1
"""

import argparse
import json
import os
import subprocess
import sys


def get_media_info(path):
    """Get media file metadata via ffprobe."""
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def format_size(bytes_val):
    """Format bytes as human-readable string."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    else:
        return f"{bytes_val / (1024 * 1024):.1f} MB"


def main():
    parser = argparse.ArgumentParser(
        description="Optimize video to compressed MP4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s recording.gif -o demo.mp4           Convert GIF to MP4
  %(prog)s raw.mov --crf 28 --max-width 1280   Compress and scale down
  %(prog)s video.mp4 --trim-start 2            Trim first 2 seconds
        """,
    )
    parser.add_argument("input", help="Input video or GIF file")
    parser.add_argument(
        "--output", "-o",
        help="Output MP4 path (default: ~/ws/docs/<name>_optimized.mp4)",
    )
    parser.add_argument(
        "--crf", type=int, default=23,
        help="Quality level: 18=high quality, 23=balanced, 28=small file (default: 23)",
    )
    parser.add_argument(
        "--max-width", type=int,
        help="Scale down to this max width, preserving aspect ratio",
    )
    parser.add_argument(
        "--resolution",
        help="Force exact resolution, e.g. 1920x1080 (adds letterboxing if needed)",
    )
    parser.add_argument(
        "--trim-start", type=float, default=0,
        help="Remove N seconds from start",
    )
    parser.add_argument(
        "--trim-end", type=float, default=0,
        help="Remove N seconds from end",
    )
    parser.add_argument(
        "--fps", type=int,
        help="Override output framerate",
    )
    parser.add_argument(
        "--preset", default="medium",
        choices=["ultrafast", "fast", "medium", "slow"],
        help="Encoding speed vs compression (default: medium)",
    )
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: {args.input} not found", file=sys.stderr)
        return 1

    input_size = os.path.getsize(args.input)
    input_ext = os.path.splitext(args.input)[1].lower()

    # Default output path
    if not args.output:
        base = os.path.splitext(os.path.basename(args.input))[0]
        args.output = os.path.expanduser(f"~/ws/docs/{base}_optimized.mp4")

    # Expand ~ in output path
    args.output = os.path.expanduser(args.output)

    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # Build ffmpeg command
    cmd = ["ffmpeg", "-hide_banner"]

    # Trim start
    if args.trim_start > 0:
        cmd.extend(["-ss", str(args.trim_start)])

    cmd.extend(["-i", args.input])

    # Trim end
    if args.trim_end > 0:
        info = get_media_info(args.input)
        if info and "format" in info:
            duration = float(info["format"].get("duration", 0))
            if duration > 0:
                effective_end = duration - args.trim_end - args.trim_start
                if effective_end > 0:
                    cmd.extend(["-t", str(effective_end)])

    # Video filters
    vf_parts = []

    if args.resolution:
        w, h = args.resolution.split("x")
        vf_parts.append(
            f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
            f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"
        )
    elif args.max_width:
        vf_parts.append(f"scale='min({args.max_width},iw):-2'")
    elif input_ext == ".gif":
        # GIF dimensions might be odd — H.264 needs even dimensions
        vf_parts.append("scale=trunc(iw/2)*2:trunc(ih/2)*2")

    if vf_parts:
        cmd.extend(["-vf", ",".join(vf_parts)])

    # FPS override
    if args.fps:
        cmd.extend(["-r", str(args.fps)])

    # Encoding settings
    cmd.extend([
        "-c:v", "libx264",
        "-preset", args.preset,
        "-crf", str(args.crf),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
    ])

    # Audio handling
    if input_ext in (".gif", ".png", ".jpg", ".jpeg", ".webp"):
        cmd.append("-an")  # No audio for image-based inputs
    else:
        cmd.extend(["-c:a", "aac", "-b:a", "128k"])

    cmd.extend(["-y", args.output])

    # Run ffmpeg
    print(f"Input:    {args.input} ({format_size(input_size)})")
    print(f"Encoding: CRF={args.crf}, preset={args.preset}")

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Show last part of stderr for diagnostics
        stderr_tail = result.stderr[-1000:] if result.stderr else "no error output"
        print(f"ffmpeg failed:\n{stderr_tail}", file=sys.stderr)
        return 1

    # Report results
    output_size = os.path.getsize(args.output)
    reduction = (1 - output_size / input_size) * 100 if input_size > 0 else 0

    # Get output duration
    info = get_media_info(args.output)
    duration_str = "unknown"
    resolution_str = "unknown"
    if info:
        if "format" in info:
            dur = float(info["format"].get("duration", 0))
            duration_str = f"{dur:.1f}s"
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                resolution_str = f"{stream['width']}x{stream['height']}"
                break

    print(f"Output:   {args.output} ({format_size(output_size)})")
    print(f"Duration: {duration_str}")
    print(f"Resolution: {resolution_str}")
    print(f"Reduction: {reduction:.0f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
