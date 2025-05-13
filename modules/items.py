"""
Items module for Root Access v3.
Handles all items in the game world.
"""

import json
import random
from .coordinates import Coordinates

class Item:
    """Base class for all items in the game."""
    def __init__(self, name, description, value=0, coordinates=None):
        self.name = name
        self.description = description
        self.value = value
        self.coordinates = coordinates if coordinates else Coordinates(0, 0, 0)
        self.pickupable = True
        self.id = f"item_{name.lower().replace(' ', '_')}"
    
    def __str__(self):
        return f"{self.name}: {self.description}"
    
    def to_dict(self):
        """Convert item to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "coordinates": self.coordinates.to_dict(),
            "type": self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create item from dictionary."""
        item = cls(
            data["name"],
            data["description"],
            data["value"],
            Coordinates.from_dict(data["coordinates"])
        )
        item.id = data.get("id", item.id)
        return item


class Consumable(Item):
    """Consumable items that can be eaten or used."""
    def __init__(self, name, description, value=0, nutrition=0, effects=None, coordinates=None):
        super().__init__(name, description, value, coordinates)
        self.nutrition = nutrition
        self.effects = effects or {}
        self.edible = True
    
    def use(self, player):
        """Use the consumable item."""
        player.eat(self.name)
    
    def effect(self, player):
        """Apply effects to the player."""
        for effect_type, amount in self.effects.items():
            if effect_type == "energy":
                player.energy = min(player.max_energy, player.energy + amount)
                print(f"You gain {amount} energy.")
    
    def to_dict(self):
        """Convert consumable to dictionary for serialization."""
        data = super().to_dict()
        data["nutrition"] = self.nutrition
        data["effects"] = self.effects
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create consumable from dictionary."""
        consumable = cls(
            data["name"],
            data["description"],
            data["value"],
            data["nutrition"],
            data["effects"],
            Coordinates.from_dict(data["coordinates"])
        )
        consumable.id = data.get("id", consumable.id)
        return consumable


class Weapon(Item):
    """Weapons that can be used for combat."""
    def __init__(self, name, description, damage=10, durability=100, value=0, coordinates=None):
        super().__init__(name, description, value, coordinates)
        self.damage = damage
        self.durability = durability
        self.max_durability = durability
    
    def use(self, player):
        """Use the weapon."""
        print(f"You ready your {self.name}. Use 'attack [target]' to attack with it.")
    
    def attack(self, target):
        """Attack a target with the weapon."""
        if self.durability <= 0:
            print(f"Your {self.name} is broken and can't be used.")
            return 0
        
        damage = self.damage
        self.durability -= 1
        
        if self.durability <= 0:
            print(f"Your {self.name} breaks after the attack!")
        elif self.durability < self.max_durability * 0.2:
            print(f"Your {self.name} is severely damaged and won't last much longer.")
        
        return damage
    
    def repair(self, amount=None):
        """Repair the weapon."""
        if amount:
            self.durability = min(self.max_durability, self.durability + amount)
        else:
            self.durability = self.max_durability
        print(f"Your {self.name} has been repaired. Durability: {self.durability}/{self.max_durability}")
    
    def to_dict(self):
        """Convert weapon to dictionary for serialization."""
        data = super().to_dict()
        data["damage"] = self.damage
        data["durability"] = self.durability
        data["max_durability"] = self.max_durability
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create weapon from dictionary."""
        weapon = cls(
            data["name"],
            data["description"],
            data["damage"],
            data["durability"],
            data["value"],
            Coordinates.from_dict(data["coordinates"])
        )
        weapon.max_durability = data.get("max_durability", weapon.durability)
        weapon.id = data.get("id", weapon.id)
        return weapon


