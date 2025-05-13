"""
Game Objects module for Root Access v3.
Handles interactive objects in the game world.
"""

import json
import random
from .coordinates import Coordinates
from .items import Plant

class GameObject:
    """Base class for all game objects."""
    def __init__(self, name, description, coordinates=None, properties=None):
        self.name = name
        self.description = description
        self.coordinates = coordinates if coordinates else Coordinates(0, 0, 0)
        self.properties = properties or {}
        self.pickupable = False
        self.id = f"object_{name.lower().replace(' ', '_')}"
    
    def __str__(self):
        return f"{self.name}: {self.description}"
    
    def interact(self, player):
        """Base interaction method."""
        print(f"You interact with the {self.name}.")
    
    def set_property(self, key, value):
        """Set a property for this object."""
        self.properties[key] = value
    
    def get_property(self, key, default=None):
        """Get a property for this object."""
        return self.properties.get(key, default)
    
    def to_dict(self):
        """Convert object to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "coordinates": self.coordinates.to_dict(),
            "properties": self.properties,
            "type": self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create object from dictionary."""
        obj = cls(
            data["name"],
            data["description"],
            Coordinates.from_dict(data["coordinates"]),
            data["properties"]
        )
        obj.id = data.get("id", obj.id)
        return obj


class Transport(GameObject):
    """Base class for transportation objects."""
    def __init__(self, name, description, coordinates=None, properties=None):
        super().__init__(name, description, coordinates, properties)
    
    def transport(self, player, destination):
        """Transport the player to a destination."""
        print(f"You use the {self.name} to travel to {destination.name}.")
        player.set_current_area(destination)


class Elevator(Transport):
    """An elevator that can transport players between floors."""
    def __init__(self, name, description, coordinates=None, properties=None):
        super().__init__(name, description, coordinates, properties)
        self.floors = {}  # Dictionary mapping floor numbers to (area, x, y) tuples
    
    def add_floor(self, floor_number, area, x, y):
        """Add a floor to the elevator."""
        self.floors[floor_number] = (area, x, y)
    
    def interact(self, player):
        """Interact with the elevator."""
        print(f"You enter the {self.name}.")
        self.show_floor_options(player)
    
    def show_floor_options(self, player):
        """Show available floor options."""
        if not self.floors:
            print("This elevator doesn't seem to go anywhere.")
            return
        
        print("\nAvailable floors:")
        for floor_num in sorted(self.floors.keys()):
            area, _, _ = self.floors[floor_num]
            print(f"{floor_num}. {area.name}")
        
        choice = input("Which floor would you like to go to? ")
        
        try:
            floor_num = int(choice)
            if floor_num in self.floors:
                area, x, y = self.floors[floor_num]
                print(f"The elevator moves to floor {floor_num}.")
                player.set_current_area(area, x, y)
            else:
                print("Invalid floor number.")
        except ValueError:
            print("Please enter a number.")
    
    def to_dict(self):
        """Convert elevator to dictionary for serialization."""
        data = super().to_dict()
        data["floors"] = {k: (v[0].id, v[1], v[2]) for k, v in self.floors.items()}
        return data
    
    @classmethod
    def from_dict(cls, data, area_resolver=None):
        """Create elevator from dictionary."""
        elevator = super().from_dict(data)
        
        # Resolve floors if area_resolver is provided
        if area_resolver and "floors" in data:
            for floor_num, (area_id, x, y) in data["floors"].items():
                area = area_resolver(area_id)
                if area:
                    elevator.floors[int(floor_num)] = (area, x, y)
        
        return elevator


