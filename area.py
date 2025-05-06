"""
Grid-based Area module for Root Access game.
This module defines the GridArea class and Grid class for the grid-based template.
"""

class Grid:
    """Represents a 2D grid for positioning game objects."""
    
    def __init__(self, width, height):
        """Initialize a grid with the specified dimensions."""
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]  # Initialize with None
    
    def is_valid_coordinate(self, x, y):
        """Check if the given coordinates are within the grid boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_cell_occupied(self, x, y):
        """Check if the cell at the given coordinates is occupied."""
        if not self.is_valid_coordinate(x, y):
            return True  # Out of bounds is considered occupied
        return self.grid[y][x] is not None
    
    def place_object(self, obj, x, y):
        """Place an object on the grid at the specified coordinates."""
        if not self.is_valid_coordinate(x, y):
            return False  # Out of bounds
        if self.is_cell_occupied(x, y):
            return False  # Cell is occupied
        self.grid[y][x] = obj
        return True
    
    def remove_object(self, x, y):
        """Remove an object from the grid at the specified coordinates."""
        if not self.is_valid_coordinate(x, y):
            return False  # Out of bounds
        if self.is_cell_occupied(x, y):
            self.grid[y][x] = None
            return True
        return False
    
    def get_object(self, x, y):
        """Get the object at the specified coordinates."""
        if not self.is_valid_coordinate(x, y):
            return None
        return self.grid[y][x]
    
    def get_objects_in_radius(self, center_x, center_y, radius):
        """Get all objects within a certain radius of the given coordinates."""
        objects = []
        for y in range(max(0, center_y - radius), min(self.height, center_y + radius + 1)):
            for x in range(max(0, center_x - radius), min(self.width, center_x + radius + 1)):
                obj = self.grid[y][x]
                if obj is not None:
                    objects.append((obj, x, y))
        return objects


class GridArea:
    """Represents a location in the game with a grid-based layout."""
    
    def __init__(self, name, description, grid_width=10, grid_height=10):
        """Initialize a GridArea object."""
        self.name = name
        self.description = description
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.connections = {}  # Direction -> Area
        self.items = []  # Items lying on the ground in the area
        self.npcs = []  # NPCs present in the area
        self.objects = []  # Interactive objects
        self.grid = Grid(grid_width, grid_height)  # The grid for this area
    
    def add_connection(self, direction, area):
        """Add a connection to another area in the specified direction."""
        self.connections[direction] = area
    
    def add_item(self, item, x=None, y=None):
        """Add an item to the area at the specified coordinates."""
        self.items.append(item)
        if x is not None and y is not None:
            item.x = x
            item.y = y
            # If the item has coordinates, place it on the grid
            if hasattr(item, 'place_on_grid'):
                item.place_on_grid(self.grid, x, y)
    
    def remove_item(self, item_name):
        """Remove an item from the area by name."""
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            # If the item has coordinates, remove it from the grid
            if hasattr(item, 'x') and hasattr(item, 'y') and item.x is not None and item.y is not None:
                self.grid.remove_object(item.x, item.y)
            self.items.remove(item)
            return item
        return None
    
    def add_npc(self, npc, x=None, y=None):
        """Add an NPC to the area at the specified coordinates."""
        self.npcs.append(npc)
        npc.location = self
        if x is not None and y is not None:
            npc.x = x
            npc.y = y
            # If the NPC has coordinates, place it on the grid
            if hasattr(npc, 'place_on_grid'):
                npc.place_on_grid(self.grid, x, y)
    
    def remove_npc(self, npc):
        """Remove an NPC from the area."""
        if npc in self.npcs:
            # If the NPC has coordinates, remove it from the grid
            if hasattr(npc, 'x') and hasattr(npc, 'y') and npc.x is not None and npc.y is not None:
                self.grid.remove_object(npc.x, npc.y)
            self.npcs.remove(npc)
            npc.location = None
    
    def add_object(self, obj, x=None, y=None):
        """Add an object to the area at the specified coordinates."""
        self.objects.append(obj)
        if hasattr(obj, 'location'):
            obj.location = self
        
        if x is not None and y is not None:
            obj.x = x
            obj.y = y
            # If the object has coordinates, place it on the grid
            if hasattr(obj, 'place_on_grid'):
                obj.place_on_grid(self.grid, x, y)
    
    def get_objects_near_player(self, player, radius=2):
        """Get all objects within a certain radius of the player."""
        if not hasattr(player, 'x') or not hasattr(player, 'y'):
            return []
        return self.grid.get_objects_in_radius(player.x, player.y, radius)
    
    def get_full_description(self, player=None):
        """Get a full description of the area, including items, NPCs, and exits."""
        desc = self.description + "\n"
        
        # Add exits
        if self.connections:
            exits = ", ".join(self.connections.keys())
            desc += f"\nExits: {exits}\n"
        
        # Add nearby objects if player has coordinates
        if player and hasattr(player, 'x') and hasattr(player, 'y'):
            nearby_objects = self.get_objects_near_player(player)
            if nearby_objects:
                desc += "\nNearby:\n"
                for obj, x, y in nearby_objects:
                    if obj != player:  # Don't include the player in the list
                        distance = max(abs(player.x - x), abs(player.y - y))
                        direction = self._get_direction(player.x, player.y, x, y)
                        desc += f"- {obj.name} ({direction}, {distance} steps away)\n"
        
        # Add items
        if self.items:
            item_names = ", ".join(str(item) for item in self.items)
            desc += f"\nItems: {item_names}\n"
        
        # Add NPCs
        if self.npcs:
            npc_names = ", ".join(npc.name for npc in self.npcs)
            desc += f"\nNPCs: {npc_names}\n"
        
        # Add objects
        if self.objects:
            object_names = ", ".join(obj.name for obj in self.objects)
            desc += f"\nObjects: {object_names}\n"
        
        return desc
    
    def _get_direction(self, from_x, from_y, to_x, to_y):
        """Get the direction from one set of coordinates to another."""
        dx = to_x - from_x
        dy = to_y - from_y
        
        if dx == 0 and dy < 0:
            return "north"
        elif dx == 0 and dy > 0:
            return "south"
        elif dx > 0 and dy == 0:
            return "east"
        elif dx < 0 and dy == 0:
            return "west"
        elif dx > 0 and dy < 0:
            return "northeast"
        elif dx < 0 and dy < 0:
            return "northwest"
        elif dx > 0 and dy > 0:
            return "southeast"
        elif dx < 0 and dy > 0:
            return "southwest"
        else:
            return "here"
