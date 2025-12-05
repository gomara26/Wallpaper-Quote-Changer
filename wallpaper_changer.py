#!/usr/bin/env python3
"""
Mac Wallpaper Quote Changer
Randomly selects a quote and sets it as the macOS wallpaper.
"""

import os
import random
import re
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Configuration
QUOTES_FILE = Path(__file__).parent / "quotes.txt"
WALLPAPER_DIR = Path.home() / "Library" / "Application Support" / "WallpaperQuoteChanger"
WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
# Use unique filename each time so macOS sees it as a new image
OUTPUT_IMAGE = WALLPAPER_DIR / f"wallpaper_{int(time.time())}.jpg"
# Also create a symlink for easy access
SYMLINK_IMAGE = WALLPAPER_DIR / "current_wallpaper.jpg"
# Background image (optional) - set to None to use gradient, or path to your image file
# Examples: Path(__file__).parent / "background.jpg" or Path.home() / "Pictures" / "my_bg.jpg"
try:
    # Use a relative path (background.jpg in the same directory as this script)
    _bg_candidate = Path(__file__).parent / "Picture1.jpg"
    BACKGROUND_IMAGE = str(_bg_candidate) if _bg_candidate.exists() else None
except Exception:
    BACKGROUND_IMAGE = None  # Fallback to gradient if any error occurs

# Text color (RGB values from 0-255)
# Examples: (255, 255, 255) = white, (0, 0, 0) = black, (255, 0, 0) = red, (0, 255, 0) = green, (255, 215, 0) = gold
TEXT_COLOR = (54, 54, 54)  # White (default)
SHADOW_COLOR = (0, 0, 0)  # Black shadow (for readability)

# Default wallpaper dimensions (will try to get screen resolution)
DEFAULT_WIDTH = 2560
DEFAULT_HEIGHT = 1440


def get_screen_resolution():
    """Get the current screen resolution using system_profiler.
    Returns a single display resolution (for backward compatibility)."""
    displays = get_all_displays()
    if displays:
        return displays[0]['width'], displays[0]['height']
    return DEFAULT_WIDTH, DEFAULT_HEIGHT


def get_all_displays():
    """Get all connected displays and their resolutions.
    Returns a list of dicts with 'width', 'height', and 'name' keys."""
    displays = []
    try:
        result = subprocess.run(
            ["system_profiler", "SPDisplaysDataType"],
            capture_output=True,
            text=True,
            check=True
        )
        
        current_display = {}
        in_displays_section = False
        previous_line = None
        previous_indent = 0
        
        for line in result.stdout.split('\n'):
            stripped = line.strip()
            # Count leading spaces to determine indentation level
            indent_level = len(line) - len(line.lstrip())
            
            # Look for "Displays:" section
            if stripped == 'Displays:':
                in_displays_section = True
                previous_line = None
                previous_indent = 0
                continue
            
            # If we're in the Displays section
            if in_displays_section:
                # Look for Resolution line (usually indented under display name)
                if 'Resolution:' in stripped:
                    # The display name should be the previous line that ends with ':'
                    # and is at a similar or less indented level
                    if previous_line and previous_line.strip().endswith(':'):
                        display_name = previous_line.strip().rstrip(':').strip()
                        if display_name:
                            # Save previous display if it has resolution
                            if current_display and 'width' in current_display:
                                displays.append(current_display)
                            # Start new display
                            current_display = {'name': display_name}
                    
                    # Parse resolution: "3440 x 1440" or "3840 x 2160"
                    # Extract numbers from the resolution string
                    # Match pattern like "3440 x 1440" or "3840x2160"
                    match = re.search(r'(\d+)\s*x\s*(\d+)', stripped, re.IGNORECASE)
                    if match:
                        try:
                            current_display['width'] = int(match.group(1))
                            current_display['height'] = int(match.group(2))
                        except ValueError:
                            pass
                    previous_line = None  # Reset after processing resolution
                    continue
                
                # Track previous line for display name detection
                # Only track lines that end with ':' and are at display name indent level (8-10 spaces)
                if stripped and stripped.endswith(':') and 8 <= indent_level <= 12:
                    previous_line = line  # Keep original line with indentation info
                    previous_indent = indent_level
                elif indent_level < 8 and stripped:
                    # If we hit a less-indented line, we might be leaving the Displays section
                    if current_display and 'width' in current_display:
                        displays.append(current_display)
                        current_display = {}
                    in_displays_section = False
                    previous_line = None
        
        # Don't forget the last display
        if current_display and 'width' in current_display:
            displays.append(current_display)
            
    except Exception as e:
        print(f"Warning: Could not detect displays ({e}), using default")
    
    # If no displays found, return default
    if not displays:
        displays = [{'name': 'Default Display', 'width': DEFAULT_WIDTH, 'height': DEFAULT_HEIGHT}]
    
    return displays


