"""Record demo.html as a GIF using Playwright screenshots + Pillow."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

DEMO_HTML = Path(__file__).parent / "demo.html"
OUTPUT_GIF = Path(__file__).parent / "demo.gif"
FRAMES_DIR = Path(__file__).parent / "frames"


async def capture_frames():
    FRAMES_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 920, "height": 680})
        await page.goto(f"file://{DEMO_HTML.resolve()}")

        # Capture frames over the animation duration
        frame_count = 0
        total_duration_ms = 28000  # ~28 seconds for full animation
        interval_ms = 200  # capture every 200ms

        for t in range(0, total_duration_ms, interval_ms):
            await page.wait_for_timeout(interval_ms)
            path = FRAMES_DIR / f"frame_{frame_count:04d}.png"
            await page.screenshot(path=str(path))
            frame_count += 1

        await browser.close()
        print(f"Captured {frame_count} frames")
        return frame_count


def create_gif(frame_count):
    frames = []
    for i in range(frame_count):
        path = FRAMES_DIR / f"frame_{i:04d}.png"
        if path.exists():
            img = Image.open(path).convert("RGBA")
            # Convert to RGB for GIF
            rgb = Image.new("RGB", img.size, (13, 17, 23))
            rgb.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            frames.append(rgb)

    if frames:
        # Remove duplicate consecutive frames to reduce file size
        deduped = [frames[0]]
        durations = [200]
        for i in range(1, len(frames)):
            if list(frames[i].getdata()) != list(frames[i-1].getdata()):
                deduped.append(frames[i])
                durations.append(200)
            else:
                durations[-1] += 200

        deduped[0].save(
            str(OUTPUT_GIF),
            save_all=True,
            append_images=deduped[1:],
            duration=durations,
            loop=0,
            optimize=True,
        )
        print(f"GIF saved to {OUTPUT_GIF} ({len(deduped)} unique frames)")
    else:
        print("No frames captured!")


async def main():
    frame_count = await capture_frames()
    create_gif(frame_count)

    # Cleanup frames
    import shutil
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
