#!/usr/bin/env python3
"""Run a local Playwright smoke test against the generated tool gallery."""

from __future__ import annotations

import argparse
import functools
import http.server
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


def browser_binary() -> Path:
    candidates = sorted(
        (Path.home() / "Library/Caches/ms-playwright").glob(
            "chromium-*/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        ),
        reverse=True,
    )
    if not candidates:
        raise SystemExit("Playwright Chromium is not installed")
    return candidates[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output_dir or Path(tempfile.mkdtemp(prefix="wutpack-gallery-qa-"))
    output.mkdir(parents=True, exist_ok=True)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    errors: list[str] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                executable_path=str(browser_binary()),
                args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
            )
            for name, width, height in [
                ("desktop", 1440, 960),
                ("compact-desktop", 1024, 820),
                ("tablet", 768, 900),
                ("mobile", 375, 812),
            ]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"{base}/index.html", wait_until="networkidle")
                assert page.locator(".tool-example-link").count() == 53
                page.locator("#tool-gallery").scroll_into_view_if_needed()
                page.screenshot(path=str(output / f"gallery-{name}.png"))
                overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
                if overflow:
                    offenders = page.evaluate(
                        """[...document.querySelectorAll('body *')]
                          .map(element => ({tag: element.tagName, cls: element.className, right: element.getBoundingClientRect().right, width: element.getBoundingClientRect().width}))
                          .filter(item => item.right > document.documentElement.clientWidth + 1 || item.width > document.documentElement.clientWidth + 1)
                          .slice(0, 8)"""
                    )
                    raise AssertionError(f"horizontal overflow at {width}px: {offenders}")
                page.close()

            search_page = browser.new_page(viewport={"width": 1200, "height": 820})
            search_page.goto(f"{base}/index.html#tool-gallery", wait_until="networkidle")
            search_page.locator("[data-tool-search]").fill("OCR")
            assert search_page.locator(".tool-example-link:visible").count() == 1
            assert search_page.locator("[data-tool-count]").inner_text() == "1 tool"
            search_page.screenshot(path=str(output / "gallery-search.png"))
            search_page.close()

            for slug, width, height in [("codex", 1440, 960), ("tesseract", 375, 812), ("ffmpeg", 1200, 820)]:
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(f"{base}/tool-examples/{slug}.html", wait_until="networkidle")
                assert page.locator("h1").inner_text().strip()
                broken_images = page.locator("img").evaluate_all(
                    "images => images.filter(image => !image.complete || image.naturalWidth === 0).length"
                )
                assert broken_images == 0, f"{slug}: {broken_images} broken images"
                overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
                assert not overflow, f"{slug}: horizontal overflow"
                page.screenshot(path=str(output / f"proof-{slug}.png"))
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    if errors:
        raise SystemExit("browser page errors:\n" + "\n".join(errors))
    print(f"Tool gallery browser checks passed. Screenshots: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
