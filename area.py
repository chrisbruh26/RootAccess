"""
Grid-based Area module for Root Access game.
This module defines the GridArea class which extends the basic Area with grid functionality.
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


class Region:
    """Represents a special region within a grid area."""
    
    def __init__(self, name, description, coordinates, area):
        """Initialize a Region object."""
        self.name = name
        self.description = description
        self.coordinates = coordinates  # List of (x, y) tuples
        self.area = area
        self.structures = []  # List of structures within this region
    
    def is_inside(self, x, y):
        """Check if the given coordinates are within the region."""
        for region_x, region_y in self.coordinates:
            if abs(x - region_x) <= 2 and abs(y - region_y) <= 2:
                return True
        return False
    
    def add_structure(self, structure):
        """Add a structure to this region."""
        self.structures.append(structure)
    
    def get_random_location(self):
        """Get a random valid location within the region."""
        import random
        while True:
            x = random.choice([coord[0] for coord in self.coordinates])
            y = random.choice([coord[1] for coord in self.coordinates])
            if not self.area.grid.is_cell_occupied(x, y):
                return x, y


class GridArea:
    """Represents a location in the game with a grid-based layout."""
    
    def __init__(self, name, description, grid_width=20, grid_height=20):
        """Initialize a GridArea object."""
        self.name = name
        self.description = description
        self.connections = {}  # Direction -> Area
        self.items = []  # Items lying on the ground in the area
        self.npcs = []  # NPCs present in the area
        self.objects = []  # Interactive objects like soil plots, computers, etc.
        self.hazards = []  # Environmental hazards
        self.storage_containers = []  # Storage containers in the area
        self.hackable_objects = []  # Objects that can be hacked
        self.locked_rooms = []  # Locked rooms in the area
        self.gang_members = []  # Gang members in the area
        self.garden_plot = []  # Garden plots in the area
        self.garden_area = False  # Whether this area has a garden
        self.environment_objects = []  # Environment objects like dumpsters, benches, etc.
        self.grid = Grid(grid_width, grid_height)  # The grid for this area
        self.regions = []  # Regions within this area
    
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
    
    def add_hazard(self, hazard, x=None, y=None):
        """Add a hazard to the area at the specified coordinates."""
        self.hazards.append(hazard)
        hazard.location = self
        if x is not None and y is not None:
            hazard.x = x
            hazard.y = y
            # If the hazard has coordinates, place it on the grid
            if hasattr(hazard, 'place_on_grid'):
                hazard.place_on_grid(self.grid, x, y)
    
    def remove_hazard(self, hazard):
        """Remove a hazard from the area."""
        if hazard in self.hazards:
            # If the hazard has coordinates, remove it from the grid
            if hasattr(hazard, 'x') and hasattr(hazard, 'y') and hazard.x is not None and hazard.y is not None:
                self.grid.remove_object(hazard.x, hazard.y)
            self.hazards.remove(hazard)
            hazard.location = None
    
    def add_region(self, region):
        """Add a region to the area."""
        self.regions.append(region)
    
    def add_storage(self, storage, x=None, y=None):
        """Add a storage container to the area at the specified coordinates."""
        self.storage_containers.append(storage)
        if hasattr(storage, 'location'):
            storage.location = self
        if x is not None and y is not None:
            storage.x = x
            storage.y = y
            # If the storage has coordinates, place it on the grid
            if hasattr(storage, 'place_on_grid'):
                storage.place_on_grid(self.grid, x, y)
    
    def add_hackable(self, hackable, x=None, y=None):
        """Add a hackable object to the area at the specified coordinates."""
        self.hackable_objects.append(hackable)
        if hasattr(hackable, 'location'):
            hackable.location = self
        if x is not None and y is not None:
            hackable.x = x
            hackable.y = y
            # If the hackable object has coordinates, place it on the grid
            if hasattr(hackable, 'place_on_grid'):
                hackable.place_on_grid(self.grid, x, y)
    
    def add_environment_object(self, obj):
        """Add an environment object to the area."""
        self.environment_objects.append(obj)
        if hasattr(obj, 'location'):
            obj.location = self
        # If the object has a place_on_grid method, call it
        if hasattr(obj, 'place_on_grid') and hasattr(obj, 'x') and hasattr(obj, 'y'):
            obj.place_on_grid(self.grid, obj.x, obj.y)
    
    def add_gangmember(self, gangmember, x=None, y=None):
        """Add a gang member to the area at the specified coordinates."""
        self.gang_members.append(gangmember)
        if hasattr(gangmember, 'location'):
            gangmember.location = self
        if x is not None and y is not None:
            gangmember.x = x
            gangmember.y = y
            # If the gang member has coordinates, place it on the grid
            if hasattr(gangmember, 'place_on_grid'):
                gangmember.place_on_grid(self.grid, x, y)
    
    def remove_gangmember(self, gangmember):
        """Remove a gang member from the area."""
        if gangmember in self.gang_members:
            # If the gang member has coordinates, remove it from the grid
            if hasattr(gangmember, 'x') and hasattr(gangmember, 'y') and gangmember.x is not None and gangmember.y is not None:
                self.grid.remove_object(gangmember.x, gangmember.y)
            self.gang_members.remove(gangmember)
    
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
                    distance = max(abs(player.x - x), abs(player.y - y))
                    direction = self._get_direction(player.x, player.y, x, y)
                    desc += f"- {obj.name} ({direction}, {distance} steps away)\n"
        
        # Add items
        if self.items:
            item_names = ", ".join(str(item) for item in self.items)
            desc += f"\nItems: {item_names}\n"
        
        # Add NPCs, categorized by type
        if self.npcs:
            # Group NPCs by type
            civilians = []
            gang_members = {}  # Gang name -> list of members
            
            for npc in self.npcs:
                if not hasattr(npc, 'is_alive') or npc.is_alive:
                    if hasattr(npc, 'gang'):
                        # This is a gang member
                        gang_name = npc.gang.name
                        if gang_name not in gang_members:
                            gang_members[gang_name] = []
                        gang_members[gang_name].append(npc.name)
                    else:
                        # This is a civilian
                        civilians.append(npc.name)
            
            # Add civilians
            if civilians:
                civilian_names = ", ".join(civilians)
                desc += f"\nCivilians: {civilian_names}\n"
            
            # Add gang members by gang
            for gang_name, members in gang_members.items():
                member_names = ", ".join(members)
                desc += f"\n{gang_name} Members: {member_names}\n"
        
        # Add objects, separating hiding spots for clarity
        if self.objects:
            # Regular objects
            regular_objects = [obj for obj in self.objects if not hasattr(obj, 'is_occupied')]
            if regular_objects:
                object_names = ", ".join(str(obj) for obj in regular_objects)
                desc += f"\nObjects: {object_names}\n"
            
            # Hiding spots
            hiding_spots = [obj for obj in self.objects if hasattr(obj, 'is_occupied')]
            if hiding_spots:
                hiding_spot_names = ", ".join(str(obj) for obj in hiding_spots)
                desc += f"\nHiding Spots: {hiding_spot_names}\n"
        
        return desc
    
    def _get_direction(self, from_x, from_y, to_x, to_y):
        """Get the direction from one point to another."""
        dx = to_x - from_x
        dy = to_y - from_y
        
        if abs(dx) > abs(dy):
            # Horizontal direction is more significant
            if dx > 0:
                return "east"
            else:
                return "west"
        else:
            # Vertical direction is more significant
            if dy > 0:
                return "north"
            else:
                return "south"
    
    def handle_gang_activity(self, gangmembers):
        """Handle gang fights within the area."""
        # Check if the area is a gang territory
        if self.name not in ["Crimson Vipers' territory", "Bloodhounds territory"]:
            return  # Not a gang territory, do nothing
        
        # Check if the territory's gang members are present
        territory_gang = None
        if self.name == "Crimson Vipers' territory":
            territory_gang = "Crimson Vipers"
        elif self.name == "Bloodhounds territory":
            territory_gang = "Bloodhounds"
        
        territory_members_present = any(
            member.gang == territory_gang for member in self.gang_members
        )
        
        if not territory_members_present:
            # Spawn territory gang members
            self.spawn_gang_members(gangmembers, territory_gang)
        
        # Check for rival gang members
        rival_gang_present = any(
            member.gang != territory_gang for member in self.gang_members
        )
        
        if not rival_gang_present and territory_members_present:
            # Spawn rival gang members
            self.spawn_rival_gang_members(gangmembers, territory_gang)
        
        # Now that we've potentially spawned gang members, proceed with the fight logic
        if len(self.gang_members) < 2:
            return  # Need at least two gang members for a fight
        
        # Check for rival gangs
        gangs_present = set(
            member.gang for member in self.gang_members if member.status == "alive"
        )
        if len(gangs_present) < 2:
            return  # Only one gang present, no fight
        
        # Print the gang conflict message only once per fight
        if not hasattr(self, 'gang_fight_announced'):
            self.gang_fight_announced = True
            
            # Get the names of the gangs involved
            gang_names = list(gangs_present)
            print(f"The {gang_names[0]} are in conflict with the {gang_names[1]}!\n")
        
        # Reset the flag before starting a new round of gang activity
        if hasattr(self, "gang_fight_announced"):
            del self.gang_fight_announced
        
        # Gang members fight each other
        # Create a copy of the list to avoid issues with removing elements during iteration
        gang_members_copy = self.gang_members[:]
        for member in gang_members_copy:
            if member.status == "alive":
                member.gangfight()
    
    def spawn_gang_members(self, gangmembers, territory_gang):
        """Spawn gang members of the territory's gang."""
        print(f"Spawning {territory_gang} members in {self.name}...")
        if territory_gang == "Crimson Vipers":
            self.add_gangmember(gangmembers["Razor"])
            self.add_gangmember(gangmembers["Hex"])
        elif territory_gang == "Bloodhounds":
            self.add_gangmember(gangmembers["Bones"])
            self.add_gangmember(gangmembers["Fang"])
    
    def spawn_rival_gang_members(self, gangmembers, territory_gang):
        """Spawn rival gang members in the territory."""
        print(f"Spawning rival gang members in {self.name}...")
        if territory_gang == "Crimson Vipers":
            self.add_gangmember(gangmembers["Bones"])
        elif territory_gang == "Bloodhounds":
            self.add_gangmember(gangmembers["Razor"])
