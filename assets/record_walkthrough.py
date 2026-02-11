"""Record walkthrough.html as a GIF — captures each section auto-advancing."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

ASSETS = Path(__file__).parent
HTML_FILE = ASSETS / "walkthrough.html"
OUTPUT_GIF = ASSETS / "walkthrough.gif"
FRAMES_DIR = ASSETS / "wframes"


async def capture_frames():
    FRAMES_DIR.mkdir(exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 940, "height": 700})
        await page.goto(f"file://{HTML_FILE.resolve()}")

        frame_count = 0
        # 6 sections × 8s each = 48s total, capture at 250ms intervals
        total_ms = 49000
        interval_ms = 250

        for t in range(0, total_ms, interval_ms):
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
            rgb = Image.new("RGB", img.size, (13, 17, 23))
            rgb.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
            frames.append(rgb)

    if frames:
        # Deduplicate consecutive identical frames
        deduped = [frames[0]]
        durations = [250]
        for i in range(1, len(frames)):
            if list(frames[i].getdata()) != list(frames[i - 1].getdata()):
                deduped.append(frames[i])
                durations.append(250)
            else:
                durations[-1] += 250

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

    import shutil
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
