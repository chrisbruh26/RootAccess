"""
Objects module for Root Access game.
This module defines various interactive objects for the game.
"""

class GameObject:
    """Base class for all interactive objects in the game."""
    
    def __init__(self, name, description):
        """Initialize a GameObject object."""
        self.name = name
        self.description = description
        self.x = None  # X coordinate on the grid
        self.y = None  # Y coordinate on the grid
        self.location = None
    
    def __str__(self):
        """Return a string representation of the object."""
        return self.name
    
    def place_on_grid(self, grid, x, y):
        """Place the object on a grid at the specified coordinates."""
        if grid.place_object(self, x, y):
            self.x = x
            self.y = y
            return True
        return False
    
    def interact(self, player):
        """Interact with the object."""
        return True, f"You interact with the {self.name}."


class Container(GameObject):
    """An object that can contain items."""
    
    def __init__(self, name, description):
        """Initialize a Container object."""
        super().__init__(name, description)
        self.items = []
    
    def add_item(self, item):
        """Add an item to the container."""
        self.items.append(item)
    
    def remove_item(self, item_name):
        """Remove an item from the container by name."""
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
            return item
        return None
    
    def interact(self, player):
        """Interact with the container."""
        if not self.items:
            return True, f"The {self.name} is empty."
        
        item_names = ", ".join(str(item) for item in self.items)
        return True, f"The {self.name} contains: {item_names}"


class Computer(GameObject):
    """A computer that can be used to run programs."""
    
    def __init__(self, name, description):
        """Initialize a Computer object."""
        super().__init__(name, description)
        self.programs = []
    
    def add_program(self, program):
        """Add a program to the computer."""
        self.programs.append(program)
    
    def interact(self, player):
        """Interact with the computer."""
        if not self.programs:
            return True, f"The {self.name} has no programs installed."
        
        program_names = ", ".join(str(program) for program in self.programs)
        return True, f"The {self.name} has the following programs: {program_names}"


class HidingSpot(GameObject):
    """A spot where the player can hide."""
    
    def __init__(self, name, description):
        """Initialize a HidingSpot object."""
        super().__init__(name, description)
        self.is_occupied = False
        self.occupant = None
    
    def enter(self, player):
        """Enter the hiding spot."""
        if self.is_occupied:
            return False, f"The {self.name} is already occupied."
        
        self.is_occupied = True
        self.occupant = player
        return True, f"You hide in the {self.name}."
    
    def leave(self, player):
        """Leave the hiding spot."""
        if not self.is_occupied or self.occupant != player:
            return False, f"You're not hiding in the {self.name}."
        
        self.is_occupied = False
        self.occupant = None
        return True, f"You emerge from the {self.name}."
    
    def interact(self, player):
        """Interact with the hiding spot."""
        if self.is_occupied:
            if self.occupant == player:
                return self.leave(player)
            return False, f"The {self.name} is occupied."
        return self.enter(player)