def load_quotes():
    """Load quotes from the quotes.txt file.
    Supports two formats:
    - Single quote per line: "Quote here"
    - Multiple quotes on same wallpaper: "Quote 1 || Quote 2"
    """
    if not QUOTES_FILE.exists():
        print(f"Error: {QUOTES_FILE} not found!")
        sys.exit(1)
    
    with open(QUOTES_FILE, 'r', encoding='utf-8') as f:
        quotes = []
        for line in f:
            line = line.strip()
            if line:
                # Check if line contains || separator for multiple quotes
                if ' || ' in line:
                    # Split by || and treat as a list of quotes for one wallpaper
                    quote_parts = [q.strip() for q in line.split('||')]
                    quotes.append(quote_parts)
                else:
                    # Single quote
                    quotes.append([line])
    
    if not quotes:
        print("Error: No quotes found in quotes.txt!")
        sys.exit(1)
    
    return quotes


def wrap_text(text, max_width, font, draw):
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = bbox[2] - bbox[0]
        
        if text_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def create_wallpaper(quotes, width, height):
    """Create a wallpaper image with the quote overlaid."""
    # Load background image if specified, otherwise create gradient
    if BACKGROUND_IMAGE and Path(BACKGROUND_IMAGE).exists():
        try:
            # Load and resize background image
            bg = Image.open(BACKGROUND_IMAGE)
            # Resize to cover the screen (maintain aspect ratio, crop if needed)
            bg_ratio = bg.width / bg.height
            screen_ratio = width / height
            
            if bg_ratio > screen_ratio:
                # Background is wider - fit to height
                new_height = height
                new_width = int(bg.width * (height / bg.height))
            else:
                # Background is taller - fit to width
                new_width = width
                new_height = int(bg.height * (width / bg.width))
            
            bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create canvas and paste background (centered, cropping if needed)
            image = Image.new('RGB', (width, height), color=(0, 0, 0))
            x_offset = (width - new_width) // 2
            y_offset = (height - new_height) // 2
            image.paste(bg, (x_offset, y_offset))
            
            # Add a semi-transparent dark overlay for better text readability
            overlay = Image.new('RGBA', (width, height), (0, 0, 0, 100))  # 100/255 opacity
            image_rgba = image.convert('RGBA')
            image = Image.alpha_composite(image_rgba, overlay).convert('RGB')
            
            draw = ImageDraw.Draw(image)
        except Exception as e:
            print(f"Warning: Could not load background image ({e}), using gradient instead")
            # Fall back to gradient
            image = Image.new('RGB', (width, height), color=(20, 30, 50))
            draw = ImageDraw.Draw(image)
            # Create a subtle gradient effect
            for y in range(height):
                ratio = y / height
                r = int(20 + (10 * ratio))
                g = int(30 + (20 * ratio))
                b = int(50 + (30 * ratio))
                draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        # Create a gradient background (dark blue to darker blue)
        image = Image.new('RGB', (width, height), color=(20, 30, 50))
        draw = ImageDraw.Draw(image)
        
        # Create a subtle gradient effect
        for y in range(height):
            ratio = y / height
            r = int(20 + (10 * ratio))
            g = int(30 + (20 * ratio))
            b = int(50 + (30 * ratio))
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Try to use a nice font, fallback to default
    try:
        # Try to use system fonts
        font_paths = [
            "/System/Library/Fonts/HelveticaNeue.ttc",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
        font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                # Load font with appropriate size
                font_size = min(width, height) // 20
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Handle multiple quotes - quotes is now a list (can be 1 or more quotes)
    if isinstance(quotes, str):
        # Backward compatibility: if a single string is passed, convert to list
        quotes = [quotes]
    
    # Wrap text to fit on screen and collect all lines
    margin = width // 10
    max_text_width = width - (2 * margin)
    all_lines = []
    
    for quote_idx, quote in enumerate(quotes):
        # Wrap each quote
        quote_lines = wrap_text(quote, max_text_width, font, draw)
        all_lines.extend(quote_lines)
        
        # Add spacing between quotes (except after the last one)
        if quote_idx < len(quotes) - 1:
            # Add an empty line between quotes for visual separation
            all_lines.append("")  # Empty line for spacing
    
    # Calculate text dimensions
    line_height = draw.textbbox((0, 0), "A", font=font)[3] - draw.textbbox((0, 0), "A", font=font)[1]
    # Calculate total height including spacing between quotes
    total_text_height = sum(
        line_height * 1.2 if line else line_height * 0.6  # Less spacing for empty lines
        for line in all_lines
    )
    start_y = (height - total_text_height) // 2
    
    # Draw text with shadow for better readability
    text_color = TEXT_COLOR
    shadow_color = SHADOW_COLOR
    shadow_offset = 3
    
    current_y = start_y
    for line in all_lines:
        if line:  # Only draw non-empty lines
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_pos = (width - text_width) // 2
            
            # Draw shadow
            draw.text((x_pos + shadow_offset, current_y + shadow_offset), line, 
                     font=font, fill=shadow_color)
            # Draw main text
            draw.text((x_pos, current_y), line, font=font, fill=text_color)
            current_y += line_height * 1.2
        else:
            # Empty line for spacing between quotes
            current_y += line_height * 0.6
    
    return image


def cleanup_old_wallpapers():
    """Clean up old wallpaper files, keeping only the 5 most recent per display."""
    try:
        # Get all wallpaper files
        all_wallpapers = list(WALLPAPER_DIR.glob("wallpaper*.jpg"))
        
        # Group by display (if multi-monitor) or keep all together
        display_groups = {}
        for wp in all_wallpapers:
            # Extract display number from filename (wallpaper_display1_*.jpg or wallpaper_*.jpg)
            if '_display' in wp.name:
                try:
                    display_num = int(wp.name.split('_display')[1].split('_')[0])
                    if display_num not in display_groups:
                        display_groups[display_num] = []
                    display_groups[display_num].append(wp)
                except:
                    # Fallback for old format
                    if 'all' not in display_groups:
                        display_groups['all'] = []
                    display_groups['all'].append(wp)
            else:
                # Old format (wallpaper_*.jpg) - treat as single group
                if 'all' not in display_groups:
                    display_groups['all'] = []
                display_groups['all'].append(wp)
        
        # Clean up each group, keeping 5 most recent
        for display_key, wallpapers in display_groups.items():
            sorted_wallpapers = sorted(
                wallpapers,
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            # Keep only the 5 most recent per display
            for old_file in sorted_wallpapers[5:]:
                try:
                    old_file.unlink()
                except:
                    pass
    except Exception:
        pass  # Don't fail if cleanup doesn't work


def set_wallpaper(image_path, desktop_index=None):
    """Set the wallpaper on macOS using osascript and force refresh.
    
    Args:
        image_path: Path to the wallpaper image
        desktop_index: Optional desktop index (1-based). If None, sets for all desktops.
    """
    # Convert path to POSIX path format
    posix_path = str(Path(image_path).absolute())
    
    if desktop_index is not None:
        # Set wallpaper for specific desktop
        script = f'''tell application "System Events"
    tell desktop {desktop_index}
        set picture to POSIX file "{posix_path}"
    end tell
end tell'''
    else:
        # Set wallpaper for all desktops (backward compatibility)
        script = f'''tell application "System Events"
    tell every desktop
        set picture to POSIX file "{posix_path}"
    end tell
end tell'''
    
    # Method 1: Direct approach
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            check=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stderr and "error" in result.stderr.lower():
            raise subprocess.CalledProcessError(1, "osascript", result.stderr)
        
        # Small delay to ensure file is written
        time.sleep(0.3)
        if desktop_index is not None:
            print(f"✓ Wallpaper set successfully for display {desktop_index}!")
        else:
            print("✓ Wallpaper set successfully!")
        
        return True
    except subprocess.TimeoutExpired:
        print("⚠ Method 1 timed out")
    except subprocess.CalledProcessError as e:
        error_out = e.stderr if e.stderr else (e.stdout if e.stdout else "Unknown error")
        print(f"⚠ Method 1 failed: {error_out}")
    except Exception as e:
        print(f"⚠ Method 1 error: {e}")
    
    # Method 2: Try with explicit desktop iteration (for all desktops only)
    if desktop_index is None:
        try:
            script2 = f'''tell application "System Events"
    set desktopCount to count of desktops
    repeat with i from 1 to desktopCount
        tell desktop i
            set picture to POSIX file "{posix_path}"
        end tell
    end repeat
end tell'''
            result = subprocess.run(
                ["osascript", "-e", script2],
                check=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.stderr and "error" in result.stderr.lower():
                raise subprocess.CalledProcessError(1, "osascript", result.stderr)
            
            # Small delay to ensure file is written
            time.sleep(0.3)
            print("✓ Wallpaper set successfully (method 2)!")
            return True
        except Exception as e:
            print(f"⚠ Method 2 failed: {e}")
    
    # Method 3: Try using alias approach
    try:
        if desktop_index is not None:
            script3 = f'''set theFile to POSIX file "{posix_path}" as alias
tell application "System Events"
    tell desktop {desktop_index}
        set picture to theFile
    end tell
end tell'''
        else:
            script3 = f'''set theFile to POSIX file "{posix_path}" as alias
tell application "System Events"
    tell every desktop
        set picture to theFile
    end tell
end tell'''
        result = subprocess.run(
            ["osascript", "-e", script3],
            check=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stderr and "error" in result.stderr.lower():
            raise subprocess.CalledProcessError(1, "osascript", result.stderr)
        
        # Small delay to ensure file is written
        time.sleep(0.3)
        if desktop_index is not None:
            print(f"✓ Wallpaper set successfully for display {desktop_index} (method 3)!")
        else:
            print("✓ Wallpaper set successfully (method 3)!")
        return True
    except Exception as e:
        print(f"⚠ Method 3 failed: {e}")
    
    # If all methods fail, provide manual instructions
    display_info = f" for display {desktop_index}" if desktop_index is not None else ""
    print(f"\n⚠ Could not set wallpaper automatically{display_info}.")
    print(f"Image saved to: {posix_path}")
    print(f"\nTo set it manually:")
    print(f"1. Open Finder")
    print(f"2. Press Cmd+Shift+G and paste this path:")
    print(f"   {os.path.dirname(posix_path)}")
    print(f"3. Find the wallpaper file and right-click → 'Set Desktop Picture'")
    return False


def main():
    """Main function to change wallpaper with multi-monitor support."""
    print("Changing wallpaper...")
    
    # Load quotes
    quotes_list = load_quotes()
    
    # Get all displays
    displays = get_all_displays()
    print(f"\nDetected {len(displays)} display(s):")
    for i, display in enumerate(displays, 1):
        print(f"  Display {i}: {display['name']} ({display['width']}x{display['height']})")
    
    # Select different random quotes for each display
    # Use random.sample to ensure no duplicate quotes if we have fewer displays than quotes
    if len(quotes_list) >= len(displays):
        selected_quotes_list = random.sample(quotes_list, len(displays))
    else:
        # If we have more displays than quotes, allow repeats
        selected_quotes_list = [random.choice(quotes_list) for _ in range(len(displays))]
    
    # Process each display
    wallpaper_paths = []
    for display_idx, display in enumerate(displays, 1):
        selected_quotes = selected_quotes_list[display_idx - 1]
        
        # Display what was selected for this display
        print(f"\n--- Display {display_idx} ({display['name']}) ---")
        if len(selected_quotes) == 1:
            print(f"Selected quote: {selected_quotes[0][:80]}...")
        else:
            print(f"Selected {len(selected_quotes)} quotes:")
            for q in selected_quotes:
                print(f"  - {q[:80]}...")
        
        # Create wallpaper for this display
        width, height = display['width'], display['height']
        print(f"Creating wallpaper at {width}x{height}")
        
        image = create_wallpaper(selected_quotes, width, height)
        
        # Save image with display-specific filename
        timestamp = int(time.time())
        output_image = WALLPAPER_DIR / f"wallpaper_display{display_idx}_{timestamp}.jpg"
        image.save(output_image, "JPEG", quality=95)
        print(f"Wallpaper saved to {output_image}")
        
        wallpaper_paths.append((display_idx, str(output_image.absolute())))
    
    # Set wallpapers for each display
    print(f"\n--- Setting Wallpapers ---")
    for display_idx, image_path in wallpaper_paths:
        if not os.path.exists(image_path):
            print(f"ERROR: Image file does not exist at {image_path}")
            continue
        
        print(f"\nSetting wallpaper for display {display_idx}...")
        set_wallpaper(image_path, desktop_index=display_idx)
    
    # Create/update symlink for the first display (for backward compatibility)
    if wallpaper_paths:
        first_image_path = Path(wallpaper_paths[0][1])
        if SYMLINK_IMAGE.exists() or SYMLINK_IMAGE.is_symlink():
            try:
                SYMLINK_IMAGE.unlink()
            except:
                pass
        try:
            SYMLINK_IMAGE.symlink_to(first_image_path)
        except:
            pass  # Symlink creation is optional
    
    # Clean up old wallpapers (keep only last 5 per display)
    cleanup_old_wallpapers()
    
    print(f"\n✓ All wallpapers updated!")


if __name__ == "__main__":
    main()


