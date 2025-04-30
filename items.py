import random

# ----------------------------- #
# ITEM CLASSES                  #
# ----------------------------- #

class Item:
    def __init__(self, name, description, value=0):
        self.name = name
        self.description = description
        self.value = value

    def __str__(self):
        return self.name


class Weapon(Item):
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value)
        self.damage = damage
        self.effects = []  # List of effects this weapon can apply

    def __str__(self):
        return f"{self.name} (Damage: {self.damage})"
        
    def add_effect(self, effect):
        """Add an effect to this weapon."""
        self.effects.append(effect)
        
    def use(self, player, game):
        """Use the weapon, applying its effects to NPCs in the current area."""
        messages = []
        
        # Basic attack message
        messages.append(f"You use the {self.name}!")
        
        # Apply effects to NPCs in the current area
        if self.effects and player.current_area and player.current_area.npcs:
            for effect in self.effects:
                # Create a copy of the effect for each NPC
                for npc in player.current_area.npcs:
                    # Skip dead NPCs
                    if hasattr(npc, 'is_alive') and not npc.is_alive:
                        continue
                        
                    # Apply the effect to the NPC
                    if hasattr(npc, 'active_effects'):
                        # Create a new instance of the effect for this NPC
                        effect_copy = type(effect)()
                        npc.active_effects.append(effect_copy)
                        #messages.append(f"{npc.name} is affected by {effect.name}!")
        
        return True, "\n".join(messages)


class Consumable(Item):
    def __init__(self, name, description, value, health_restore):
        super().__init__(name, description, value)
        self.health_restore = health_restore

    def __str__(self):
        return f"{self.name} (Restores: {self.health_restore} health)"
