"""
Grid-based Structure module for Root Access game.
This module defines the GridStructure class for buildings and other structures on the grid.

NOT in the template
"""

class GridStructure:
    """Represents a structure on the grid, such as a building or container."""
    
    def __init__(self, name, description, area, region=None, relative_to=None, relative_position=None):
        """Initialize a GridStructure object."""
        self.name = name
        self.description = description
        self.area = area
        self.coordinates = []  # List of coordinates the structure occupies
        self.rooms = []  # List of rooms (can be other structures or areas)
        self.locked = True
        self.region = region  # The region this structure belongs to
        self.relative_to = relative_to  # Another structure to be relative to
        self.relative_position = relative_position  # "left", "right", "front", "back"
    
    def place_on_grid(self):
        """Place the structure on the area's grid."""
        if self.region:
            if self.relative_to:
                # Place relative to another structure
                self.place_relative_to(self.relative_to, self.relative_position)
            else:
                # Place randomly within the region
                self.place_randomly_in_region()
        else:
            # Place at the specified coordinates
            for x, y in self.coordinates:
                if not self.area.grid.place_object(self, x, y):
                    print(f"Warning: Could not place {self.name} at ({x}, {y}) on the grid.")
    
    def place_randomly_in_region(self):
        """Place the structure at a random location within its region."""
        if not self.region:
            print(f"Error: {self.name} has no region to place in.")
            return
        
        x, y = self.region.get_random_location()
        self.coordinates = [(x, y)]  # For now, assume 1x1 size
        if not self.area.grid.place_object(self, x, y):
            print(f"Warning: Could not place {self.name} at ({x}, {y}) on the grid.")
    
    def place_relative_to(self, other_structure, position):
        """Place the structure relative to another structure."""
        if not self.region:
            print(f"Error: {self.name} has no region to place in.")
            return
        
        if not other_structure.coordinates:
            print(f"Error: {other_structure.name} has no coordinates to be relative to.")
            return
        
        # Get a coordinate from the other structure
        other_x, other_y = other_structure.coordinates[0]
        
        # Calculate the new coordinates based on the position
        if position == "left":
            new_x, new_y = other_x - 1, other_y
        elif position == "right":
            new_x, new_y = other_x + 1, other_y
        elif position == "front":
            new_x, new_y = other_x, other_y + 1
        elif position == "back":
            new_x, new_y = other_x, other_y - 1
        else:
            print(f"Error: Invalid relative position '{position}'.")
            return
        
        # Check if the new coordinates are valid
        if not self.area.grid.is_valid_coordinate(new_x, new_y):
            print(f"Warning: Could not place {self.name} at ({new_x}, {new_y}) - out of bounds.")
            return
        
        # Check if the new cell is occupied
        if self.area.grid.is_cell_occupied(new_x, new_y):
            print(f"Warning: Could not place {self.name} at ({new_x}, {new_y}) - cell occupied.")
            return
        
        self.coordinates = [(new_x, new_y)]
        if not self.area.grid.place_object(self, new_x, new_y):
            print(f"Warning: Could not place {self.name} at ({new_x}, {new_y}) on the grid.")
    
    def remove_from_grid(self):
        """Remove the structure from the area's grid."""
        for x, y in self.coordinates:
            self.area.grid.remove_object(x, y)
    
    def add_room(self, room):
        """Add a room to the structure."""
        self.rooms.append(room)
    
    def enter(self, player):
        """Allow the player to enter the structure."""
        if self.rooms:
            for room in self.rooms:
                if hasattr(room, 'enter'):
                    return room.enter(player)
            return False, "This structure has no accessible rooms."
        return False, "This structure has no rooms to enter."
    
    def is_near(self, player):
        """Check if the player is near the structure."""
        for x, y in self.coordinates:
            if abs(player.x - x) <= 1 and abs(player.y - y) <= 1:
                return True
        return False
    
    def interact(self, player):
        """Interact with the structure."""
        if not self.is_near(player):
            return False, f"You're not close enough to the {self.name} to interact with it."
        
        if self.locked:
            return False, f"The {self.name} is locked."
        
        return self.enter(player)
    
    def unlock(self, player):
        """Unlock the structure."""
        if not self.is_near(player):
            return False, f"You're not close enough to the {self.name} to unlock it."
        
        if not self.locked:
            return False, f"The {self.name} is already unlocked."
        
        # Check if the player has the key
        key = next((item for item in player.inventory if item.name.lower() == "keycard"), None)
        if not key:
            return False, f"You don't have the key to unlock the {self.name}."
        
        self.locked = False
        return True, f"You unlock the {self.name}."


class LockedRoom:
    """Represents a locked room within a structure."""
    
    def __init__(self, name, description, locked=True, unlock_method=None, loot=None):
        """Initialize a LockedRoom object."""
        self.name = name
        self.description = description
        self.locked = locked  # Determines if the room is accessible
        self.unlock_method = unlock_method  # "hack" or "keycard"
        self.loot = loot if loot else []  # Items stored in the room
    
    def unlock(self, player):
        """Unlock the room."""
        if not self.locked:
            return False, f"{self.name} is already unlocked."
        
        if self.unlock_method == "hack" and any(item.name.lower() == "hacking tool" for item in player.inventory):
            self.locked = False
            return True, f"You hacked into {self.name}!"
        elif self.unlock_method == "keycard":
            keycard = next((item for item in player.inventory if item.name.lower() == "keycard"), None)
            if keycard:
                self.locked = False
                player.inventory.remove(keycard)
                return True, f"You used a keycard to unlock {self.name}! You can now enter."
        
        return False, "You don't have the necessary tool to unlock this room."
    
    def enter(self, player):
        """Allow the player to enter the room."""
        if self.locked:
            return False, f"{self.name} is locked. You can't enter yet."
        
        result_message = f"You enter {self.name}. {self.description}"
        
        # Provide loot
        if self.loot:
            result_message += "\nYou found the following items:"
            for item in self.loot:
                result_message += f"\n- {item.name}"
                item.x = player.x
                item.y = player.y
                player.current_area.add_item(item)
            self.loot = []
        else:
            result_message += "\nThe room is empty."
        
        return True, result_message
    
    def add_item(self, item):
        """Add an item to the room's loot."""
        self.loot.append(item)
    
    def remove_item(self, item):
        """Remove an item from the room's loot."""
        if item in self.loot:
            self.loot.remove(item)
