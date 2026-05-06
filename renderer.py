"""
renderer.py - Rendering engine for the text adventure game
Handles screen clearing and frame composition (border + image + art + text + menu)
STRICT 100x40 canvas with proper emoji handling
"""

import os
import sys
import textwrap
from wcwidth import wcswidth

# Constants for canvas dimensions - HARD LIMITS
CANVAS_WIDTH = 100
CANVAS_HEIGHT = 40

# Zone heights - EXACT allocation
TOP_BORDER_LINES = 3       # Top border + separator
IMAGE_ZONE_HEIGHT = 15     # ASCII art zone (including internal borders)
TEXT_ZONE_HEIGHT = 15      # Description zone (including internal borders)
INPUT_ZONE_HEIGHT = 10     # Menu buttons zone (2 lines per button × 5 buttons)
BOTTOM_BORDER_LINES = 1    # Bottom border only

# Verify total: 3 + 15 + 15 + 10 + 1 = 44... need to adjust
# Recalculated:
# Line 0: ┌──────────────────────────────────────────────────────────────────────────────────────────────┐ (top border)
# Lines 1-14: Image zone (14 lines including top/bottom separators)
# Lines 15-28: Text zone (14 lines including top/bottom separators)  
# Lines 29-38: Input zone (10 lines for 5 buttons, 2 lines each)
# Line 39: └──────────────────────────────────────────────────────────────────────────────────────────────┘ (bottom border)
# Total: 1 + 14 + 14 + 10 + 1 = 40 ✓

IMAGE_ZONE_INNER_HEIGHT = 12  # Inside image zone, excluding borders
TEXT_ZONE_INNER_HEIGHT = 12   # Inside text zone, excluding borders


def get_string_display_width(s: str) -> int:
    """
    Get the display width of a string, accounting for emojis and wide characters.
    Emojis and some Unicode characters take 2 terminal columns.
    """
    width = wcswidth(s)
    return width if width >= 0 else len(s)


def truncate_to_width(text: str, max_width: int) -> str:
    """
    Truncate text to fit within max_width display columns.
    Properly handles emojis and wide characters.
    """
    if not text:
        return ""
    
    current_width = 0
    result = []
    
    for char in text:
        char_width = wcswidth(char)
        if char_width < 0:
            char_width = 1  # Fallback for unknown characters
        elif char_width == 0:
            char_width = 0  # Zero-width characters
        
        if current_width + char_width <= max_width:
            result.append(char)
            current_width += char_width
        else:
            break
    
    return ''.join(result)


def pad_to_width(text: str, target_width: int) -> str:
    """
    Pad text with spaces to reach target display width.
    Accounts for emoji double-width when calculating padding needed.
    Returns a string with exactly target_width characters (byte length).
    """
    current_width = get_string_display_width(text)
    padding_needed = max(0, target_width - current_width)
    # Add padding and ensure we return exactly target_width bytes
    result = text + (' ' * padding_needed)
    # Final safety check - truncate or pad to exact byte length
    if len(result) > target_width:
        result = result[:target_width]
    elif len(result) < target_width:
        result = result + (' ' * (target_width - len(result)))
    return result


def clear_screen():
    """Clear the console screen and move cursor to home position"""
    # Use ANSI escape codes for cleaner clearing
    os.system('cls' if os.name == 'nt' else 'clear')
    # Move cursor to top-left
    print('\033[H', end='')


def create_horizontal_border(width: int, left_corner: str, middle: str, right_corner: str) -> str:
    """Create a horizontal border line of exact width"""
    inner_width = width - 2
    return left_corner + (middle * inner_width) + right_corner


def wrap_text(text: str, max_width: int) -> list:
    """
    Wrap text to fit within max_width, respecting word boundaries.
    Returns list of lines, each fitting within max_width display columns.
    """
    if not text:
        return []
    
    # Use textwrap for initial wrapping
    wrapped = textwrap.wrap(text, width=max_width, break_long_words=True, replace_whitespace=False)
    
    # Further process each line to handle emojis
    result = []
    for line in wrapped:
        # If line is still too wide due to emojis, truncate it
        if get_string_display_width(line) > max_width:
            line = truncate_to_width(line, max_width)
        result.append(line)
    
    return result


