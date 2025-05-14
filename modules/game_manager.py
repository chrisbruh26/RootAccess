"""
Game Manager module for Root Access v3.
Handles game state, saving/loading, and overall game flow.
"""

import json
import os
import time
from .player import Player
from .area import Area, Building, AreaManager
from .items import Item, Consumable, Weapon, TechItem, EffectItem, Seed, Plant, Tool, WateringCan, ItemManager
from .game_objects import GameObject, Transport, Elevator, Door, Vehicle, Computer, HidingSpot, VendingMachine, SoilPlot, GameObjectManager
from .npc import NPC, Civilian, GangMember, Gang, NPCManager
from .coordinates import Coordinates
from .time_system import TimeSystem

class GameManager:
    """Manages the overall game state and systems."""
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.player = Player()
        self.area_manager = AreaManager()
        self.item_manager = ItemManager()
        self.object_manager = GameObjectManager()
        self.npc_manager = NPCManager()
        self.time_system = TimeSystem()
        self.running = True
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def initialize_game(self):
        """Initialize the game with default areas, items, NPCs, etc."""
        self.load_templates()
        self.create_starting_world()
        self.place_player_in_starting_area()
    
    def load_templates(self):
        """Load templates from JSON files."""
        # Load area templates
        area_templates_file = os.path.join(self.data_dir, "area_templates.json")
        if os.path.exists(area_templates_file):
            with open(area_templates_file, 'r') as f:
                self.area_manager.templates = json.load(f)
        
        # Load item templates
        item_templates_file = os.path.join(self.data_dir, "item_templates.json")
        if os.path.exists(item_templates_file):
            with open(item_templates_file, 'r') as f:
                self.item_manager.templates = json.load(f)
        
        # Load object templates
        object_templates_file = os.path.join(self.data_dir, "object_templates.json")
        if os.path.exists(object_templates_file):
            with open(object_templates_file, 'r') as f:
                self.object_manager.templates = json.load(f)
        
        # Load NPC templates
        npc_templates_file = os.path.join(self.data_dir, "npc_templates.json")
        if os.path.exists(npc_templates_file):
            with open(npc_templates_file, 'r') as f:
                self.npc_manager.templates = json.load(f)
    
    def create_starting_world(self):
        """Create the starting world with areas, items, NPCs, etc."""
        # Create areas
        self.create_starting_areas()
        
        # Create items
        self.create_starting_items()
        
        # Create NPCs
        self.create_starting_npcs()
        
        # Create objects
        self.create_starting_objects()
    
    def create_starting_areas(self):
        """Create the starting areas for the game."""
        # Create areas from templates
        area_coordinates = {
            "home": Coordinates(0, 0, 0),
            "garden": Coordinates(0, 5, 0),
            "street": Coordinates(8, 5, 0),
            "shop": Coordinates(15, 5, 0),  # Add shop next to street
            "alley": Coordinates(23, 5, 0),
            "plaza": Coordinates(8, 10, 0),
            "warehouse": Coordinates(8, -5, 0),
            "construction_site": Coordinates(20, 10, 0)
        }
        
        # Create areas from templates
        for area_id, coords in area_coordinates.items():
            template = self.area_manager.templates.get(area_id)
            if template:
                if template.get("type") == "Area":
                    area = Area(
                        template.get("name", area_id.capitalize()),
                        template.get("description", "An area in the game."),
                        coords,
                        grid_width=template.get("grid_width", 10),
                        grid_length=template.get("grid_length", 10),
                        weather=template.get("weather", "clear")
                    )
                    self.area_manager.add_area(area)
                    print(f"Created area: {area.name}")
        
        # Create office building
        office_template = self.area_manager.templates.get("office_building")
        if office_template:
            office_building = Building(
                office_template.get("name", "Office Building"),
                office_template.get("description", "A tall office building."),
                Coordinates(0, 15, 0),
                num_floors=office_template.get("num_floors", 5),
                grid_width=office_template.get("grid_width", 10),
                grid_length=office_template.get("grid_length", 10)
            )
            self.area_manager.add_area(office_building)
            
            # Create floors for the office building
            floor_template = self.area_manager.templates.get("office_floor")
            for floor in range(1, office_template.get("num_floors", 5) + 1):
                floor_area = Area(
                    f"Office Floor {floor}",
                    f"Floor {floor} of the office building.",
                    Coordinates(0, 15, floor - 1),
                    grid_width=floor_template.get("grid_width", 10),
                    grid_length=floor_template.get("grid_length", 10),
                    weather=floor_template.get("weather", "controlled")
                )
                self.area_manager.add_area(floor_area)
                office_building.add_floor(floor, floor_area)
        
        # Connect areas
        home = self.area_manager.get_area("home")
        garden = self.area_manager.get_area("garden")
        street = self.area_manager.get_area("street")
        shop = self.area_manager.get_area("shop")
        alley = self.area_manager.get_area("alley")
        plaza = self.area_manager.get_area("plaza")
        warehouse = self.area_manager.get_area("warehouse")
        construction_site = self.area_manager.get_area("construction_site")
        office_building = self.area_manager.get_area("office_building")
        
        if home and garden:
            self.area_manager.connect_areas(home.id, "north", garden.id)
        
        if garden and street:
            self.area_manager.connect_areas(garden.id, "east", street.id)
        
        if street and shop:
            self.area_manager.connect_areas(street.id, "east", shop.id)
            
        if shop and alley:
            self.area_manager.connect_areas(shop.id, "east", alley.id)
        
        if street and plaza:
            self.area_manager.connect_areas(street.id, "north", plaza.id)
        
        if street and warehouse:
            self.area_manager.connect_areas(street.id, "south", warehouse.id)
        
        if plaza and construction_site:
            self.area_manager.connect_areas(plaza.id, "east", construction_site.id)
        
        if plaza and office_building:
            self.area_manager.connect_areas(plaza.id, "west", office_building.id)
    
    def create_starting_items(self):
        """Create the starting items for the game."""
        # Create a backpack
        backpack = Item(
            "Backpack",
            "A sturdy backpack for carrying items.",
            value=20
        )
        self.item_manager.add_item(backpack)
        
        # Create weapons
        pipe = Weapon(
            "Pipe",
            "A metal pipe that can be used as a weapon.",
            damage=15,
            durability=10,
            value=15
        )
        self.item_manager.add_item(pipe)
        
        gun = Weapon(
            "Gun",
            "A standard firearm.",
            damage=50,
            durability=20,
            value=50
        )
        self.item_manager.add_item(gun)
        
        machine_gun = Weapon(
            "Machine Gun",
            "A machine gun with high damage output.",
            damage=100,
            durability=50,
            value=100
        )
        self.item_manager.add_item(machine_gun)
        
        # Create tech items
        smoke_bomb = TechItem(
            "Smoke Bomb",
            "A device that creates a smoke screen for stealth.",
            effect_type="smoke",
            duration=3,
            value=30
        )
        self.item_manager.add_item(smoke_bomb)
        
        decoy = TechItem(
            "Decoy",
            "A device that creates a holographic decoy to distract enemies.",
            effect_type="decoy",
            duration=5,
            value=40
        )
        self.item_manager.add_item(decoy)
        
        drone = TechItem(
            "Drone",
            "A small drone that can be used for reconnaissance.",
            effect_type="recon",
            duration=10,
            value=80
        )
        self.item_manager.add_item(drone)
        
        # Create effect items
        hacked_milk_blaster = EffectItem(
            "Hacked Milk Blaster",
            "A strange device that sprays hacked milk, causing hallucinations.",
            effect_type="hallucination",
            duration=5,
            value=50
        )
        self.item_manager.add_item(hacked_milk_blaster)
        
        confusion_ray = EffectItem(
            "Confusion Ray",
            "A device that emits waves that confuse the target.",
            effect_type="confusion",
            duration=4,
            value=60
        )
        self.item_manager.add_item(confusion_ray)
        
        # Create seeds
        tomato_seed = Seed(
            "Tomato Seed",
            "A seed for growing tomatoes.",
            plant_type="tomato",
            growth_time=5,
            value=5
        )
        self.item_manager.add_item(tomato_seed)
        
        potato_seed = Seed(
            "Potato Seed",
            "A seed for growing potatoes.",
            plant_type="potato",
            growth_time=4,
            value=5
        )
        self.item_manager.add_item(potato_seed)
        
        carrot_seed = Seed(
            "Carrot Seed",
            "A seed for growing carrots.",
            plant_type="carrot",
            growth_time=3,
            value=5
        )
        self.item_manager.add_item(carrot_seed)
        
        # Create tools
        watering_can = WateringCan()
        self.item_manager.add_item(watering_can)
        
        # Create consumables
        energy_drink = Consumable(
            "Energy Drink",
            "A caffeinated beverage that restores health.",
            value=10,
            nutrition=10,
            effects={"energy": 20}
        )
        self.item_manager.add_item(energy_drink)
        
        # Place items in areas
        home = self.area_manager.get_area("home")
        if home:
            home.place_object_at(backpack, 2, 2)
            home.place_object_at(watering_can, 3, 2)
            home.place_object_at(hacked_milk_blaster, 4, 2)
            home.place_object_at(drone, 2, 3)
        
        garden = self.area_manager.get_area("garden")
        if garden:
            garden.place_object_at(tomato_seed, 3, 3)
            garden.place_object_at(potato_seed, 4, 3)
            garden.place_object_at(carrot_seed, 5, 3)
        
        street = self.area_manager.get_area("street")
        if street:
            street.place_object_at(energy_drink, 5, 2)
        
        alley = self.area_manager.get_area("alley")
        if alley:
            alley.place_object_at(pipe, 3, 1)
            alley.place_object_at(confusion_ray, 5, 1)
        
        warehouse = self.area_manager.get_area("warehouse")
        if warehouse:
            warehouse.place_object_at(gun, 5, 5)
            warehouse.place_object_at(smoke_bomb, 7, 7)
            warehouse.place_object_at(decoy, 9, 9)
    
    def create_starting_npcs(self):
        """Create the starting NPCs for the game."""
        import random
        
        # Create gangs
        bloodhounds = self.npc_manager.create_gang("Bloodhounds")
        crimson_vipers = self.npc_manager.create_gang("Crimson Vipers")
        
        # Generate random names for NPCs
        first_names = ["Alex", "Ben", "Charlie", "David", "Emma", "Frank", "Grace", "Hannah", "Ian", "Julia", 
                      "Kai", "Lily", "Max", "Nina", "Oscar", "Penny", "Quinn", "Ruby", "Sam", "Tina"]
        
        # Create NPCs from templates
        # Civilians
        shop = self.area_manager.get_area("shop")
        street = self.area_manager.get_area("street")
        garden = self.area_manager.get_area("garden")
        plaza = self.area_manager.get_area("plaza")
        warehouse = self.area_manager.get_area("warehouse")
        construction_site = self.area_manager.get_area("construction_site")
        alley = self.area_manager.get_area("alley")
        
        # Set up time constants for schedules
        morning = 8 * 60  # 8:00 AM in minutes
        noon = 12 * 60    # 12:00 PM in minutes
        afternoon = 15 * 60  # 3:00 PM in minutes
        evening = 18 * 60  # 6:00 PM in minutes
        night = 22 * 60   # 10:00 PM in minutes
        
        # Create civilians
        civilian_template = self.npc_manager.templates.get("civilian")
        if civilian_template:
            for i in range(8):  # Create 8 civilians
                # Generate a unique name for this civilian
                name = random.choice(first_names)
                first_names.remove(name)  # Ensure unique names
                
                # Create a civilian with a hidden name
                civilian = Civilian(
                    name,  # Real name stored internally
                    civilian_template.get("description", "An ordinary citizen going about their day."),
                    personality=civilian_template.get("personality", {"friendliness": 50, "curiosity": 40}),
                    money=civilian_template.get("money", 50) + random.randint(-20, 20),
                    dialogue=civilian_template.get("dialogue", {"default": "Hello there!"})
                )
                
                # Set display name to generic "Civilian" (will be revealed on interaction)
                civilian.display_name = "Civilian"
                civilian.known_to_player = False
                
                self.npc_manager.add_npc(civilian)
                
                # Add random items to civilians based on template
                possible_items = civilian_template.get("possible_items", [])
                if possible_items:
                    # Give each civilian 1-2 random items from their possible items
                    num_items = random.randint(1, 2)
                    for _ in range(num_items):
                        item_template_id = random.choice(possible_items)
                        item = self.item_manager.create_from_template(item_template_id)
                        if item:
                            civilian.add_to_inventory(item)
        
                # Place civilians in different areas
                if i < 3 and garden:
                    garden.place_object_at(civilian, 2 + i, 2)
                    civilian.set_schedule(morning, "working", garden)
                    civilian.set_schedule(noon, "eating", plaza if plaza else garden)
                    civilian.set_schedule(afternoon, "walking", street if street else garden)
                    civilian.set_schedule(evening, "shopping", shop if shop else street if street else garden)
                    civilian.set_schedule(night, "sleeping", garden)
                    civilian.current_action = "enjoying the garden"
                elif i < 6 and street:
                    street.place_object_at(civilian, 5 + i, 2)
                    civilian.set_schedule(morning, "walking", street)
                    civilian.set_schedule(noon, "eating", plaza if plaza else street)
                    civilian.set_schedule(afternoon, "shopping", shop if shop else street)
                    civilian.set_schedule(evening, "idle", street)
                    civilian.set_schedule(night, "sleeping", street)
                    civilian.current_action = "walking down the street"
                elif plaza:
                    plaza.place_object_at(civilian, 3 + i % 3, 3 + i % 3)
                    civilian.set_schedule(morning, "walking", plaza)
                    civilian.set_schedule(noon, "eating", plaza)
                    civilian.set_schedule(afternoon, "idle", plaza)
                    civilian.set_schedule(evening, "shopping", shop if shop else street if street else plaza)
                    civilian.set_schedule(night, "sleeping", plaza)
                    civilian.current_action = "relaxing in the plaza"
        
        # Create shopkeeper
        shopkeeper_template = self.npc_manager.templates.get("shopkeeper")
        if shopkeeper_template and shop:
            shopkeeper = Civilian(
                shopkeeper_template.get("name", "Shopkeeper"),
                shopkeeper_template.get("description", "A friendly shopkeeper selling various goods."),
                dialogue=shopkeeper_template.get("dialogue", {"default": "Welcome to my shop!"}),
                personality=shopkeeper_template.get("personality", {"friendliness": 60, "greed": 40}),
                money=shopkeeper_template.get("money", 500)
            )
            self.npc_manager.add_npc(shopkeeper)
            
            # Add items to shopkeeper's inventory
            possible_items = shopkeeper_template.get("possible_items", [])
            if possible_items:
                for item_template_id in possible_items:
                    item = self.item_manager.create_from_template(item_template_id)
                    if item:
                        shopkeeper.add_to_inventory(item)
            
            # Place shopkeeper in shop
            shop.place_object_at(shopkeeper, 3, 3)
            
            # Set shopkeeper schedule
            shopkeeper.set_schedule(morning - 60, "opening_shop", shop)
            shopkeeper.set_schedule(morning, "selling", shop)
            shopkeeper.set_schedule(evening, "closing_shop", shop)
            shopkeeper.set_schedule(night, "idle", shop)
            
            # Set current action
            shopkeeper.current_action = "managing the shop"
        
        # Create Bloodhound gang members
        bloodhound_template = self.npc_manager.templates.get("gang_member_bloodhound")
        if bloodhound_template:
            for i in range(5):  # Create 5 Bloodhound members
                # Generate a unique name for this gang member
                name = f"Bloodhound {random.choice(['Crusher', 'Smasher', 'Bruiser', 'Thug', 'Enforcer', 'Goon', 'Muscle'])} {i+1}"
                
                gang_member = GangMember(
                    name,
                    bloodhound_template.get("description", "A member of the Bloodhounds gang."),
                    "Bloodhounds",
                    personality=bloodhound_template.get("personality", {"aggression": 70, "loyalty": 80}),
                    money=bloodhound_template.get("money", 100) + random.randint(-20, 20),
                    dialogue=bloodhound_template.get("dialogue", {"default": "What do you want?"})
                )
                
                # Set display name to generic gang member (will be revealed on interaction)
                gang_member.display_name = "Bloodhound Gang Member"
                gang_member.known_to_player = False
                
                self.npc_manager.add_npc(gang_member)
                bloodhounds.add_member(gang_member)
                
                # Add items to gang member's inventory
                possible_items = bloodhound_template.get("possible_items", [])
                if possible_items:
                    # Give each gang member 1-2 random items from their possible items
                    num_items = random.randint(1, 2)
                    for _ in range(num_items):
                        item_template_id = random.choice(possible_items)
                        item = self.item_manager.create_from_template(item_template_id)
                        if item:
                            gang_member.add_to_inventory(item)
                
                # Place gang members in warehouse or alley
                if i < 3 and warehouse:
                    warehouse.place_object_at(gang_member, 3 + i, 3 + i)
                    gang_member.set_schedule(morning, "patrolling", warehouse)
                    gang_member.set_schedule(noon, "guarding", warehouse)
                    gang_member.set_schedule(evening, "meeting", warehouse)
                    gang_member.set_schedule(night, "sleeping", warehouse)
                    gang_member.current_action = "patrolling the warehouse"
                elif alley:
                    alley.place_object_at(gang_member, 2 + i % 3, 1)
                    gang_member.set_schedule(morning, "patrolling", alley)
                    gang_member.set_schedule(noon, "guarding", alley)
                    gang_member.set_schedule(evening, "dealing", alley)
                    gang_member.set_schedule(night, "patrolling", alley)
                    gang_member.current_action = "guarding the alley"
        
        # Create Crimson Viper gang members
        viper_template = self.npc_manager.templates.get("gang_member_viper")
        if viper_template:
            for i in range(5):  # Create 5 Viper members
                # Generate a unique name for this gang member
                name = f"Viper {random.choice(['Striker', 'Slasher', 'Venom', 'Fang', 'Cobra', 'Python', 'Serpent'])} {i+1}"
                
                gang_member = GangMember(
                    name,
                    viper_template.get("description", "A member of the Crimson Vipers gang."),
                    "Crimson Vipers",
                    personality=viper_template.get("personality", {"aggression": 60, "cunning": 70}),
                    money=viper_template.get("money", 100) + random.randint(-20, 20),
                    dialogue=viper_template.get("dialogue", {"default": "Keep moving."})
                )
                
                # Set display name to generic gang member (will be revealed on interaction)
                gang_member.display_name = "Crimson Viper Gang Member"
                gang_member.known_to_player = False
                
                self.npc_manager.add_npc(gang_member)
                crimson_vipers.add_member(gang_member)
                
                # Add items to gang member's inventory
                possible_items = viper_template.get("possible_items", [])
                if possible_items:
                    # Give each gang member 1-2 random items from their possible items
                    num_items = random.randint(1, 2)
                    for _ in range(num_items):
                        item_template_id = random.choice(possible_items)
                        item = self.item_manager.create_from_template(item_template_id)
                        if item:
                            gang_member.add_to_inventory(item)
                
                # Place gang members in construction site
                if construction_site:
                    construction_site.place_object_at(gang_member, 5 + i % 5, 2 + i % 3)
                    gang_member.set_schedule(morning, "patrolling", construction_site)
                    gang_member.set_schedule(noon, "meeting", construction_site)
                    gang_member.set_schedule(evening, "guarding", construction_site)
                    gang_member.set_schedule(night, "sleeping", construction_site)
                    gang_member.current_action = "hanging out at the construction site"
        
        # Claim territories for gangs
        if warehouse:
            # Claim warehouse as Bloodhounds territory
            bloodhounds.claim_territory(warehouse)
        
        if construction_site:
            # Claim construction site as Crimson Vipers territory
            crimson_vipers.claim_territory(construction_site)
    
    def create_starting_objects(self):
        """Create the starting objects for the game."""
        # Create soil plots
        garden = self.area_manager.get_area("garden")
        if garden:
            for i in range(3):
                for j in range(2):
                    soil_plot = SoilPlot()
                    garden.place_object_at(soil_plot, 3 + i, 5 + j)
        
        warehouse = self.area_manager.get_area("warehouse")
        if warehouse:
            soil_plot = SoilPlot()
            warehouse.place_object_at(soil_plot, 10, 10)
        
        # Create computers
        home = self.area_manager.get_area("home")
        if home:
            computer = Computer(
                "Hacking Terminal",
                "A specialized terminal for hacking operations.",
                programs=["data_miner", "security_override", "plant_hacker"]
            )
            home.place_object_at(computer, 1, 1)
        
        # Create hiding spots
        if home:
            closet = HidingSpot(
                "Closet",
                "A small closet that you can hide in.",
                stealth_bonus=0.8
            )
            home.place_object_at(closet, 4, 4)
        
        if garden:
            bushes = HidingSpot(
                "Bushes",
                "Dense bushes that provide good cover.",
                stealth_bonus=0.7
            )
            garden.place_object_at(bushes, 6, 6)
        
        alley = self.area_manager.get_area("alley")
        if alley:
            dumpster = HidingSpot(
                "Dumpster",
                "A large dumpster you can hide behind.",
                stealth_bonus=0.6
            )
            alley.place_object_at(dumpster, 5, 1)
        
        plaza = self.area_manager.get_area("plaza")
        if plaza:
            fountain = HidingSpot(
                "Fountain",
                "A large fountain with decorative elements to hide behind.",
                stealth_bonus=0.5
            )
            plaza.place_object_at(fountain, 6, 6)
        
        if warehouse:
            crates = HidingSpot(
                "Crates",
                "Stacked crates that provide decent cover.",
                stealth_bonus=0.6
            )
            warehouse.place_object_at(crates, 12, 12)
        
        # Create vending machine
        street = self.area_manager.get_area("street")
        if street:
            vending_machine = VendingMachine("Vending Machine")
            street.place_object_at(vending_machine, 12, 2)
            
            # Add items to vending machine
            vending_machine.add_item(Consumable(
                "Soda",
                "A refreshing soda.",
                value=5,
                nutrition=5,
                effects={"energy": 10}
            ))
            vending_machine.add_item(Consumable(
                "Chips",
                "A bag of chips.",
                value=5,
                nutrition=5,
                effects={"energy": 5}
            ))
            vending_machine.add_item(Consumable(
                "Candy Bar",
                "A chocolate candy bar.",
                value=5,
                nutrition=5,
                effects={"energy": 15}
            ))
            vending_machine.add_item(Consumable(
                "Energy Drink",
                "A caffeinated beverage that restores health.",
                value=10,
                nutrition=10,
                effects={"energy": 20}
            ))
        
        # Create elevator in office building
        office_building = self.area_manager.get_area("office_building")
        if office_building and isinstance(office_building, Building):
            elevator = Elevator(
                "Office Elevator",
                "An elevator that can take you to different floors of the office building."
            )
            self.object_manager.add_object(elevator)
            
            # Add floors to the elevator
            for floor_num, floor_area in office_building.floors.items():
                elevator.add_floor(floor_num, floor_area, 5, 5)  # Place elevator at center of each floor
            
            # Place elevator in the office building
            office_building.place_object_at(elevator, 5, 5)
        
        # Create a car on the street
        if street:
            car = Vehicle(
                "Car",
                "A standard car that can be driven around.",
                speed=3,
                fuel=100,
                max_fuel=100
            )
            street.place_object_at(car, 3, 2)
    
    def place_player_in_starting_area(self):
        """Place the player in the starting area."""
        starting_area = self.area_manager.get_area("home")
        if starting_area:
            self.player.set_current_area(starting_area, 2, 2)
            
            # Give player some starting items
            self.player.money = 100
            
            # Add a weapon
            pipe = Weapon(
                "Pipe",
                "A metal pipe that can be used as a weapon.",
                damage=15,
                durability=10,
                value=15
            )
            self.player.add_item(pipe)
            
            # Add a tech item
            smoke_bomb = TechItem(
                "Smoke Bomb",
                "A device that creates a smoke screen for stealth.",
                effect_type="smoke",
                duration=3,
                value=30
            )
            self.player.add_item(smoke_bomb)
    
    def save_game(self, filename="savegame.json"):
        """Save the current game state to a file."""
        save_path = os.path.join(self.data_dir, filename)
        
        # Create save data
        save_data = {
            "player": self.player.to_dict(),
            "time_system": self.time_system.to_dict()
        }
        
        # Save to file
        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=4)
        
        print(f"Game saved to {save_path}")
    
    def load_game(self, filename="savegame.json"):
        """Load a game state from a file."""
        save_path = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(save_path):
            print(f"Save file {save_path} not found.")
            return False
        
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            # Load time system
            time_data = save_data.get("time_system", {})
            self.time_system = TimeSystem.from_dict(time_data)
            
            # Load player
            player_data = save_data.get("player", {})
            self.player = Player.from_dict(
                player_data,
                self.area_manager.get_area,
                self.item_manager.get_item,
                self.object_manager.get_object
            )
            
            print(f"Game loaded from {save_path}")
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
    
    def update_game_time(self, minutes=1):
        """Update the game time and related systems."""
        self.time_system.advance_time(minutes)
        
        # Update all NPCs based on time
        self.npc_manager.update_all_npcs(self.time_system.get_time_key(), self)
        
        # Get behavior messages only for NPCs in the player's current area
        if self.player and self.player.current_area:
            current_area_npcs = [npc for npc in self.player.current_area.npcs]
            
            if current_area_npcs:
                # Get behavior messages for NPCs in the player's area
                area_behavior_message = self.npc_manager.get_area_npc_behaviors(
                    self.player.current_area, 
                    current_area_npcs,
                    self
                )
                
                # Display NPC behavior messages if any
                if area_behavior_message:
                    print("\nAround you:")
                    print(area_behavior_message)
        
        # Update player hunger
        self.player.hunger = min(self.player.max_hunger, self.player.hunger + minutes * 0.1)
        
        # Check if player is too hungry
        if self.player.hunger >= self.player.max_hunger:
            print("You're starving! You need to eat something.")
            self.player.energy = max(0, self.player.energy - minutes)
            
            # Check if player has no energy
            if self.player.energy <= 0:
                print("You collapsed from hunger and exhaustion!")
                # In a full implementation, this might trigger a game over or respawn
    
    def process_command(self, command):
        """Process a player command."""
        parts = command.lower().split()
        if not parts:
            return
        
        action = parts[0]
        
        # Movement commands
        if action in ["north", "south", "east", "west", "forward", "backward", "right", "left"]:
            self.player.move(action)
        
        # Look command
        elif action == "look":
            self.player.look_around()
        
        # Inventory command
        elif action in ["inventory", "inv"]:
            self.show_inventory()
        
        # Pick up command
        elif action in ["pickup", "take", "get", "grab"]:
            if len(parts) > 1:
                item_name = " ".join(parts[1:])
                self.player.pick_up(item_name)
            else:
                print("What do you want to pick up?")
        
        # Drop command
        elif action == "drop":
            if len(parts) > 1:
                item_name = " ".join(parts[1:])
                self.player.drop(item_name)
            else:
                print("What do you want to drop?")
        
        # Use command
        elif action == "use":
            if len(parts) > 1:
                item_name = " ".join(parts[1:])
                self.player.use(item_name)
            else:
                print("What do you want to use?")
        
        # Eat command
        elif action == "eat":
            if len(parts) > 1:
                item_name = " ".join(parts[1:])
                self.player.eat(item_name)
            else:
                print("What do you want to eat?")
        
        # Talk command
        elif action == "talk":
            if len(parts) > 1:
                npc_name = " ".join(parts[1:])
                # Find the NPC
                npc = next((n for n in self.player.current_area.npcs if n.name.lower() == npc_name.lower()), None)
                self.player.talk_to(npc_name)
                
                # Trigger NPC reactions to the conversation
                if npc:
                    self.player._trigger_npc_reactions(self, "talk", npc)
            else:
                print("Who do you want to talk to?")
        
        # Interact command
        elif action == "interact":
            if len(parts) > 1:
                object_name = " ".join(parts[1:])
                self.player.interact_with(object_name)
            else:
                print("What do you want to interact with?")
        
        # Hide command
        elif action == "hide":
            if len(parts) > 1:
                hiding_spot = " ".join(parts[1:])
                self.player.hide(hiding_spot)
            else:
                print("Where do you want to hide?")
        
        # Unhide command
        elif action in ["unhide", "emerge"]:
            self.player.unhide()
        
        # Hack command
        elif action == "hack":
            if len(parts) > 1:
                target = " ".join(parts[1:])
                self.player.hack(target)
            else:
                print("What do you want to hack?")
        
        # Attack command
        elif action == "attack":
            if len(parts) > 1:
                target = " ".join(parts[1:])
                self.player.attack(target, self)  # Pass the game_manager instance
            else:
                print("What do you want to attack?")
        
        # Plant command
        elif action == "plant":
            if len(parts) >= 4 and parts[2] == "in":
                seed_name = parts[1]
                plot_name = " ".join(parts[3:])
                self.player.plant(seed_name, plot_name)
            else:
                print("Usage: plant [seed] in [soil plot]")
        
        # Water command
        elif action == "water":
            if len(parts) > 1:
                plot_name = " ".join(parts[1:])
                self.player.water(plot_name)
            else:
                print("What do you want to water?")
        
        # Harvest command
        elif action == "harvest":
            if len(parts) > 1:
                plot_name = " ".join(parts[1:])
                self.player.harvest(plot_name)
            else:
                print("What do you want to harvest?")
        
        # Time commands
        elif action == "time":
            print(f"Current time: {self.time_system.get_time_string()}")
            print(f"Time of day: {self.time_system.get_time_of_day()}")
            
        # Advance time command
        elif action in ["advance_time", "wait", "skip"]:
            if len(parts) > 1:
                try:
                    minutes = int(parts[1])
                    if minutes > 0:
                        print(f"Advancing time by {minutes} minutes...")
                        self.update_game_time(minutes)
                        print(f"Current time: {self.time_system.get_time_string()}")
                        self.player.look_around()  # Show updated environment
                    else:
                        print("Please specify a positive number of minutes.")
                except ValueError:
                    print("Please specify a valid number of minutes.")
            else:
                print("Usage: advance_time [minutes]")
                print("Example: advance_time 60 (advances time by 1 hour)")
        
        # Position/coordinates command
        elif action in ["position", "pos", "coordinates", "coords", "where"]:
            # If no arguments, show player's position
            if len(parts) == 1:
                if self.player.current_area:
                    grid_x, grid_y, grid_z = self.player.get_grid_position()
                    print(f"You are in: {self.player.current_area.name}")
                    print(f"Grid coordinates: ({grid_x}, {grid_y})")
                    print(f"Area dimensions: {self.player.current_area.grid_width}x{self.player.current_area.grid_length}")
                else:
                    print("You're not in any area.")
            # If arguments, find the coordinates of the specified entity
            else:
                entity_name = " ".join(parts[1:]).lower()
                self.find_entity_coordinates(entity_name)
        
        # Teleport command
        elif action in ["teleport", "tp"]:
            if len(parts) > 1:
                # Parse the command to extract area name and/or coordinates
                area = None
                grid_x = None
                grid_y = None
                
                # Check for coordinates in the format "x,y" or "x y"
                coord_parts = []
                area_name_parts = []
                
                for part in parts[1:]:
                    # Check if part is a coordinate pair (x,y)
                    if "," in part:
                        try:
                            x, y = map(int, part.split(","))
                            grid_x, grid_y = x, y
                            continue  # Skip this part in further processing
                        except ValueError:
                            pass  # Not valid coordinates, treat as part of area name
                    
                    # Check if part is a number (potential coordinate)
                    if part.isdigit():
                        coord_parts.append(int(part))
                        continue  # Skip this part in further processing
                    
                    # If we get here, it's part of the area name
                    area_name_parts.append(part)
                
                # Process coordinates if found as separate numbers
                if len(coord_parts) >= 2:
                    grid_x, grid_y = coord_parts[0], coord_parts[1]
                
                # Process area name if found
                if area_name_parts:
                    area_name = " ".join(area_name_parts)
                    area = next((a for a in self.area_manager.areas.values() 
                                if a.name.lower() == area_name.lower()), None)
                    if not area:
                        print(f"Area '{area_name}' not found.")
                        return
                
                # If only coordinates were specified (no area name), use current area
                if area is None and (grid_x is not None or grid_y is not None):
                    area = self.player.current_area
                
                # Teleport the player
                self.player.teleport(area, grid_x, grid_y)
            else:
                print("Usage: teleport [area name] [x,y]")
                print("Examples:")
                print("  teleport Home")
                print("  teleport 3,4")
                print("  teleport Home 3,4")
                print("  teleport Home 3 4")
        
        # Areas command (for debugging)
        elif action == "areas":
            print("Available areas:")
            for area in self.area_manager.areas.values():
                print(f"- {area.name}")
        
        # NPCs command (for debugging)
        elif action == "npcs":
            if self.player.current_area and self.player.current_area.npcs:
                print("NPCs in this area:")
                for npc in self.player.current_area.npcs:
                    print(f"- {npc.name}: {npc.description}")
            else:
                print("No NPCs in this area.")
        
        # Save and load commands
        elif action == "save":
            if len(parts) > 1:
                filename = parts[1] + ".json"
                self.save_game(filename)
            else:
                self.save_game()
        
        elif action == "load":
            if len(parts) > 1:
                filename = parts[1] + ".json"
                self.load_game(filename)
            else:
                self.load_game()
        
        # Help command
        elif action == "help":
            self.show_help()
        
        # Quit command
        elif action in ["quit", "exit"]:
            self.running = False
        
        # Unknown command
        else:
            print(f"Unknown command: {command}")
    
    def show_inventory(self):
        """Show the player's inventory."""
        if not self.player.inventory:
            print("Your inventory is empty.")
            return
        
        print("\nInventory:")
        for i, item in enumerate(self.player.inventory, 1):
            print(f"{i}. {item.name}: {item.description}")
        
        print(f"\nMoney: ${self.player.money}")
        print(f"Energy: {self.player.energy}/{self.player.max_energy}")
        print(f"Hunger: {self.player.hunger}/{self.player.max_hunger}")
        print(f"Street Cred: {self.player.street_cred}")
        print(f"Hacking Level: {self.player.hacking_level}")
        print(f"Stealth Level: {self.player.stealth_level}")
        print(f"Combat Level: {self.player.combat_level}")
    
    def find_entity_coordinates(self, entity_name):
        """Find the coordinates of an entity (NPC, item, or object) by name."""
        found_entities = []
        entity_name = entity_name.lower()
        
        # Search for NPCs in areas
        for area in self.area_manager.areas.values():
            for npc in area.npcs:
                if entity_name in npc.name.lower():
                    # Get relative coordinates within the area
                    rel_x, rel_y, rel_z = area.get_relative_coordinates(npc.coordinates)
                    found_entities.append({
                        "type": "NPC",
                        "name": npc.name,
                        "area": area.name,
                        "rel_coords": (rel_x, rel_y, rel_z),
                        "global_coords": (npc.coordinates.x, npc.coordinates.y, npc.coordinates.z),
                        "activity": npc.current_activity
                    })
        
        # Also search for NPCs in the NPC manager (in case they're not in an area yet)
        for npc_id, npc in self.npc_manager.npcs.items():
            if entity_name in npc.name.lower():
                # Check if this NPC is already in our results (from an area)
                if not any(e["type"] == "NPC" and e["name"] == npc.name for e in found_entities):
                    # NPC not in an area, add with unknown location
                    found_entities.append({
                        "type": "NPC",
                        "name": npc.name,
                        "area": "Unknown (not in any area)",
                        "rel_coords": "Unknown",
                        "global_coords": (npc.coordinates.x, npc.coordinates.y, npc.coordinates.z) if hasattr(npc, 'coordinates') else "Unknown",
                        "activity": npc.current_activity
                    })
        
        # Search for items
        for area in self.area_manager.areas.values():
            for item in area.items:
                if entity_name in item.name.lower():
                    # Get relative coordinates within the area
                    rel_x, rel_y, rel_z = area.get_relative_coordinates(item.coordinates)
                    found_entities.append({
                        "type": "Item",
                        "name": item.name,
                        "area": area.name,
                        "rel_coords": (rel_x, rel_y, rel_z),
                        "global_coords": (item.coordinates.x, item.coordinates.y, item.coordinates.z)
                    })
        
        # Search for objects
        for area in self.area_manager.areas.values():
            for obj in area.objects:
                if entity_name in obj.name.lower():
                    # Get relative coordinates within the area
                    rel_x, rel_y, rel_z = area.get_relative_coordinates(obj.coordinates)
                    found_entities.append({
                        "type": "Object",
                        "name": obj.name,
                        "area": area.name,
                        "rel_coords": (rel_x, rel_y, rel_z),
                        "global_coords": (obj.coordinates.x, obj.coordinates.y, obj.coordinates.z)
                    })
        
        # Display results
        if found_entities:
            # If there's an exact match, prioritize it
            exact_matches = [e for e in found_entities if e["name"].lower() == entity_name]
            if exact_matches:
                found_entities = exact_matches
            
            # If we have multiple matches, show all of them
            if len(found_entities) > 1:
                print(f"Found {len(found_entities)} entities matching '{entity_name}':")
                for i, entity in enumerate(found_entities, 1):
                    print(f"{i}. {entity['type']} '{entity['name']}' in {entity['area']}")
                    if entity['rel_coords'] != "Unknown":
                        print(f"   Area coordinates: {entity['rel_coords']}")
                    if entity['type'] == 'NPC':
                        print(f"   Current activity: {entity['activity']}")
            else:
                # Just one match, show detailed info
                entity = found_entities[0]
                print(f"Found {entity['type']} '{entity['name']}' in {entity['area']}")
                if entity['rel_coords'] != "Unknown":
                    print(f"Area coordinates: {entity['rel_coords']}")
                if entity['global_coords'] != "Unknown":
                    print(f"Global coordinates: {entity['global_coords']}")
                if entity['type'] == 'NPC':
                    print(f"Current activity: {entity['activity']}")
        else:
            print(f"Could not find any entity matching '{entity_name}' in the game world.")
    
    def show_help(self):
        """Show help information for the game."""
        print("\n=== Root Access v3 Help ===")
        print("\nMovement Commands:")
        print("  north, south, east, west - Move in a direction")
        print("  forward, backward, right, left - Alternative movement commands")
        
        print("\nLocation Commands:")
        print("  look - Look around your current location")
        print("  position, coords, where - Show your current position and coordinates")
        print("  where [name], coordinates [name] - Find the coordinates of an NPC, item, or object")
        print("    Examples: 'where Flop', 'where gun', 'coordinates Flop'")
        print("    Note: Partial matches work too, like 'where blood' to find Bloodhound gang members")
        print("  teleport [area] [x,y] - Teleport to an area and/or coordinates")
        print("    Examples: 'teleport Home', 'teleport 3,4', 'teleport Home 3,4'")
        print("  areas - List all available areas")
        
        print("\nInventory Commands:")
        print("  inventory, inv - Show your inventory")
        print("  pickup, take, get, grab [item] - Pick up an item")
        print("  drop [item] - Drop an item")
        print("  use [item] - Use an item")
        print("  eat [item] - Eat a consumable item")
        
        print("\nInteraction Commands:")
        print("  talk [npc] - Talk to an NPC")
        print("  interact [object] - Interact with an object")
        print("  hide [spot] - Hide in a hiding spot")
        print("  unhide, emerge - Come out of hiding")
        print("  hack [target] - Hack a target")
        print("  attack [target] - Attack a target")
        
        print("\nFarming Commands:")
        print("  plant [seed] in [soil plot] - Plant a seed in a soil plot")
        print("  water [plot] - Water a soil plot")
        print("  harvest [plot] - Harvest a mature plant")
        
        print("\nSystem Commands:")
        print("  time - Show the current game time")
        print("  advance_time, wait, skip [minutes] - Advance time by specified minutes")
        print("  save [filename] - Save the game")
        print("  load [filename] - Load a saved game")
        print("  help - Show this help information")
        print("  quit, exit - Exit the game")
        
        print("\n=== End of Help ===\n")
    
    def run(self):
        """Run the game loop."""
        print("Welcome to Root Access v3!")
        print("Type 'help' for a list of commands.")
        
        while self.running:
            command = input("\n> ")
            self.process_command(command)
            
            # Update game time after each command
            self.update_game_time(1)
        
        print("Thanks for playing Root Access v3!")