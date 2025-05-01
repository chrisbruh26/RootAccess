from color_system import colorize, semantic, style

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
        # Area name and description with color
        desc = semantic(style(self.name, "bold"), "area_name") + "\n"
        desc += self.description + "\n"
        
        # Add exits with color
        if self.connections:
            exits_list = []
            for direction in self.connections.keys():
                exits_list.append(semantic(direction, "direction"))
            exits = ", ".join(exits_list)
            desc += f"\n{style('Exits:', 'bold')} {exits}\n"
        
        # Add items with color based on item type
        if self.items:
            item_names = []
            for item in self.items:
                # Determine item category for coloring
                category = "object"  # Default category
                if hasattr(item, '__class__'):
                    class_name = item.__class__.__name__.lower()
                    if "weapon" in class_name:
                        category = "weapon"
                    elif "consumable" in class_name:
                        category = "consumable"
                    elif "effect" in class_name:
                        category = "effect"
                    elif "tech" in class_name or "usb" in class_name:
                        category = "tech"
                    elif "seed" in class_name or "plant" in class_name:
                        category = "plant"
                
                item_names.append(semantic(str(item), category))
            
            items_str = ", ".join(item_names)
            desc += f"\n{style('Items:', 'bold')} {items_str}\n"
        
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
                        gang_members[gang_name].append(semantic(npc.name, "gang_member"))
                    else:
                        # This is a civilian
                        civilians.append(semantic(npc.name, "civilian"))
            
            # Add civilians with color
            if civilians:
                civilian_names = ", ".join(civilians)
                desc += f"\n{style('Civilians:', 'bold')} {civilian_names}\n"
            
            # Add gang members by gang with color
            for gang_name, members in gang_members.items():
                member_names = ", ".join(members)
                desc += f"\n{style(gang_name + ' Members:', 'bold')} {member_names}\n"
        
        # Add objects, separating hiding spots for clarity
        if self.objects:
            # Regular objects with color
            regular_objects = [obj for obj in self.objects if not hasattr(obj, 'is_occupied')]
            if regular_objects:
                object_names = ", ".join(semantic(str(obj), "object") for obj in regular_objects)
                desc += f"\n{style('Objects:', 'bold')} {object_names}\n"
            
            # Hiding spots with color
            hiding_spots = [obj for obj in self.objects if hasattr(obj, 'is_occupied')]
            if hiding_spots:
                hiding_spot_names = ", ".join(semantic(str(obj), "hiding") for obj in hiding_spots)
                desc += f"\n{style('Hiding Spots:', 'bold')} {hiding_spot_names}\n"
        
        return desc
