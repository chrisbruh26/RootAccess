class SubArea:
    """
    A class representing a sub-area within a main area.
    Sub-areas contain their own items, NPCs, and objects, but are part of a parent area.
    """
    def __init__(self, name, description, parent_area=None):
        self.name = name
        self.description = description
        self.parent_area = parent_area
        self.items = []
        self.npcs = []
        self.objects = []  # Interactive objects like soil plots, computers, etc.
        self.hazards = []  # Environmental hazards
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
            return item
        return None
    
    def add_npc(self, npc):
        self.npcs.append(npc)
        npc.location = self.parent_area
        npc.sub_location = self
    
    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)
            npc.sub_location = None
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def add_hazard(self, hazard):
        self.hazards.append(hazard)
        hazard.location = self.parent_area
        hazard.sub_location = self
    
    def remove_hazard(self, hazard):
        if hazard in self.hazards:
            self.hazards.remove(hazard)
            hazard.sub_location = None
    
    def get_full_description(self):
        """Get a full description of the sub-area, including items, NPCs, and objects."""
        desc = f"{self.name}: {self.description}\n"
        
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


class Area:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connections = {}  # Direction -> Area
        self.items = []
        self.npcs = []
        self.objects = []  # Interactive objects like soil plots, computers, etc.
        self.hazards = []  # Environmental hazards
        self.sub_areas = {}  # Name -> SubArea
    
    def add_connection(self, direction, area):
        self.connections[direction] = area
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
            return item
        return None
    
    def add_npc(self, npc):
        self.npcs.append(npc)
        npc.location = self
        npc.sub_location = None  # Reset sub-location when adding to main area
    
    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)
            npc.location = None
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def add_hazard(self, hazard):
        self.hazards.append(hazard)
        hazard.location = self
    
    def remove_hazard(self, hazard):
        if hazard in self.hazards:
            self.hazards.remove(hazard)
            hazard.location = None
    
    def add_sub_area(self, name, description):
        """Add a sub-area to this area."""
        sub_area = SubArea(name, description, self)
        self.sub_areas[name.lower()] = sub_area
        return sub_area
    
    def get_sub_area(self, name):
        """Get a sub-area by name."""
        return self.sub_areas.get(name.lower())
    
    def move_npc_to_sub_area(self, npc, sub_area_name):
        """Move an NPC from the main area to a sub-area."""
        if npc in self.npcs and sub_area_name.lower() in self.sub_areas:
            sub_area = self.sub_areas[sub_area_name.lower()]
            self.npcs.remove(npc)
            sub_area.add_npc(npc)
            return True
        return False
    
    def move_npc_from_sub_area(self, npc, sub_area_name):
        """Move an NPC from a sub-area to the main area."""
        if sub_area_name.lower() in self.sub_areas:
            sub_area = self.sub_areas[sub_area_name.lower()]
            if npc in sub_area.npcs:
                sub_area.remove_npc(npc)
                self.add_npc(npc)
                return True
        return False
    
    def get_visible_npcs(self, player_sub_area=None):
        """
        Get all NPCs visible to the player based on their location.
        If player is in a sub-area, only NPCs in that sub-area are visible.
        If player is in the main area, only NPCs in the main area are visible.
        """
        if player_sub_area:
            # Player is in a sub-area, only show NPCs in that sub-area
            if player_sub_area.lower() in self.sub_areas:
                return self.sub_areas[player_sub_area.lower()].npcs
            return []
        else:
            # Player is in the main area, only show NPCs in the main area
            return self.npcs
    
    def get_full_description(self, player_sub_area=None):
        """
        Get a full description of the area, including items, NPCs, and exits.
        If player_sub_area is provided, show the description of that sub-area instead.
        """
        if player_sub_area and player_sub_area.lower() in self.sub_areas:
            # Player is in a sub-area, show that sub-area's description
            sub_area = self.sub_areas[player_sub_area.lower()]
            desc = f"You are in {self.name} - {sub_area.name}\n"
            desc += sub_area.get_full_description()
            desc += "\nType 'exit' to return to the main area.\n"
            return desc
        
        # Player is in the main area
        desc = self.description + "\n"
        
        # Add exits
        if self.connections:
            exits = ", ".join(self.connections.keys())
            desc += f"\nExits: {exits}\n"
        
        # Add sub-areas if any
        if self.sub_areas:
            sub_area_names = ", ".join(sub_area.name for sub_area in self.sub_areas.values())
            desc += f"\nSub-areas: {sub_area_names}\n"
        
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
