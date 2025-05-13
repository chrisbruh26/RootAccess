# Root Access v3

A text-based adventure game combining elements of Animal Crossing and Watch Dogs 2 in a wacky and entertaining way.

## Overview

Root Access v3 is an open-world text-based game in Python where you can:
- Explore different areas in a grid-based world
- Interact with NPCs and influence their behavior
- Hack computers and other electronic devices
- Plant and grow crops
- Hide from enemies using stealth mechanics
- Join or fight against gangs
- Drive vehicles
- And much more!

## Features

- **Grid-based Movement**: Navigate through areas using cardinal directions
- **NPC System**: NPCs with schedules, personalities, and relationships
- **Hacking Mechanics**: Hack computers, vending machines, and more
- **Gardening System**: Plant seeds, water plants, and harvest crops
- **Stealth System**: Hide in various hiding spots to avoid detection
- **Gang System**: Interact with different gangs that control territories
- **Vehicle System**: Drive cars to move faster around the world
- **Time System**: In-game time affects NPC schedules and activities
- **Item System**: Collect, use, and trade various items
- **Combat System**: Fight enemies using different weapons

## How to Play

1. Run the game:
   ```
   python main.py
   ```

2. Basic commands:
   - Movement: `north`, `south`, `east`, `west`, `forward`, `backward`, `right`, `left`
   - Look around: `look`
   - Inventory: `inventory` or `inv`
   - Pick up item: `take [item]`
   - Drop item: `drop [item]`
   - Use item: `use [item]`
   - Talk to NPC: `talk [npc]`
   - Interact with object: `interact [object]`
   - Hide: `hide [hiding spot]`
   - Unhide: `unhide` or `emerge`
   - Hack: `hack [target]`
   - Attack: `attack [target]`
   - Plant: `plant [seed] in [soil plot]`
   - Water: `water [soil plot]`
   - Harvest: `harvest [soil plot]`
   - Check time: `time`
   - Save/Load: `save [filename]`, `load [filename]`
   - Help: `help`
   - Quit: `quit` or `exit`

## Game Structure

The game is organized into modules:
- `main.py`: Entry point for the game
- `modules/game_manager.py`: Manages the overall game state and systems
- `modules/player.py`: Handles the player character and interactions
- `modules/area.py`: Manages areas and their connections
- `modules/npc.py`: Handles NPCs, their behaviors, and gangs
- `modules/items.py`: Manages all items in the game
- `modules/game_objects.py`: Handles interactive objects
- `modules/coordinates.py`: Manages positions in the 3D game world
- `modules/time_system.py`: Handles the in-game time and scheduling

## Customization

The game uses JSON templates for easy customization:
- `data/area_templates.json`: Templates for creating areas
- `data/item_templates.json`: Templates for creating items
- `data/object_templates.json`: Templates for creating objects
- `data/npc_templates.json`: Templates for creating NPCs

You can modify these files to add new content to the game without changing the code.

## Expanding the Game

To add new features:
1. Create new item/object/NPC classes in the appropriate module
2. Add templates for your new content in the JSON files
3. Update the game manager to handle your new content

The modular design makes it easy to add new features without breaking existing functionality.

## Enjoy!

Have fun exploring the world of Root Access v3!
