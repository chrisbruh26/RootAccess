"""
Items module for Root Access game.
This module defines the Item class and its subclasses.
"""

class Item:
    """Base class for all items in the game."""
    
    def __init__(self, name, description, value=0):
        """Initialize an Item object."""
        self.name = name
        self.description = description
        self.value = value
        self.x = None  # X coordinate on the grid
        self.y = None  # Y coordinate on the grid
    
    def __str__(self):
        """Return a string representation of the item."""
        return self.name
    
    def examine(self):
        """Return a detailed description of the item."""
        return f"{self.name}: {self.description} (Value: ${self.value})"
    
    def place_on_grid(self, grid, x, y):
        """Place the item on a grid at the specified coordinates."""
        if grid.place_object(self, x, y):
            self.x = x
            self.y = y
            return True
        return False


class Consumable(Item):
    """An item that can be consumed for an effect."""
    
    def __init__(self, name, description, value=0, health_restore=0):
        """Initialize a Consumable object."""
        super().__init__(name, description, value)
        self.health_restore = health_restore
    
    def examine(self):
        """Return a detailed description of the consumable."""
        return f"{self.name}: {self.description} (Value: ${self.value}, Health: +{self.health_restore})"


class Weapon(Item):
    """An item that can be used as a weapon."""
    
    def __init__(self, name, description, value=0, damage=10):
        """Initialize a Weapon object."""
        super().__init__(name, description, value)
        self.damage = damage
    
    def examine(self):
        """Return a detailed description of the weapon."""
        return f"{self.name}: {self.description} (Value: ${self.value}, Damage: {self.damage})"
    
    def attack_npc(self, player, npc):
        """Attack an NPC with this weapon."""
        if hasattr(npc, 'health'):
            npc.health -= self.damage
            if npc.health <= 0:
                npc.health = 0
                npc.is_alive = False
                return True, f"You attack {npc.name} with the {self.name} for {self.damage} damage. {npc.name} is defeated!"
            return True, f"You attack {npc.name} with the {self.name} for {self.damage} damage. {npc.name}'s health: {npc.health}/100"
        return False, f"You can't attack {npc.name} with the {self.name}."
