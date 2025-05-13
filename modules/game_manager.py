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
        # Create home area
        home = Area(
            "Home",
            "Your secret base of operations. It's small but functional.",
            Coordinates(0, 0, 0),
            grid_width=5,
            grid_length=5
        )
        self.area_manager.add_area(home)
        
        # Create garden area
        garden = Area(
            "Garden",
            "A small garden area with fertile soil.",
            Coordinates(0, 5, 0),
            grid_width=8,
            grid_length=8,
            weather="sunny"
        )
        self.area_manager.add_area(garden)
        
        # Create street area
        street = Area(
            "Street",
            "A busy street with various shops and people.",
            Coordinates(8, 5, 0),
            grid_width=15,
            grid_length=5
        )
        self.area_manager.add_area(street)
        
        # Create alley area
        alley = Area(
            "Alley",
            "A dark alley between buildings.",
            Coordinates(23, 5, 0),
            grid_width=10,
            grid_length=3,
            weather="foggy"
        )
        self.area_manager.add_area(alley)
        
        # Create plaza area
        plaza = Area(
            "Plaza",
            "A large open plaza with a fountain in the center.",
            Coordinates(8, 10, 0),
            grid_width=12,
            grid_length=12,
            weather="sunny"
        )
        self.area_manager.add_area(plaza)
        
        # Create warehouse area
        warehouse = Area(
            "Warehouse",
            "An abandoned warehouse, taken over by the Bloodhounds.",
            Coordinates(8, -5, 0),
            grid_width=15,
            grid_length=15,
            weather="dusty"
        )
        self.area_manager.add_area(warehouse)
        
        # Create construction site area
        construction_site = Area(
            "Construction Site",
            "A construction site with various equipment and materials.",
            Coordinates(20, 10, 0),
            grid_width=20,
            grid_length=10
        )
        self.area_manager.add_area(construction_site)
        
        # Create office building
        office_building = Building(
            "Office Building",
            "A tall office building with multiple floors.",
            Coordinates(0, 15, 0),
            num_floors=5,
            grid_width=10,
            grid_length=10
        )
        self.area_manager.add_area(office_building)
        
        # Create floors for the office building
        for floor in range(1, 6):
            floor_area = Area(
                f"Office Floor {floor}",
                f"Floor {floor} of the office building.",
                Coordinates(0, 15, floor - 1),
                grid_width=10,
                grid_length=10,
                weather="controlled"
            )
            self.area_manager.add_area(floor_area)
            office_building.add_floor(floor, floor_area)
        
        # Connect areas
        self.area_manager.connect_areas(home.id, "north", garden.id)
        self.area_manager.connect_areas(garden.id, "east", street.id)
        self.area_manager.connect_areas(street.id, "east", alley.id)
        self.area_manager.connect_areas(street.id, "north", plaza.id)
        self.area_manager.connect_areas(street.id, "south", warehouse.id)
        self.area_manager.connect_areas(plaza.id, "east", construction_site.id)
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
        # Create gangs
        bloodhounds = self.npc_manager.create_gang("Bloodhounds")
        crimson_vipers = self.npc_manager.create_gang("Crimson Vipers")
        
        # Create civilian NPCs
        civilian_names = ["Ben", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Hannah", "Ian", "Julia"]
        for i, name in enumerate(civilian_names[:5]):
            civilian = Civilian(
                name,
                f"A civilian named {name}.",
                personality={
                    "friendliness": 50 + i * 5,
                    "curiosity": 40 + i * 5
                },
                money=50 + i * 10
            )
            self.npc_manager.add_npc(civilian)
            
            # Add some items to civilians
            if i % 2 == 0:  # Every other civilian gets a watering can
                watering_can = WateringCan()
                civilian.add_to_inventory(watering_can)
            
            if i % 3 == 0:  # Every third civilian gets a seed
                seed = Seed(
                    "Carrot Seed",
                    "A seed for growing carrots.",
                    plant_type="carrot",
                    growth_time=3,
                    value=5
                )
                civilian.add_to_inventory(seed)
        
        # Create Bloodhound gang members
        bloodhound_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop"]
        for i, name in enumerate(bloodhound_names):
            gang_member = GangMember(
                name,
                f"A member of the Bloodhounds named {name}.",
                "Bloodhounds",
                personality={
                    "aggression": 70,
                    "loyalty": 80
                },
                money=100
            )
            self.npc_manager.add_npc(gang_member)
            bloodhounds.add_member(gang_member)
            
            # Add weapons to gang members
            gun = Weapon(
                "Gun",
                "A standard firearm.",
                damage=50,
                durability=20,
                value=50
            )
            gang_member.add_to_inventory(gun)
        
        # Create Crimson Viper gang members
        viper_names = ["Vipoop", "Snakle", "Rattlesnop", "Pythirt", "Anaceaky"]
        for i, name in enumerate(viper_names):
            gang_member = GangMember(
                name,
                f"A member of the Crimson Vipers named {name}.",
                "Crimson Vipers",
                personality={
                    "aggression": 60,
                    "cunning": 70
                },
                money=100
            )
            self.npc_manager.add_npc(gang_member)
            crimson_vipers.add_member(gang_member)
            
            # Add weapons to gang members
            pipe = Weapon(
                "Pipe",
                "A metal pipe that can be used as a weapon.",
                damage=15,
                durability=10,
                value=15
            )
            gang_member.add_to_inventory(pipe)
        
        # Create a shopkeeper
        shopkeeper = Civilian(
            "Shopkeeper",
            "A friendly shopkeeper selling various goods.",
            dialogue={
                "default": "Welcome to my shop! Feel free to browse around.",
                "friendly": "Ah, my favorite customer! What can I get for you today?"
            },
            personality={
                "friendliness": 60,
                "greed": 40
            },
            money=500
        )
        self.npc_manager.add_npc(shopkeeper)
        
        # Place NPCs in areas
        garden = self.area_manager.get_area("garden")
        if garden:
            for i, name in enumerate(civilian_names[:3]):
                civilian = next((npc for npc in self.npc_manager.npcs.values() if npc.name == name), None)
                if civilian:
                    garden.place_object_at(civilian, 2 + i, 2)
        
        street = self.area_manager.get_area("street")
        if street:
            shopkeeper = next((npc for npc in self.npc_manager.npcs.values() if npc.name == "Shopkeeper"), None)
            if shopkeeper:
                street.place_object_at(shopkeeper, 7, 2)
            
            for i, name in enumerate(civilian_names[3:5]):
                civilian = next((npc for npc in self.npc_manager.npcs.values() if npc.name == name), None)
                if civilian:
                    street.place_object_at(civilian, 10 + i, 2)
        
        warehouse = self.area_manager.get_area("warehouse")
        if warehouse:
            for i, name in enumerate(bloodhound_names):
                gang_member = next((npc for npc in self.npc_manager.npcs.values() if npc.name == name), None)
                if gang_member:
                    warehouse.place_object_at(gang_member, 3 + i * 2, 3 + i)
            
            # Claim warehouse as Bloodhounds territory
            bloodhounds.claim_territory(warehouse)
        
        construction_site = self.area_manager.get_area("construction_site")
        if construction_site:
            for i, name in enumerate(viper_names):
                gang_member = next((npc for npc in self.npc_manager.npcs.values() if npc.name == name), None)
                if gang_member:
                    construction_site.place_object_at(gang_member, 5 + i * 2, 5)
            
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
        
        # Update NPCs based on time
        self.npc_manager.update_all_npcs(self.time_system.get_time_key())
        
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
                self.player.talk_to(npc_name)
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
                self.player.attack(target)
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
        
        # Teleport command (for debugging)
        elif action in ["teleport", "tp"]:
            if len(parts) > 1:
                area_name = " ".join(parts[1:])
                area = next((a for a in self.area_manager.areas.values() if a.name.lower() == area_name.lower()), None)
                if area:
                    self.player.set_current_area(area, area.grid_width // 2, area.grid_length // 2)
                else:
                    print(f"Area '{area_name}' not found.")
            else:
                print("Usage: teleport [area name]")
        
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
    
    def show_help(self):
        """Show help information."""
        print("\nRoot Access v3 Help:")
        print("Movement: north, south, east, west, forward, backward, right, left")
        print("Look around: look")
        print("Inventory: inventory, inv")
        print("Pick up item: pickup/take/get/grab [item]")
        print("Drop item: drop [item]")
        print("Use item: use [item]")
        print("Eat item: eat [item]")
        print("Talk to NPC: talk [npc]")
        print("Interact with object: interact [object]")
        print("Hide: hide [hiding spot]")
        print("Unhide: unhide, emerge")
        print("Hack: hack [target]")
        print("Attack: attack [target]")
        print("Plant: plant [seed] in [soil plot]")
        print("Water: water [soil plot]")
        print("Harvest: harvest [soil plot]")
        print("Check time: time")
        print("Save/Load: save [filename], load [filename]")
        print("Help: help")
        print("Quit: quit, exit")
    
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