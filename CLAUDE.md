# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Install deps: `pip3 install -r requirements.txt` (only dep is Pillow)
- Run: `./change_wallpaper.sh` or `python3 wallpaper_changer.py`

There is no test suite, linter, or build step.

## Architecture

Single-script macOS app (`wallpaper_changer.py`) that generates a quote wallpaper per display and sets it via AppleScript. The flow in `main()`:

1. `load_quotes()` reads `quotes.txt`. Lines containing ` || ` are split into multiple quotes that share a single wallpaper (rendered stacked). Each line becomes a `list[str]`.
2. `get_all_displays()` shells out to `system_profiler SPDisplaysDataType` and parses the indented text output to extract per-display name + resolution. The parser is indentation-sensitive (display names live at indent 8–12) — be careful when editing. Falls back to `DEFAULT_WIDTH/HEIGHT` on any failure.
3. `random.sample` picks a distinct quote-line per display (with replacement only if there are more displays than quotes).
4. `create_wallpaper()` builds the image: uses `Picture1.jpg` (sibling of the script, hardcoded via `BACKGROUND_IMAGE`) cover-fitted with a dark overlay, else a blue gradient. Tries Helvetica/Arial system fonts, falls back to PIL default. Font size is `min(width, height) // 20`.
5. Each image is written to `~/Library/Application Support/WallpaperQuoteChanger/wallpaper_display{N}_{timestamp}.jpg`. A unique timestamped filename is required because macOS caches wallpapers by path — reusing a name causes the desktop not to refresh.
6. `set_wallpaper()` runs `osascript` with three fallback AppleScript variants (direct `tell desktop N`, iterated `repeat`, and POSIX-file-as-alias). Each is wrapped with a 5s timeout and stderr is inspected because `osascript` can return success while logging an error.
7. `cleanup_old_wallpapers()` keeps the 5 newest files per display, grouping by the `_display{N}_` token in the filename (older format files without that token are grouped under `'all'`).
8. A `current_wallpaper.jpg` symlink to display 1's image is maintained for backward compat with the old single-display layout.

## Configuration

User-tunable constants live at the top of `wallpaper_changer.py` (not env vars or CLI flags): `BACKGROUND_IMAGE`, `TEXT_COLOR`, `SHADOW_COLOR`, `DEFAULT_WIDTH/HEIGHT`. The README documents these for end users — keep README examples in sync when changing defaults.
