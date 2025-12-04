# Mac Wallpaper Quote Changer

A Python project that randomly selects quotes from a text file, generates beautiful wallpapers with the quote overlaid on a background, and sets them as your macOS wallpaper.

## Features

- Randomly selects quotes from `quotes.txt`
- Creates beautiful gradient wallpapers with styled text
- Automatically detects your screen resolution
- One-click wallpaper change via shell script shortcut

## Installation

1. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Make the shell script executable:**
   ```bash
   chmod +x change_wallpaper.sh
   ```

## Usage

### Setting a Custom Background Image

To use your own background image instead of the gradient:

1. Open `wallpaper_changer.py` in a text editor
2. Find the line that says: `BACKGROUND_IMAGE = None`
3. Change it to point to your image file. Examples:
   ```python
   # If your image is in the same folder as the script:
   BACKGROUND_IMAGE = Path(__file__).parent / "background.jpg"
   
   # If your image is in your Pictures folder:
   BACKGROUND_IMAGE = Path.home() / "Pictures" / "my_background.jpg"
   
   # Or use an absolute path:
   BACKGROUND_IMAGE = Path("/Users/gavinomara/Pictures/background.jpg")
   ```
4. Save the file
5. The script will automatically resize your image to fit the screen and add a subtle dark overlay so the quote text is readable

**Note:** Leave it as `BACKGROUND_IMAGE = None` to use the default gradient background.

### Changing Text Color

To change the quote text color:

1. Open `wallpaper_changer.py` in a text editor
2. Find the line that says: `TEXT_COLOR = (255, 255, 255)`
3. Change the RGB values (each number is 0-255). Examples:
   ```python
   TEXT_COLOR = (255, 255, 255)  # White (default)
   TEXT_COLOR = (0, 0, 0)        # Black
   TEXT_COLOR = (240, 240, 240)  # Very light gray
   TEXT_COLOR = (220, 220, 220)  # Light gray
   TEXT_COLOR = (192, 192, 192)  # Silver gray
   TEXT_COLOR = (128, 128, 128)  # Medium gray
   TEXT_COLOR = (105, 105, 105)  # Dim gray
   TEXT_COLOR = (80, 80, 80)     # Dark gray
   TEXT_COLOR = (64, 64, 64)     # Very dark gray
   TEXT_COLOR = (54, 54, 54)     # Charcoal
   TEXT_COLOR = (255, 0, 0)      # Red
   TEXT_COLOR = (0, 255, 0)      # Green
   TEXT_COLOR = (255, 215, 0)    # Gold
   TEXT_COLOR = (255, 192, 203)  # Pink
   TEXT_COLOR = (135, 206, 250)  # Light blue
   ```
4. You can also change the shadow color with `SHADOW_COLOR` (default is black for readability)
5. Save the file

**RGB Color Guide:**
- `(255, 255, 255)` = White
- `(0, 0, 0)` = Black
- `(255, 0, 0)` = Red
- `(0, 255, 0)` = Green
- `(0, 0, 255)` = Blue
- Mix values to create any color you want!

### Adding Quotes

Edit `quotes.txt` and add one quote per line. Empty lines will be ignored.

**Single quote per line:**
```
The only way to do great work is to love what you do.
Innovation distinguishes between a leader and a follower.
Life is what happens to you while you're busy making other plans.
```

**Multiple quotes on the same wallpaper (use ` || ` separator):**
```
Risk more than others think is safe. || Dream more than others think is practical.
Be bold. || Be brave. || Be yourself.
```

When you use ` || ` (space, two pipes, space), both quotes will appear on the same wallpaper, one on each line with spacing between them.

### Running the Script

**Option 1: Using the shell script**
```bash
./change_wallpaper.sh
```

**Option 2: Running Python directly**
```bash
python3 wallpaper_changer.py
```

### Adding to Dock (macOS Shortcut)

**Option 1: Using Automator (Recommended)**

1. Open Automator (Applications > Automator)
2. Create a new **"Application"** (not "Workflow" or "Quick Action")
3. Add a **"Run Shell Script"** action from the left sidebar
4. In the script field, enter:
   ```bash
   cd /Users/gavinomara/Desktop/Python
   ./change_wallpaper.sh
   ```
   (Replace the path with your actual project path)
5. **Save the application:**
   - Press `Cmd+S` or go to File > Save
   - Choose a name like "Change Wallpaper" or "Change Quote"
   - **Important:** Make sure "File Format" is set to **"Application"**
   - Save it to your Desktop or Applications folder
6. **Add to Dock:**
   - Drag the saved `.app` file to your Dock
   - Right-click the Dock icon > Options > Keep in Dock
7. **Click it anytime** to change your wallpaper!

**Option 2: Quick Access from Finder**

- Right-click the `change_wallpaper.sh` file in Finder
- Select "Make Alias"
- Drag the alias to your Dock
- Right-click the alias in Dock > Options > Keep in Dock

Alternatively, you can:
- Right-click the `change_wallpaper.sh` file in Finder
- Select "Make Alias"
- Drag the alias to your Dock
- Right-click the alias in Dock > Options > Keep in Dock

## How It Works

1. The script reads all quotes from `quotes.txt`
2. Randomly selects one quote
3. Detects your screen resolution
4. Creates a gradient background image
5. Overlays the quote text with shadow for readability
6. Saves the image to `~/Library/Application Support/WallpaperQuoteChanger/`
7. Sets it as your macOS wallpaper using AppleScript

## Files

- `wallpaper_changer.py` - Main Python script
- `quotes.txt` - Your quotes file (one per line)
- `change_wallpaper.sh` - Shell script shortcut
- `requirements.txt` - Python dependencies

## Where is the Wallpaper Saved?

The generated wallpaper is automatically saved to:
```
~/Library/Application Support/WallpaperQuoteChanger/current_wallpaper.jpg
```

The script should automatically set it as your wallpaper. If it doesn't work automatically, you can set it manually:

### Manual Method 1: Using Finder
1. Open Finder
2. Press `Cmd+Shift+G` (Go to Folder)
3. Paste this path: `~/Library/Application Support/WallpaperQuoteChanger`
4. Find `current_wallpaper.jpg`
5. Right-click it and select **"Set Desktop Picture"**

### Manual Method 2: Using System Preferences
1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Desktop & Screen Saver**
3. Drag the `current_wallpaper.jpg` file into the wallpaper selection area

### Manual Method 3: Using Terminal
```bash
osascript -e 'tell application "System Events" to tell every desktop to set picture to POSIX file "'"$(echo ~/Library/Application\ Support/WallpaperQuoteChanger/current_wallpaper.jpg)"'"'
```

## Troubleshooting

- **Permission errors**: Make sure the shell script is executable (`chmod +x change_wallpaper.sh`)
- **Wallpaper not changing automatically**: 
  - **First time setup**: You may need to manually set the wallpaper once:
    1. Run the script: `./change_wallpaper.sh`
    2. Open System Settings > Wallpaper
    3. Find the wallpaper in "Your Photos" section
    4. Click on it to set it
    5. After this first time, the script will automatically update it
  - **If it still doesn't auto-update**: 
    - The script restarts the Dock to force refresh (Dock restarts in ~1 second)
    - Check System Settings > Privacy & Security > Automation to ensure Terminal/Automator has permission to control System Events
    - Try running the script again
- **Font issues**: The script will fall back to default fonts if system fonts aren't available
- **Wallpaper syncing**: Make sure "Show on all Spaces" is enabled in System Settings > Wallpaper to ensure the wallpaper updates across all desktops


# Wallpaper-Quote-Changer
