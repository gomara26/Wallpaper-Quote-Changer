#!/usr/bin/env python3
"""
Test script to diagnose wallpaper setting issues
"""
import subprocess
import sys
from pathlib import Path

# Get the wallpaper path
wallpaper_dir = Path.home() / "Library" / "Application Support" / "WallpaperQuoteChanger"
wallpaper_path = wallpaper_dir / "current_wallpaper.jpg"

if not wallpaper_path.exists():
    print(f"ERROR: Wallpaper file not found at {wallpaper_path}")
    print("Please run wallpaper_changer.py first to generate the wallpaper.")
    sys.exit(1)

posix_path = str(wallpaper_path.absolute())
print(f"Testing wallpaper setting with path: {posix_path}")
print("-" * 60)

# Test Method 1
print("\nMethod 1: Simple System Events")
script1 = f'tell application "System Events" to tell every desktop to set picture to POSIX file "{posix_path}"'
try:
    result = subprocess.run(
        ["osascript", "-e", script1],
        check=True,
        capture_output=True,
        text=True,
        timeout=5
    )
    print("✓ SUCCESS!")
    if result.stdout:
        print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Stderr: {result.stderr}")
except subprocess.CalledProcessError as e:
    print(f"✗ FAILED")
    print(f"Return code: {e.returncode}")
    if e.stdout:
        print(f"Stdout: {e.stdout}")
    if e.stderr:
        print(f"Stderr: {e.stderr}")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Test Method 2
print("\nMethod 2: Multi-line System Events")
script2 = f'''tell application "System Events"
    set desktopCount to count of desktops
    repeat with i from 1 to desktopCount
        tell desktop i
            set picture to POSIX file "{posix_path}"
        end tell
    end repeat
end tell'''
try:
    result = subprocess.run(
        ["osascript", "-e", script2],
        check=True,
        capture_output=True,
        text=True,
        timeout=5
    )
    print("✓ SUCCESS!")
    if result.stdout:
        print(f"Output: {result.stdout}")
    if result.stderr:
        print(f"Stderr: {result.stderr}")
except subprocess.CalledProcessError as e:
    print(f"✗ FAILED")
    print(f"Return code: {e.returncode}")
    if e.stdout:
        print(f"Stdout: {e.stdout}")
    if e.stderr:
        print(f"Stderr: {e.stderr}")
except Exception as e:
    print(f"✗ ERROR: {e}")

print("\n" + "-" * 60)
print("\nIf both methods failed, you may need to:")
print("1. Grant Terminal/Automator permission in System Settings > Privacy & Security > Automation")
print("2. Or set the wallpaper manually using Finder")





