import json
import os
import random
from items import Item, Weapon, Consumable, EffectItem, SmokeBomb, Decoy, Drone
from objects import VendingMachine, Computer, HidingSpot
from gardening import Seed, Plant, SoilPlot, WateringCan
from effects import Effect, PlantEffect, SupervisionEffect, HackedPlantEffect, Substance, HackedMilk, HallucinationEffect, ConfusionEffect
from npc_behavior import NPC, Civilian, Gang, GangMember, BehaviorType, BehaviorSettings, NPCBehaviorCoordinator, behavior_settings
from area import Area

class WorldLoader:
    def __init__(self, game):
        self.game = game
        self.templates = {
            "objects": {},
            "items": {},
            "npcs": {}
        }
        
    def load_world_data(self, file_path):
        """Load world data from a JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            # Load templates first
            if "templates" in data:
                self._load_templates(data["templates"])
                
            # Create areas
            if "areas" in data:
                self._create_areas(data["areas"])
                
            # Create connections between areas
            if "connections" in data:
                self._create_connections(data["connections"])
                
            # Create gangs
            if "gangs" in data:
                self._create_gangs(data["gangs"])
                
            # Add objects to areas
            if "objects" in data:
                self._add_objects_to_areas(data["objects"])
                
            # Add items to areas and player
            if "items" in data:
                self._add_items_to_areas_and_player(data["items"])
                
            # Add NPCs to areas
            if "npcs" in data:
                self._add_npcs_to_areas(data["npcs"])
                
            # Set player's starting location
            if "Home" in self.game.areas:
                self.game.player.current_area = self.game.areas["Home"]
                
            return True, "World loaded successfully."
        except Exception as e:
            return False, f"Error loading world data: {str(e)}"
    
    def _load_templates(self, templates_data):
        """Load templates from the templates section of the JSON data."""
        if "objects" in templates_data:
            self.templates["objects"] = templates_data["objects"]
        if "items" in templates_data:
            self.templates["items"] = templates_data["items"]
        if "npcs" in templates_data:
            self.templates["npcs"] = templates_data["npcs"]
    
    def _create_areas(self, areas_data):
        """Create areas from the areas section of the JSON data."""
        for area_id, area_data in areas_data.items():
            name = area_data.get("name", area_id)
            description = area_data.get("description", "")
            self.game.areas[area_id] = Area(name, description)
    
    def _create_connections(self, connections_data):
        """Create connections between areas from the connections section of the JSON data."""
        for connection in connections_data:
            source = connection.get("source")
            direction = connection.get("direction")
            destination = connection.get("destination")
            
            if source in self.game.areas and destination in self.game.areas:
                self.game.areas[source].add_connection(direction, self.game.areas[destination])
    
    def _create_gangs(self, gangs_data):
        """Create gangs from the gangs section of the JSON data."""
        for gang_name, gang_data in gangs_data.items():
            self.game.gangs[gang_name] = Gang(gang_name)
            # Store gang member names for later use when creating NPCs
            if "names" in gang_data:
                self.game.gangs[gang_name].member_names = gang_data["names"]
    
    def _add_objects_to_areas(self, objects_data):
        """Add objects to areas from the objects section of the JSON data."""
        for area_id, objects_list in objects_data.items():
            if area_id not in self.game.areas:
                continue
                
            for obj_data in objects_list:
                obj = self._create_object(obj_data)
                if obj:
                    self.game.areas[area_id].add_object(obj)
    
    def _add_items_to_areas_and_player(self, items_data):
        """Add items to areas and player from the items section of the JSON data."""
        for location_id, items_list in items_data.items():
            for item_data in items_list:
                item = self._create_item(item_data)
                if item:
                    if location_id == "player":
                        self.game.player.add_item(item)
                    elif location_id in self.game.areas:
                        self.game.areas[location_id].add_item(item)
    
    def _add_npcs_to_areas(self, npcs_data):
        """Add NPCs to areas from the npcs section of the JSON data."""
        for area_id, npcs_list in npcs_data.items():
            if area_id not in self.game.areas:
                continue
                
            for npc_data in npcs_list:
                npc = self._create_npc(npc_data)
                if npc:
                    self.game.areas[area_id].add_npc(npc)
                    
                    # Add items to NPC if specified
                    if "items" in npc_data:
                        for item_data in npc_data["items"]:
                            item = self._create_item(item_data)
                            if item:
                                npc.add_item(item)
    
    def _create_object(self, obj_data):
        """Create an object based on the provided data."""
        # Check if using a template
        if "template" in obj_data:
            template_path = obj_data["template"].split(":")
            if len(template_path) == 2 and template_path[0] == "objects" and template_path[1] in self.templates["objects"]:
                template = self.templates["objects"][template_path[1]]
                # Merge template with object data (object data overrides template)
                merged_data = {**template, **obj_data}
                # Remove template key
                merged_data.pop("template")
                return self._create_object(merged_data)
        
        obj_type = obj_data.get("type", "").lower()
        
        if obj_type == "vending_machine":
            name = obj_data.get("name", "Vending Machine")
            description = obj_data.get("description", "A vending machine filled with snacks and drinks.")
            vending_machine = VendingMachine(name)
            
            # Add items to vending machine
            if "items" in obj_data:
                for item_data in obj_data["items"]:
                    item = self._create_item(item_data)
                    if item:
                        vending_machine.add_item(item)
            
            return vending_machine
            
        elif obj_type == "computer":
            name = obj_data.get("name", "Computer Terminal")
            description = obj_data.get("description", "A computer terminal for various operations.")
            computer = Computer(name, description)
            
            # Add programs to computer
            if "programs" in obj_data:
                computer.programs = obj_data["programs"]
            
            return computer
            
        elif obj_type == "hiding_spot":
            name = obj_data.get("name", "Hiding Spot")
            description = obj_data.get("description", "A place to hide from NPCs.")
            effectiveness = obj_data.get("effectiveness", 0.5)
            return HidingSpot(name, description, effectiveness)
            
        elif obj_type == "soil_plot":
            return SoilPlot()
        
        return None
    
    def _create_item(self, item_data):
        """Create an item based on the provided data."""
        # Check if using a template
        if "template" in item_data:
            template_path = item_data["template"].split(":")
            if len(template_path) == 2 and template_path[0] == "items" and template_path[1] in self.templates["items"]:
                template = self.templates["items"][template_path[1]]
                # Merge template with item data (item data overrides template)
                merged_data = {**template, **item_data}
                # Remove template key
                merged_data.pop("template")
                return self._create_item(merged_data)
        
        item_type = item_data.get("type", "").lower()
        name = item_data.get("name", "Unknown Item")
        description = item_data.get("description", "")
        value = item_data.get("value", 0)
        
        if item_type == "weapon":
            damage = item_data.get("damage", 10)
            return Weapon(name, description, value, damage)
            
        elif item_type == "consumable":
            health_restore = item_data.get("health_restore", 10)
            return Consumable(name, description, value, health_restore)
            
        elif item_type == "effect_item":
            effect_type = item_data.get("effect_type", "").lower()
            effect = None
            
            if effect_type == "hallucination":
                effect = HallucinationEffect()
            elif effect_type == "confusion":
                effect = ConfusionEffect()
            
            if effect:
                return EffectItem(name, description, value, effect)
            
        elif item_type == "smoke_bomb":
            return SmokeBomb()
            
        elif item_type == "decoy":
            return Decoy()
            
        elif item_type == "seed":
            plant_type = item_data.get("plant_type", "generic")
            return Seed(name, description, plant_type, value)
            
        elif item_type == "watering_can":
            return WateringCan(name)
            
        elif item_type == "drone":
            return Drone()
            
        elif item_type == "regular":
            return Item(name, description, value)
        
        return None
    
    def _create_npc(self, npc_data):
        """Create an NPC based on the provided data."""
        # Check if using a template
        if "template" in npc_data:
            template_path = npc_data["template"].split(":")
            if len(template_path) == 2 and template_path[0] == "npcs" and template_path[1] in self.templates["npcs"]:
                template = self.templates["npcs"][template_path[1]]
                # Merge template with NPC data (NPC data overrides template)
                merged_data = {**template, **npc_data}
                # Remove template key
                merged_data.pop("template")
                return self._create_npc(merged_data)
        
        npc_type = npc_data.get("type", "").lower()
        name = npc_data.get("name", "Unknown NPC")
        description = npc_data.get("description", "")
        
        if npc_type == "gang_member":
            gang_name = npc_data.get("gang", "")
            if gang_name in self.game.gangs:
                gang = self.game.gangs[gang_name]
                return GangMember(name, description, gang)
            else:
                return None
                
        elif npc_type == "civilian":
            return Civilian(name, description)
        
        return None