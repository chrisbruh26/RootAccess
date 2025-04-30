import random
from items import Item

# ----------------------------- #
# EFFECTS SYSTEM                #
# ----------------------------- #

class Effect:
    """Represents a hazard effect with duration and properties"""
    def __init__(self, name, description, duration=3, stackable=False):
        self.name = name
        self.description = description
        self.duration = duration
        self.stackable = stackable
        self.remaining_turns = duration

    def update(self):
        """Decrement remaining turns and return True if expired"""
        self.remaining_turns -= 1
        return self.remaining_turns <= 0

    def __str__(self):
        return f"{self.name}"
        
    @staticmethod
    def load_effect_messages(effect_type):
        """Load effect messages from the JSON file."""
        import json
        import os
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, 'npc_effects.json')
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get(effect_type, {})
        except (FileNotFoundError, json.JSONDecodeError):
            # Return empty dict if file not found or invalid
            return {}
    

class HallucinationEffect(Effect):
    """Hallucinogenic effect that affects perception and behavior."""
    def __init__(self):
        super().__init__("Hallucination", "Perception altered by hallucinogens")
        self.duration = 5
        self.effect_data = self.load_effect_messages("hallucination")
    
    def get_hallucination_message(self, plural=False):
        """Get a random hallucination message."""
        message_type = "plural" if plural else "singular"
        messages = self.effect_data.get(message_type, ["is hallucinating"])
        return random.choice(messages)
    
    def get_combat_prevention_message(self):
        """Get a message explaining why the NPC can't fight."""
        messages = self.effect_data.get("combat_prevention", ["is too distracted to fight"])
        return random.choice(messages)
        
    def affects_combat(self):
        """Determines if this effect prevents combat behavior."""
        return True  # This effect prevents combat


class ConfusionEffect(Effect):
    """Confusion effect that makes NPCs behave erratically."""
    def __init__(self):
        super().__init__("Confusion", "Confused and disoriented", duration=3)
        self.effect_data = self.load_effect_messages("confusion")
    
    def get_confusion_message(self, plural=False):
        """Get a random confusion message."""
        message_type = "plural" if plural else "singular"
        messages = self.effect_data.get(message_type, ["is confused"])
        return random.choice(messages)
    
    def affects_combat(self):
        """Determines if this effect prevents combat behavior."""
        # 50% chance to prevent combat
        return random.random() < 0.5
        



class PlantEffect:
    """Base class for all plant effects."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def apply_to_player(self, player, game):
        """Apply this effect to the player."""
        return f"The {self.name} effect is applied to you."
    
    def __str__(self):
        return self.name


class SupervisionEffect(PlantEffect):
    """Effect that allows the player to see hidden items."""
    def __init__(self):
        super().__init__("Supervision", "Allows you to see hidden items")
        self.duration = 3  # Number of turns the effect lasts
    
    def apply_to_player(self, player, game):
        """Apply supervision effect to player, spawning hidden items in the area."""
        # Add the effect to player's active effects
        if not hasattr(player, 'active_effects'):
            player.active_effects = {}
        
        player.active_effects[self.name] = self.duration
        
        # Spawn hidden items in the current area
        hidden_items = [
            Item("Encrypted USB", "A USB stick with encrypted data.", 50),
            Item("Strange Crystal", "A crystal that glows with an otherworldly light.", 75),
            Item("Tech Fragment", "A piece of advanced technology.", 30)
        ]
        
        # Add 1-2 random hidden items to the area
        num_items = random.randint(1, 2)
        for _ in range(num_items):
            item = random.choice(hidden_items)
            player.current_area.add_item(item)
        
        return f"Your vision shifts and warps. Suddenly, you can see things that weren't visible before. The {self.name} effect will last for {self.duration} turns."


class HackedPlantEffect(PlantEffect):
    """Effect that makes plants come alive."""
    def __init__(self):
        super().__init__("Hacked Plant", "Plants may come alive and follow commands")
    
    def apply_to_player(self, player, game):
        """Apply hacked plant effect, allowing control of plants."""
        if not hasattr(player, 'active_effects'):
            player.active_effects = {}
        
        player.active_effects[self.name] = 5  # Lasts for 5 turns
        
        return "You feel a strange connection to the plants around you. They seem to respond to your thoughts."


class Substance:
    """Base class for substances that can be used on plants."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.effects = []
    
    def add_effect(self, effect):
        """Add an effect to this substance."""
        self.effects.append(effect)
    
    def __str__(self):
        return self.name


class HackedMilk(Substance):
    """A special substance that gives plants the supervision effect."""
    def __init__(self):
        super().__init__("Hacked Milk", "A strange, glowing milk-like substance that can alter plant growth.")
        self.add_effect(SupervisionEffect())


# idea for later: a substance that causes NPCs to use the garden uncontrollably, call the effect "green fever" and make it spawn tons of seeds and possibly add more soil plots.
