"""
renderer.py - Rendering engine for the text adventure game
Handles screen clearing and frame composition (border + image + text + menu)
"""

import os
import sys

# Constants for canvas dimensions
CANVAS_WIDTH = 100
CANVAS_HEIGHT = 40

# Zone heights
IMAGE_ZONE_HEIGHT = 12      # Top zone for ASCII art
TEXT_ZONE_HEIGHT = 18       # Middle zone for descriptions
INPUT_ZONE_HEIGHT = 5       # Bottom zone for menu buttons
BORDER_TOP = 3              # Top border lines
BORDER_BOTTOM = 2           # Bottom border lines


def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def create_horizontal_border(width: int, left_corner: str, middle: str, right_corner: str) -> str:
    """Create a horizontal border line"""
    return left_corner + (middle * (width - 2)) + right_corner


def render_frame(art_lines: list, description_lines: list, menu_options: list, 
                 selected_index: int = 0) -> str:
    """
    Render a complete game frame with border, art, text, and menu.
    
    Args:
        art_lines: List of strings for ASCII art
        description_lines: List of strings for scene description
        menu_options: List of 5 menu option strings
        selected_index: Currently selected menu item (0-4)
    
    Returns:
        Complete frame as a string ready for display
    """
    frame = []
    
    # Calculate available widths (accounting for side borders)
    inner_width = CANVAS_WIDTH - 2
    
    # === TOP BORDER ===
    frame.append("┌" + "─" * inner_width + "┐")
    frame.append("│" + " " * inner_width + "│")
    frame.append("├" + "─" * inner_width + "┤")
    
    # === IMAGE ZONE ===
    art_display_lines = IMAGE_ZONE_HEIGHT - 2  # Subtract internal borders
    
    # Process art lines to fit the zone
    art_to_display = art_lines[:art_display_lines] if art_lines else []
    
    # Add top internal border
    frame.append("│" + " " * inner_width + "│")
    
    for art_line in art_to_display:
        # Truncate or pad art line to fit
        clean_line = art_line.replace('\n', '')[:inner_width]
        padded_line = clean_line.ljust(inner_width)
        frame.append("│" + padded_line + "│")
    
    # Fill remaining art zone if needed
    remaining_art_lines = art_display_lines - len(art_to_display)
    for _ in range(remaining_art_lines):
        frame.append("│" + " " * inner_width + "│")
    
    # Add separator after image zone
    frame.append("├" + "─" * inner_width + "┤")
    
    # === TEXT ZONE ===
    text_display_lines = TEXT_ZONE_HEIGHT - 2  # Subtract internal borders
    
    # Add top internal border
    frame.append("│" + " " * inner_width + "│")
    
    for desc_line in description_lines[:text_display_lines]:
        # Center or left-align text, truncate if too long
        clean_line = desc_line[:inner_width]
        padded_line = clean_line.ljust(inner_width)
        frame.append("│" + padded_line + "│")
    
    # Fill remaining text zone if needed
    remaining_text_lines = text_display_lines - len(description_lines[:text_display_lines])
    for _ in range(remaining_text_lines):
        frame.append("│" + " " * inner_width + "│")
    
    # Add separator before input zone
    frame.append("├" + "─" * inner_width + "┤")
    
    # === INPUT ZONE (Menu Buttons) ===
    button_height = INPUT_ZONE_HEIGHT - 2  # Internal space for buttons
    
    # We have 5 buttons to display, distribute them evenly
    options_per_button = button_height // 5 if button_height >= 5 else 1
    
    for idx, option in enumerate(menu_options[:5]):
        # Create button appearance
        is_selected = (idx == selected_index)
        
        # Button styling
        if is_selected:
            prefix = f" [{idx + 1}] "
            suffix_style = " ◄"
        else:
            prefix = f"  {idx + 1}  "
            suffix_style = ""
        
        # Clean and format option text
        clean_option = option[:inner_width - len(prefix) - len(suffix_style)]
        
        # Create button row(s)
        button_content = prefix + clean_option + suffix_style
        button_padded = button_content.ljust(inner_width)
        
        # Add button with top border (except first)
        if idx > 0:
            frame.append("│" + "─" * inner_width + "│")
        
        frame.append("│" + button_padded + "│")
    
    # === BOTTOM BORDER ===
    frame.append("└" + "─" * inner_width + "┘")
    
    # Pad to reach exact CANVAS_HEIGHT if needed
    while len(frame) < CANVAS_HEIGHT:
        frame.append("")
    
    return '\n'.join(frame[:CANVAS_HEIGHT])


def render_title_screen() -> str:
    """Render a special title screen frame"""
    frame = []
    inner_width = CANVAS_WIDTH - 2
    
    # Top border
    frame.append("┌" + "═" * inner_width + "┐")
    for _ in range(CANVAS_HEIGHT - 2):
        frame.append("│" + " " * inner_width + "│")
    frame.append("└" + "═" * inner_width + "┘")
    
    return '\n'.join(frame)


def get_terminal_size():
    """Get current terminal size"""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return CANVAS_WIDTH, CANVAS_HEIGHT


def draw_frame(art_lines: list, description_lines: list, menu_options: list,
               selected_index: int = 0):
    """
    Clear screen and draw a complete frame.
    This is the main function called by the game loop.
    """
    clear_screen()
    frame = render_frame(art_lines, description_lines, menu_options, selected_index)
    print(frame)


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
    
    # Center the message horizontally
    msg_len = min(len(message), inner_width - 4)
    padding = (inner_width - msg_len - 4) // 2
    centered_msg = "  " + (" " * padding) + message[:msg_len] + (" " * padding) + "  "
    centered_msg = centered_msg[:inner_width].ljust(inner_width)
    frame.append("│" + centered_msg + "│")
    
    empty_lines_bottom = CANVAS_HEIGHT - 3 - empty_lines_top - 1
    for _ in range(empty_lines_bottom):
        frame.append("│" + " " * inner_width + "│")
    
    frame.append("└" + "─" * inner_width + "┘")
    
    print('\n'.join(frame))