class TechItem(Item):
    """Technology items with special effects."""
    def __init__(self, name, description, effect_type, duration=0, value=0, coordinates=None):
        super().__init__(name, description, value, coordinates)
        self.effect_type = effect_type
        self.duration = duration
    
    def use(self, player):
        """Use the tech item."""
        if self.effect_type == "smoke":
            print(f"You deploy the {self.name}, creating a smoke screen!")
            # In a full implementation, this would affect NPC visibility and behavior
            player.set_property("smoke_screen_active", self.duration)
            player.inventory.remove(self)
        elif self.effect_type == "decoy":
            print(f"You deploy the {self.name}, creating a holographic decoy!")
            # In a full implementation, this would create a decoy object that distracts NPCs
            player.set_property("decoy_active", self.duration)
            player.inventory.remove(self)
        elif self.effect_type == "recon":
            print(f"You deploy the {self.name} to scout the area!")
            # In a full implementation, this would reveal hidden items and NPCs
            player.set_property("recon_active", self.duration)
            # Drones aren't consumed when used
        else:
            print(f"You're not sure how to use the {self.name}.")
    
    def to_dict(self):
        """Convert tech item to dictionary for serialization."""
        data = super().to_dict()
        data["effect_type"] = self.effect_type
        data["duration"] = self.duration
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create tech item from dictionary."""
        tech_item = cls(
            data["name"],
            data["description"],
            data["effect_type"],
            data["duration"],
            data["value"],
            Coordinates.from_dict(data["coordinates"])
        )
        tech_item.id = data.get("id", tech_item.id)
        return tech_item


class EffectItem(Item):
    """Items that apply effects to targets."""
    def __init__(self, name, description, effect_type, duration=0, value=0, coordinates=None):
        super().__init__(name, description, value, coordinates)
        self.effect_type = effect_type
        self.duration = duration
    
    def use(self, player):
        """Use the effect item on a target."""
        print(f"You ready your {self.name}. Use 'use {self.name} on [target]' to apply its effect.")
    
    def apply_effect(self, target):
        """Apply the effect to a target."""
        if self.effect_type == "hallucination":
            print(f"You spray {target.name} with the {self.name}!")
            print(f"{target.name} starts hallucinating!")
            # In a full implementation, this would affect NPC behavior
            target.set_property("hallucinating", self.duration)
        elif self.effect_type == "confusion":
            print(f"You zap {target.name} with the {self.name}!")
            print(f"{target.name} becomes confused!")
            # In a full implementation, this would affect NPC behavior
            target.set_property("confused", self.duration)
        else:
            print(f"The {self.name} has no effect on {target.name}.")
    
    def to_dict(self):
        """Convert effect item to dictionary for serialization."""
        data = super().to_dict()
        data["effect_type"] = self.effect_type
        data["duration"] = self.duration
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create effect item from dictionary."""
        effect_item = cls(
            data["name"],
            data["description"],
            data["effect_type"],
            data["duration"],
            data["value"],
            Coordinates.from_dict(data["coordinates"])
        )
        effect_item.id = data.get("id", effect_item.id)
        return effect_item


class Seed(Item):
    """Seeds that can be planted to grow plants."""
    def __init__(self, name, description, plant_type, growth_time=5, value=0, coordinates=None):
        super().__init__(name, description, value, coordinates)
        self.plant_type = plant_type
        self.growth_time = growth_time
    
    def use(self, player):
        """Use the seed."""
        print(f"You need to plant this seed in a soil plot. Use 'plant {self.name} in [soil plot]'.")
    
    def to_dict(self):
        """Convert seed to dictionary for serialization."""
        data = super().to_dict()
        data["plant_type"] = self.plant_type
        data["growth_time"] = self.growth_time
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create seed from dictionary."""
        seed = cls(
            data["name"],
            data["description"],
            data["plant_type"],
            data["growth_time"],
            data["value"],
            Coordinates.from_dict(data["coordinates"])
        )
        seed.id = data.get("id", seed.id)
        return seed


class Plant(Item):
    """Plants that grow from seeds."""
    def __init__(self, name, description, plant_type, growth_stage=0, max_growth=5, needs_water=True, value=0, coordinates=None):
        super().__init__(name, description, value, coordinates)
        self.plant_type = plant_type
        self.growth_stage = growth_stage
        self.max_growth = max_growth
        self.needs_water = needs_water
        self.is_mature = False
        self.pickupable = False
        self.effects = []
    
    def grow(self):
        """Grow the plant by one stage."""
        if self.growth_stage < self.max_growth:
            self.growth_stage += 1
            self.needs_water = True
            print(f"The {self.name} grows to stage {self.growth_stage}/{self.max_growth}.")
            
            if self.growth_stage == self.max_growth:
                self.is_mature = True
                print(f"The {self.name} is now mature and ready to harvest!")
        else:
            print(f"The {self.name} is already fully grown.")
    
    def add_effect(self, effect):
        """Add an effect to the plant."""
        self.effects.append(effect)
    
    def to_dict(self):
        """Convert plant to dictionary for serialization."""
        data = super().to_dict()
        data["plant_type"] = self.plant_type
        data["growth_stage"] = self.growth_stage
        data["max_growth"] = self.max_growth
        data["needs_water"] = self.needs_water
        data["is_mature"] = self.is_mature
        data["effects"] = [effect.__class__.__name__ for effect in self.effects]
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create plant from dictionary."""
        plant = cls(
            data["name"],
            data["description"],
            data["plant_type"],
            data["growth_stage"],
            data["max_growth"],
            data["needs_water"],
            data["value"],
            Coordinates.from_dict(data["coordinates"])
        )
        plant.is_mature = data.get("is_mature", False)
        plant.id = data.get("id", plant.id)
        # Effects would need to be resolved separately
        return plant


