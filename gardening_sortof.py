class Item:
    def __init__(self, name, description, value=0):
        self.name = name
        self.description = description
        self.value = value

    def __str__(self):
        return self.name


class Weapon(Item):
    def __init__(self, name, description, value, damage):
        super().__init__(name, description, value)
        self.damage = damage

    def __str__(self):
        return f"{self.name} (Damage: {self.damage})"


class Consumable(Item):
    def __init__(self, name, description, value, health_restore):
        super().__init__(name, description, value)
        self.health_restore = health_restore

    def __str__(self):
        return f"{self.name} (Restores: {self.health_restore} health)"
    
class Intel(Item):
    def __init__(self,name,description, info_method, value):
        super().__init__(name,description,value)
        self.info_method = info_method # how the player gets the intel item's info
        self.info = None 

    def __str__(self):
        return f"{self.name} (Value: {self.value})"
        
        # info methods include "read" and "insert" for notes and USB sticks respectively.

class Seed(Item):
    def __init__(self, name, description, crop_type, value, growth_time=3):
        super().__init__(name, description, value)
        self.crop_type = crop_type
        self.growth_time = growth_time  # Number of turns until fully grown
    
    def __str__(self):
        return f"{self.name} ({self.crop_type})"

class Plant(Item):
    def __init__(self, name, description, crop_type, value, growth_stage=0, max_growth=3):
        super().__init__(name, description, value)
        self.crop_type = crop_type
        self.growth_stage = growth_stage
        self.max_growth = max_growth
        
    def grow(self):
        if self.growth_stage < self.max_growth:
            self.growth_stage += 1
            return True
        return False
    
    def is_harvestable(self):
        return self.growth_stage >= self.max_growth
    
    def __str__(self):
        stage_desc = "seedling" if self.growth_stage == 0 else \
                    "growing" if self.growth_stage < self.max_growth else \
                    "ready to harvest"
        return f"{self.name} ({stage_desc})"


class Object(): # this was initially a subclass of item, not sure if I want to keep it that way
        def __init__(self, name, description, portable=True, value=0):
            self.name = name
            self.description = description
            self.portable = portable
            self.value = value

class Soil(Object):
    def __init__(self, name, description, capacity=5):
        super().__init__(name, description, portable=False)
        self.plants = []
        self.capacity = capacity  # Maximum number of plants this soil can hold
    
    def add_plant(self, seed):
        """Convert a seed into a plant and add it to the soil."""
        if len(self.plants) >= self.capacity:
            return False, "This soil is already at full capacity."
        
        # Create a new plant from the seed
        plant_name = f"{seed.crop_type.capitalize()} Plant"
        plant_desc = f"A young {seed.crop_type} plant growing in the soil."
        new_plant = Plant(plant_name, plant_desc, seed.crop_type, seed.value * 2, 0, seed.growth_time)
        
        self.plants.append(new_plant)
        return True, f"You planted a {seed.crop_type} seed. It will take {seed.growth_time} turns to grow."
    
    def get_plant(self, plant_name):
        """Find a plant by name."""
        for plant in self.plants:
            if plant.name.lower() == plant_name.lower():
                return plant
        return None
    
    def remove_plant(self, plant):
        """Remove a plant from the soil."""
        if plant in self.plants:
            self.plants.remove(plant)
            return True
        return False
    
    def __str__(self):
        base_str = f"{self.name}"
        if self.plants:
            base_str += f" with {len(self.plants)} plants growing"
        return base_str



class Area:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.npcs = []
        self.objects = []
        self.exits = {}  # Dictionary to hold exits: direction -> Area

    def add_exit(self, direction, area):
        """Add an exit to another area in a given direction."""
        self.exits[direction] = area

    def get_exit(self, direction):
        """Get the area in the given direction."""
        return self.exits.get(direction, None)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, obj):
        if obj in self.objects: # using the word item in place of object because the word "object" is a keyword
            self.objects.remove(obj)
            return True
        return False

    def describe(self):
        desc = f"{self.name}\n{self.description}\n"
        if self.items:
            desc += "You see the following items:\n"
            for item in self.items:
                desc += f" - {item}\n"
        if self.npcs:
            desc += "You see the following people:\n"
            for npc in self.npcs:
                desc += f" - {npc}\n"
        if self.objects:
            desc += "There are some objects here:\n"
            for obj in self.objects:
                desc += f" - {obj.name}\n"
                # If it's soil, show the plants
                if isinstance(obj, Soil) and obj.plants:
                    desc += "   Plants in this soil:\n"
                    for plant in obj.plants:
                        desc += f"   * {plant}\n"
        return desc


