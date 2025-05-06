"""
NPC module for Root Access game.
This module defines the NPC class and its subclasses.
"""

import random

class NPC:
    """Base class for all NPCs in the game."""
    
    def __init__(self, name, description):
        """Initialize an NPC object."""
        self.name = name
        self.description = description
        self.location = None
        self.x = None  # X coordinate on the grid
        self.y = None  # Y coordinate on the grid
        self.is_alive = True
        self.health = 100
        self.inventory = []
    
    def __str__(self):
        """Return a string representation of the NPC."""
        return self.name
    
    def place_on_grid(self, grid, x, y):
        """Place the NPC on a grid at the specified coordinates."""
        if grid.place_object(self, x, y):
            self.x = x
            self.y = y
            return True
        return False
    
    def move(self, direction):
        """Move the NPC in the specified direction."""
        if not self.location:
            return False
        
        # Calculate new coordinates based on direction
        new_x, new_y = self.x, self.y
        if direction == "north":
            new_y -= 1
        elif direction == "south":
            new_y += 1
        elif direction == "east":
            new_x += 1
        elif direction == "west":
            new_x -= 1
        else:
            return False
        
        # Check if the new coordinates are valid
        if not self.location.grid.is_valid_coordinate(new_x, new_y):
            return False
        
        # Check if the new cell is occupied
        if self.location.grid.is_cell_occupied(new_x, new_y):
            return False
        
        # Update NPC's position
        self.location.grid.remove_object(self.x, self.y)
        self.x, self.y = new_x, new_y
        self.location.grid.place_object(self, new_x, new_y)
        
        return True
    
    def update(self, player):
        """Update the NPC's state for a new turn."""
        # Random movement
        if random.random() < 0.3:  # 30% chance to move
            directions = ["north", "south", "east", "west"]
            direction = random.choice(directions)
            self.move(direction)
    
    def talk(self, player):
        """Talk to the player."""
        return True, f"{self.name} says: Hello there!"


class Civilian(NPC):
    """A civilian NPC."""
    
    def __init__(self, name, description):
        """Initialize a Civilian object."""
        super().__init__(name, description)
    
    def talk(self, player):
        """Talk to the player."""
        responses = [
            f"Hello there! Nice day, isn't it?",
            f"I'm just minding my own business.",
            f"Have you seen anything interesting around here?",
            f"I'm new to this area. Do you know any good places to visit?"
        ]
        return True, f"{self.name} says: {random.choice(responses)}"


class GangMember(NPC):
    """A gang member NPC."""
    
    def __init__(self, name, description, gang_name):
        """Initialize a GangMember object."""
        super().__init__(name, description)
        self.gang_name = gang_name
        self.aggressive = random.choice([True, False])
    
    def talk(self, player):
        """Talk to the player."""
        if self.aggressive:
            responses = [
                f"What are you looking at?",
                f"This is {self.gang_name} territory. Watch yourself.",
                f"You better move along if you know what's good for you.",
                f"I don't like your face."
            ]
        else:
            responses = [
                f"Hey, what's up?",
                f"I'm with the {self.gang_name}. We keep things chill around here.",
                f"You seem cool. Want to hang out?",
                f"Have you seen my pet rock? I lost it somewhere around here."
            ]
        return True, f"{self.name} says: {random.choice(responses)}"
    
    def update(self, player):
        """Update the gang member's state for a new turn."""
        super().update(player)
        
        # Randomly switch between aggressive and non-aggressive
        if random.random() < 0.1:  # 10% chance to switch
            self.aggressive = not self.aggressive
