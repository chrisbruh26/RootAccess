"""
Root Access v3 - A text-based adventure game combining elements of Animal Crossing and Watch Dogs 2.
This game focuses on hacking, stealth, and social interactions in a wacky and entertaining way.
"""

import os
import sys
import json

# Import modules directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the game manager
from modules.game_manager import GameManager

def create_default_templates():
    """Create default templates if they don't exist."""
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Area templates
    area_templates = {
        "home": {
            "type": "Area",
            "name": "Home",
            "description": "Your secret base of operations. It's small but functional.",
            "grid_width": 5,
            "grid_length": 5,
            "weather": "clear"
        },
        "garden": {
            "type": "Area",
            "name": "Garden",
            "description": "A small garden area with fertile soil.",
            "grid_width": 8,
            "grid_length": 8,
            "weather": "sunny"
        },
        "street": {
            "type": "Area",
            "name": "Street",
            "description": "A busy street with various shops and people.",
            "grid_width": 15,
            "grid_length": 5,
            "weather": "clear"
        },
        "alley": {
            "type": "Area",
            "name": "Alley",
            "description": "A dark alley between buildings.",
            "grid_width": 10,
            "grid_length": 3,
            "weather": "foggy"
        },
        "plaza": {
            "type": "Area",
            "name": "Plaza",
            "description": "A large open plaza with a fountain in the center.",
            "grid_width": 12,
            "grid_length": 12,
            "weather": "sunny"
        },
        "warehouse": {
            "type": "Area",
            "name": "Warehouse",
            "description": "An abandoned warehouse, taken over by the Bloodhounds.",
            "grid_width": 15,
            "grid_length": 15,
            "weather": "dusty"
        },
        "construction_site": {
            "type": "Area",
            "name": "Construction Site",
            "description": "A construction site with various equipment and materials.",
            "grid_width": 20,
            "grid_length": 10,
            "weather": "clear"
        },
        "office_building": {
            "type": "Building",
            "name": "Office Building",
            "description": "A tall office building with multiple floors.",
            "grid_width": 10,
            "grid_length": 10,
            "num_floors": 5,
            "weather": "clear"
        },
        "office_floor": {
            "type": "Area",
            "name": "Office Floor",
            "description": "A floor in an office building with cubicles and offices.",
            "grid_width": 10,
            "grid_length": 10,
            "weather": "controlled"
        }
    }
    
    # Item templates
    item_templates = {
        "backpack": {
            "type": "Item",
            "name": "Backpack",
            "description": "A sturdy backpack for carrying items.",
            "value": 20
        },
        "energy_drink": {
            "type": "Consumable",
            "name": "Energy Drink",
            "description": "A caffeinated beverage that restores health.",
            "nutrition": 10,
            "effects": {"energy": 20},
            "value": 10
        },
        "pipe": {
            "type": "Weapon",
            "name": "Pipe",
            "description": "A metal pipe that can be used as a weapon.",
            "damage": 15,
            "durability": 10,
            "value": 15
        },
        "gun": {
            "type": "Weapon",
            "name": "Gun",
            "description": "A standard firearm.",
            "damage": 50,
            "durability": 20,
            "value": 50
        },
        "machine_gun": {
            "type": "Weapon",
            "name": "Machine Gun",
            "description": "A machine gun with high damage output.",
            "damage": 100,
            "durability": 50,
            "value": 100
        },
        "smoke_bomb": {
            "type": "TechItem",
            "name": "Smoke Bomb",
            "description": "A device that creates a smoke screen for stealth.",
            "effect_type": "smoke",
            "duration": 3,
            "value": 30
        },
        "decoy": {
            "type": "TechItem",
            "name": "Decoy",
            "description": "A device that creates a holographic decoy to distract enemies.",
            "effect_type": "decoy",
            "duration": 5,
            "value": 40
        },
        "drone": {
            "type": "TechItem",
            "name": "Drone",
            "description": "A small drone that can be used for reconnaissance.",
            "effect_type": "recon",
            "battery": 100,
            "max_battery": 100,
            "value": 80
        },
        "hacked_milk_blaster": {
            "type": "EffectItem",
            "name": "Hacked Milk Blaster",
            "description": "A strange device that sprays hacked milk, causing hallucinations.",
            "effect_type": "hallucination",
            "duration": 5,
            "value": 50
        },
        "confusion_ray": {
            "type": "EffectItem",
            "name": "Confusion Ray",
            "description": "A device that emits waves that confuse the target.",
            "effect_type": "confusion",
            "duration": 4,
            "value": 60
        },
        "tomato_seed": {
            "type": "Seed",
            "name": "Tomato Seed",
            "description": "A seed for growing tomatoes.",
            "plant_type": "tomato",
            "growth_time": 5,
            "value": 5
        },
        "potato_seed": {
            "type": "Seed",
            "name": "Potato Seed",
            "description": "A seed for growing potatoes.",
            "plant_type": "potato",
            "growth_time": 4,
            "value": 5
        },
        "carrot_seed": {
            "type": "Seed",
            "name": "Carrot Seed",
            "description": "A seed for growing carrots.",
            "plant_type": "carrot",
            "growth_time": 3,
            "value": 5
        },
        "watering_can": {
            "type": "Tool",
            "name": "Watering Can",
            "description": "A can for watering plants.",
            "tool_type": "watering",
            "uses": 10,
            "max_uses": 10,
            "value": 15
        }
    }
    
    # Object templates
    object_templates = {
        "soil_plot": {
            "type": "SoilPlot",
            "name": "Soil Plot",
            "description": "A plot of soil for planting seeds."
        },
        "computer": {
            "type": "Computer",
            "name": "Computer",
            "description": "A computer that can be used for hacking.",
            "programs": ["data_miner", "security_override", "plant_hacker"]
        },
        "hacking_terminal": {
            "type": "Computer",
            "name": "Hacking Terminal",
            "description": "A specialized terminal for hacking operations.",
            "programs": ["data_miner", "security_override", "plant_hacker"]
        },
        "closet": {
            "type": "HidingSpot",
            "name": "Closet",
            "description": "A small closet that you can hide in.",
            "stealth_bonus": 0.8
        },
        "bushes": {
            "type": "HidingSpot",
            "name": "Bushes",
            "description": "Dense bushes that provide good cover.",
            "stealth_bonus": 0.7
        },
        "dumpster": {
            "type": "HidingSpot",
            "name": "Dumpster",
            "description": "A large dumpster you can hide behind.",
            "stealth_bonus": 0.6
        },
        "fountain": {
            "type": "HidingSpot",
            "name": "Fountain",
            "description": "A large fountain with decorative elements to hide behind.",
            "stealth_bonus": 0.5
        },
        "crates": {
            "type": "HidingSpot",
            "name": "Crates",
            "description": "Stacked crates that provide decent cover.",
            "stealth_bonus": 0.6
        },
        "vending_machine": {
            "type": "VendingMachine",
            "name": "Vending Machine",
            "description": "A vending machine selling various items."
        },
        "elevator": {
            "type": "Elevator",
            "name": "Elevator",
            "description": "An elevator that can take you to different floors."
        },
        "car": {
            "type": "Vehicle",
            "name": "Car",
            "description": "A standard car that can be driven around.",
            "speed": 3,
            "fuel": 100,
            "max_fuel": 100
        },
        "door": {
            "type": "Door",
            "name": "Door",
            "description": "A standard door that connects areas."
        }
    }
    
    # NPC templates
    npc_templates = {
        "civilian": {
            "name": "Civilian",
            "description": "An ordinary citizen going about their day.",
            "dialogue": {
                "default": "Hello there!",
                "friendly": "Nice to see you again!"
            },
            "personality": {
                "friendliness": 50,
                "curiosity": 40
            },
            "money": 50,
            "schedule": {
                "8:00": ["walking", "plaza"],
                "12:00": ["eating", "street"],
                "18:00": ["shopping", "plaza"],
                "22:00": ["sleeping", "home"]
            }
        },
        "gang_member_bloodhound": {
            "name": "Bloodhound Gang Member",
            "description": "A member of the Bloodhounds gang.",
            "dialogue": {
                "default": "What do you want? This is Bloodhound territory.",
                "hostile": "You're asking for trouble coming here!"
            },
            "personality": {
                "aggression": 70,
                "loyalty": 80
            },
            "money": 100,
            "gang": "Bloodhounds",
            "schedule": {
                "10:00": ["patrolling", "warehouse"],
                "14:00": ["guarding", "alley"],
                "20:00": ["meeting", "warehouse"],
                "2:00": ["sleeping", "warehouse"]
            }
        },
        "gang_member_viper": {
            "name": "Crimson Viper Gang Member",
            "description": "A member of the Crimson Vipers gang.",
            "dialogue": {
                "default": "Keep moving. Vipers don't like strangers.",
                "hostile": "You're in Viper territory now. Big mistake."
            },
            "personality": {
                "aggression": 60,
                "cunning": 70
            },
            "money": 100,
            "gang": "Crimson Vipers",
            "schedule": {
                "9:00": ["patrolling", "plaza"],
                "15:00": ["dealing", "alley"],
                "21:00": ["meeting", "construction_site"],
                "3:00": ["sleeping", "construction_site"]
            }
        },
        "shopkeeper": {
            "name": "Shopkeeper",
            "description": "A friendly shopkeeper selling various goods.",
            "dialogue": {
                "default": "Welcome to my shop! Feel free to browse around.",
                "friendly": "Ah, my favorite customer! What can I get for you today?"
            },
            "personality": {
                "friendliness": 60,
                "greed": 40
            },
            "money": 500,
            "schedule": {
                "8:00": ["opening_shop", "street"],
                "12:00": ["selling", "street"],
                "20:00": ["closing_shop", "street"],
                "22:00": ["sleeping", "home"]
            }
        }
    }
    
    # Save templates to files
    with open(os.path.join(data_dir, "area_templates.json"), 'w') as f:
        json.dump(area_templates, f, indent=4)
    
    with open(os.path.join(data_dir, "item_templates.json"), 'w') as f:
        json.dump(item_templates, f, indent=4)
    
    with open(os.path.join(data_dir, "object_templates.json"), 'w') as f:
        json.dump(object_templates, f, indent=4)
    
    with open(os.path.join(data_dir, "npc_templates.json"), 'w') as f:
        json.dump(npc_templates, f, indent=4)

def main():
    """Main function to run the game."""
    # Create default templates if they don't exist
    create_default_templates()
    
    # Create and initialize the game manager
    game_manager = GameManager()
    game_manager.initialize_game()
    
    # Run the game
    game_manager.run()

if __name__ == "__main__":
    main()
