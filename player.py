"""
Grid-based Player module for Root Access game.
This module defines the GridPlayer class for the grid-based template.
"""

class GridPlayer:
    """Represents the player in the grid-based game."""
    
    def __init__(self):
        """Initialize a GridPlayer object."""
        self.inventory = []
        self.health = 100
        self.max_health = 100
        self.money = 100
        self.current_area = None
        self.x = 0  # X coordinate on the grid
        self.y = 0  # Y coordinate on the grid
    
    def add_item(self, item):
        """Add an item to the player's inventory."""
        self.inventory.append(item)
    
    def remove_item(self, item_name):
        """Remove an item from the player's inventory by name."""
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item:
            self.inventory.remove(item)
            return item
        return None
    
    def use_item(self, item_name, game):
        """Use an item from the player's inventory."""
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            return False, f"You don't have a {item_name}."
        
        # Handle consumables
        if hasattr(item, 'health_restore'):
            self.health = min(self.max_health, self.health + item.health_restore)
            self.inventory.remove(item)
            return True, f"You use the {item.name} and restore {item.health_restore} health."
        
        # Handle other items with use method
        if hasattr(item, 'use'):
            return item.use(self, game)
        
        # Default behavior
        return False, f"You can't use the {item.name} right now."
    
    def move(self, direction):
        """Move the player in the specified direction within the current area."""
        if not self.current_area:
            return False, "You're not in any area."
        
        # Calculate new coordinates based on direction
        new_x, new_y = self.x, self.y
        if direction == "north" or direction == "forward":
            new_y -= 1
        elif direction == "south" or direction == "backward":
            new_y += 1
        elif direction == "east" or direction == "right":
            new_x += 1
        elif direction == "west" or direction == "left":
            new_x -= 1
        else:
            return False, f"Unknown direction: {direction}"
        
        # Check if the new coordinates are valid
        if not self.current_area.grid.is_valid_coordinate(new_x, new_y):
            return False, "You can't move in that direction."
        
        # Check if the new cell is occupied
        if self.current_area.grid.is_cell_occupied(new_x, new_y):
            obj = self.current_area.grid.get_object(new_x, new_y)
            return False, f"You can't move there. There's a {obj.name} in the way."
        
        # Update player's position
        self.current_area.grid.remove_object(self.x, self.y)
        self.x, self.y = new_x, new_y
        self.current_area.grid.place_object(self, new_x, new_y)
        
        # Check for items at the new coordinates
        nearby_items = [item for item in self.current_area.items 
                       if hasattr(item, 'x') and hasattr(item, 'y') 
                       and item.x == self.x and item.y == self.y]
        
        if nearby_items:
            item_names = ", ".join(item.name for item in nearby_items)
            return True, f"You move {direction}. You see: {item_names}"
        
        return True, f"You move {direction}."
    
    def change_area(self, direction):
        """Move to a different area in the specified direction."""
        if not self.current_area:
            return False, "You're not in any area."
        
        if direction not in self.current_area.connections:
            return False, "You can't go that way."
        
        # Remove player from current grid
        if hasattr(self.current_area, 'grid'):
            self.current_area.grid.remove_object(self.x, self.y)
        
        # Change area
        self.current_area = self.current_area.connections[direction]
        
        # Reset coordinates when changing areas
        self.x = self.current_area.grid_width // 2
        self.y = self.current_area.grid_height // 2
        
        # Place player on new grid
        if hasattr(self.current_area, 'grid'):
            self.current_area.grid.place_object(self, self.x, self.y)
        
        return True, f"You move {direction} to {self.current_area.name}.\n\n{self.current_area.get_full_description(self)}"
    
    def take_item(self, item_name):
        """Take an item from the current area."""
        if not self.current_area:
            return False, "You're not in any area."
        
        # Find the item in the current area
        item = next((i for i in self.current_area.items if i.name.lower() == item_name.lower()), None)
        if not item:
            return False, f"There is no {item_name} here."
        
        # Check if the player is close enough to the item
        if hasattr(item, 'x') and hasattr(item, 'y') and not self._is_near_coordinates(item.x, item.y):
            return False, f"You're not close enough to the {item_name} to pick it up."
        
        # Take the item
        self.current_area.remove_item(item_name)
        self.add_item(item)
        return True, f"You take the {item.name}."
    
    def drop_item(self, item_name):
        """Drop an item from the player's inventory."""
        if not self.current_area:
            return False, "You're not in any area."
        
        # Find the item in the player's inventory
        item = self.remove_item(item_name)
        if not item:
            return False, f"You don't have a {item_name}."
        
        # Set the item's coordinates to the player's coordinates
        if hasattr(item, 'x') and hasattr(item, 'y'):
            item.x = self.x
            item.y = self.y
        
        # Add the item to the current area
        self.current_area.add_item(item, self.x, self.y)
        return True, f"You drop the {item.name}."
    
    def interact_with_object(self, object_name):
        """Interact with an object in the current area."""
        if not self.current_area:
            return False, "You're not in any area."
        
        # Find the object in the current area
        obj = next((o for o in self.current_area.objects if o.name.lower() == object_name.lower()), None)
        if not obj:
            return False, f"There is no {object_name} here."
        
        # Check if the player is close enough to the object
        if hasattr(obj, 'x') and hasattr(obj, 'y') and not self._is_near_coordinates(obj.x, obj.y):
            return False, f"You're not close enough to the {object_name} to interact with it."
        
        # Interact with the object
        if hasattr(obj, 'interact'):
            return obj.interact(self)
        
        # Default interaction
        return True, f"You interact with the {obj.name}."
    
    def _is_near_coordinates(self, x, y, radius=1):
        """Check if the player is near the specified coordinates."""
        return abs(self.x - x) <= radius and abs(self.y - y) <= radius
    
    def _is_near_object(self, obj, radius=1):
        """Check if the player is near the specified object."""
        if hasattr(obj, 'x') and hasattr(obj, 'y'):
            return self._is_near_coordinates(obj.x, obj.y, radius)
        return False
