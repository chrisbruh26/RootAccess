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
        
        # Load world data if available
        self.world_data = {}
        self._load_world_data()
    
    def _load_world_data(self):
        """Load world data from JSON files if they exist."""
        data_files = {
            'areas': 'world_data/areas.json',
            'connections': 'world_data/connections.json',
            'items': 'world_data/items.json',
            'objects': 'world_data/objects.json',
            'npcs': 'world_data/npcs.json',
            'gangs': 'world_data/gangs.json'
        }
        
        # Create world_data directory if it doesn't exist
        os.makedirs('world_data', exist_ok=True)
        
        for key, filepath in data_files.items():
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'r') as f:
                        self.world_data[key] = json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
                self.world_data[key] = {}
    
    def build_world(self):
        """Main method to build the entire world."""
        self.create_areas()
        self.connect_areas()
        self.create_gangs()
        self.add_objects_to_areas()
        self.add_items_to_areas()
        self.add_npcs_to_areas()
        self.setup_player()
    
    def create_areas(self):
        """Create all game areas."""
        # Check if we have area data from JSON
        if 'areas' in self.world_data and self.world_data['areas']:
            # Create areas from JSON data
            for area_id, area_data in self.world_data['areas'].items():
                self.game.areas[area_id] = Area(area_data['name'], area_data['description'])
            print(f"Created {len(self.world_data['areas'])} areas from JSON data")
        else:
            # Define areas with their names and descriptions (fallback)
            area_definitions = {
                "Home": "Your secret base of operations. It's small but functional.",
                "garden": "A small garden area with fertile soil.",
                "street": "A busy street with various shops and people.",
                "alley": "A dark alley between buildings.",
                "plaza": "A large open plaza with a fountain in the center.",
                "warehouse": "An abandoned warehouse, taken over by the Bloodhounds.",
                "construction": "A construction site with various equipment and materials."
            }
            
            # Create each area
            for area_id, description in area_definitions.items():
                self.game.areas[area_id] = Area(area_id.capitalize(), description)
            print("Created areas from hardcoded definitions")
    
    def connect_areas(self):
        """Connect areas to create the world map."""
        # Check if we have connection data from JSON
        if 'connections' in self.world_data and self.world_data['connections']:
            # Create connections from JSON data
            for connection in self.world_data['connections']:
                source = connection['source']
                direction = connection['direction']
                destination = connection['destination']
                
                if source in self.game.areas and destination in self.game.areas:
                    self.game.areas[source].add_connection(direction, self.game.areas[destination])
            
            print(f"Created {len(self.world_data['connections'])} connections from JSON data")
        else:
            # Define connections between areas (fallback)
            connections = [
                ("Home", "north", "garden"),
                ("garden", "south", "Home"),
                ("garden", "east", "street"),
                ("street", "west", "garden"),
                ("street", "north", "plaza"),
                ("plaza", "south", "street"),
                ("street", "east", "alley"),
                ("alley", "west", "street"),
                ("street", "south", "warehouse"),
                ("warehouse", "north", "street"),
                ("plaza", "east", "construction"),
                ("construction", "west", "plaza")
            ]
            
            # Create each connection
            for source, direction, destination in connections:
                self.game.areas[source].add_connection(direction, self.game.areas[destination])
            
            print("Created connections from hardcoded definitions")
    
    def create_gangs(self):
        """Create gangs in the game world."""
        # Define gangs
        gang_definitions = {
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
        
        # Create each gang
        for gang_name, gang_data in gang_definitions.items():
            self.game.gangs[gang_name] = Gang(gang_name)
            self.game.gangs[gang_name].member_names = gang_data["names"]
    
    def add_objects_to_areas(self):
        """Add objects to areas."""
        # Add soil plots
        self._add_soil_plots()
        
        # Add computers
        self._add_computers()
        
        # Add hiding spots
        self._add_hiding_spots()
        
        # Add vending machines
        self._add_vending_machines()
    
    def _add_soil_plots(self):
        """Add soil plots to appropriate areas."""
        garden_soil = SoilPlot()
        self.game.areas["garden"].add_object(garden_soil)
        
        warehouse_soil = SoilPlot()
        self.game.areas["warehouse"].add_object(warehouse_soil)
    
    def _add_computers(self):
        """Add computers to appropriate areas."""
        computer = Computer("Hacking Terminal", "A specialized terminal for hacking operations.")
        computer.programs = ["data_miner", "security_override", "plant_hacker"]
        self.game.areas["Home"].add_object(computer)
    
    def _add_hiding_spots(self):
        """Add hiding spots to appropriate areas."""
        hiding_spots = {
            "Home": [
                ("Closet", "A small closet that you can hide in.", 0.8)
            ],
            "garden": [
                ("Bushes", "Dense bushes that provide good cover.", 0.7)
            ],
            "alley": [
                ("Dumpster", "A large dumpster you can hide behind.", 0.6)
            ],
            "plaza": [
                ("Fountain", "A large fountain with decorative elements to hide behind.", 0.5)
            ],
            "warehouse": [
                ("Crates", "Stacked crates that provide decent cover.", 0.6),
                ("Construction Container", "A large metal container used for storing construction materials.", 0.9),
                ("Equipment Shed", "A small shed for storing construction equipment.", 0.8),
                ("Cement Mixer", "A large cement mixer you can hide behind.", 0.7)
            ]
        }
        
        for area_id, spots in hiding_spots.items():
            for name, description, effectiveness in spots:
                hiding_spot = HidingSpot(name, description, effectiveness)
                self.game.areas[area_id].add_object(hiding_spot)
    
    def _add_vending_machines(self):
        """Add vending machines to appropriate areas."""
        vending_machine = VendingMachine("Vending Machine")
        self.game.areas["warehouse"].add_object(vending_machine)
        
        # Add items to vending machine
        vending_items = [
            Consumable("Soda", "A refreshing soda.", 5, 10),
            Consumable("Chips", "A bag of chips.", 5, 5),
            Consumable("Candy Bar", "A chocolate candy bar.", 5, 15),
            Consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20)
        ]
        
        for item in vending_items:
            vending_machine.add_item(item)
    
    def add_items_to_areas(self):
        """Add items to areas."""
        # Basic items
        self._add_basic_items()
        
        # Weapons
        self._add_weapons()
        
        # Seeds and gardening items
        self._add_gardening_items()
        
        # Tech items
        self._add_tech_items()
    
    def _add_basic_items(self):
        """Add basic items to areas."""
        self.game.areas["Home"].add_item(Item("Backpack", "A sturdy backpack for carrying items.", 20))
        self.game.areas["street"].add_item(Consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20))
    
    def _add_weapons(self):
        """Add weapons to areas."""
        # Basic weapons
        self.game.areas["alley"].add_item(Weapon("Pipe", "A metal pipe that can be used as a weapon.", 15, 10))
        
        # Advanced weapons
        gun = Weapon("Gun", "A standard firearm.", 50, 20)
        machine_gun = Weapon("Machine Gun", "A machine gun.", 100, 50)
        
        # Effect weapons
        hacked_milk_blaster = EffectItem("Hacked Milk Blaster", "A strange device that sprays hacked milk.", 50, HallucinationEffect())
        confusion_ray = EffectItem("Confusion Ray", "A device that emits waves that confuse the target.", 60, ConfusionEffect())
        
        # Add to areas
        self.game.areas["warehouse"].add_item(hacked_milk_blaster)
        self.game.areas["alley"].add_item(confusion_ray)
        self.game.areas["Home"].add_item(hacked_milk_blaster)
        
        # Add to player
        self.game.player.add_item(machine_gun)
    
    def _add_gardening_items(self):
        """Add gardening items to areas."""
        # Create seeds
        tomato_seed = Seed("Tomato Seed", "A seed for growing tomatoes.", "tomato", 5)
        potato_seed = Seed("Potato Seed", "A seed for growing potatoes.", "potato", 5)
        carrot_seed = Seed("Carrot Seed", "A seed for growing carrot.", "carrot", 5)
        
        # Create watering can
        watering_can = WateringCan("watering can")
        
        # Add to areas
        self.game.areas["garden"].add_item(tomato_seed)
        self.game.areas["garden"].add_item(potato_seed)
        self.game.areas["Home"].add_item(carrot_seed)
        self.game.areas["Home"].add_item(watering_can)
        self.game.areas["warehouse"].add_item(carrot_seed)
        
        # Add to player
        self.game.player.add_item(watering_can)
    
    def _add_tech_items(self):
        """Add tech items to areas."""
        # Create tech items
        smoke_bomb = SmokeBomb()
        tech_decoy = Decoy()
        drone = Drone()
        
        # Add to areas
        self.game.areas["alley"].add_item(SmokeBomb())
        self.game.areas["street"].add_item(SmokeBomb())
        self.game.areas["warehouse"].add_item(Decoy())
        self.game.areas["garden"].add_item(Decoy())
        self.game.areas["Home"].add_item(drone)
        
        # Add to player
        self.game.player.add_item(smoke_bomb)
        self.game.player.add_item(tech_decoy)
    
    def add_npcs_to_areas(self):
        """Add NPCs to areas."""
        # Add civilians
        self._add_civilians()
        
        # Add gang members
        self._add_gang_members()
    
    def _add_civilians(self):
        """Add civilian NPCs to areas."""
        # Add gardener
        gardener = Civilian("Gardener", "A friendly gardener tending to the plants.")
        self.game.areas["garden"].add_npc(gardener)
        
        # Add John
        john = Civilian("John", "A random guy.")
        self.game.areas["warehouse"].add_npc(john)
        
        # Add random civilians to garden
        civilian_names = ["Ben", "Bob", "Charl", "Muckle", "Beevo", "ZeFronk", "Grazey", "Honk", "Ivee", "Jork"]
        name_variations = ["etti", "oodle", "op", "eeky", "-eep", "uffin", "bertmo", "athur", "ubble", "uck", 
                          "ington", "sworth", "thistle", "quibble", "fizzle", "whistle", "plume", "tumble", 
                          "whisk", "glimmer", "thrax", "gloop", "splunk", "dribble", "crunch", "splorp", 
                          "quack", "splat", "grizzle", "blorp", "kins", "muff", "snuff", "puff", "whiff", 
                          "bloop", "twizzle", "flibble", "squibble", "wobble", "izzle", "oodle", "bop", 
                          "snorp", "florp", "wump", "zorp", "plonk", "squee", "boop", "doodle", "ucklebuck", "shoop"]
        
        # Create items for civilians
        watering_can = WateringCan("watering can")
        carrot_seed = Seed("Carrot Seed", "A seed for growing carrot.", "carrot", 5)
        hacked_milk_blaster = EffectItem("Hacked Milk Blaster", "A strange device that sprays hacked milk.", 50, HallucinationEffect())
        
        for i in range(5):
            name_start = random.choice(civilian_names)
            name_end = random.choice(name_variations)
            name = f"{name_start}{name_end}"
            
            civilian = Civilian(name, f"A random civilian named {name}.")
            civilian.add_item(watering_can)
            civilian.add_item(carrot_seed)
            civilian.add_item(hacked_milk_blaster)
            
            self.game.areas["garden"].add_npc(civilian)
    
    def _add_gang_members(self):
        """Add gang members to areas."""
        # Add Crimson Vipers member
        crimson_vipers_names = self.game.gangs["Crimson Vipers"].member_names
        name = random.choice(crimson_vipers_names)
        vipers_member = GangMember(name, f"A member of the Crimson Vipers named {name}.", self.game.gangs["Crimson Vipers"])
        self.game.areas["warehouse"].add_npc(vipers_member)
        
        # Add Bloodhounds members
        bloodhounds_names = self.game.gangs["Bloodhounds"].member_names.copy()
        
        # Items for gang members
        gun = Weapon("Gun", "A standard firearm.", 50, 20)
        watering_can = WateringCan("watering can")
        confusion_ray = EffectItem("Confusion Ray", "A device that emits waves that confuse the target.", 60, ConfusionEffect())
        
        for i in range(5):
            name = random.choice(bloodhounds_names)
            bloodhounds_names.remove(name)
            
            member = GangMember(name, f"A member of the Bloodhounds named {name}.", self.game.gangs["Bloodhounds"])
            member.add_item(gun)
            member.add_item(watering_can)
            member.add_item(confusion_ray)
            
            self.game.areas["warehouse"].add_npc(member)
    
    def setup_player(self):
        """Set up the player's starting location and items."""
        self.game.player.current_area = self.game.areas["Home"]
