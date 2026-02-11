"""Render Copilot CLI session HTML files to PNG screenshots."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ASSETS = Path(__file__).parent

PAGES = [
    ("copilot-explain.html", "copilot-explain.png"),
    ("copilot-suggest.html", "copilot-suggest.png"),
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        for html_file, png_file in PAGES:
            page = await browser.new_page(viewport={"width": 960, "height": 800})
            await page.goto(f"file://{(ASSETS / html_file).resolve()}")
            await page.wait_for_timeout(2000)  # wait for fonts

            # Get the .term element bounding box for tight crop
            term = page.locator(".term")
            box = await term.bounding_box()
            if box:
                await page.screenshot(
                    path=str(ASSETS / png_file),
                    clip={
                        "x": max(0, box["x"] - 20),
                        "y": max(0, box["y"] - 20),
                        "width": box["width"] + 40,
                        "height": box["height"] + 40,
                    },
                )
            else:
                await page.screenshot(path=str(ASSETS / png_file))

            print(f"✓ {png_file}")
            await page.close()

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