class Vehicle(Transport):
    """A vehicle that can be driven around."""
    def __init__(self, name, description, speed=1, fuel=100, max_fuel=100, coordinates=None, properties=None):
        super().__init__(name, description, coordinates, properties)
        self.speed = speed
        self.fuel = fuel
        self.max_fuel = max_fuel
    
    def interact(self, player):
        """Interact with the vehicle."""
        if player.current_vehicle == self:
            print(f"You exit the {self.name}.")
            player.current_vehicle = None
        else:
            print(f"You enter the {self.name}.")
            player.current_vehicle = self
    
    def drive(self, player, direction, distance=1):
        """Drive the vehicle in a direction."""
        if self.fuel <= 0:
            print(f"The {self.name} is out of fuel.")
            return False
        
        # Calculate fuel consumption
        fuel_used = distance / self.speed
        if fuel_used > self.fuel:
            print(f"The {self.name} doesn't have enough fuel to go that far.")
            return False
        
        # Consume fuel
        self.fuel -= fuel_used
        
        # Move the player (and vehicle)
        result = player.move(direction, distance * self.speed)
        
        # Update vehicle coordinates to match player
        if result:
            self.coordinates = Coordinates(player.coordinates.x, player.coordinates.y, player.coordinates.z)
            print(f"Fuel remaining: {self.fuel:.1f}/{self.max_fuel}")
        
        return result
    
    def refuel(self, amount=None):
        """Refuel the vehicle."""
        if amount:
            self.fuel = min(self.max_fuel, self.fuel + amount)
        else:
            self.fuel = self.max_fuel
        print(f"The {self.name} has been refueled. Fuel: {self.fuel}/{self.max_fuel}")
    
    def to_dict(self):
        """Convert vehicle to dictionary for serialization."""
        data = super().to_dict()
        data["speed"] = self.speed
        data["fuel"] = self.fuel
        data["max_fuel"] = self.max_fuel
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create vehicle from dictionary."""
        vehicle = cls(
            data["name"],
            data["description"],
            data["speed"],
            data["fuel"],
            data["max_fuel"],
            Coordinates.from_dict(data["coordinates"]),
            data["properties"]
        )
        vehicle.id = data.get("id", vehicle.id)
        return vehicle


class Door(Transport):
    """A door that connects two areas."""
    def __init__(self, name, description, coordinates=None, properties=None):
        super().__init__(name, description, coordinates, properties)
        self.destination = None  # (area, x, y) tuple
        self.locked = False
        self.key_id = None
    
    def set_destination(self, area, x, y):
        """Set the destination for this door."""
        self.destination = (area, x, y)
    
    def lock(self, key_id=None):
        """Lock the door, optionally requiring a specific key."""
        self.locked = True
        self.key_id = key_id
        print(f"The {self.name} is now locked.")
    
    def unlock(self, key=None):
        """Unlock the door, checking if the key matches."""
        if not self.locked:
            print(f"The {self.name} is already unlocked.")
            return True
        
        if self.key_id and (not key or key.id != self.key_id):
            print(f"You need the correct key to unlock this door.")
            return False
        
        self.locked = False
        print(f"The {self.name} is now unlocked.")
        return True
    
    def interact(self, player):
        """Interact with the door."""
        if not self.destination:
            print(f"The {self.name} doesn't seem to lead anywhere.")
            return
        
        if self.locked:
            print(f"The {self.name} is locked.")
            
            # Check if player has the key
            if self.key_id:
                key = next((item for item in player.inventory if item.id == self.key_id), None)
                if key:
                    print(f"You use the {key.name} to unlock the door.")
                    self.unlock(key)
                else:
                    print("You need a key to unlock this door.")
            return
        
        area, x, y = self.destination
        print(f"You go through the {self.name}.")
        player.set_current_area(area, x, y)
    
    def to_dict(self):
        """Convert door to dictionary for serialization."""
        data = super().to_dict()
        data["locked"] = self.locked
        data["key_id"] = self.key_id
        if self.destination:
            data["destination"] = (self.destination[0].id, self.destination[1], self.destination[2])
        return data
    
    @classmethod
    def from_dict(cls, data, area_resolver=None):
        """Create door from dictionary."""
        door = super().from_dict(data)
        door.locked = data.get("locked", False)
        door.key_id = data.get("key_id")
        
        # Resolve destination if area_resolver is provided
        if area_resolver and "destination" in data:
            area_id, x, y = data["destination"]
            area = area_resolver(area_id)
            if area:
                door.destination = (area, x, y)
        
        return door


class Computer(GameObject):
    """A computer that can be used for hacking."""
    def __init__(self, name, description, coordinates=None, properties=None, programs=None):
        super().__init__(name, description, coordinates, properties)
        self.programs = programs or []
        self.hacked = False
    
    def interact(self, player):
        """Interact with the computer."""
        print(f"You sit down at the {self.name}.")
        if not self.hacked and player.hacking_level < 2:
            print("This computer is locked. You need to hack it first.")
            return
        
        self.show_programs(player)
    
    def show_programs(self, player):
        """Show available programs on the computer."""
        if not self.programs:
            print("This computer doesn't have any programs installed.")
            return
        
        print("\nAvailable programs:")
        for i, program in enumerate(self.programs, 1):
            print(f"{i}. {program}")
        
        choice = input("Which program would you like to run? ")
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.programs):
                program = self.programs[index]
                self.run_program(program, player)
            else:
                print("Invalid program number.")
        except ValueError:
            print("Please enter a number.")
    
    def run_program(self, program, player):
        """Run a program on the computer."""
        if program == "data_miner":
            print("Running Data Miner...")
            print("Scanning for valuable data...")
            # In a full implementation, this would generate random data or secrets
            money_found = random.randint(10, 50)
            player.money += money_found
            print(f"You found ${money_found} worth of cryptocurrency!")
            
        elif program == "security_override":
            print("Running Security Override...")
            print("Attempting to bypass security systems...")
            # In a full implementation, this would affect area security levels
            success = random.random() < 0.7  # 70% success rate
            if success:
                print("Security systems bypassed successfully!")
                player.current_area.set_property("security_level", "bypassed")
            else:
                print("Security override failed. Security level increased!")
                player.current_area.set_property("security_level", "heightened")
            
        elif program == "plant_hacker":
            print("Running Plant Hacker...")
            print("This program can modify plant genetics remotely.")
            # Find nearby plants
            grid_x, grid_y, grid_z = player.get_grid_position()
            plants_found = []
            
            # Check all objects in the area for soil plots with plants
            for obj in player.current_area.objects:
                if obj.__class__.__name__ == "SoilPlot" and obj.has_plant:
                    # Get the relative position of the soil plot
                    obj_rel_x = obj.coordinates.x - player.current_area.coordinates.x
                    obj_rel_y = obj.coordinates.y - player.current_area.coordinates.y
                    
                    # Calculate distance to the plant
                    distance = ((grid_x - obj_rel_x) ** 2 + (grid_y - obj_rel_y) ** 2) ** 0.5
                    if distance <= 5:  # Can hack plants within 5 grid units
                        plants_found.append(obj)
            
            if not plants_found:
                print("No plants found within range.")
                return
            
            print("\nPlants within range:")
            for i, soil_plot in enumerate(plants_found, 1):
                print(f"{i}. {soil_plot.plant.name} (Growth: {soil_plot.plant.growth_stage}/{soil_plot.plant.max_growth})")
            
            choice = input("Which plant would you like to hack? ")
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(plants_found):
                    soil_plot = plants_found[index]
                    print(f"Hacking {soil_plot.plant.name}...")
                    
                    # Apply a random effect to the plant
                    effects = ["growth_boost", "yield_increase", "special_properties"]
                    effect = random.choice(effects)
                    
                    if effect == "growth_boost":
                        soil_plot.plant.growth_stage = min(soil_plot.plant.max_growth, soil_plot.plant.growth_stage + 2)
                        print(f"Growth accelerated! New stage: {soil_plot.plant.growth_stage}/{soil_plot.plant.max_growth}")
                        if soil_plot.plant.growth_stage == soil_plot.plant.max_growth:
                            soil_plot.plant.is_mature = True
                            print(f"The {soil_plot.plant.name} is now mature and ready to harvest!")
                    
                    elif effect == "yield_increase":
                        soil_plot.plant.value *= 1.5
                        print(f"Yield increased! New value: ${soil_plot.plant.value}")
                    
                    elif effect == "special_properties":
                        soil_plot.plant.set_property("hacked", True)
                        soil_plot.plant.set_property("special_effect", "hallucination")
                        print(f"Special properties added to the plant!")
                else:
                    print("Invalid plant number.")
            except ValueError:
                print("Please enter a number.")
        
        else:
            print(f"Unknown program: {program}")
    
    def hack(self, player):
        """Hack the computer."""
        if self.hacked:
            print(f"The {self.name} is already hacked.")
            return
        
        print(f"Attempting to hack the {self.name}...")
        
        # Calculate hack success chance based on player's hacking level
        success_chance = 30 + player.hacking_level * 10
        success_chance = min(90, success_chance)  # Cap at 90%
        
        if random.random() * 100 < success_chance:
            print("Hack successful!")
            self.hacked = True
            player.hacking_level += 0.1  # Small skill increase
            self.interact(player)
        else:
            print("Hack failed. Try again or improve your hacking skills.")
    
    def to_dict(self):
        """Convert computer to dictionary for serialization."""
        data = super().to_dict()
        data["programs"] = self.programs
        data["hacked"] = self.hacked
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create computer from dictionary."""
        computer = cls(
            data["name"],
            data["description"],
            Coordinates.from_dict(data["coordinates"]),
            data["properties"],
            data["programs"]
        )
        computer.hacked = data.get("hacked", False)
        computer.id = data.get("id", computer.id)
        return computer