class Tool(Item):
    """Tools that can be used for various tasks."""
    def __init__(self, name, description, tool_type, uses=10, max_uses=10, value=0, coordinates=None):
        super().__init__(name, description, value, coordinates)
        self.tool_type = tool_type
        self.uses = uses
        self.max_uses = max_uses
    
    def use(self, player):
        """Use the tool."""
        if self.uses <= 0:
            print(f"Your {self.name} is depleted and needs to be refilled.")
            return False
        
        if self.tool_type == "watering":
            print(f"You need to use this on a plant. Use 'water [soil plot]'.")
        else:
            print(f"You use the {self.name}.")
            self.uses -= 1
            
            if self.uses <= 0:
                print(f"Your {self.name} is now depleted.")
            elif self.uses < self.max_uses * 0.2:
                print(f"Your {self.name} is running low.")
        
        return True
    
    def refill(self):
        """Refill the tool."""
        self.uses = self.max_uses
        print(f"Your {self.name} has been refilled. Uses: {self.uses}/{self.max_uses}")
    
    def to_dict(self):
        """Convert tool to dictionary for serialization."""
        data = super().to_dict()
        data["tool_type"] = self.tool_type
        data["uses"] = self.uses
        data["max_uses"] = self.max_uses
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create tool from dictionary."""
        tool = cls(
            data["name"],
            data["description"],
            data["tool_type"],
            data["uses"],
            data["max_uses"],
            data["value"],
            Coordinates.from_dict(data["coordinates"])
        )
        tool.id = data.get("id", tool.id)
        return tool


class WateringCan(Tool):
    """A watering can for watering plants."""
    def __init__(self, name="Watering Can", description="A can for watering plants.", value=15, coordinates=None):
        super().__init__(name, description, "watering", 10, 10, value, coordinates)
    
    def use(self, player):
        """Use the watering can."""
        print(f"You need to use this on a plant. Use 'water [soil plot]'.")
    
    def refill(self):
        """Refill the watering can."""
        self.uses = self.max_uses
        print(f"Your {self.name} has been refilled with water. Uses: {self.uses}/{self.max_uses}")


class ItemManager:
    """Manages all items in the game."""
    def __init__(self):
        self.items = {}  # Dictionary mapping item IDs to Item objects
        self.templates = {}  # Dictionary of item templates
    
    def add_item(self, item):
        """Add an item to the manager."""
        self.items[item.id] = item
    
    def get_item(self, item_id):
        """Get an item by ID."""
        return self.items.get(item_id)
    
    def create_from_template(self, template_id, **kwargs):
        """Create an item from a template."""
        if template_id not in self.templates:
            raise ValueError(f"Unknown item template: {template_id}")
        
        template = self.templates[template_id].copy()
        
        # Override template values with provided kwargs
        for key, value in kwargs.items():
            if key in template:
                template[key] = value
        
        # Create the appropriate item type
        item_type = template.get("type", "Item")
        
        if item_type == "Consumable":
            item = Consumable(
                template["name"],
                template["description"],
                template.get("value", 0),
                template.get("nutrition", 0),
                template.get("effects", {}),
                Coordinates(0, 0, 0)  # Will be set by caller
            )
        elif item_type == "Weapon":
            item = Weapon(
                template["name"],
                template["description"],
                template.get("damage", 10),
                template.get("durability", 100),
                template.get("value", 0),
                Coordinates(0, 0, 0)  # Will be set by caller
            )
        elif item_type == "TechItem":
            item = TechItem(
                template["name"],
                template["description"],
                template.get("effect_type", "none"),
                template.get("duration", 0),
                template.get("value", 0),
                Coordinates(0, 0, 0)  # Will be set by caller
            )
        elif item_type == "EffectItem":
            item = EffectItem(
                template["name"],
                template["description"],
                template.get("effect_type", "none"),
                template.get("duration", 0),
                template.get("value", 0),
                Coordinates(0, 0, 0)  # Will be set by caller
            )
        elif item_type == "Seed":
            item = Seed(
                template["name"],
                template["description"],
                template.get("plant_type", "generic"),
                template.get("growth_time", 5),
                template.get("value", 0),
                Coordinates(0, 0, 0)  # Will be set by caller
            )
        elif item_type == "Tool":
            item = Tool(
                template["name"],
                template["description"],
                template.get("tool_type", "generic"),
                template.get("uses", 10),
                template.get("max_uses", 10),
                template.get("value", 0),
                Coordinates(0, 0, 0)  # Will be set by caller
            )
        else:
            item = Item(
                template["name"],
                template["description"],
                template.get("value", 0),
                Coordinates(0, 0, 0)  # Will be set by caller
            )
        
        # Generate a unique ID if needed
        if "id" in kwargs:
            item.id = kwargs["id"]
        
        return item
    
    def save_to_json(self, filename):
        """Save all items to a JSON file."""
        data = {
            "items": {item_id: item.to_dict() for item_id, item in self.items.items()},
            "templates": self.templates
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_from_json(self, filename):
        """Load items from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Load templates
        self.templates = data.get("templates", {})
        
        # Load items
        for item_id, item_data in data.get("items", {}).items():
            item_type = item_data.get("type", "Item")
            
            if item_type == "Consumable":
                item = Consumable.from_dict(item_data)
            elif item_type == "Weapon":
                item = Weapon.from_dict(item_data)
            elif item_type == "TechItem":
                item = TechItem.from_dict(item_data)
            elif item_type == "EffectItem":
                item = EffectItem.from_dict(item_data)
            elif item_type == "Seed":
                item = Seed.from_dict(item_data)
            elif item_type == "Plant":
                item = Plant.from_dict(item_data)
            elif item_type == "Tool":
                item = Tool.from_dict(item_data)
            elif item_type == "WateringCan":
                item = WateringCan.from_dict(item_data)
            else:
                item = Item.from_dict(item_data)
            
            self.add_item(item)