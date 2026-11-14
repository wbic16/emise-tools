#!/usr/bin/env python3
"""Playwright screen test for a published page (simple-html-publish skill).

Loads the live URL in headless Chromium, hard-reloads, scrolls to the
very bottom, and asserts on the RENDERED text:
  --expect TEXT   key UI text that must be visible (repeatable)
  --forbid TEXT   text that must NOT be visible — leaked source,
                  stray markup, error strings (repeatable)
  --tail TEXT     the visible page text must END with this text
                  (catches anything rendered below the footer)
  --shot PATH     save a full-page screenshot here
Exit 0 = PASS, 1 = FAIL (offending text printed).
"""
import argparse
import sys

from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--expect", action="append", default=[])
    ap.add_argument("--forbid", action="append", default=[])
    ap.add_argument("--tail", default=None)
    ap.add_argument("--shot", default=None)
    args = ap.parse_args()

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(args.url, wait_until="networkidle")
        page.reload(wait_until="networkidle", bypass_cache=True)
        # scroll to the very bottom, in steps, letting lazy content settle
        page.evaluate("""async () => {
          await new Promise(done => {
            let y = 0;
            const t = setInterval(() => {
              y += 600; scrollTo(0, y);
              if (y >= document.body.scrollHeight) { clearInterval(t); done(); }
            }, 60);
          });
          scrollTo(0, document.body.scrollHeight);
        }""")
        page.wait_for_timeout(400)
        text = page.evaluate("document.body.innerText")
        if args.shot:
            page.screenshot(path=args.shot, full_page=True)
        browser.close()

    failures = []
    for needle in args.expect:
        if needle not in text:
            failures.append(f"EXPECT missing: {needle!r}")
    for needle in args.forbid:
        if needle in text:
            i = text.find(needle)
            failures.append(f"FORBID present: {needle!r} …context: {text[max(0,i-60):i+80]!r}")
    if args.tail and not text.rstrip().endswith(args.tail):
        failures.append(f"TAIL mismatch: page text ends with {text.rstrip()[-120:]!r}, expected tail {args.tail!r}")

    if failures:
        print("SCREEN TEST FAIL —", args.url)
        for f in failures:
            print(" -", f)
        return 1
    print(f"SCREEN TEST PASS — {args.url} (visible text {len(text)} chars; "
          f"{len(args.expect)} expect, {len(args.forbid)} forbid, tail {'ok' if args.tail else 'n/a'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
