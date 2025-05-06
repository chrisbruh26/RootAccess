"""
Random Events module for Root Access game.
This module defines random events that can occur during gameplay.
"""

import random
from items import Item, Weapon, Consumable, EffectItem
from effects import HallucinationEffect, ConfusionEffect
from npc_behavior import Civilian, GangMember

class RandomEvent:
    """Base class for random events."""
    
    def __init__(self, name, description, chance=0.1):
        """Initialize a RandomEvent object."""
        self.name = name
        self.description = description
        self.chance = chance  # Chance of the event occurring (0.0 to 1.0)
    
    def should_trigger(self):
        """Check if the event should trigger based on its chance."""
        return random.random() < self.chance
    
    def trigger(self, game):
        """Trigger the event."""
        return f"Event: {self.name}\n{self.description}"


class ItemDiscoveryEvent(RandomEvent):
    """An event where the player discovers an item."""
    
    def __init__(self):
        """Initialize an ItemDiscoveryEvent object."""
        super().__init__(
            "Item Discovery",
            "You discover an item!",
            0.05
        )
    
    def trigger(self, game):
        """Trigger the event."""
        # Create a random item
        item_types = ["normal", "weapon", "consumable", "effect"]
        item_type = random.choice(item_types)
        
        if item_type == "normal":
            item = Item(
                random.choice(["Strange Device", "Mysterious Gadget", "Unknown Tool", "Odd Contraption"]),
                "A strange item you found.",
                random.randint(10, 50)
            )
        elif item_type == "weapon":
            item = Weapon(
                random.choice(["Rusty Knife", "Old Pipe", "Broken Bat", "Heavy Wrench"]),
                "A makeshift weapon you found.",
                random.randint(20, 100),
                random.randint(5, 20)
            )
        elif item_type == "consumable":
            item = Consumable(
                random.choice(["Energy Bar", "Medkit", "Bandages", "Pain Pills"]),
                "A consumable item you found.",
                random.randint(5, 30),
                random.randint(10, 50)
            )
        elif item_type == "effect":
            effect = random.choice([HallucinationEffect(), ConfusionEffect()])
            item = EffectItem(
                random.choice(["Strange Vial", "Glowing Orb", "Pulsing Crystal", "Weird Fungus"]),
                "An item with strange effects you found.",
                random.randint(30, 150),
                effect
            )
        
        # Add the item to the player's current area
        if game.player.current_area:
            item.x = game.player.x
            item.y = game.player.y
            game.player.current_area.add_item(item)
        
        return f"Event: {self.name}\nYou discover a {item.name} on the ground!"


class NPCEncounterEvent(RandomEvent):
    """An event where the player encounters an NPC."""
    
    def __init__(self):
        """Initialize an NPCEncounterEvent object."""
        super().__init__(
            "NPC Encounter",
            "You encounter an NPC!",
            0.03
        )
    
    def trigger(self, game):
        """Trigger the event."""
        # Determine NPC type
        npc_type = random.choice(["civilian", "gang_member"])
        
        if npc_type == "civilian":
            # Create a civilian NPC
            names = ["Ben", "Bob", "Charl", "Muckle", "Beevo", "ZeFronk", "Grazey", "Honk", "Ivee", "Jork"]
            name_variations = ["etti", "oodle", "op", "eeky", "-eep", "uffin", "bertmo", "athur", "ubble", "uck"]
            name = random.choice(names) + random.choice(name_variations)
            
            npc = Civilian(name, f"A random civilian named {name}.")
            
            # Give the NPC a random item
            item = Item(
                random.choice(["Phone", "Wallet", "Keys", "Watch"]),
                "A personal item.",
                random.randint(5, 20)
            )
            npc.items = [item]
        else:
            # Create a gang member NPC
            gang_names = list(game.gangs.keys())
            if not gang_names:
                gang_names = ["Crimson Vipers", "Bloodhounds"]
            
            gang_name = random.choice(gang_names)
            gang = game.gangs.get(gang_name)
            
            if gang and gang.member_names:
                name = random.choice(gang.member_names)
            else:
                names = ["Spike", "Blade", "Knuckles", "Shadow", "Venom", "Fang", "Razor", "Cobra", "Viper", "Skull"]
                name = random.choice(names)
            
            npc = GangMember(name, f"A member of the {gang_name} gang.")
            npc.gang = gang
            
            # Give the NPC a random weapon
            weapon = Weapon(
                random.choice(["Knife", "Pipe", "Chain", "Brass Knuckles"]),
                "A gang weapon.",
                random.randint(20, 100),
                random.randint(5, 20)
            )
            npc.items = [weapon]
        
        # Add the NPC to the player's current area
        if game.player.current_area:
            # Find a valid position near the player
            for _ in range(10):  # Try 10 times
                dx = random.randint(-3, 3)
                dy = random.randint(-3, 3)
                x = game.player.x + dx
                y = game.player.y + dy
                
                if (x != game.player.x or y != game.player.y) and \
                   game.player.current_area.grid.is_valid_coordinate(x, y) and \
                   not game.player.current_area.grid.is_cell_occupied(x, y):
                    game.player.current_area.add_npc(npc, x, y)
                    break
        
        return f"Event: {self.name}\n{npc.name} appears nearby!"


