#!/usr/bin/env python3
"""
main.py - Main game loop and state machine for the text adventure game
Handles input processing and scene transitions
"""

import sys
import time

from renderer import draw_frame, CANVAS_WIDTH, CANVAS_HEIGHT
from assets import get_art, get_menu_options
from logic import GameState, process_action, navigate_menu, get_scene_description_lines


class Game:
    """Main game class implementing the state machine"""
    
    def __init__(self):
        self.state = GameState()
        self.running = True
    
    def get_input(self) -> str:
        """
        Get player input (number 1-5 or arrow keys).
        Uses non-blocking input where possible.
        """
        try:
            # For Unix-like systems, use termios for non-blocking input
            if sys.platform != 'win32':
                import termios
                import tty
                
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                
                try:
                    tty.setraw(fd)
                    ch = sys.stdin.read(1)
                    
                    # Handle escape sequences (arrow keys)
                    if ch == '\x1b':
                        # Escape sequence - read more characters
                        ch2 = sys.stdin.read(1)
                        if ch2 == '[':
                            ch3 = sys.stdin.read(1)
                            if ch3 == 'A':
                                return 'UP'
                            elif ch3 == 'B':
                                return 'DOWN'
                    
                    return ch
                    
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            else:
                # Windows fallback - simple input
                import msvcrt
                if msvcrt.kbhit():
                    ch = msvcrt.getch().decode('utf-8', errors='ignore')
                    if ch == '\xe0':  # Arrow key prefix
                        ch2 = msvcrt.getch().decode('utf-8', errors='ignore')
                        if ch2 == 'H':
                            return 'UP'
                        elif ch2 == 'P':
                            return 'DOWN'
                    return ch
                return ''
                
        except Exception:
            # Fallback to regular input
            try:
                return input().strip()
            except EOFError:
                return ''
    
    def handle_input(self, user_input: str) -> None:
        """
        Process user input and update game state.
        
        Args:
            user_input: Raw input string from player
        """
        if not user_input:
            return
        
        # Handle navigation arrows
        if user_input == 'UP':
            navigate_menu('up', self.state)
            return
        
        if user_input == 'DOWN':
            navigate_menu('down', self.state)
            return
        
        # Handle number keys (1-5)
        if user_input in '12345':
            option_index = int(user_input) - 1
            
            # Validate option index
            if 0 <= option_index < 5:
                self.state.selected_option = option_index
                self.running = process_action(option_index, self.state)
            return
        
        # Handle Enter key (activate selected option)
        if user_input == '\r' or user_input == '\n':
            self.running = process_action(self.state.selected_option, self.state)
            return
        
        # Handle 'q' for quit
        if user_input.lower() == 'q':
            self.running = False
    
    def render_current_scene(self) -> None:
        """Render the current game scene"""
        # Get assets for current scene
        art = get_art(self.state.current_scene)
        description = get_scene_description_lines(self.state.current_scene, self.state)
        menu_options = get_menu_options(self.state.current_scene)
        
        # Split art into lines
        art_lines = art.strip().split('\n') if art else []
        
        # Render the frame
        draw_frame(art_lines, description, menu_options, self.state.selected_option)
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Render current scene
            self.render_current_scene()
            
            # Get and process input
            user_input = self.get_input()
            self.handle_input(user_input)
            
            # Small delay to prevent CPU spinning
            time.sleep(0.05)
        
        # Game exit
        self.show_exit_message()
    
    def show_exit_message(self):
        """Display exit message"""
        from renderer import clear_screen, draw_centered_message
        
        clear_screen()
        print("\n" * (CANVAS_HEIGHT // 2))
        print(" " * (CANVAS_WIDTH // 2 - 10) + "Спасибо за игру!")
        print(" " * (CANVAS_WIDTH // 2 - 10) + "До свидания!\n")


def main():
    """Entry point for the game"""
    print("Загрузка игры...")
    
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n\nИгра прервана пользователем.")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
