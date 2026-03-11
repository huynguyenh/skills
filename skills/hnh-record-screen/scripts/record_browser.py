#!/usr/bin/env python3
"""
Record a browser session as video using Playwright.

Takes a JSON plan of actions and produces:
1. A WebM video recording of the entire session
2. A moments.json file with timestamps of each action

Usage:
  python3 record_browser.py plan.json --output recording.webm
  python3 record_browser.py plan.json --output recording.webm --headed
"""

import argparse
import json
import os
import sys
import time


def run_recording(plan, output_path, moments_path, headed=False, viewport=None):
    """Execute a recording plan and save the video."""
    from playwright.sync_api import sync_playwright

    if viewport is None:
        viewport = plan.get("viewport", {"width": 1920, "height": 1080})

    video_dir = os.path.dirname(output_path) or "/tmp"
    os.makedirs(video_dir, exist_ok=True)

    moments = []
    start_time = None

    def record_moment(action_type, label, x=None, y=None):
        elapsed = int((time.time() - start_time) * 1000) if start_time else 0
        moments.append({
            "time_ms": elapsed,
            "type": action_type,
            "label": label,
            "x": x,
            "y": y,
        })

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not headed,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            viewport=viewport,
            record_video_dir=video_dir,
            record_video_size=viewport,
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()
        start_time = time.time()

        # Navigate to starting URL if provided
        start_url = plan.get("url")
        if start_url:
            page.goto(start_url, wait_until="domcontentloaded")
            record_moment("navigate", f"Open {start_url}")
            page.wait_for_timeout(int(plan.get("initial_wait", 2) * 1000))

        # Execute each step
        for i, step in enumerate(plan.get("steps", [])):
            action = step["action"]
            desc = step.get("description", step.get("label", f"Step {i+1}"))
            wait_ms = int(step.get("wait", 1.5) * 1000)

            try:
                if action == "navigate":
                    url = step["url"]
                    page.goto(url, wait_until="domcontentloaded")
                    record_moment("navigate", desc)

                elif action == "click":
                    selector = step.get("selector")
                    text = step.get("text")
                    if selector:
                        el = page.locator(selector).first
                    elif text:
                        el = page.get_by_text(text).first
                    else:
                        print(f"  Step {i+1}: click needs 'selector' or 'text'", file=sys.stderr)
                        continue
                    box = el.bounding_box()
                    x = int(box["x"] + box["width"] / 2) if box else None
                    y = int(box["y"] + box["height"] / 2) if box else None
                    el.click()
                    record_moment("click", desc, x, y)

                elif action == "type":
                    selector = step.get("selector")
                    text = step["text"]
                    delay = step.get("type_delay", 80)
                    if selector:
                        page.locator(selector).first.click()
                        page.wait_for_timeout(200)
                    page.keyboard.type(text, delay=delay)
                    record_moment("type", desc)

                elif action == "press":
                    key = step["key"]
                    page.keyboard.press(key)
                    record_moment("press", desc)

                elif action == "scroll":
                    direction = step.get("direction", "down")
                    amount = step.get("amount", 3)
                    delta = amount * 120 * (-1 if direction == "up" else 1)
                    page.mouse.wheel(0, delta)
                    record_moment("scroll", desc)

                elif action == "hover":
                    selector = step.get("selector")
                    text = step.get("text")
                    if selector:
                        el = page.locator(selector).first
                    elif text:
                        el = page.get_by_text(text).first
                    else:
                        continue
                    box = el.bounding_box()
                    if box:
                        el.hover()
                    record_moment("hover", desc)

                elif action == "wait":
                    # Extra wait, on top of the step wait
                    extra = int(step.get("duration", 2) * 1000)
                    page.wait_for_timeout(extra)
                    record_moment("wait", desc)

                elif action == "screenshot":
                    # Take a screenshot (doesn't affect video, just for reference)
                    path = step.get("path", f"/tmp/screenshot_{i}.png")
                    page.screenshot(path=path)
                    record_moment("screenshot", desc)

                else:
                    print(f"  Step {i+1}: unknown action '{action}'", file=sys.stderr)
                    continue

                print(f"  [{i+1}/{len(plan['steps'])}] {desc}")

            except Exception as e:
                print(f"  [{i+1}] Error on '{desc}': {e}", file=sys.stderr)
                record_moment("error", f"Failed: {desc}")

            # Wait between steps
            page.wait_for_timeout(wait_ms)

        # Final pause to capture ending state
        page.wait_for_timeout(2000)
        record_moment("end", "Recording complete")

        # Close context to finalize video
        video_path = page.video.path()
        context.close()
        browser.close()

    # Move video to desired output path
    if video_path and os.path.exists(video_path):
        if os.path.abspath(video_path) != os.path.abspath(output_path):
            import shutil
            shutil.move(video_path, output_path)
        size = os.path.getsize(output_path)
        print(f"\nVideo saved: {output_path} ({size / 1024 / 1024:.1f} MB)")
    else:
        print("Warning: video file not found", file=sys.stderr)

    # Save moments
    with open(moments_path, "w") as f:
        json.dump(moments, f, indent=2)
    print(f"Moments saved: {moments_path} ({len(moments)} events)")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Record browser session as video")
    parser.add_argument("plan", help="JSON plan file or '-' for stdin")
    parser.add_argument("--output", "-o", default="/tmp/recording.webm",
                        help="Output video path (default: /tmp/recording.webm)")
    parser.add_argument("--moments", "-m",
                        help="Output moments.json path (default: <output>.moments.json)")
    parser.add_argument("--headed", action="store_true",
                        help="Show browser window (default: headless)")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height")
    args = parser.parse_args()

    # Read plan
    if args.plan == "-":
        plan = json.load(sys.stdin)
    else:
        with open(args.plan) as f:
            plan = json.load(f)

    # Defaults
    if not args.moments:
        base = os.path.splitext(args.output)[0]
        args.moments = f"{base}.moments.json"

    viewport = {"width": args.width, "height": args.height}

    print(f"Recording: {plan.get('title', 'Untitled')}")
    print(f"Steps: {len(plan.get('steps', []))}")
    print(f"Viewport: {viewport['width']}x{viewport['height']}")
    print(f"Mode: {'headed' if args.headed else 'headless'}")
    print()

    run_recording(plan, args.output, args.moments, args.headed, viewport)


if __name__ == "__main__":
    main()
