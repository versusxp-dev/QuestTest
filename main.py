#!/usr/bin/env python3
"""
main.py - Main game loop and state machine for the text adventure game
Engine that interprets scenario.json ( cartridge format)
"""

import sys
import json
import time

from renderer import draw_frame, CANVAS_WIDTH, CANVAS_HEIGHT


class Game:
    """Main game class - engine that interprets scenario data"""
    
    def __init__(self):
        self.scenario = self.load_scenario()
        self.current_state = "main_menu"
        self.running = True
        self.state = {"flags": set()}  # Player state with flags/inventory
    
    def load_scenario(self) -> dict:
        """Load scenario data from JSON file"""
        try:
            with open('scenario.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Ошибка: файл scenario.json не найден!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Ошибка parsing JSON: {e}")
            sys.exit(1)
    
    def load_scenario(self) -> dict:
        """Load scenario data from JSON file"""
        try:
            with open('scenario.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Ошибка: файл scenario.json не найден!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Ошибка parsing JSON: {e}")
            sys.exit(1)
    
    def get_input(self) -> str:
        """
        Get player input (number for action selection).
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
    
    def handle_input(self, user_input: str, actions: list) -> None:
        """
        Process user input and update game state.
        
        Args:
            user_input: Raw input string from player
            actions: List of available actions from current location
        """
        if not user_input:
            return
        
        # Handle navigation arrows
        if user_input == 'UP':
            if self.selected_option > 0:
                self.selected_option -= 1
            return
        
        if user_input == 'DOWN':
            if self.selected_option < len(actions) - 1:
                self.selected_option += 1
            return
        
        # Handle number keys
        if user_input in '12345':
            option_index = int(user_input) - 1
            
            # Validate option index
            if 0 <= option_index < len(actions):
                self.selected_option = option_index
                self.execute_action(actions[option_index])
            return
        
        # Handle Enter key (activate selected option)
        if user_input == '\r' or user_input == '\n':
            if 0 <= self.selected_option < len(actions):
                self.execute_action(actions[self.selected_option])
            return
        
        # Handle 'q' for quit
        if user_input.lower() == 'q':
            self.running = False
    
    def execute_action(self, action: dict) -> None:
        """Execute an action and transition to new state"""
        # Set flag if specified in action
        if "set_flag" in action:
            self.state["flags"].add(action["set_flag"])
        
        target = action.get("target", "")
        
        if target == "exit":
            self.running = False
        elif target in self.scenario:
            self.current_state = target
        # If target is invalid, stay in current state
    
    def render_current_scene(self) -> None:
        """Render the current game scene based on scenario data"""
        # Get current location data from scenario
        location = self.scenario.get(self.current_state, {})
        
        art_id = location.get("art_id", "default")
        text = location.get("text", "Unknown location.")
        all_actions = location.get("actions", [])
        
        # Filter actions based on flags
        actions = []
        for action in all_actions:
            # Check require_flag: action visible only if player HAS this flag
            if "require_flag" in action:
                if action["require_flag"] not in self.state["flags"]:
                    continue  # Skip this action
            
            # Check require_no_flag: action visible only if player does NOT have this flag
            if "require_no_flag" in action:
                if action["require_no_flag"] in self.state["flags"]:
                    continue  # Skip this action
            
            actions.append(action)
        
        # Extract button texts from filtered actions
        menu_options = [action.get("text", f"Option {i+1}") for i, action in enumerate(actions)]
        
        # Pad menu_options to always have 5 items (renderer expects exactly 5)
        while len(menu_options) < 5:
            menu_options.append("")
        
        # Get art placeholder based on art_id
        art_lines = self.get_art_for_id(art_id)
        
        # Split text into lines for description
        description_lines = text.split('\n')
        
        # Render the frame
        draw_frame(art_lines, description_lines, menu_options, self.selected_option)
    
    def get_art_for_id(self, art_id: str) -> list:
        """Get ASCII art lines based on art_id (placeholder implementation)"""
        # Simple placeholder arts for demonstration
        arts = {
            "main_menu_art": [
                "  ____  _          _ _             ",
                " |  _ \\(_) ___ ___| (_) ___ _ __   ",
                " | | | | |/ __/ _ \\ | |/ _ \\ '__|  ",
                " | |_| | | (_|  __/ | |  __/ |     ",
                " |____/|_|\\___\\___|_|_|\\___|_|     ",
                "",
                "       === QUESTTEST ===           ",
            ],
            "start_room": [
                "  +---------------------+          ",
                "  |                     |          ",
                "  |      [ROOM]         |          ",
                "  |         |           |          ",
                "  |      [MAP]          |          ",
                "  |                     |          ",
                "  +----------+----------+          ",
            ],
            "forest_scene": [
                "    /\\    /\\                         ",
                "   //\\\\  //\\\\                        ",
                "  ///\\\\///\\\\\\                       ",
                "    ||  ||                          ",
                "   _||__||_                         ",
                "  |        |                        ",
                "  | TUNNEL |                        ",
            ],
            "default": [
                "  ???                              ",
                "  Unknown location art             ",
                "  ???                              ",
            ]
        }
        return arts.get(art_id, arts["default"])
    
    def run(self):
        """Main game loop"""
        self.selected_option = 0  # Initialize selected option
        
        while self.running:
            # Render current scene
            self.render_current_scene()
            
            # Get and process input
            location = self.scenario.get(self.current_state, {})
            actions = location.get("actions", [])
            
            user_input = self.get_input()
            self.handle_input(user_input, actions)
            
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
    print("Загрузка движка QUESTTEST v1.0...")
    
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