def render_frame(art_lines: list, description_lines: list, menu_options: list, 
                 selected_index: int = 0) -> str:
    """
    Render a complete game frame with EXACT 100x40 dimensions.
    
    Layout:
    - Line 0: Top border
    - Lines 1-2: Top border area / title space
    - Lines 3-14: Image zone (12 inner lines + 2 border lines)
    - Line 15: Separator
    - Lines 16-27: Text zone (12 inner lines + 2 border lines)
    - Line 28: Separator before input
    - Lines 29-38: Input zone (5 buttons × 2 lines each)
    - Line 39: Bottom border
    
    Args:
        art_lines: List of strings for ASCII art
        description_lines: List of strings for scene description
        menu_options: List of exactly 5 menu option strings
        selected_index: Currently selected menu item (0-4)
    
    Returns:
        Complete frame as a string with exactly CANVAS_HEIGHT lines,
        each line exactly CANVAS_WIDTH characters.
    """
    frame = []
    inner_width = CANVAS_WIDTH - 2  # 98 characters for content
    
    # === LINE 0: TOP BORDER ===
    frame.append("┌" + "─" * inner_width + "┐")
    
    # === LINES 1-2: TOP PADDING/TITLE AREA ===
    frame.append("│" + " " * inner_width + "│")
    frame.append("│" + " " * inner_width + "│")
    
    # === LINES 3-14: IMAGE ZONE (12 inner lines) ===
    # Process art to fit exactly 12 lines
    art_to_display = []
    for line in art_lines:
        clean_line = line.replace('\n', '').replace('\r', '')
        # Truncate to inner width considering emoji width
        truncated = truncate_to_width(clean_line, inner_width)
        art_to_display.append(truncated)
    
    # Take only what fits or pad with empty lines
    if len(art_to_display) > IMAGE_ZONE_INNER_HEIGHT:
        art_to_display = art_to_display[:IMAGE_ZONE_INNER_HEIGHT]
    
    # Add art lines, padded to full width
    for art_line in art_to_display:
        padded = pad_to_width(art_line, inner_width)
        frame.append("│" + padded + "│")
    
    # Fill remaining image zone lines
    while len(frame) < 3 + IMAGE_ZONE_INNER_HEIGHT:
        frame.append("│" + " " * inner_width + "│")
    
    # === LINE 15: SEPARATOR AFTER IMAGE ===
    frame.append("├" + "─" * inner_width + "┤")
    
    # === LINES 16-27: TEXT ZONE (12 inner lines) ===
    # Process description text with wrapping
    text_to_display = []
    for desc_line in description_lines:
        wrapped = wrap_text(desc_line, inner_width)
        text_to_display.extend(wrapped)
    
    # Take only what fits
    if len(text_to_display) > TEXT_ZONE_INNER_HEIGHT:
        text_to_display = text_to_display[:TEXT_ZONE_INNER_HEIGHT]
    
    # Add text lines, padded to full width
    for text_line in text_to_display:
        padded = pad_to_width(text_line, inner_width)
        frame.append("│" + padded + "│")
    
    # Fill remaining text zone lines
    while len(frame) < 16 + TEXT_ZONE_INNER_HEIGHT:
        frame.append("│" + " " * inner_width + "│")
    
    # === LINE 28: SEPARATOR BEFORE INPUT ===
    frame.append("├" + "─" * inner_width + "┤")
    
    # === LINES 29-38: INPUT ZONE (5 buttons × 2 lines each = 10 lines) ===
    # Each button gets 2 lines for a "chunky" appearance
    for idx in range(5):
        option = menu_options[idx] if idx < len(menu_options) else f"Option {idx + 1}"
        is_selected = (idx == selected_index)
        
        # Button number prefix: "[1] ", " 2  ", etc.
        if is_selected:
            prefix = f"[{idx + 1}] "
            suffix = " ◄"
        else:
            prefix = f" {idx + 1}  "
            suffix = ""
        
        # Calculate available width for option text
        prefix_width = get_string_display_width(prefix)
        suffix_width = get_string_display_width(suffix)
        text_available = inner_width - prefix_width - suffix_width
        
        # Truncate option text to fit
        option_text = truncate_to_width(option, text_available)
        
        # Build the button line
        button_line = prefix + option_text + suffix
        button_padded = pad_to_width(button_line, inner_width)
        
        # First line of button: the actual button content
        frame.append("│" + button_padded + "│")
        
        # Second line of button: visual separator (dashed line between buttons)
        if idx < 4:
            # Dashed separator between buttons
            frame.append("│" + "─" * inner_width + "│")
        else:
            # Last button - just empty space before bottom border
            frame.append("│" + " " * inner_width + "│")
    
    # === LINE 39: BOTTOM BORDER ===
    frame.append("└" + "─" * inner_width + "┘")
    
    # Ensure exactly CANVAS_HEIGHT lines
    while len(frame) < CANVAS_HEIGHT:
        frame.append("│" + " " * inner_width + "│")
    
    # Truncate to exactly CANVAS_HEIGHT lines
    frame = frame[:CANVAS_HEIGHT]
    
    # Final verification: ensure every line is exactly CANVAS_WIDTH
    verified_frame = []
    for line in frame:
        # Truncate if too long, pad if too short
        if len(line) > CANVAS_WIDTH:
            line = line[:CANVAS_WIDTH]
        else:
            line = pad_to_width(line, CANVAS_WIDTH)
        verified_frame.append(line)
    
    return '\n'.join(verified_frame)


