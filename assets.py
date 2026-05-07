"""
assets.py - ASCII art and content storage for game scenes
Art is designed to fit within the 100x40 canvas image zone (98 chars wide, 12 lines tall)
"""

# ASCII Art dictionary - each scene has its own art
# Note: Art should be clean without outer borders since renderer adds the frame
ASCII_ART = {
    "main_menu": """
    
          ██████╗  ██████╗ ██╗  ██╗███████╗
         ██╔════╝ ██╔═══██╗██║  ██║██╔════╝
         ██║  ███╗██████╔╝███████║█████╗  
         ██║   ██║██╔══██╗╚════██║██╔══╝  
         ╚██████╔╝██║  ██║     ██║███████╗
          ╚═════╝ ╚═╝  ╚═╝     ╚═╝╚══════╝
    
                  T E X T   A D V E N T U R E
    
    """,

    "room": """
    
          ┌─────────────┐                       ╔═══════╗
          │   [WINDOW]  │      SUNLIGHT         ║ TABLE ║  [LAMP]
          │      ☀      │         ═════         ╚═══════╝    💡
          │             │                                   
          └─────────────┘                                   
    
        ╔════╗                              ╔═══════╗
        ║ DOOR║                             ║ CHEST ║
        ╚════╝                              ╚═══════╝
    
              ░░░░░░░░░░ FLOOR RUG ░░░░░░░░░░░░░    
    """,

    "forest": """
    
            🌲🌳🌲     🌲🌲🌳       🌲🌲                    
         🌳    🌲🌳  🌲     🌳  🌲   🌳                     
       🌲  🌳  🌲  🌳🌲  🌳  🌲🌳  🌲  🌳                  
          🌲🌳🌲  PATH  🌳🌲🌳  🌲🌳🌲                      
       🌳  🌲  🌳🌲  🌳  🌲  🌳🌲  🌳  🌲                  
         🌲   🌳🌲  🌳    🌲 🌳  🌲🌳                       
            🌳🌲    🌳🌲🌳      🌳🌲                        
    
    """,

    "cave": """
    
            ⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️              
          ⛰️                      ⛰️                   
        ⛰️      💎  GLOWING       ⛰️                   
       ⛰️         CRYSTALS         ⛰️                  
      ⛰️                            ⛰️                 
     ⛰️         ~~~ WATER ~~~        ⛰️                
     ⛰️                              ⛰️                 
      ⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️⛰️              
    
    """,

    "empty": """
    
    
    
    
    
    
    
    
    
    """
}

# Scene descriptions (lore, dialogues, situation text)
SCENE_DESCRIPTIONS = {
    "main_menu": [
        "Добро пожаловать в текстовую игру Adventure Quest!",
        "",
        "Используйте цифры 1-5 или стрелки для навигации.",
        "Ваше приключение начинается здесь...",
        "",
        "Нажмите 'Начать игру' чтобы продолжить."
    ],

    "room": [
        "Вы находитесь в старой заброшенной комнате.",
        "",
        "Сквозь окно пробивается тусклый свет. На столе стоит",
        "старая лампа, а в углу виден сундук.",
        "",
        "Дверь слегка приоткрыта, издавая скрип.",
        "Что вы будете делать?"
    ],

    "forest": [
        "Вы вышли в темный лес.",
        "",
        "Деревья высокие и густые, свет едва пробивается сквозь листву.",
        "Где-то вдалеке слышен шум ручья.",
        "",
        "Тропинка ведет вглубь леса."
    ],

    "cave": [
        "Вы вошли в пещеру.",
        "",
        "Стены покрыты светящимися кристаллами,",
        "которые освещают путь.",
        "",
        "В центре пещеры небольшой подземный водоем."
    ],

    "default": [
        "Здесь пока ничего нет.",
        "Раздел в разработке..."
    ]
}

# Menu options for each scene
MENU_OPTIONS = {
    "main_menu": [
        "🎮 Начать игру",
        "📖 О игре",
        "⚙️ Настройки",
        "🏆 Достижения",
        "❌ Выход"
    ],

    "room": [
        "🚪 Осмотреть дверь",
        "🗃️ Проверить сундук",
        "💡 Взять лампу",
        "🪟 Посмотреть в окно",
        "↩️ Назад в меню"
    ],

    "forest": [
        "🚶 Идти по тропинке",
        "🌳 Осмотреть деревья",
        "💧 Найти источник шума",
        "🎒 Проверить рюкзак",
        "↩️ Вернуться в комнату"
    ],

    "cave": [
        "💎 Взять кристалл",
        "💧 Исследовать водоем",
        "🔦 Осветить глубже",
        "🗺️ Проверить карту",
        "↩️ Вернуться в лес"
    ]
}


def get_art(scene_name: str) -> str:
    """Get ASCII art for a scene"""
    return ASCII_ART.get(scene_name, ASCII_ART["empty"])


def get_description(scene_name: str) -> list:
    """Get description lines for a scene"""
    return SCENE_DESCRIPTIONS.get(scene_name, SCENE_DESCRIPTIONS["default"])


def get_menu_options(scene_name: str) -> list:
    """Get menu options for a scene"""
    return MENU_OPTIONS.get(scene_name, [])
