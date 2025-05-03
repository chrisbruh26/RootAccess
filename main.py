import random
import os
import json

# Import game modules
from items import Item, Weapon, Consumable, EffectItem, SmokeBomb, Decoy
from objects import VendingMachine
from gardening import Seed, Plant, SoilPlot, WateringCan
from effects import Effect, PlantEffect, SupervisionEffect, HackedPlantEffect, Substance, HackedMilk, HallucinationEffect, ConfusionEffect
from npc_behavior import NPC, Civilian, Gang, GangMember, BehaviorType, BehaviorSettings, NPCBehaviorCoordinator, behavior_settings
from objects import Computer, HidingSpot
from player import Player
from area import Area

# ----------------------------- #
# GAME MANAGEMENT               #
# ----------------------------- #

class Game:
    def __init__(self):
        self.player = None
        self.areas = {}
        self.current_turn = 0
        self.gangs = {}
        self.npc_coordinator = NPCBehaviorCoordinator()
        self.running = True
        
        # Weapon targeting system
        self.targeting_weapon = None
        self.targeting_npcs = None
        self.in_targeting_mode = False
        
        # Initialize command system
        self.commands = {
            # Movement commands
            'north': {'handler': self.cmd_move, 'category': 'movement'},
            'south': {'handler': self.cmd_move, 'category': 'movement'},
            'east': {'handler': self.cmd_move, 'category': 'movement'},
            'west': {'handler': self.cmd_move, 'category': 'movement'},
            'move': {'handler': self.cmd_move, 'category': 'movement'},
            'go': {'handler': self.cmd_move, 'category': 'movement'},
            'areas': {'handler': self.cmd_areas, 'category': 'movement'},
            
            # Add teleport commands
            'teleport': {'handler': self.cmd_teleport, 'category': 'movement'},
            'tp': {'handler': self.cmd_teleport, 'category': 'movement'},
            
            # Basic interaction commands
            'look': {'handler': self.cmd_look, 'category': 'interaction'},
            'inventory': {'handler': self.cmd_inventory, 'category': 'interaction'},
            'inv': {'handler': self.cmd_inventory, 'category': 'interaction'},
            'take': {'handler': self.cmd_take, 'category': 'interaction'},
            'drop': {'handler': self.cmd_drop, 'category': 'interaction'},
            'use': {'handler': self.cmd_use, 'category': 'interaction'},
            'interact': {'handler': self.cmd_interact, 'category': 'interaction'},
            'npcs': {'handler': self.cmd_npcs, 'category': 'interaction'},
            
            # Add breaking mechanic command
            'break': {'handler': self.cmd_break, 'category': 'interaction'},
            'smash': {'handler': self.cmd_break, 'category': 'interaction'},
            'shoot': {'handler': self.cmd_break, 'category': 'interaction'},
            
            # Combat commands
            'attack': {'handler': self.cmd_attack, 'category': 'combat'},
            
            # Plant/garden commands
            'plant': {'handler': self.cmd_plant, 'category': 'gardening'},
            'water': {'handler': self.cmd_water, 'category': 'gardening'},
            'harvest': {'handler': self.cmd_harvest, 'category': 'gardening'},
            
            # Hiding commands
            'hide': {'handler': self.cmd_hide, 'category': 'stealth'},
            'unhide': {'handler': self.cmd_unhide, 'category': 'stealth'},
            'emerge': {'handler': self.cmd_unhide, 'category': 'stealth'},
            'hiding_spots': {'handler': self.cmd_hiding_spots, 'category': 'stealth'},
            
            # Tech commands
            'hack': {'handler': self.cmd_hack, 'category': 'tech'},
            'run': {'handler': self.cmd_run_program, 'category': 'tech'},
            
            # System commands
            'help': {'handler': self.cmd_help, 'category': 'system'},
            'quit': {'handler': self.cmd_quit, 'category': 'system'},
        }

    def create_player(self):
        self.player = Player()
        
    def create_world(self):
        # Create areas
        self.areas["Home"] = Area("Home", "Your secret base of operations. It's small but functional.")
        self.areas["garden"] = Area("Garden", "A small garden area with fertile soil.")
        self.areas["street"] = Area("Street", "A busy street with various shops and people.")
        self.areas["alley"] = Area("Alley", "A dark alley between buildings.")
        self.areas["plaza"] = Area("Plaza", "A large open plaza with a fountain in the center.")
        self.areas["warehouse"] = Area("Warehouse", "An abandoned warehouse, taken over by the Bloodhounds.")
        self.areas["construction"] = Area("Construction Site", "A construction site with various equipment and materials.")
        
        # Connect areas
        self.areas["Home"].add_connection("north", self.areas["garden"])
        self.areas["garden"].add_connection("south", self.areas["Home"])
        self.areas["garden"].add_connection("east", self.areas["street"])
        self.areas["street"].add_connection("west", self.areas["garden"])
        self.areas["street"].add_connection("north", self.areas["plaza"])
        self.areas["plaza"].add_connection("south", self.areas["street"])
        self.areas["street"].add_connection("east", self.areas["alley"])
        self.areas["alley"].add_connection("west", self.areas["street"])
        self.areas["street"].add_connection("south", self.areas["warehouse"])
        self.areas["warehouse"].add_connection("north", self.areas["street"])
        self.areas["plaza"].add_connection("east", self.areas["construction"])
        self.areas["construction"].add_connection("west", self.areas["plaza"])
        
        # Add objects to areas
        soil_plot = SoilPlot()
        self.areas["garden"].add_object(soil_plot)
        self.areas["warehouse"].add_object(soil_plot)
        
        computer = Computer("Hacking Terminal", "A specialized terminal for hacking operations.")
        computer.programs = ["data_miner", "security_override", "plant_hacker"]
        self.areas["Home"].add_object(computer)
        
        # Add hiding spots to areas
        closet = HidingSpot("Closet", "A small closet that you can hide in.", 0.8)
        self.areas["Home"].add_object(closet)
        
        bushes = HidingSpot("Bushes", "Dense bushes that provide good cover.", 0.7)
        self.areas["garden"].add_object(bushes)
        
        dumpster = HidingSpot("Dumpster", "A large dumpster you can hide behind.", 0.6)
        self.areas["alley"].add_object(dumpster)
        
        fountain = HidingSpot("Fountain", "A large fountain with decorative elements to hide behind.", 0.5)
        self.areas["plaza"].add_object(fountain)
        
        crates = HidingSpot("Crates", "Stacked crates that provide decent cover.", 0.6)
        self.areas["warehouse"].add_object(crates)
        
        # Add construction containers as hiding spots
        container1 = HidingSpot("Construction Container", "A large metal container used for storing construction materials.", 0.9)
        container2 = HidingSpot("Equipment Shed", "A small shed for storing construction equipment.", 0.8)
        container3 = HidingSpot("Cement Mixer", "A large cement mixer you can hide behind.", 0.7)
        self.areas["warehouse"].add_object(container1)
        self.areas["warehouse"].add_object(container2)
        self.areas["warehouse"].add_object(container3)
        
        # Add items to areas
        self.areas["Home"].add_item(Item("Backpack", "A sturdy backpack for carrying items.", 20))
        self.areas["garden"].add_item(Seed("Tomato Seed", "A seed for growing tomatoes.", "tomato", 5))
        self.areas["garden"].add_item(Seed("Potato Seed", "A seed for growing potatoes.", "potato", 5))
        self.areas["street"].add_item(Consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20))
        self.areas["alley"].add_item(Weapon("Pipe", "A metal pipe that can be used as a weapon.", 15, 10))


        vending_machine = VendingMachine("Vending Machine")

        self.areas["warehouse"].add_object(vending_machine)


        vending_machine.add_item(Consumable("Soda", "A refreshing soda.", 5, 10))
        vending_machine.add_item(Consumable("Chips", "A bag of chips.", 5, 5))
        vending_machine.add_item(Consumable("Candy Bar", "A chocolate candy bar.", 5, 15))
        vending_machine.add_item(Consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20))


        
        # create better weapons

        # Hacked Milk Blaster - causes hallucinations
        hacked_milk_blaster = EffectItem("Hacked Milk Blaster", "A strange device that sprays hacked milk.", 50, HallucinationEffect())
        self.areas["warehouse"].add_item(hacked_milk_blaster)
        
        # Confusion Ray - causes confusion
        confusion_ray = EffectItem("Confusion Ray", "A device that emits waves that confuse the target.", 60, ConfusionEffect())
        self.areas["alley"].add_item(confusion_ray)
        self.areas["Home"].add_item(hacked_milk_blaster)


        # WHEN ADDING EFFECTS TO ITEMS LIKE CROPS: example_crop.add_effect(ExampleEffect())





        # Create gangs
        self.gangs["Crimson Vipers"] = Gang("Crimson Vipers")
        self.gangs["Bloodhounds"] = Gang("Bloodhounds")

        # add gang members to areas
        


        bloodhounds_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]
        

        # create crimson vipers names list
        crimson_vipers_names = ["Vipoop", "Snakle", "Rattlesnop", "Pythirt", "Anaceaky", "Cobrus-brus", "Lizuddles", "Viperino", "Slitherpuff", "Hissypants", "Slinker", "Snakester"]
        # choose random name to create a Crimson Vipers gang member
        name = random.choice(crimson_vipers_names)
        self.areas["warehouse"].add_npc(GangMember(name, f"A member of the Crimson Vipers named {name}.", self.gangs["Crimson Vipers"]))





        # add 5 NPCs from the bloodhounds_name list to the warehouse

        gun = Weapon("Gun", "A standard firearm.", 50, 20)

        watering_can = WateringCan("watering can")
        self.player.add_item(watering_can)
        self.areas["Home"].add_item(watering_can)

        carrot_seed =Seed("Carrot Seed", "A seed for growing carrot.", "carrot", 5)


        # add NPCs to the garden to observe how normal civillians interact with plants

        civilian_names = ["Ben", "Bob", "Charl", "Muckle", "Beevo", "ZeFronk", "Grazey", "Honk", "Ivee", "Jork"]

        name_variations = ["etti", "oodle", "op", "eeky", "-eep", "uffin", "bertmo", "athur", "ubble", "uck", "ington", "sworth", "thistle", "quibble", "fizzle", "whistle", "plume", "tumble", "whisk", "glimmer", "thrax", "gloop", "splunk", "dribble", "crunch", "splorp", "quack", "splat", "grizzle", "blorp", "kins", "muff", "snuff", "puff", "whiff", "bloop", "twizzle", "flibble", "squibble", "wobble", "izzle", "oodle", "bop", "snorp", "florp", "wump", "zorp", "plonk", "squee", "boop", "doodle", "ucklebuck", "shoop"]

        for i in range(5):
            name_start = random.choice(civilian_names)
            name_end = random.choice(name_variations)
            name = f"{name_start}{name_end}"
            self.areas["garden"].add_npc(Civilian(name, f"A random civilian named {name}."))
            self.areas["garden"].npcs[-1].add_item(watering_can)
            self.areas["garden"].npcs[-1].add_item(carrot_seed)
            self.areas["garden"].npcs[-1].add_item(hacked_milk_blaster)

        for i in range(5):
            name = random.choice(bloodhounds_names)
            bloodhounds_names.remove(name)
            self.areas["warehouse"].add_npc(GangMember(name, f"A member of the Bloodhounds named {name}.", self.gangs["Bloodhounds"]))
            # add a gun to inventory of each gang member
            self.areas["warehouse"].npcs[-1].add_item(gun)
            self.areas["warehouse"].npcs[-1].add_item(watering_can)
            self.areas["warehouse"].npcs[-1].add_item(confusion_ray)
            self.areas["warehouse"].add_item(carrot_seed)


        machine_gun = Weapon("Machine Gun", "A machine gun.", 100, 50)
        smoke_bomb = SmokeBomb()
        tech_decoy = Decoy()

        self.player.add_item(machine_gun)
        self.player.add_item(smoke_bomb)
        self.player.add_item(tech_decoy)
        
        # Add smoke bombs and decoys to various areas for the player to find
        self.areas["alley"].add_item(SmokeBomb())
        self.areas["street"].add_item(SmokeBomb())
        self.areas["warehouse"].add_item(Decoy())
        self.areas["garden"].add_item(Decoy())
        self.areas["Home"].add_item(carrot_seed)

        self.areas["warehouse"].add_npc(Civilian("John", "A random guy."))





        self.areas["garden"].add_npc(Civilian("Gardener", "A friendly gardener tending to the plants."))


        # Set player's starting location
        self.player.current_area = self.areas["Home"]
        
    def process_command(self, command):
        """Process a player command."""
        command = command.lower().strip()
        parts = command.split()
        
        if not parts:
            return "Please enter a command."
        
        # Check if we're in targeting mode
        if self.targeting_weapon and self.targeting_npcs:
            # If user types 'cancel', exit targeting mode
            if command.lower() == 'cancel':
                self.targeting_weapon = None
                self.targeting_npcs = None
                return "Targeting canceled."
                
            # Try to find the target NPC by name
            target_name = command
            target = next((npc for npc in self.targeting_npcs if npc.name.lower() == target_name.lower()), None)
            
            if target:
                # Attack the target with the weapon
                result = self.targeting_weapon.attack_npc(self.player, target)
                
                # Reset targeting
                self.targeting_weapon = None
                self.targeting_npcs = None
                
                # Update turn after attack
                self.update_turn()
                
                return result[1]
            else:
                # If target not found, show available targets again
                npc_names = [npc.name for npc in self.targeting_npcs]
                npc_list = ", ".join(npc_names)
                return f"Target not found. You can target: {npc_list}\nType the name of the NPC you want to attack, or 'cancel' to stop."
        
        # Normal command processing
        action = parts[0]
        args = parts[1:]

        # Check if command exists in command system
        cmd_entry = self.commands.get(action)
        if cmd_entry:
            return cmd_entry['handler'](args)

        return "Unknown command. Type 'help' for a list of commands."
        
    def cmd_attack(self, args):
        """Attack an NPC with your equipped weapon."""
        if not args:
            return "Attack who? Specify a target."
            
        # Find weapons in inventory
        weapons = [item for item in self.player.inventory if hasattr(item, 'damage')]
        
        if not weapons:
            return "You don't have any weapons to attack with."
            
        # Get target name
        target_name = " ".join(args)
        
        # Find target NPC
        target = next((npc for npc in self.player.current_area.npcs 
                      if npc.name.lower() == target_name.lower() and npc.is_alive), None)
                      
        if not target:
            return f"There is no {target_name} here to attack."
            
        # Use the first weapon in inventory
        weapon = weapons[0]
        result = weapon.attack_npc(self.player, target)
        
        # Update turn after attack
        self.update_turn()
        
        return result[1]

    # Command handlers
    def cmd_move(self, args):
        """Process movement command. Usage: move [direction] or just [direction]"""
        if not args:
            return "Move where? Specify a direction."
        direction = args[0].lower()
        if direction in self.player.current_area.connections:
            # If player is hidden, they need to unhide first
            if self.player.hidden:
                hiding_spot = self.player.hiding_spot
                result = hiding_spot.leave(self.player)
                self.update_turn()
                return f"{result[1]}\nYou move {direction} to {self.player.current_area.connections[direction].name}.\n\n{self.player.current_area.connections[direction].get_full_description()}"
            
            self.player.current_area = self.player.current_area.connections[direction]
            self.update_turn()
            return f"You move {direction} to {self.player.current_area.name}.\n\n{self.player.current_area.get_full_description()}"
        return "You can't go that way."

    def cmd_look(self, args):
        """Look around the current area."""
        return self.player.current_area.get_full_description()

    def cmd_inventory(self, args):
        """Check your inventory."""
        if not self.player.inventory:
            return "Your inventory is empty."
        items = ", ".join(str(item) for item in self.player.inventory)
        return f"Inventory: {items}"

    def cmd_take(self, args):
        """Take an item from the area."""
        if not args:
            return "Take what? Specify an item."
        item_name = " ".join(args)
        item = self.player.current_area.remove_item(item_name)
        if item:
            self.player.add_item(item)
            self.update_turn()
            return f"You take the {item.name}."
        return f"There is no {item_name} here."

    def cmd_drop(self, args):
        """Drop an item from your inventory."""
        if not args:
            return "Drop what? Specify an item."
        item_name = " ".join(args)
        item = self.player.remove_item(item_name)
        if item:
            self.player.current_area.add_item(item)
            self.update_turn()
            return f"You drop the {item.name}."
        return f"You don't have a {item_name}."

    def cmd_use(self, args):
        """Use an item from your inventory."""
        if not args:
            return "Use what? Specify an item."
        item_name = " ".join(args)
        result = self.player.use_item(item_name, self)
        
        # Check if this is a weapon targeting request
        if len(result) > 2 and result[2] == "target_selection":
            # Store the weapon and potential targets for later use
            self.targeting_weapon = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
            self.targeting_npcs = result[3]
            return result[1]
        
        if result[0]:
            self.update_turn()
            return result[1]
        return result[1]

    def cmd_interact(self, args):
        """Interact with an object in the area."""
        if not args:
            return "Interact with what? Specify an object."
        object_name = " ".join(args)
        obj = next((o for o in self.player.current_area.objects if o.name.lower() == object_name.lower()), None)
        if not obj:
            return f"There is no {object_name} here."
        
        # Handle different object types
        if isinstance(obj, SoilPlot):
            plants = ", ".join(str(plant) for plant in obj.plants) if obj.plants else "none"
            return f"Soil Plot: {plants}"
        elif isinstance(obj, Computer):
            return f"Computer: {obj.description}"
        
        return f"You interact with the {obj.name}."

    def cmd_areas(self, args):
        """List all available areas."""
        area_list = ", ".join(sorted(self.areas.keys()))
        return f"Available areas: {area_list}"

    def cmd_npcs(self, args):
        """Show information about NPCs in the current area."""
        if not self.player.current_area.npcs:
            return "There are no NPCs in this area."
            
        npc_info = []
        for npc in self.player.current_area.npcs:
            info = f"{npc.name}: {npc.description}"
            
            # Add inventory information if NPC has items
            if hasattr(npc, 'items') and npc.items:
                items = ", ".join(str(item) for item in npc.items)
                info += f"\n  Inventory: {items}"
                
            # Add health information if NPC has health
            if hasattr(npc, 'health'):
                info += f"\n  Health: {npc.health}/100"
                
            npc_info.append(info)
            
        return "NPCs in this area:\n" + "\n\n".join(npc_info)

    def cmd_plant(self, args):
        """Plant a seed in soil."""
        if not args:
            return "Plant what? Specify a seed."
        seed_name = " ".join(args)
        seed = next((i for i in self.player.inventory if i.name.lower() == seed_name.lower() and isinstance(i, Seed)), None)
        if not seed:
            return f"You don't have a {seed_name}."
        
        soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, SoilPlot)), None)
        if not soil:
            return "There's no soil here to plant seeds."
        
        plant = Plant(
            f"{seed.crop_type} plant", 
            f"A young {seed.crop_type} plant.", 
            seed.crop_type, 
            seed.value * 2
        )
        
        result = soil.add_plant(plant)
        if result[0]:
            self.player.inventory.remove(seed)
            self.update_turn()
        return result[1]

    def cmd_water(self, args):
        """Water plants in soil."""
        soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, SoilPlot)), None)
        if not soil:
            return "There are no plants here to water."
        
        # Check if the player has a watering can
        watering_can = next((item for item in self.player.inventory if isinstance(item, WateringCan)), None)
        if not watering_can:
            return "You need a watering can to water plants."
        
        # Use the watering can to water the plants
        result = soil.water_plants(watering_can=watering_can)
        if result[0]:
            self.update_turn()
        return result[1]

    def cmd_harvest(self, args):
        """Harvest a fully grown plant."""
        if not args:
            return "Harvest what? Specify a plant."
        plant_name = " ".join(args)
        soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, SoilPlot)), None)
        if not soil:
            return "There are no plants here to harvest."
        
        result = soil.harvest_plant(plant_name)
        if not result[0]:
            return result[1]
        
        message, harvested_item = result[1]
        self.player.add_item(harvested_item)
        self.update_turn()
        return message

    def cmd_hide(self, args):
        """Hide in a hiding spot to avoid detection."""
        if not args:
            return "Hide where? Specify a hiding spot."
        # Check if player is already hidden
        if self.player.hidden:
            return "You are already hiding."
        
        # Find the hiding spot by name
        hiding_spot_name = " ".join(args)
        hiding_spot = next((obj for obj in self.player.current_area.objects 
                          if isinstance(obj, HidingSpot) and obj.name.lower() == hiding_spot_name.lower()), None)
        
        if not hiding_spot:
            # Try partial matching
            hiding_spot = next((obj for obj in self.player.current_area.objects 
                              if isinstance(obj, HidingSpot) and hiding_spot_name.lower() in obj.name.lower()), None)
        
        if not hiding_spot:
            # List available hiding spots
            hiding_spots = [obj.name for obj in self.player.current_area.objects if isinstance(obj, HidingSpot)]
            if hiding_spots:
                return f"There is no '{hiding_spot_name}' to hide in. Available hiding spots: {', '.join(hiding_spots)}"
            else:
                return "There are no hiding spots in this area."
        
        # Try to hide
        result = hiding_spot.hide(self.player)
        if result[0]:
            self.update_turn()
        return result[1]

    def cmd_unhide(self, args):
        """Come out of hiding."""
        if not self.player.hidden:
            return "You are not currently hiding."
        
        result = self.player.hiding_spot.leave(self.player)
        if result[0]:
            self.update_turn()
        return result[1]

    def cmd_hiding_spots(self, args):
        """List all available hiding spots in the area."""
        hiding_spots = [obj.name for obj in self.player.current_area.objects if isinstance(obj, HidingSpot)]
        if hiding_spots:
            return f"Available hiding spots in this area: {', '.join(hiding_spots)}"
        else:
            return "There are no hiding spots in this area."

    def cmd_hack(self, args):
        """Hack a computer."""
        computer = next((obj for obj in self.player.current_area.objects if isinstance(obj, Computer)), None)
        if not computer:
            return "There's no computer here to hack."
        
        result = computer.hack(self.player)
        if result[0]:
            self.update_turn()
        return result[1]

    def cmd_run_program(self, args):
        """Run a program on a hacked computer."""
        if not args:
            return "Run what? Specify a program."
        program_name = " ".join(args)
        computer = next((obj for obj in self.player.current_area.objects if isinstance(obj, Computer)), None)
        if not computer:
            return "There's no computer here to run programs on."
        
        result = computer.run_program(program_name, self.player, self)
        if result[0]:
            self.update_turn()
        return result[1]

    def cmd_teleport(self, args):
        """Teleport to any area. Usage: teleport [area name]"""
        if not args:
            return "Teleport where? Specify an area name."
        area_name = " ".join(args).lower()
        
        # Search for area ignoring case
        for area in self.areas.values():
            if area.name.lower() == area_name:
                # If player is hidden, they need to unhide first
                if self.player.hidden:
                    hiding_spot = self.player.hiding_spot
                    result = hiding_spot.leave(self.player)
                    self.update_turn()
                    return f"{result[1]}\nYou teleport to {area.name}.\n\n{area.get_full_description()}"
                
                self.player.current_area = area
                self.update_turn()
                return f"You teleport to {area.name}.\n\n{area.get_full_description()}"
        
        return f"No such area: {' '.join(args)}"

    def cmd_help(self, args):
        """Show help information grouped by command category."""
        help_text = ["Available commands:"]
        
        # Group commands by category
        categories = {}
        for cmd, info in self.commands.items():
            cat = info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(cmd)
        
        # Display commands by category
        for category in sorted(categories.keys()):
            help_text.append(f"\n{category.capitalize()} commands:")
            cmd_list = sorted(categories[category])
            help_text.append("  " + ", ".join(cmd_list))
        
        return "\n".join(help_text)

    def cmd_quit(self, args):
        """Exit the game."""
        self.running = False
        return "Thanks for playing!"
        
    def cmd_break(self, args):
        """Break or smash objects. Usage: break [object] with [weapon] or break [object]"""
        if not args:
            return "Break what? Specify an object."
            
        # Parse arguments
        if "with" in args:
            # Format: break [object] with [weapon]
            with_index = args.index("with")
            object_name = " ".join(args[:with_index])
            weapon_name = " ".join(args[with_index+1:])
            
            # Find weapon in inventory
            weapon = next((i for i in self.player.inventory if i.name.lower() == weapon_name.lower() and hasattr(i, 'damage')), None)
            if not weapon:
                return f"You don't have a {weapon_name} to break things with."
            
            method = "shoot" if weapon.name.lower() == "gun" else "smash"
        else:
            # Format: break [object]
            object_name = " ".join(args)
            weapon = None
            method = "smash"
        
        # Find the breakable object
        breakable_obj = next((obj for obj in self.player.current_area.objects 
                            if obj.name.lower() == object_name.lower() and 
                            hasattr(obj, 'break_glass')), None)
        
        if not breakable_obj:
            return f"There is no breakable {object_name} here."
        
        # Break the object
        if hasattr(breakable_obj, 'break_glass'):
            result = breakable_obj.break_glass(self.player, method)
            if result[0]:
                self.update_turn()
                # If items were spilled, add them to the area
                if len(result) > 2 and result[2]:
                    for item in result[2]:
                        self.player.current_area.add_item(item)
                    breakable_obj.items.clear()
            return result[1]
        
        return f"You can't break the {object_name}."

    def update_turn(self):
        """Update the game state for a new turn."""
        self.current_turn += 1
        
        # Update player effects
        expired_effects = self.player.update_effects()
        if expired_effects:
            print(f"Effects expired: {', '.join(expired_effects)}")
        
        # Check for random events (10% chance per turn)
        if random.random() < 0.1:
            self.trigger_random_event()
        
        # Process NPC behaviors in the current area
        npc_messages = self.npc_coordinator.process_npc_behaviors(self, self.player.current_area.npcs)
        
        # Display NPC action summary
        npc_summary = self.npc_coordinator.get_npc_summary()
        if npc_summary:
            # If player is hidden, add a stealth indicator
            if self.player.hidden:
                print("\n[STEALTH MODE ACTIVE]")
            
            print("\nNPC ACTIONS:")
            print(npc_summary)
            print()
        
    def trigger_random_event(self):
        """Trigger a random event in the current area."""
        # List of possible random events
        events = [
            self.event_rival_gang_appears,
            self.event_tech_malfunction,
            self.event_plant_mutation,
            self.event_mass_confusion
        ]
        
        # Choose and trigger a random event
        event = random.choice(events)
        event()
        
    def event_rival_gang_appears(self):
        """Random event: A rival gang appears and starts a fight."""
        # Only trigger in areas that make sense (not Home)
        if self.player.current_area.name != "warehouse":
            return
            
        # Get all gangs in the area
        gangs_present = set()
        for npc in self.player.current_area.npcs:
            if hasattr(npc, 'gang'):
                gangs_present.add(npc.gang.name)
                
        # If there's only one or no gangs, bring in a rival
        if len(gangs_present) <= 1:
            # Choose a rival gang that's not already present
            available_gangs = [gang for gang_name, gang in self.gangs.items() 
                              if gang_name not in gangs_present]
            
            if not available_gangs:
                return  # No available rival gangs
                
            rival_gang = random.choice(available_gangs)
            
            # Create 1-3 rival gang members
            num_rivals = random.randint(1, 3)
            
            # Gang member name lists
            bloodhounds_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]
            crimson_vipers_names = ["Vipoop", "Snakle", "Rattlesnop", "Pythirt", "Anaceaky", "Cobrus-brus", "Lizuddles", "Viperino", "Slitherpuff", "Hissypants", "Slinker", "Snakester"]
            
            # Choose appropriate name list
            if rival_gang.name == "Crimson Vipers":
                name_list = crimson_vipers_names
            else:
                name_list = bloodhounds_names
                
            # Add rival gang members
            for i in range(num_rivals):
                if name_list:
                    name = random.choice(name_list)
                    name_list.remove(name)
                else:
                    # Generate a random name if we run out
                    name = f"{rival_gang.name[0]}-{random.randint(1, 100)}"
                    
                # Create and add the gang member
                rival = GangMember(name, f"A member of the {rival_gang.name} named {name}.", rival_gang)
                self.player.current_area.add_npc(rival)
                
                # Give them weapons and items
                gun = Weapon("Gun", "A standard firearm.", 50, 20)
                rival.add_item(gun)
                
                # 50% chance to have an effect item
                if random.random() < 0.5:
                    effect_item = EffectItem("Confusion Ray", "A device that emits waves that confuse the target.", 60, ConfusionEffect())
                    rival.add_item(effect_item)
            
            print(f"\n*** RANDOM EVENT: A group of {rival_gang.name} members has appeared! ***")
            
            # Make them immediately hostile to other gangs
            for npc in self.player.current_area.npcs:
                if hasattr(npc, 'gang') and npc.gang != rival_gang:
                    # Force an attack between rival gang members
                    for rival_member in [n for n in self.player.current_area.npcs if hasattr(n, 'gang') and n.gang == rival_gang]:
                        attack_result = rival_member.attack_npc(npc)
                        if attack_result:
                            print(attack_result)
                            break
                    break
        
    def event_tech_malfunction(self):
        """Random event: Technology in the area malfunctions, causing distractions."""
        # Check if there are any tech objects in the area
        tech_objects = [obj for obj in self.player.current_area.objects 
                       if hasattr(obj, 'is_electronic') and obj.is_electronic]
        
        if not tech_objects:
            return  # No tech objects to malfunction
            
        # Choose a random tech object
        tech_object = random.choice(tech_objects)
        
        # Generate a malfunction effect
        effects = [
            f"The {tech_object.name} suddenly sparks and emits a loud noise!",
            f"The {tech_object.name} starts flashing with bright lights!",
            f"The {tech_object.name} makes a series of strange beeping sounds!"
        ]
        
        effect = random.choice(effects)
        print(f"\n*** RANDOM EVENT: TECH MALFUNCTION ***\n{effect}")
        
        # Distract NPCs - 50% chance for each NPC to be affected
        affected_npcs = []
        for npc in self.player.current_area.npcs:
            if random.random() < 0.5 and hasattr(npc, 'active_effects'):
                # Create a temporary confusion effect
                confusion = ConfusionEffect()
                confusion.remaining_turns = 1  # Only lasts 1 turn
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
                
        # If player was detected, 30% chance to lose detection
        if self.player.detected_by and random.random() < 0.3:
            # Choose one random gang to lose detection
            if self.player.detected_by:
                gang_to_forget = random.choice(list(self.player.detected_by))
                self.player.detected_by.remove(gang_to_forget)
                print(f"The {gang_to_forget.name} seem distracted by the malfunction and have lost track of you!")
        
    def event_plant_mutation(self):
        """Random event: Plants in the area mutate and release strange effects."""
        # Check if there are any soil plots with plants
        soil_plots = [obj for obj in self.player.current_area.objects 
                     if hasattr(obj, 'plants') and obj.plants]
        
        if not soil_plots:
            return  # No plants to mutate
            
        # Choose a random soil plot
        soil = random.choice(soil_plots)
        
        # Choose a random plant
        if not soil.plants:
            return
            
        plant = random.choice(soil.plants)
        
        # Generate a mutation effect
        effects = [
            f"The {plant.name} suddenly grows to twice its size!",
            f"The {plant.name} releases a cloud of spores!",
            f"The {plant.name} starts glowing with an eerie light!",
            f"The {plant.name} makes a strange rustling sound!"
        ]
        
        effect = random.choice(effects)
        print(f"\n*** RANDOM EVENT: PLANT MUTATION ***\n{effect}")
        
        # Apply random effects to NPCs
        for npc in self.player.current_area.npcs:
            if hasattr(npc, 'active_effects') and random.random() < 0.4:  # 40% chance
                # Choose between hallucination and confusion
                if random.random() < 0.5:
                    effect = HallucinationEffect()
                else:
                    effect = ConfusionEffect()
                    
                npc.active_effects.append(effect)
                print(f"{npc.name} is affected by the plant mutation!")
                
        # 20% chance to heal the player a bit
        if random.random() < 0.2:
            heal_amount = random.randint(5, 15)
            self.player.health = min(self.player.max_health, self.player.health + heal_amount)
            print(f"You feel rejuvenated by the plant's energy! (+{heal_amount} health)")
        
    def event_mass_confusion(self):
        """Random event: A wave of confusion sweeps through the area."""
        # Only trigger if there are NPCs in the area
        if not self.player.current_area.npcs:
            return
            
        print("\n*** RANDOM EVENT: MASS CONFUSION ***")
        print("A strange wave of energy pulses through the area!")
        
        # Apply confusion to most NPCs
        affected_npcs = []
        for npc in self.player.current_area.npcs:
            if hasattr(npc, 'active_effects') and random.random() < 0.7:  # 70% chance
                confusion = ConfusionEffect()
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
                
        # If NPCs were affected, add effect messages
        if affected_npcs and self.npc_coordinator:
            self.npc_coordinator.add_effect_messages(affected_npcs, ConfusionEffect())
        
        # If player is hidden, there's a small chance they get discovered anyway
        if self.player.hidden and random.random() < 0.05:  # 5% chance per turn
            # Only if there are gang members in the area
            gang_members = [npc for npc in self.player.current_area.npcs 
                           if isinstance(npc, GangMember) and npc.is_alive]
            
            if gang_members and random.random() < 0.3:  # 30% chance if there are gang members
                # Player is discovered!
                discovered_by = random.choice(gang_members)
                self.player.hidden = False
                self.player.hiding_spot.is_occupied = False
                self.player.hiding_spot.occupant = None
                self.player.hiding_spot = None
                
                # Add the gang to detected_by
                self.player.detected_by.add(discovered_by.gang)
                
                print(f"\n{discovered_by.name} has discovered your hiding spot! You are no longer hidden.")
        
        # Update plants in all areas
        for area_name, area in self.areas.items():
            for obj in area.objects:
                if hasattr(obj, 'plants'):
                    for plant in obj.plants:
                        if hasattr(plant, 'grow') and random.random() < 0.3:  # 30% chance to grow each turn
                            plant.grow()
    
    def respawn_player(self):
        """Respawn the player at their home after death."""
        print("\n*** You have been defeated! ***")
        print("You wake up back at home, feeling disoriented...")
        
        # Reset player health
        self.player.health = self.player.max_health
        
        # Move player back to home
        self.player.current_area = self.areas["Home"]
        
        # Clear detection status
        self.player.detected_by.clear()
        
        # If player was hidden, reset hiding status
        if self.player.hidden:
            if self.player.hiding_spot:
                self.player.hiding_spot.is_occupied = False
                self.player.hiding_spot.occupant = None
            self.player.hiding_spot = None
            self.player.hidden = False
        
        # Lose some items (50% chance to lose each item)
        lost_items = []
        kept_items = []
        
        for item in self.player.inventory[:]:  # Create a copy to iterate over
            if random.random() < 0.5:  # 50% chance to lose the item
                self.player.inventory.remove(item)
                lost_items.append(item.name)
            else:
                kept_items.append(item.name)
        
        # Add some health items to help the player recover
        energy_drink = Consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20)
        self.player.add_item(energy_drink)
        self.player.add_item(SmokeBomb())  # Always give a smoke bomb for escape
        
        # 50% chance to get a decoy
        if random.random() < 0.5:
            self.player.add_item(Decoy())
        
        # Print status message
        print(f"\nYou've respawned at Home with {self.player.health} health.")
        print("You found some supplies to help you recover.")
        
        if lost_items:
            print(f"You lost some items in the process: {', '.join(lost_items)}")
        
        if kept_items:
            print(f"You managed to keep: {', '.join(kept_items)}")
        
        # Show the current area description
        print("\n" + self.player.current_area.get_full_description())
    
    def run(self):
        """Run the main game loop."""
        print("Welcome to Root Access!")
        self.create_player()
        self.create_world()
        
        print(self.player.current_area.get_full_description())
        
        while self.running:
            command = input("\n> ")
            result = self.process_command(command)
            print(result)
            
            # Check if player is dead
            if self.player.health <= 0:
                self.respawn_player()
                continue


# ----------------------------- #
# MAIN ENTRY POINT              #
# ----------------------------- #

if __name__ == "__main__":
    game = Game()
    game.run()