class WeatherEvent(RandomEvent):
    """An event that changes the weather."""
    
    def __init__(self):
        """Initialize a WeatherEvent object."""
        super().__init__(
            "Weather Change",
            "The weather changes!",
            0.02
        )
        self.weather_types = ["rain", "fog", "clear", "windy", "stormy"]
    
    def trigger(self, game):
        """Trigger the event."""
        weather = random.choice(self.weather_types)
        
        effects = {
            "rain": "The rain makes it harder to see and hear.",
            "fog": "The fog reduces visibility significantly.",
            "clear": "The clear weather improves visibility.",
            "windy": "The wind makes it harder to hear.",
            "stormy": "The storm creates chaos and confusion."
        }
        
        # Apply weather effects to the current area
        if game.player.current_area:
            game.player.current_area.weather = weather
        
        return f"Event: {self.name}\nThe weather changes to {weather}. {effects[weather]}"


class GangActivityEvent(RandomEvent):
    """An event that triggers gang activity."""
    
    def __init__(self):
        """Initialize a GangActivityEvent object."""
        super().__init__(
            "Gang Activity",
            "Gang activity increases in the area!",
            0.04
        )
    
    def trigger(self, game):
        """Trigger the event."""
        # Check if the player is in a gang territory
        if not game.player.current_area:
            return f"Event: {self.name}\nYou hear distant sounds of gang activity."
        
        # Trigger gang activity in the current area
        result = game.player.current_area.handle_gang_activity(game.gangs)
        
        return f"Event: {self.name}\nGang activity increases in {game.player.current_area.name}!"


class RandomEventManager:
    """Manages random events in the game."""
    
    def __init__(self, game):
        """Initialize a RandomEventManager object."""
        self.game = game
        self.events = [
            ItemDiscoveryEvent(),
            NPCEncounterEvent(),
            WeatherEvent(),
            GangActivityEvent()
        ]
        self.last_event_turn = 0
        self.event_cooldown = 10  # Minimum turns between events
    
    def trigger_random_event(self):
        """Trigger a random event if conditions are met."""
        # Check if enough turns have passed since the last event
        if self.game.current_turn - self.last_event_turn < self.event_cooldown:
            return None
        
        # Check each event to see if it should trigger
        triggerable_events = [event for event in self.events if event.should_trigger()]
        
        if triggerable_events:
            # Choose a random event from the triggerable events
            event = random.choice(triggerable_events)
            
            # Trigger the event
            result = event.trigger(self.game)
            
            # Update the last event turn
            self.last_event_turn = self.game.current_turn
            
            # Print the event result
            print(result)
            
            return result
        
        return None
