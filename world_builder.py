import random
import json
import os
from area import Area
from items import Item, Weapon, Consumable, EffectItem, SmokeBomb, Decoy, Drone
from objects import VendingMachine, Computer, HidingSpot
from gardening import Seed, Plant, SoilPlot, WateringCan
from effects import Effect, PlantEffect, SupervisionEffect, HackedPlantEffect, Substance, HackedMilk, HallucinationEffect, ConfusionEffect
from npc_behavior import NPC, Civilian, Gang, GangMember, BehaviorType, BehaviorSettings

class WorldBuilder:
    """
    A class responsible for building the game world.
    This separates world creation logic from the main game class.
    """
    
    def __init__(self, game):
        """Initialize with a reference to the game instance."""
        self.game = game
        self.world_data = {}
        
        # Try to load world data from JSON file
        try:
            data_path = os.path.join(os.path.dirname(__file__), 'data', 'world_data.json')
            if os.path.exists(data_path):
                with open(data_path, 'r') as f:
                    self.world_data = json.load(f)
                print(f"Loaded world data from {data_path}")
            else:
                print(f"World data file not found at {data_path}, using default data")
        except Exception as e:
            print(f"Error loading world data: {e}, using default data")
    
    def _load_world_data(self):
        """
        Legacy method for backward compatibility.
        This method is no longer used as we now load all world data from a single JSON file.
        """
        # This method is kept for backward compatibility but doesn't do anything
        pass
    
    def build_world(self):
        """Main method to build the entire world."""
        self.create_areas()
        self.connect_areas()
        self.create_sub_areas()
        self.create_gangs()
        self.add_objects_to_areas()
        self.add_items_to_areas()
        self.add_npcs_to_areas()
        self.setup_player()
        
    def create_sub_areas(self):
        """Create sub-areas for certain areas using a data-driven approach."""
        # Use sub-area data from JSON or create default data if not available
        sub_areas_data = self.world_data.get('sub_areas', self._get_default_sub_areas_data())
        
        # Create sub-areas from the data
        self._create_sub_areas_from_data(sub_areas_data)
        print(f"Created sub-areas for areas")
    
    def _create_sub_areas_from_data(self, sub_areas_data):
        """Create sub-areas from data (either JSON or hardcoded)."""
        for area_id, area_sub_areas in sub_areas_data.items():
            if area_id not in self.game.areas:
                print(f"Warning: Area '{area_id}' not found, skipping sub-areas")
                continue
                
            area = self.game.areas[area_id]
            
            for sub_area_data in area_sub_areas:
                name = sub_area_data.get('name')
                description = sub_area_data.get('description')
                
                if not name or not description:
                    print(f"Warning: Sub-area missing name or description in area '{area_id}', skipping")
                    continue
                
                # Create the sub-area
                sub_area = area.add_sub_area(name, description)
                
                # Add items to the sub-area if specified
                if 'items' in sub_area_data:
                    for item_data in sub_area_data['items']:
                        item_type = item_data.get('type', 'regular')
                        item_name = item_data.get('name', 'Item')
                        item_description = item_data.get('description', 'An item.')
                        item_value = item_data.get('value', 10)
                        
                        if item_type == 'consumable':
                            health_restore = item_data.get('health_restore', 10)
                            item = Consumable(item_name, item_description, item_value, health_restore)
                        else:
                            item = Item(item_name, item_description, item_value)
                            
                        sub_area.add_item(item)
                
                # Add NPCs to the sub-area if specified
                if 'npcs' in sub_area_data:
                    for npc_data in sub_area_data['npcs']:
                        npc_type = npc_data.get('type', 'civilian')
                        npc_name = npc_data.get('name', 'NPC')
                        npc_description = npc_data.get('description', 'A person.')
                        
                        if npc_type == 'civilian':
                            npc = Civilian(npc_name, npc_description)
                        elif npc_type == 'gang_member' and 'gang' in npc_data:
                            gang_name = npc_data['gang']
                            if gang_name in self.game.gangs:
                                npc = GangMember(npc_name, npc_description, self.game.gangs[gang_name])
                            else:
                                print(f"Warning: Gang '{gang_name}' not found, creating civilian instead")
                                npc = Civilian(npc_name, npc_description)
                        else:
                            npc = Civilian(npc_name, npc_description)
                            
                        sub_area.add_npc(npc)
    
    def _get_default_sub_areas_data(self):
        """Return default sub-area data for the game world.
        
        This is used when no JSON data is available. In a production environment,
        you would typically create these default JSON files during installation
        rather than hardcoding them here.
        """
        # Define minimal default sub-areas
        return {
            "mall": [
                {
                    "name": "Tech Store",
                    "description": "A store selling the latest gadgets and technology.",
                    "items": [
                        {"name": "Smartphone", "description": "A high-tech smartphone.", "value": 200}
                    ],
                    "npcs": [
                        {"name": "Tech Clerk", "description": "A knowledgeable clerk working at the tech store."}
                    ]
                },
                {
                    "name": "Food Court",
                    "description": "A bustling food court with various food stalls.",
                    "items": [
                        {"type": "consumable", "name": "Pizza", "description": "A slice of pizza.", "value": 5, "health_restore": 15}
                    ]
                }
            ]
        }
    
    def create_areas(self):
        """Create all game areas."""
        # Use area data from JSON or create default data if not available
        areas_data = self.world_data.get('areas', self._get_default_areas_data())
        
        # Create areas from the data
        for area_id, area_data in areas_data.items():
            self.game.areas[area_id] = Area(area_data['name'], area_data['description'])
        
        print(f"Created {len(self.game.areas)} areas")
    
    def _get_default_areas_data(self):
        """Return default area data for the game world."""
        return {
            "Home": {
                "name": "Home",
                "description": "Your secret base of operations. It's small but functional."
            },
            "garden": {
                "name": "Garden",
                "description": "A small garden area with fertile soil."
            },
            "street": {
                "name": "Street",
                "description": "A busy street with various shops and people."
            },
            "alley": {
                "name": "Alley",
                "description": "A dark alley between buildings."
            },
            "plaza": {
                "name": "Plaza",
                "description": "A large open plaza with a fountain in the center."
            },
            "warehouse": {
                "name": "Warehouse",
                "description": "An abandoned warehouse, taken over by the Bloodhounds."
            },
            "construction": {
                "name": "Construction Site",
                "description": "A construction site with various equipment and materials."
            },
            "mall": {
                "name": "Mall",
                "description": "A large shopping mall with multiple stores and a food court."
            }
        }
    
    def connect_areas(self):
        """Connect areas to create the world map."""
        # Use connection data from JSON or create default data if not available
        connections_data = self.world_data.get('connections', self._get_default_connections_data())
        
        # Create connections from the data
        connection_count = 0
        for connection in connections_data:
            source = connection['source']
            direction = connection['direction']
            destination = connection['destination']
            
            if source in self.game.areas and destination in self.game.areas:
                self.game.areas[source].add_connection(direction, self.game.areas[destination])
                connection_count += 1
        
        print(f"Created {connection_count} connections between areas")
        
    def _get_default_connections_data(self):
        """Return default connection data for the game world."""
        return [
            {"source": "Home", "direction": "north", "destination": "garden"},
            {"source": "garden", "direction": "south", "destination": "Home"},
            {"source": "garden", "direction": "east", "destination": "street"},
            {"source": "street", "direction": "west", "destination": "garden"},
            {"source": "street", "direction": "north", "destination": "plaza"},
            {"source": "plaza", "direction": "south", "destination": "street"},
            {"source": "street", "direction": "east", "destination": "alley"},
            {"source": "alley", "direction": "west", "destination": "street"},
            {"source": "street", "direction": "south", "destination": "warehouse"},
            {"source": "warehouse", "direction": "north", "destination": "street"},
            {"source": "plaza", "direction": "east", "destination": "construction"},
            {"source": "construction", "direction": "west", "destination": "plaza"},
            {"source": "plaza", "direction": "north", "destination": "mall"},
            {"source": "mall", "direction": "south", "destination": "plaza"}
        ]
    
    def create_gangs(self):
        """Create gangs in the game world."""
        # Use gang data from JSON or create default data if not available
        gangs_data = self.world_data.get('gangs', self._get_default_gangs_data())
        
        # Create gangs from the data
        for gang_name, gang_data in gangs_data.items():
            self.game.gangs[gang_name] = Gang(gang_name)
            self.game.gangs[gang_name].member_names = gang_data.get("names", [])
        
        print(f"Created {len(self.game.gangs)} gangs")
        
    def _get_default_gangs_data(self):
        """Return default gang data for the game world."""
        return {
            "Crimson Vipers": {
                "names": ["Vipoop", "Snakle", "Rattlesnop", "Pythirt", "Anaceaky", 
                          "Cobrus-brus", "Lizuddles", "Viperino", "Slitherpuff", 
                          "Hissypants", "Slinker", "Snakester"]
            },
            "Bloodhounds": {
                "names": ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", 
                          "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]
            }
        }
    
    def add_objects_to_areas(self):
        """Add objects to areas using a data-driven approach."""
        # Use object data from JSON or create default data if not available
        objects_data = self.world_data.get('objects', self._get_default_objects_data())
        
        # Create objects from the data
        self._create_objects_from_data(objects_data)
        print(f"Created objects for areas")
    
    def _create_objects_from_data(self, objects_data):
        """Create objects from data (either JSON or hardcoded)."""
        for area_id, area_objects in objects_data.items():
            if area_id not in self.game.areas:
                print(f"Warning: Area '{area_id}' not found, skipping objects")
                continue
                
            area = self.game.areas[area_id]
            
            for obj_data in area_objects:
                # Check if this is a template reference
                if 'template' in obj_data:
                    template_name = obj_data.get('template')
                    game_object = self._create_object_from_template(template_name, obj_data)
                    if not game_object:
                        print(f"Warning: Failed to create object from template '{template_name}' in area '{area_id}', skipping")
                        continue
                else:
                    # Regular object creation by type
                    obj_type = obj_data.get('type')
                    if not obj_type:
                        print(f"Warning: Object missing type in area '{area_id}', skipping")
                        continue
                    
                    # Create the object based on its type
                    game_object = self._create_object_by_type(obj_type, obj_data)
                    if not game_object:
                        continue
                
                # Add to main area or sub-area
                if 'sub_area' in obj_data and obj_data['sub_area']:
                    sub_area = area.get_sub_area(obj_data['sub_area'])
                    if sub_area:
                        sub_area.add_object(game_object)
                    else:
                        print(f"Warning: Sub-area '{obj_data['sub_area']}' not found in '{area_id}', adding to main area")
                        area.add_object(game_object)
                else:
                    area.add_object(game_object)
    
    def _create_object_from_template(self, template_name, obj_data):
        """Create an object from a template defined in world_data.json."""
        # Get templates from world data
        templates = self.world_data.get('templates', {})
        object_templates = templates.get('objects', {})
        
        # Find the template
        if template_name not in object_templates:
            print(f"Warning: Template '{template_name}' not found in templates")
            return None
            
        # Get the template data
        template_data = object_templates[template_name]
        
        # Create a copy of the template data and update it with any overrides from obj_data
        merged_data = template_data.copy()
        
        # Override name if provided
        if 'name' in obj_data:
            merged_data['name'] = obj_data['name']
            
        # Create the object based on the template type
        obj_type = merged_data.get('type')
        if not obj_type:
            print(f"Warning: Template '{template_name}' missing type")
            return None
            
        # Create the object using the merged data
        return self._create_object_by_type(obj_type, merged_data)
    
    def _create_object_by_type(self, obj_type, obj_data):
        """Factory method to create objects of different types."""
        if obj_type == 'soil_plot':
            return SoilPlot()
            
        elif obj_type == 'computer':
            name = obj_data.get('name', 'Computer')
            description = obj_data.get('description', 'A computer terminal.')
            computer = Computer(name, description)
            
            # Add programs if specified
            if 'programs' in obj_data:
                computer.programs = obj_data['programs']
                
            return computer
            
        elif obj_type == 'hiding_spot':
            name = obj_data.get('name', 'Hiding Spot')
            description = obj_data.get('description', 'A place to hide.')
            effectiveness = obj_data.get('effectiveness', 0.5)
            return HidingSpot(name, description, effectiveness)
            
        elif obj_type == 'vending_machine':
            name = obj_data.get('name', 'Vending Machine')
            vending_machine = VendingMachine(name)
            
            # Add items if specified
            if 'items' in obj_data:
                for item_data in obj_data['items']:
                    item_name = item_data.get('name', 'Item')
                    item_description = item_data.get('description', 'A vending machine item.')
                    item_price = item_data.get('price', 5)
                    item_health = item_data.get('health', 10)
                    
                    item = Consumable(item_name, item_description, item_price, item_health)
                    vending_machine.add_item(item)
                    
            return vending_machine
            
        # Add more object types as needed
        # elif obj_type == 'new_object_type':
        #     return NewObjectType(...)
            
        else:
            print(f"Warning: Unknown object type '{obj_type}', skipping")
            return None
    
    def _get_default_objects_data(self):
        """Return default object data for the game world.
        
        This is used when no JSON data is available. In a production environment,
        you would typically create these default JSON files during installation
        rather than hardcoding them here.
        """
        # Define minimal default objects for each area
        return {
            "garden": [
                {"type": "soil_plot"}
            ],
            "warehouse": [
                {"type": "soil_plot"},
                {
                    "type": "vending_machine",
                    "name": "Vending Machine",
                    "items": [
                        {"name": "Soda", "description": "A refreshing soda.", "price": 5, "health": 10},
                        {"name": "Chips", "description": "A bag of chips.", "price": 5, "health": 5}
                    ]
                }
            ],
            "Home": [
                {
                    "type": "computer",
                    "name": "Hacking Terminal",
                    "description": "A specialized terminal for hacking operations.",
                    "programs": ["data_miner", "security_override", "plant_hacker"]
                }
            ]
        }
    
    def add_items_to_areas(self):
        """Add items to areas using a data-driven approach."""
        # Use item data from JSON or create default data if not available
        items_data = self.world_data.get('items', self._get_default_items_data())
        
        # Create items from the data
        item_count = 0
        
        # Process player items separately
        player_items = items_data.pop('player', [])  # Remove and get player items
        
        # Process area items
        for area_id, area_items in items_data.items():
            if area_id not in self.game.areas:
                print(f"Warning: Area '{area_id}' not found, skipping items")
                continue
                
            area = self.game.areas[area_id]
            
            for item_data in area_items:
                item = self._create_item_from_data(item_data)
                if item:
                    area.add_item(item)
                    item_count += 1
        
        # Add items to player
        for item_data in player_items:
            item = self._create_item_from_data(item_data)
            if item:
                self.game.player.add_item(item)
                item_count += 1
        
        print(f"Added {item_count} items to areas and player")
    
    def _create_item_from_data(self, item_data):
        """Create an item from data."""
        item_type = item_data.get('type', 'regular')
        name = item_data.get('name', 'Item')
        description = item_data.get('description', 'An item.')
        value = item_data.get('value', 10)
        
        if item_type == 'regular':
            return Item(name, description, value)
            
        elif item_type == 'consumable':
            health_restore = item_data.get('health_restore', 10)
            return Consumable(name, description, value, health_restore)
            
        elif item_type == 'weapon':
            damage = item_data.get('damage', 10)
            return Weapon(name, description, value, damage)
            
        elif item_type == 'seed':
            plant_type = item_data.get('plant_type', 'generic')
            return Seed(name, description, plant_type, value)
            
        elif item_type == 'watering_can':
            return WateringCan(name)
            
        elif item_type == 'effect_item':
            effect_type = item_data.get('effect_type', 'hallucination')
            if effect_type == 'hallucination':
                effect = HallucinationEffect()
            elif effect_type == 'confusion':
                effect = ConfusionEffect()
            else:
                effect = Effect()
            return EffectItem(name, description, value, effect)
            
        elif item_type == 'smoke_bomb':
            return SmokeBomb()
            
        elif item_type == 'decoy':
            return Decoy()
            
        elif item_type == 'drone':
            return Drone()
            
        else:
            print(f"Warning: Unknown item type '{item_type}', creating regular item")
            return Item(name, description, value)
    
    def _get_default_items_data(self):
        """Return default item data for the game world."""
        return {
            "Home": [
                {"type": "regular", "name": "Backpack", "description": "A sturdy backpack for carrying items.", "value": 20},
                {"type": "effect_item", "name": "Hacked Milk Blaster", "description": "A strange device that sprays hacked milk.", "value": 50, "effect_type": "hallucination"},
                {"type": "seed", "name": "Carrot Seed", "description": "A seed for growing carrot.", "value": 5, "plant_type": "carrot"},
                {"type": "watering_can", "name": "Watering Can"},
                {"type": "drone", "name": "Drone"}
            ],
            "street": [
                {"type": "consumable", "name": "Energy Drink", "description": "A caffeinated beverage that restores health.", "value": 10, "health_restore": 20},
                {"type": "smoke_bomb", "name": "Smoke Bomb"}
            ],
            "alley": [
                {"type": "weapon", "name": "Pipe", "description": "A metal pipe that can be used as a weapon.", "value": 15, "damage": 10},
                {"type": "effect_item", "name": "Confusion Ray", "description": "A device that emits waves that confuse the target.", "value": 60, "effect_type": "confusion"},
                {"type": "smoke_bomb", "name": "Smoke Bomb"}
            ],
            "garden": [
                {"type": "seed", "name": "Tomato Seed", "description": "A seed for growing tomatoes.", "value": 5, "plant_type": "tomato"},
                {"type": "seed", "name": "Potato Seed", "description": "A seed for growing potatoes.", "value": 5, "plant_type": "potato"},
                {"type": "decoy", "name": "Decoy"}
            ],
            "warehouse": [
                {"type": "effect_item", "name": "Hacked Milk Blaster", "description": "A strange device that sprays hacked milk.", "value": 50, "effect_type": "hallucination"},
                {"type": "seed", "name": "Carrot Seed", "description": "A seed for growing carrot.", "value": 5, "plant_type": "carrot"},
                {"type": "decoy", "name": "Decoy"}
            ],
            "player": [
                {"type": "weapon", "name": "Machine Gun", "description": "A machine gun.", "value": 100, "damage": 50},
                {"type": "watering_can", "name": "Watering Can"},
                {"type": "smoke_bomb", "name": "Smoke Bomb"},
                {"type": "decoy", "name": "Decoy"}
            ]
        }
    
    def add_npcs_to_areas(self):
        """Add NPCs to areas using a data-driven approach."""
        # Use NPC data from JSON or create default data if not available
        npcs_data = self.world_data.get('npcs', self._get_default_npcs_data())
        
        # Create NPCs from the data
        npc_count = 0
        for area_id, area_npcs in npcs_data.items():
            if area_id not in self.game.areas:
                print(f"Warning: Area '{area_id}' not found, skipping NPCs")
                continue
                
            area = self.game.areas[area_id]
            
            for npc_data in area_npcs:
                npc = self._create_npc_from_data(npc_data)
                if npc:
                    area.add_npc(npc)
                    npc_count += 1
        
        print(f"Added {npc_count} NPCs to areas")
    
    def _create_npc_from_data(self, npc_data):
        """Create an NPC from data."""
        npc_type = npc_data.get('type', 'civilian')
        name = npc_data.get('name', 'NPC')
        description = npc_data.get('description', 'A person.')
        
        if npc_type == 'civilian':
            npc = Civilian(name, description)
        elif npc_type == 'gang_member':
            gang_name = npc_data.get('gang')
            if gang_name in self.game.gangs:
                npc = GangMember(name, description, self.game.gangs[gang_name])
            else:
                print(f"Warning: Gang '{gang_name}' not found, creating civilian instead")
                npc = Civilian(name, description)
        else:
            print(f"Warning: Unknown NPC type '{npc_type}', creating civilian")
            npc = Civilian(name, description)
        
        # Add items to the NPC if specified
        if 'items' in npc_data:
            for item_data in npc_data['items']:
                item = self._create_item_from_data(item_data)
                if item:
                    npc.add_item(item)
        
        return npc
    
    def _get_default_npcs_data(self):
        """Return default NPC data for the game world."""
        # Generate random civilian names
        civilian_names = ["Ben", "Bob", "Charl", "Muckle", "Beevo", "ZeFronk", "Grazey", "Honk", "Ivee", "Jork"]
        name_variations = ["etti", "oodle", "op", "eeky", "-eep", "uffin", "bertmo", "athur", "ubble", "uck"]
        
        # Generate random civilians
        random_civilians = []
        for i in range(5):
            name_start = random.choice(civilian_names)
            name_end = random.choice(name_variations)
            name = f"{name_start}{name_end}"
            
            random_civilians.append({
                "type": "civilian",
                "name": name,
                "description": f"A random civilian named {name}.",
                "items": [
                    {"type": "watering_can", "name": "Watering Can"},
                    {"type": "seed", "name": "Carrot Seed", "description": "A seed for growing carrot.", "value": 5, "plant_type": "carrot"},
                    {"type": "effect_item", "name": "Hacked Milk Blaster", "description": "A strange device that sprays hacked milk.", "value": 50, "effect_type": "hallucination"}
                ]
            })
        
        # Generate random Bloodhounds members
        bloodhounds_members = []
        bloodhounds_names = self.game.gangs["Bloodhounds"].member_names.copy() if "Bloodhounds" in self.game.gangs else ["Member1", "Member2", "Member3", "Member4", "Member5"]
        
        for i in range(min(5, len(bloodhounds_names))):
            name = random.choice(bloodhounds_names)
            bloodhounds_names.remove(name)
            
            bloodhounds_members.append({
                "type": "gang_member",
                "name": name,
                "description": f"A member of the Bloodhounds named {name}.",
                "gang": "Bloodhounds",
                "items": [
                    {"type": "weapon", "name": "Gun", "description": "A standard firearm.", "value": 50, "damage": 20},
                    {"type": "watering_can", "name": "Watering Can"},
                    {"type": "effect_item", "name": "Confusion Ray", "description": "A device that emits waves that confuse the target.", "value": 60, "effect_type": "confusion"}
                ]
            })
        
        return {
            "garden": [
                {
                    "type": "civilian",
                    "name": "Gardener",
                    "description": "A friendly gardener tending to the plants."
                }
            ] + random_civilians,
            "warehouse": [
                {
                    "type": "civilian",
                    "name": "John",
                    "description": "A random guy."
                },
                {
                    "type": "gang_member",
                    "name": random.choice(self.game.gangs["Crimson Vipers"].member_names) if "Crimson Vipers" in self.game.gangs else "Viper",
                    "description": "A member of the Crimson Vipers.",
                    "gang": "Crimson Vipers"
                }
            ] + bloodhounds_members
        }
    
    def setup_player(self):
        """Set up the player's starting location and items."""
        self.game.player.current_area = self.game.areas["Home"]
