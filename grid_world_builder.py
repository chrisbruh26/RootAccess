"""
Grid-based World Builder module for Root Access game.
This module defines the GridWorldBuilder class for creating the game world.
"""

import random
from grid_area import GridArea
from items import Item

class GridWorldBuilder:
    """Class for building the game world."""
    
    def __init__(self, game):
        """Initialize a GridWorldBuilder object."""
        self.game = game
    
    def build_world(self):
        """Build the game world."""
        # Create areas
        self._create_areas()
        
        # Connect areas
        self._connect_areas()
        
        # Add items and objects to areas
        self._populate_areas()
        
        # Set player's starting area
        self.game.player.current_area = self.game.areas["Downtown"]
        self.game.player.x = self.game.player.current_area.grid_width // 2
        self.game.player.y = self.game.player.current_area.grid_height // 2
        
        # Place player on the grid
        self.game.player.current_area.grid.place_object(self.game.player, self.game.player.x, self.game.player.y)
    
    def _create_areas(self):
        """Create the areas in the game world."""
        # Create Downtown area
        downtown = GridArea("Downtown", "The bustling downtown area of the city.", 10, 10)
        self.game.areas["Downtown"] = downtown
        
        # Create Park area
        park = GridArea("Park", "A peaceful park with trees and benches.", 8, 8)
        self.game.areas["Park"] = park
        
        # Create Mall area
        mall = GridArea("Mall", "A shopping mall with various stores.", 12, 12)
        self.game.areas["Mall"] = mall
        
        # Create Residential area
        residential = GridArea("Residential", "A quiet residential neighborhood.", 10, 10)
        self.game.areas["Residential"] = residential
    
    def _connect_areas(self):
        """Connect the areas in the game world."""
        # Connect Downtown to other areas
        self.game.areas["Downtown"].add_connection("north", self.game.areas["Park"])
        self.game.areas["Downtown"].add_connection("east", self.game.areas["Mall"])
        self.game.areas["Downtown"].add_connection("south", self.game.areas["Residential"])
        
        # Connect Park to other areas
        self.game.areas["Park"].add_connection("south", self.game.areas["Downtown"])
        
        # Connect Mall to other areas
        self.game.areas["Mall"].add_connection("west", self.game.areas["Downtown"])
        
        # Connect Residential to other areas
        self.game.areas["Residential"].add_connection("north", self.game.areas["Downtown"])
    
    def _populate_areas(self):
        """Add items and objects to the areas."""
        # Add items to Downtown
        self._add_item_to_area("Downtown", "Wallet", "A leather wallet with some cash.", 20)
        self._add_item_to_area("Downtown", "Phone", "A smartphone with a cracked screen.", 50)
        
        # Add items to Park
        self._add_item_to_area("Park", "Frisbee", "A plastic frisbee.", 5)
        self._add_item_to_area("Park", "Water Bottle", "A reusable water bottle.", 10)
        
        # Add items to Mall
        self._add_item_to_area("Mall", "Shopping Bag", "A paper shopping bag.", 2)
        self._add_item_to_area("Mall", "Gift Card", "A gift card with $25 balance.", 25)
        
        # Add items to Residential
        self._add_item_to_area("Residential", "Key", "A house key.", 5)
        self._add_item_to_area("Residential", "Mail", "Some unopened mail.", 1)
    
    def _add_item_to_area(self, area_name, item_name, item_description, item_value):
        """Add an item to an area at a random position."""
        area = self.game.areas[area_name]
        
        # Create the item
        item = Item(item_name, item_description, item_value)
        
        # Find a random empty position
        x, y = self._find_empty_position(area)
        
        # Add the item to the area
        if x is not None and y is not None:
            item.x = x
            item.y = y
            area.add_item(item, x, y)
    
    def _find_empty_position(self, area):
        """Find a random empty position in the area."""
        for _ in range(100):  # Try 100 times to find an empty position
            x = random.randint(0, area.grid_width - 1)
            y = random.randint(0, area.grid_height - 1)
            if not area.grid.is_cell_occupied(x, y):
                return x, y
        return None, None  # If no empty position is found