class HidingSpot(GameObject):
    """A spot where the player can hide."""
    def __init__(self, name, description, stealth_bonus=0.5, coordinates=None, properties=None):
        super().__init__(name, description, coordinates, properties)
        self.stealth_bonus = stealth_bonus  # How much this spot improves stealth (0.0 to 1.0)
    
    def interact(self, player):
        """Interact with the hiding spot."""
        if player.is_hidden and player.current_hiding_spot == self:
            player.unhide()
        else:
            player.hide(self.name)
    
    def to_dict(self):
        """Convert hiding spot to dictionary for serialization."""
        data = super().to_dict()
        data["stealth_bonus"] = self.stealth_bonus
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create hiding spot from dictionary."""
        hiding_spot = cls(
            data["name"],
            data["description"],
            data["stealth_bonus"],
            Coordinates.from_dict(data["coordinates"]),
            data["properties"]
        )
        hiding_spot.id = data.get("id", hiding_spot.id)
        return hiding_spot


class VendingMachine(GameObject):
    """A vending machine that sells items."""
    def __init__(self, name, description="A vending machine selling various items.", coordinates=None, properties=None):
        super().__init__(name, description, coordinates, properties)
        self.items = []  # List of items for sale
        self.prices = {}  # Dictionary mapping item IDs to prices
    
    def add_item(self, item, price=None):
        """Add an item to the vending machine."""
        self.items.append(item)
        if price is None:
            price = item.value * 1.5  # Default markup
        self.prices[item.id] = price
    
    def interact(self, player):
        """Interact with the vending machine."""
        print(f"You approach the {self.name}.")
        self.show_items(player)
    
    def show_items(self, player):
        """Show items available in the vending machine."""
        if not self.items:
            print("This vending machine is empty.")
            return
        
        print("\nItems for sale:")
        for i, item in enumerate(self.items, 1):
            price = self.prices.get(item.id, item.value * 1.5)
            print(f"{i}. {item.name}: ${price}")
        
        choice = input("What would you like to buy? (or 'cancel') ")
        
        if choice.lower() == 'cancel':
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.items):
                item = self.items[index]
                price = self.prices.get(item.id, item.value * 1.5)
                
                if player.money >= price:
                    player.money -= price
                    self.items.remove(item)
                    player.add_item(item)
                    print(f"You bought {item.name} for ${price}.")
                else:
                    print(f"You don't have enough money. {item.name} costs ${price}.")
            else:
                print("Invalid item number.")
        except ValueError:
            print("Please enter a number.")
    
    def hack(self, player):
        """Hack the vending machine."""
        print(f"Attempting to hack the {self.name}...")
        
        # Calculate hack success chance based on player's hacking level
        success_chance = 20 + player.hacking_level * 10
        success_chance = min(80, success_chance)  # Cap at 80%
        
        if random.random() * 100 < success_chance:
            print("Hack successful!")
            
            # Choose a random effect
            effects = ["free_item", "price_reduction", "money_refund"]
            effect = random.choice(effects)
            
            if effect == "free_item" and self.items:
                item = random.choice(self.items)
                self.items.remove(item)
                player.add_item(item)
                print(f"You hacked the machine to dispense a free {item.name}!")
                
            elif effect == "price_reduction":
                for item_id in self.prices:
                    self.prices[item_id] *= 0.5
                print("You hacked the machine to reduce all prices by 50%!")
                self.show_items(player)
                
            elif effect == "money_refund":
                refund = random.randint(5, 20)
                player.money += refund
                print(f"You hacked the machine to refund ${refund}!")
                
            player.hacking_level += 0.1  # Small skill increase
        else:
            print("Hack failed. Try again or improve your hacking skills.")
    
    def to_dict(self):
        """Convert vending machine to dictionary for serialization."""
        data = super().to_dict()
        data["items"] = [item.id for item in self.items]
        data["prices"] = self.prices
        return data
    
    @classmethod
    def from_dict(cls, data, item_resolver=None):
        """Create vending machine from dictionary."""
        vending_machine = cls(
            data["name"],
            data["description"],
            Coordinates.from_dict(data["coordinates"]),
            data["properties"]
        )
        
        # Resolve items if item_resolver is provided
        if item_resolver and "items" in data:
            for item_id in data["items"]:
                item = item_resolver(item_id)
                if item:
                    vending_machine.items.append(item)
        
        vending_machine.prices = data.get("prices", {})
        vending_machine.id = data.get("id", vending_machine.id)
        return vending_machine


class SoilPlot(GameObject):
    """A plot of soil for planting seeds."""
    def __init__(self, name="Soil Plot", description="A plot of soil for planting seeds.", coordinates=None, properties=None):
        super().__init__(name, description, coordinates, properties)
        self.has_plant = False
        self.plant = None
    
    def interact(self, player):
        """Interact with the soil plot."""
        if not self.has_plant:
            print(f"This {self.name} is empty. You can plant a seed here.")
            
            # Check if player has seeds
            seeds = [item for item in player.inventory if item.__class__.__name__ == "Seed"]
            if seeds:
                print("\nAvailable seeds:")
                for i, seed in enumerate(seeds, 1):
                    print(f"{i}. {seed.name}")
                
                choice = input("Which seed would you like to plant? (or 'cancel') ")
                
                if choice.lower() == 'cancel':
                    return
                
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(seeds):
                        seed = seeds[index]
                        player.inventory.remove(seed)
                        self.plant(seed)
                        print(f"You plant the {seed.name} in the {self.name}.")
                    else:
                        print("Invalid seed number.")
                except ValueError:
                    print("Please enter a number.")
            else:
                print("You don't have any seeds to plant.")
        else:
            print(f"This {self.name} has a {self.plant.name} (Growth: {self.plant.growth_stage}/{self.plant.max_growth}).")
            
            if self.plant.is_mature:
                print("The plant is ready to harvest.")
                
                choice = input("Would you like to harvest it? (yes/no) ")
                
                if choice.lower() == 'yes':
                    harvested_item = self.harvest()
                    player.add_item(harvested_item)
                    print(f"You harvest the {harvested_item.name} from the {self.name}.")
            elif self.plant.needs_water:
                print("The plant needs water.")
                
                # Check if player has a watering can
                watering_can = next((item for item in player.inventory if item.__class__.__name__ == "WateringCan"), None)
                if watering_can and watering_can.uses > 0:
                    choice = input("Would you like to water it? (yes/no) ")
                    
                    if choice.lower() == 'yes':
                        watering_can.uses -= 1
                        self.water()
                        print(f"You water the {self.plant.name}.")
                        if watering_can.uses == 0:
                            print("Your watering can is empty. You need to refill it.")
                elif watering_can and watering_can.uses <= 0:
                    print("Your watering can is empty. You need to refill it.")
                else:
                    print("You don't have a watering can.")
    
    def plant(self, seed):
        """Plant a seed in the soil plot."""
        if self.has_plant:
            return False
        
        # Create a plant based on the seed
        plant_name = seed.plant_type.capitalize()
        self.plant = Plant(
            plant_name,
            f"A {seed.plant_type} plant.",
            seed.plant_type,
            0,  # Initial growth stage
            seed.growth_time,  # Max growth stage
            True,  # Needs water
            seed.value * 2  # Value is double the seed value
        )
        
        self.has_plant = True
        return True
    
    def water(self):
        """Water the plant in the soil plot."""
        if not self.has_plant:
            return False
        
        self.plant.needs_water = False
        
        # 50% chance to grow when watered
        if random.random() < 0.5:
            self.plant.grow()
        
        return True
    
    def harvest(self):
        """Harvest the plant from the soil plot."""
        if not self.has_plant or not self.plant.is_mature:
            return None
        
        harvested_plant = self.plant
        self.plant = None
        self.has_plant = False
        
        # Make the harvested plant pickupable
        harvested_plant.pickupable = True
        
        return harvested_plant
    
    def to_dict(self):
        """Convert soil plot to dictionary for serialization."""
        data = super().to_dict()
        data["has_plant"] = self.has_plant
        if self.has_plant:
            data["plant"] = self.plant.to_dict()
        return data
    
    @classmethod
    def from_dict(cls, data):
        """Create soil plot from dictionary."""
        soil_plot = cls(
            data["name"],
            data["description"],
            Coordinates.from_dict(data["coordinates"]),
            data["properties"]
        )
        soil_plot.has_plant = data.get("has_plant", False)
        
        if soil_plot.has_plant and "plant" in data:
            plant_data = data["plant"]
            soil_plot.plant = Plant(
                plant_data["name"],
                plant_data["description"],
                plant_data["plant_type"],
                plant_data["growth_stage"],
                plant_data["max_growth"],
                plant_data["needs_water"],
                plant_data["value"],
                Coordinates.from_dict(plant_data["coordinates"])
            )
            soil_plot.plant.is_mature = plant_data.get("is_mature", False)
        
        soil_plot.id = data.get("id", soil_plot.id)
        return soil_plot


class GameObjectManager:
    """Manages all game objects."""
    def __init__(self):
        self.objects = {}  # Dictionary mapping object IDs to GameObject objects
        self.templates = {}  # Dictionary of object templates
    
    def add_object(self, obj):
        """Add an object to the manager."""
        self.objects[obj.id] = obj
    
    def get_object(self, object_id):
        """Get an object by ID."""
        return self.objects.get(object_id)
    
    def create_from_template(self, template_id, **kwargs):
        """Create an object from a template."""
        if template_id not in self.templates:
            raise ValueError(f"Unknown object template: {template_id}")
        
        template = self.templates[template_id].copy()
        
        # Override template values with provided kwargs
        for key, value in kwargs.items():
            if key in template:
                template[key] = value
        
        # Create the appropriate object type
        object_type = template.get("type", "GameObject")
        
        if object_type == "Elevator":
            obj = Elevator(
                template["name"],
                template["description"],
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {})
            )
        elif object_type == "Vehicle":
            obj = Vehicle(
                template["name"],
                template["description"],
                template.get("speed", 1),
                template.get("fuel", 100),
                template.get("max_fuel", 100),
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {})
            )
        elif object_type == "Door":
            obj = Door(
                template["name"],
                template["description"],
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {})
            )
        elif object_type == "Computer":
            obj = Computer(
                template["name"],
                template["description"],
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {}),
                template.get("programs", [])
            )
        elif object_type == "HidingSpot":
            obj = HidingSpot(
                template["name"],
                template["description"],
                template.get("stealth_bonus", 0.5),
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {})
            )
        elif object_type == "VendingMachine":
            obj = VendingMachine(
                template["name"],
                template["description"],
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {})
            )
        elif object_type == "SoilPlot":
            obj = SoilPlot(
                template["name"],
                template["description"],
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {})
            )
        else:
            obj = GameObject(
                template["name"],
                template["description"],
                Coordinates(0, 0, 0),  # Will be set by caller
                template.get("properties", {})
            )
        
        # Generate a unique ID if needed
        if "id" in kwargs:
            obj.id = kwargs["id"]
        
        return obj
    
    def save_to_json(self, filename):
        """Save all objects to a JSON file."""
        data = {
            "objects": {obj_id: obj.to_dict() for obj_id, obj in self.objects.items()},
            "templates": self.templates
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_from_json(self, filename, area_resolver=None, item_resolver=None):
        """Load objects from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Load templates
        self.templates = data.get("templates", {})
        
        # Load objects
        for obj_id, obj_data in data.get("objects", {}).items():
            obj_type = obj_data.get("type", "GameObject")
            
            if obj_type == "Elevator":
                obj = Elevator.from_dict(obj_data, area_resolver)
            elif obj_type == "Vehicle":
                obj = Vehicle.from_dict(obj_data)
            elif obj_type == "Door":
                obj = Door.from_dict(obj_data, area_resolver)
            elif obj_type == "Computer":
                obj = Computer.from_dict(obj_data)
            elif obj_type == "HidingSpot":
                obj = HidingSpot.from_dict(obj_data)
            elif obj_type == "VendingMachine":
                obj = VendingMachine.from_dict(obj_data, item_resolver)
            elif obj_type == "SoilPlot":
                obj = SoilPlot.from_dict(obj_data)
            else:
                obj = GameObject.from_dict(obj_data)
            
            self.add_object(obj)