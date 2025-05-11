# Root Access Template System

This document explains the template system used in Root Access to make the game more scalable and easier to modify.

## Overview

The template system uses JSON files to define game elements such as areas, objects, items, and NPCs. This approach offers several advantages:

1. **Scalability**: Easily add new game elements without modifying code
2. **Reusability**: Define templates once and reuse them throughout the game
3. **Maintainability**: Separate game content from game logic
4. **Flexibility**: Modify game content without programming knowledge

## JSON Structure

The world data is stored in `data/world_data.json` with the following structure:

```json
{
    "templates": {
        "objects": { ... },
        "items": { ... },
        "npcs": { ... }
    },
    "areas": { ... },
    "connections": [ ... ],
    "gangs": { ... },
    "objects": { ... },
    "items": { ... },
    "npcs": { ... }
}
```

### Templates

Templates define reusable patterns for game elements. For example:

```json
"templates": {
    "objects": {
        "standard_vending_machine": {
            "type": "vending_machine",
            "name": "Vending Machine",
            "items": [
                {"name": "Soda", "description": "A refreshing soda.", "price": 5, "health": 10},
                {"name": "Chips", "description": "A bag of chips.", "price": 5, "health": 5}
            ]
        }
    }
}
```

### Using Templates

To use a template, reference it with the `template` property:

```json
"objects": {
    "warehouse": [
        {"template": "objects:standard_vending_machine"}
    ]
}
```

You can also override template properties:

```json
"objects": {
    "warehouse": [
        {"template": "objects:standard_vending_machine", "name": "Warehouse Vending Machine"}
    ]
}
```

## Template Types

### Object Templates

Object templates define interactive objects like vending machines, computers, and hiding spots.

Example:
```json
"basic_computer": {
    "type": "computer",
    "name": "Computer Terminal",
    "description": "A computer terminal for various operations.",
    "programs": ["data_miner", "security_override"]
}
```

### Item Templates

Item templates define items that can be picked up, used, or consumed.

Example:
```json
"smoke_bomb": {
    "type": "smoke_bomb",
    "name": "Smoke Bomb",
    "description": "A device that creates a thick cloud of smoke, allowing for escape.",
    "value": 30
}
```

### NPC Templates

NPC templates define non-player characters with specific behaviors.

Example:
```json
"gang_member": {
    "type": "gang_member",
    "name": "Gang Member",
    "description": "A member of a gang.",
    "items": [
        {"template": "items:basic_weapon", "name": "Gun", "description": "A standard firearm."}
    ]
}
```

## Adding New Content

To add new content to the game:

1. Edit the `data/world_data.json` file
2. Add new templates or use existing ones
3. Add new areas, objects, items, or NPCs
4. Define connections between areas

No code changes are required for most additions!

## Implementation Details

The template system is implemented in `world_loader.py`, which:

1. Loads the JSON data
2. Processes templates
3. Creates game objects based on the templates
4. Adds the objects to the game world

If the JSON file is missing or invalid, the game falls back to a hardcoded world creation method.

## Future Improvements

Potential improvements to the template system:

1. Support for more complex object behaviors
2. Quest and mission templates
3. Dynamic world generation based on templates
4. Editor tool for creating and modifying templates
5. Support for multiple JSON files for different aspects of the game