def draw_frame(art_lines: list, description_lines: list, menu_options: list,
               selected_index: int = 0):
    """
    Clear screen and draw a complete frame.
    This is the main function called by the game loop.
    """
    clear_screen()
    frame = render_frame(art_lines, description_lines, menu_options, selected_index)
    print(frame, end='')
    # Ensure cursor is positioned correctly after drawing
    sys.stdout.flush()


def render_title_screen() -> str:
    """Render a special title screen frame with exact 100x40 dimensions"""
    frame = []
    inner_width = CANVAS_WIDTH - 2
    
    # Top border with double-line style
    frame.append("┌" + "═" * inner_width + "┐")
    
    # Fill with empty space
    for _ in range(CANVAS_HEIGHT - 2):
        frame.append("│" + " " * inner_width + "│")
    
    # Bottom border
    frame.append("└" + "═" * inner_width + "┘")
    
    return '\n'.join(frame)


def get_terminal_size():
    """Get current terminal size"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return CANVAS_WIDTH, CANVAS_HEIGHT


def draw_centered_message(message: str):
    """Draw a centered message on screen (for loading, errors, etc.)"""
    clear_screen()
    inner_width = CANVAS_WIDTH - 2
    
    frame = []
    frame.append("┌" + "─" * inner_width + "┐")
    
    # Calculate vertical center
    empty_lines_top = (CANVAS_HEIGHT - 3) // 2
    
    for _ in range(empty_lines_top):
        frame.append("│" + " " * inner_width + "│")
    
    # Center the message horizontally (accounting for emoji width)
    msg_display_width = get_string_display_width(message)
    msg_truncated = truncate_to_width(message, inner_width - 4)
    msg_display_width = get_string_display_width(msg_truncated)
    padding = (inner_width - msg_display_width - 4) // 2
    centered_msg = "  " + (" " * padding) + msg_truncated + (" " * padding) + "  "
    centered_msg = pad_to_width(centered_msg, inner_width)
    frame.append("│" + centered_msg + "│")
    
    empty_lines_bottom = CANVAS_HEIGHT - 3 - empty_lines_top - 1
    for _ in range(empty_lines_bottom):
        frame.append("│" + " " * inner_width + "│")
    
    frame.append("└" + "─" * inner_width + "┘")
    
    print('\n'.join(frame))