class Player:
    def __init__(self, starting_area):
        self.current_area = starting_area
        self.inventory = []
        self.health = 100

    def move(self, direction):
        """Move the player to the area in the given direction if possible."""
        next_area = self.current_area.get_exit(direction)
        if next_area:
            self.current_area = next_area
            return f"You move {direction} to {self.current_area.name}."
        else:
            return "You can't go that way."

    def teleport(self, area):
        """Teleport the player to any area."""
        self.current_area = area
        return f"You teleport to {self.current_area.name}."

    def pick_up(self, item):
        if item in self.current_area.items:
            self.inventory.append(item)
            self.current_area.remove_item(item)
            return f"You picked up {item}."
        else:
            return "That item is not here."

    def drop(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            self.current_area.add_item(item)
            return f"You dropped {item}."
        else:
            return "You don't have that item."


class Game:
    def __init__(self):
        self.areas = {}
        self.items = {}  # Centralized item registry
        self.objects = {}  # Centralized object registry
        self.create_items()

        # Initialize areas here or load from data
        self.create_areas()
        self.create_objects()

        self.player = Player(self.areas.get('Home'))
        self.commands = {
            'move': {'handler': self.cmd_move, 'category': 'movement'},
            'go': {'handler': self.cmd_move, 'category': 'movement'},
            'teleport': {'handler': self.cmd_teleport, 'category': 'movement'},
            'tp': {'handler': self.cmd_teleport, 'category': 'movement'},
            'look': {'handler': self.cmd_look, 'category': 'system'},
            'inventory': {'handler': self.cmd_inventory, 'category': 'system'},
            'inv': {'handler': self.cmd_inventory, 'category': 'system'},
            'pickup': {'handler': self.cmd_pick_up, 'category': 'interaction'},
            'take': {'handler': self.cmd_pick_up, 'category': 'interaction'},
            'drop': {'handler': self.cmd_drop, 'category': 'interaction'},
            'quit': {'handler': self.cmd_quit, 'category': 'system'},
            'exit': {'handler': self.cmd_exit, 'category': 'system'},
            'help': {'handler': self.cmd_help, 'category': 'system'},
            'plant': {'handler': self.cmd_plant, 'category': 'interaction'},
            'harvest': {'handler': self.cmd_harvest, 'category': 'interaction'}
           
        }
        self.is_running = True

    def add_item_to_area(self, area_name, item_name):
        """Add an item to a specified area."""
        area = self.areas.get(area_name)
        item = self.items.get(item_name)
        if area and item:
            area.add_item(item)
            return f"Added {item.name} to {area.name}."
        return "Area or item not found."
    

    def add_object_to_area(self, area_name, object_name):
        """Add an object to a specified area."""
        area = self.areas.get(area_name)
        object = self.objects.get(object_name)
        if area and object:
            area.add_object(object)
            return f"Added {object.name} to {area.name}."
        return "Area or item not found."


    def create_items(self):
        """Dynamically create and register items."""

        # regular items
        shovel = Item("Shovel", "A shovel for digging.", 5)

        
        # weapons
        knife = Weapon("Knife","A sharp blade.", 10, 20)
        
        # Intel
        usb_stick = Intel("USB stick", "A USB stick with data on it.", "insert", 10)
        farm_note = Intel("Note", "An old, crumbled up piece of paper with some scribbled writing on it.", "read", 10) # not set up to use yet



        # Register items in the centralized item registry
        self.items["Shovel"] = shovel
        self.items["Knife"] = knife
        self.items["USB stick"] = usb_stick  # item.name is also a valid key
        self.items["Note"] = farm_note  # need to organize this better for multiple notes

        farm_note.info = lambda: "The note reads: Take the backroads. You'll find what you're looking for up north."


        carrot_seed = Seed("Carrot Seed", "A seed for planting carrots.", "carrot", 5)
        self.items["Carrot Seed"] = carrot_seed

    def create_objects(self):
        """Dynamically create and register objects."""


        test = Object("Test", "This is just a test object.")
        garden = Soil("Garden", "A garden full of plants.")
        
        # Register objects in the centralized object registry

        self.objects["Test"] = test
        self.objects["Garden"] = garden

        self.add_object_to_area('Home', 'Test')
        self.add_object_to_area('Home', 'Garden')



    def create_areas(self):
        """Create and connect areas in a scalable way."""
        Home = Area("Home", "You are at home.")
        Downtown = Area("Downtown", "A bustling city area.")
        Warehouse = Area("Warehouse", "An abandoned warehouse with construction containers lining the walls, stacked up to the ceiling, run by the Bloodhounds.")
        Backroads = Area("Backroads", "A foggy, long stretch of road leads to the unknown.")
        JacksFuel = Area("Jack's Fuel Station", "On the side of the road, a small fuel station with a sign that reads 'Jack's Fuel'.")
        Farm = Area("The Farm", "A seemingly abandoned farm taken over by the Bloodhounds.")

        # Connect areas
        Home.add_exit("north", Downtown)
        Home.add_exit("east", Warehouse)
        Downtown.add_exit("south", Home)
        Downtown.add_exit("east", Warehouse)
        Warehouse.add_exit("west", Downtown)
        Warehouse.add_exit("north", Backroads)
        Backroads.add_exit("North", Farm)
        Backroads.add_exit("west", JacksFuel)

        # Add areas to the dictionary
        self.areas['Home'] = Home
        self.areas['Downtown'] = Downtown
        self.areas['Warehouse'] = Warehouse
        self.areas['Backroads'] = Backroads
        self.areas['JacksFuel'] = JacksFuel
        self.areas['Farm'] = Farm

        # Add items to areas
        self.add_item_to_area('Home', 'Shovel')
        self.add_item_to_area('Downtown', 'Knife')
        self.add_item_to_area('Warehouse', 'USB stick')
        self.add_item_to_area('Warehouse', 'Note')
        self.add_item_to_area('Backroads', 'Carrot Seed')

    


    def game_loop(self):
        print("Welcome to the Text Adventure Game!")
        print("Type 'help' for a list of commands.\n")
        while self.is_running:
            
            print(f"\nCurrent location: {self.player.current_area.name}")
            command_input = input("> ").strip()
            if not command_input:
                continue
            parts = command_input.split()
            command = parts[0].lower()
            args = parts[1:]
            cmd_entry = self.commands.get(command)
            if cmd_entry:
                output = cmd_entry['handler'](args)
                if output:
                    print(output)
            else:
                print("Unknown command. Type 'help' for a list of commands.")

    def cmd_move(self, args):
        if not args:
            return "Move where? Specify a direction."
        direction = args[0].lower()
        return self.player.move(direction)

    def cmd_teleport(self, args):
        if not args:
            return "Teleport where? Specify an area name."
        area_name = " ".join(args)
        area = self.areas.get(area_name)
        if area:
            return self.player.teleport(area)
        else:
            return f"No such area: {area_name}"

    def cmd_look(self, args):
        return self.player.current_area.describe()

    def cmd_inventory(self, args):
        if self.player.inventory:
            return "You have:\n" + "\n".join(f" - {item}" for item in self.player.inventory)
        else:
            return "Your inventory is empty."

    def cmd_pick_up(self, args):
        if not args:
            return "pick up what? Specify an item name."
        item_name = " ".join(args)
        # Find item in current area by name
        for item in self.player.current_area.items:
            if item.name.lower() == item_name.lower():
                return self.player.pick_up(item)
        return f"No such item here: {item_name}"

    def cmd_drop(self, args):
        if not args:
            return "Drop what? Specify an item name."
        item_name = " ".join(args)
        # Find item in inventory by name
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                return self.player.drop(item)
        return f"You don't have that item: {item_name}"

    def cmd_quit(self, args):
        self.is_running = False
        return "Thanks for playing! Goodbye."

    def cmd_exit(self, args):
        """List exits for current area or specified area."""
        if not args:
            area = self.player.current_area
        else:
            area_name = " ".join(args)
            area = self.areas.get(area_name)
            if not area:
                return f"No such area: {area_name}"
        exits = area.exits
        if not exits:
            return f"{area.name} has no exits."
        exit_list = ", ".join(f"{direction} -> {dest.name}" for direction, dest in exits.items())
        return f"Exits for {area.name}: {exit_list}"

    def cmd_help(self, args):
        categories = {}
        for cmd, info in self.commands.items():
            cat = info['category']
            categories.setdefault(cat, []).append(cmd)
        help_msg = "Available commands:\n"
        for cat in sorted(categories.keys()):
            cmds = ", ".join(sorted(categories[cat]))
            help_msg += f"  {cat.capitalize()}: {cmds}\n"
        return help_msg
    
    def cmd_plant(self, args):
        """Plant a seed in soil. Usage: plant [seed name] in [soil name]"""
        if not args:
            return "Plant what? Usage: plant [seed name] in [soil name]"
        
        # Check if the command includes "in" to specify the soil
        if "in" in args:
            in_index = args.index("in")
            seed_name = " ".join(args[:in_index])
            soil_name = " ".join(args[in_index+1:])
        else:
            seed_name = " ".join(args)
            soil_name = None  # Will try to find any soil in the area
        
        # Find seed in inventory
        seed = None
        for item in self.player.inventory:
            if item.name.lower() == seed_name.lower() and isinstance(item, Seed):
                seed = item
                break
        
        if not seed:
            return f"You don't have a seed called '{seed_name}' in your inventory."
        
        # Find soil in the current area
        soil = None
        if soil_name:
            # Look for specific soil
            for obj in self.player.current_area.objects:
                if isinstance(obj, Soil) and obj.name.lower() == soil_name.lower():
                    soil = obj
                    break
            if not soil:
                return f"There is no soil called '{soil_name}' in this area."
        else:
            # Look for any soil
            for obj in self.player.current_area.objects:
                if isinstance(obj, Soil):
                    soil = obj
                    break
            if not soil:
                return "There is no soil in this area to plant seeds in."
        
        # Plant the seed in the soil
        success, message = soil.add_plant(seed)
        if success:
            self.player.inventory.remove(seed)
            return message
        else:
            return message
        
    def cmd_harvest(self, args):
        """Harvest a plant from soil. Usage: harvest [plant name] from [soil name]"""
        if not args:
            return "Harvest what? Usage: harvest [plant name] from [soil name]"
        
        # Check if the command includes "from" to specify the soil
        if "from" in args:
            from_index = args.index("from")
            plant_name = " ".join(args[:from_index])
            soil_name = " ".join(args[from_index+1:])
        else:
            plant_name = " ".join(args)
            soil_name = None  # Will try to find the plant in any soil
        
        # Find soil and plant
        for obj in self.player.current_area.objects:
            if isinstance(obj, Soil):
                if soil_name and obj.name.lower() != soil_name.lower():
                    continue  # Skip this soil if we're looking for a specific one
                
                plant = obj.get_plant(plant_name)
                if plant:
                    if plant.is_harvestable():
                        # Create a harvested item based on the plant type
                        harvested_item = Item(
                            f"Harvested {plant.crop_type}", 
                            f"A freshly harvested {plant.crop_type}.", 
                            plant.value
                        )
                        
                        # Add to inventory and remove from soil
                        self.player.inventory.append(harvested_item)
                        obj.remove_plant(plant)
                        
                        return f"You harvested a {plant.crop_type} from the {obj.name}."
                    else:
                        return f"The {plant.name} is not ready to harvest yet."
        
        if soil_name:
            return f"Could not find a plant called '{plant_name}' in the '{soil_name}'."
        else:
            return f"Could not find a plant called '{plant_name}' in any soil in this area."
        
    
            

if __name__ == '__main__':
    game = Game()
    game.game_loop()


