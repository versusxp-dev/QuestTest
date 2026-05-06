"""
logic.py - Game logic and action handling for the text adventure
Processes player choices and manages scene transitions
"""

from typing import Dict, Callable, Optional, Tuple


class GameState:
    """Represents the current state of the game"""
    
    def __init__(self):
        self.current_scene: str = "main_menu"
        self.previous_scene: str = ""
        self.selected_option: int = 0  # Currently highlighted menu item (0-4)
        self.game_flags: Dict[str, bool] = {}  # Story flags
        self.inventory: list = []
        self.message: str = ""  # Temporary message to display
    
    def set_scene(self, scene_name: str):
        """Change current scene, storing previous for back navigation"""
        self.previous_scene = self.current_scene
        self.current_scene = scene_name
        self.selected_option = 0
        self.message = ""
    
    def go_back(self):
        """Return to previous scene"""
        if self.previous_scene:
            self.current_scene = self.previous_scene
            self.previous_scene = ""
            self.selected_option = 0
        else:
            # No previous scene, stay in main menu
            self.current_scene = "main_menu"
            self.selected_option = 0
    
    def set_message(self, msg: str):
        """Set a temporary message (e.g., item picked up)"""
        self.message = msg
    
    def clear_message(self):
        """Clear the temporary message"""
        self.message = ""


# Action result type: (new_scene_name, message_to_display)
ActionResult = Tuple[Optional[str], Optional[str]]


def handle_main_menu_action(option_index: int, state: GameState) -> ActionResult:
    """
    Handle actions from the main menu.
    
    Args:
        option_index: Selected option (0-4)
        state: Current game state
    
    Returns:
        Tuple of (new_scene_name or None, message or None)
    """
    actions = {
        0: ("room", "Игра начинается..."),      # Начать игру
        1: (None, "О игре: Версия 1.0 MVP"),    # О игре
        2: (None, "Настройки в разработке"),     # Настройки
        3: (None, "Достижения заблокированы"),   # Достижения
        4: ("exit", "До свидания!")              # Выход
    }
    
    return actions.get(option_index, (None, "Неизвестная опция"))


def handle_room_action(option_index: int, state: GameState) -> ActionResult:
    """
    Handle actions from the room scene.
    
    Args:
        option_index: Selected option (0-4)
        state: Current game state
    
    Returns:
        Tuple of (new_scene_name or None, message or None)
    """
    actions = {
        0: (None, "Дверь заперта изнутри. Нужно найти ключ."),    # Осмотреть дверь
        1: (None, "Сундук пуст. Кто-то уже обыскал его."),         # Проверить сундук
        2: ("forest", "Вы взяли лампу и вышли через дверь!"),      # Взять лампу
        3: (None, "За окном виден темный лес."),                   # Посмотреть в окно
        4: ("main_menu", "Возврат в главное меню")                 # Назад в меню
    }
    
    # Special case: taking the lamp sets a flag
    if option_index == 2:
        state.game_flags["has_lamp"] = True
        state.inventory.append("Лампа")
    
    return actions.get(option_index, (None, "Что-то пошло не так..."))


def handle_forest_action(option_index: int, state: GameState) -> ActionResult:
    """
    Handle actions from the forest scene.
    """
    actions = {
        0: ("cave", "Вы идете по тропинке и находите пещеру!"),   # Идти по тропинке
        1: (None, "Деревья старые, покрыты мхом."),               # Осмотреть деревья
        2: (None, "Это был ручей. Вода холодная и чистая."),       # Найти источник шума
        3: (None, f"В рюкзаке: {', '.join(state.inventory) or 'ничего'}"),  # Проверить рюкзак
        4: ("room", "Вы вернулись в комнату")                      # Вернуться в комнату
    }
    
    return actions.get(option_index, (None, "Странное ощущение..."))


def handle_cave_action(option_index: int, state: GameState) -> ActionResult:
    """
    Handle actions from the cave scene.
    """
    actions = {
        0: (None, "Кристалл светится в вашей руке!"),             # Взять кристалл
        1: (None, "В воде что-то блестит... но вы не достали."),  # Исследовать водоем
        2: (None, "Луч света освещает древние символы на стене."), # Осветить глубже
        3: (None, "Карта показывает путь к выходу."),             # Проверить карту
        4: ("forest", "Вы вернулись в лес")                        # Вернуться в лес
    }
    
    # Special case: taking crystal
    if option_index == 0 and "Кристалл" not in state.inventory:
        state.inventory.append("Кристалл")
    
    return actions.get(option_index, (None, "Пещера хранит секреты..."))


def handle_default_action(option_index: int, state: GameState) -> ActionResult:
    """
    Default handler for unknown scenes.
    """
    if option_index == 4:
        # Last option is always "back"
        state.go_back()
        return (state.current_scene, "Возврат назад")
    
    return (None, "Здесь пока ничего не происходит...")


# Map of scene names to their action handlers
SCENE_HANDLERS: Dict[str, Callable[[int, GameState], ActionResult]] = {
    "main_menu": handle_main_menu_action,
    "room": handle_room_action,
    "forest": handle_forest_action,
    "cave": handle_cave_action
}


def process_action(option_index: int, state: GameState) -> bool:
    """
    Process a player's action choice.
    
    Args:
        option_index: Selected option (0-4)
        state: Current game state
    
    Returns:
        True if game should continue, False if exit requested
    """
    # Get the handler for current scene
    handler = SCENE_HANDLERS.get(state.current_scene, handle_default_action)
    
    # Execute the action
    new_scene, message = handler(option_index, state)
    
    # Handle scene transition
    if new_scene:
        if new_scene == "exit":
            return False  # Signal to exit the game
        
        state.set_scene(new_scene)
        
        if message:
            state.set_message(message)
    elif message:
        state.set_message(message)
    
    return True


def navigate_menu(direction: str, state: GameState, num_options: int = 5) -> None:
    """
    Navigate the menu with arrow keys.
    
    Args:
        direction: "up" or "down"
        state: Current game state
        num_options: Number of menu options (default 5)
    """
    if direction == "up":
        state.selected_option = (state.selected_option - 1) % num_options
    elif direction == "down":
        state.selected_option = (state.selected_option + 1) % num_options


def get_scene_description_lines(scene_name: str, state: GameState) -> list:
    """
    Get description lines for a scene, including any temporary messages.
    
    Args:
        scene_name: Name of the scene
        state: Current game state
    
    Returns:
        List of description lines
    """
    from assets import get_description
    
    base_description = get_description(scene_name)
    
    # Add temporary message at the beginning if exists
    if state.message:
        return [f">>> {state.message}"] + base_description
    
    return base_description
