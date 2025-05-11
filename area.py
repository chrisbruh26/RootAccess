class Area:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connections = {}  # Direction -> Area
        self.items = []
        self.npcs = []
        self.objects = []  # Interactive objects like soil plots, computers, etc.
        self.hazards = []  # Environmental hazards
    
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
    
    def get_full_description(self):
        """Get a full description of the area, including items, NPCs, and exits."""
        desc = self.description + "\n"
        
        # Add exits
        if self.connections:
            exits = ", ".join(self.connections.keys())
            desc += f"\nExits: {exits}\n"
        
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
