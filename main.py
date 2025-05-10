"""
Root Access v2 - Enhanced Component Version
A text-based game that combines elements of Animal Crossing and Watch Dogs 2
in a wacky and entertaining way.

This version uses an enhanced component-based system for maximum flexibility and scalability,
with special focus on hybrid items that maintain all original functionality.
"""

import random
import os
import json
import time
import copy

# Import the enhanced component system
from components import (
    Entity, Component, 
    InventoryComponent, HealthComponent, UsableComponent, WeaponComponent,
    BreakableComponent, EffectComponent, GardeningComponent, HidingComponent,
    TechComponent, BehaviorComponent, SeedComponent, PlantComponent, SoilComponent,
    WateringCanComponent,
    create_weapon, create_consumable, create_effect_item, create_tech_item,
    create_hiding_spot, create_vending_machine, create_seed, create_watering_can,
    create_soil_plot, create_plant, combine_items
)

from entity_factory import EntityFactory

# Import effects (these will still be class-based for now)
from effects import Effect, PlantEffect, SupervisionEffect, HackedPlantEffect, Substance, HackedMilk, HallucinationEffect, ConfusionEffect

# Import NPC behavior (these will still be class-based for now)
from npc_behavior import Gang, BehaviorType, NPCBehaviorCoordinator, behavior_settings

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
        self.event_manager = None  # Will be initialized after game is fully set up
        
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
            'recharge': {'handler': self.cmd_recharge, 'category': 'tech'},
            
            # Hybrid item commands
            'combine': {'handler': self.cmd_combine, 'category': 'crafting'},
            'craft': {'handler': self.cmd_combine, 'category': 'crafting'},
            'merge': {'handler': self.cmd_combine, 'category': 'crafting'},
            'examine': {'handler': self.cmd_examine, 'category': 'interaction'},
            
            # Storage commands
            'store': {'handler': self.cmd_store, 'category': 'storage'},
            'retrieve': {'handler': self.cmd_retrieve, 'category': 'storage'},
            'containers': {'handler': self.cmd_containers, 'category': 'storage'},
            
            # System commands
            'help': {'handler': self.cmd_help, 'category': 'system'},
            'quit': {'handler': self.cmd_quit, 'category': 'system'},
        }

    def create_player(self):
        """Create the player using the component system."""
        self.player = EntityFactory.create_player()
        
    def create_world(self):
        """Create the game world using the component system."""
        # Create areas
        self.areas["Home"] = EntityFactory.create_area("Home", "Your secret base of operations. It's small but functional.")
        self.areas["garden"] = EntityFactory.create_area("Garden", "A small garden area with fertile soil.")
        self.areas["street"] = EntityFactory.create_area("Street", "A busy street with various shops and people.")
        self.areas["alley"] = EntityFactory.create_area("Alley", "A dark alley between buildings.")
        self.areas["plaza"] = EntityFactory.create_area("Plaza", "A large open plaza with a fountain in the center.")
        self.areas["warehouse"] = EntityFactory.create_area("Warehouse", "An abandoned warehouse, taken over by the Bloodhounds.")
        self.areas["construction"] = EntityFactory.create_area("Construction Site", "A construction site with various equipment and materials.")
        
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
        soil_plot = EntityFactory.create_soil_plot()
        self.areas["garden"].add_object(soil_plot)
        self.areas["warehouse"].add_object(EntityFactory.create_soil_plot())
        
        computer = EntityFactory.create_computer("Hacking Terminal", "A specialized terminal for hacking operations.")
        computer.programs = ["data_miner", "security_override", "plant_hacker"]
        self.areas["Home"].add_object(computer)
        
        # Add hiding spots to areas
        closet = create_hiding_spot("Closet", "A small closet that you can hide in.", 0.8)
        self.areas["Home"].add_object(closet)
        
        bushes = create_hiding_spot("Bushes", "Dense bushes that provide good cover.", 0.7)
        self.areas["garden"].add_object(bushes)
        
        dumpster = create_hiding_spot("Dumpster", "A large dumpster you can hide behind.", 0.6)
        self.areas["alley"].add_object(dumpster)
        
        fountain = create_hiding_spot("Fountain", "A large fountain with decorative elements to hide behind.", 0.5)
        self.areas["plaza"].add_object(fountain)
        
        crates = create_hiding_spot("Crates", "Stacked crates that provide decent cover.", 0.6)
        self.areas["warehouse"].add_object(crates)
        
        # Add construction containers as hiding spots
        container1 = create_hiding_spot("Construction Container", "A large metal container used for storing construction materials.", 0.9)
        container2 = create_hiding_spot("Equipment Shed", "A small shed for storing construction equipment.", 0.8)
        container3 = create_hiding_spot("Cement Mixer", "A large cement mixer you can hide behind.", 0.7)
        self.areas["warehouse"].add_object(container1)
        self.areas["warehouse"].add_object(container2)
        self.areas["warehouse"].add_object(container3)
        
        # Add items to areas
        from components import create_backpack, create_safe, create_refrigerator, create_storage_container
        
        # Replace the old backpack with our new storage backpack
        backpack = create_backpack("Backpack", "A sturdy backpack for carrying items.", capacity=10, value=20)
        self.areas["Home"].add_item(backpack)
        
        # Add a safe to the home area
        safe = create_safe("Safe", "A secure safe for storing valuable items.", capacity=5, value=100)
        self.areas["Home"].add_object(safe)
        
        # Add a refrigerator to the home area
        fridge = create_refrigerator("Refrigerator", "A refrigerator for storing food items.", capacity=15, value=75)
        self.areas["Home"].add_object(fridge)
        
        # Add a toolbox to the warehouse
        toolbox = create_storage_container(
            "Toolbox", 
            "A metal toolbox for storing tools.", 
            capacity=8, 
            storage_name="Toolbox", 
            value=30
        )
        toolbox.add_tag("toolbox")
        self.areas["warehouse"].add_item(toolbox)
        
        tomato_seed = create_seed("Tomato Seed", "A seed for growing tomatoes.", "tomato", 5)
        self.areas["garden"].add_item(tomato_seed)
        
        potato_seed = create_seed("Potato Seed", "A seed for growing potatoes.", "potato", 5)
        self.areas["garden"].add_item(potato_seed)
        
        energy_drink = create_consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20)
        self.areas["street"].add_item(energy_drink)
        
        pipe = create_weapon("Pipe", "A metal pipe that can be used as a weapon.", 15, 10)
        self.areas["alley"].add_item(pipe)
        
        vending_machine = create_vending_machine("Vending Machine")
        self.areas["warehouse"].add_object(vending_machine)
        
        # Add items to vending machine
        vending_inventory = vending_machine.get_component("inventory")
        vending_inventory.add_item(create_consumable("Soda", "A refreshing soda.", 5, 10))
        vending_inventory.add_item(create_consumable("Chips", "A bag of chips.", 5, 5))
        vending_inventory.add_item(create_consumable("Candy Bar", "A chocolate candy bar.", 5, 15))
        vending_inventory.add_item(create_consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20))
        
        # Create better weapons
        hacked_milk_blaster = create_effect_item("Hacked Milk Blaster", "A strange device that sprays hacked milk.", 50, HallucinationEffect)
        self.areas["warehouse"].add_item(hacked_milk_blaster)
        
        confusion_ray = create_effect_item("Confusion Ray", "A device that emits waves that confuse the target.", 60, ConfusionEffect)
        self.areas["alley"].add_item(confusion_ray)
        
        drone = EntityFactory.create_drone()
        self.areas["Home"].add_item(drone)
        
        # Create gangs
        self.gangs["Crimson Vipers"] = Gang("Crimson Vipers")
        self.gangs["Bloodhounds"] = Gang("Bloodhounds")
        
        # Add gang members to areas
        bloodhounds_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]
        crimson_vipers_names = ["Vipoop", "Snakle", "Rattlesnop", "Pythirt", "Anaceaky", "Cobrus-brus", "Lizuddles", "Viperino", "Slitherpuff", "Hissypants", "Slinker", "Snakester"]
        
        # Choose random name to create a Crimson Vipers gang member
        name = random.choice(crimson_vipers_names)
        self.areas["warehouse"].add_npc(EntityFactory.create_gang_member(name, f"A member of the Crimson Vipers named {name}.", self.gangs["Crimson Vipers"]))
        
        gun = create_weapon("Gun", "A standard firearm.", 50, 20)
        
        watering_can = create_watering_can()
        player_inventory = self.player.get_component("inventory")
        if player_inventory:
            player_inventory.add_item(watering_can)
        self.areas["Home"].add_item(watering_can)
        
        carrot_seed = create_seed("Carrot Seed", "A seed for growing carrot.", "carrot", 5)
        
        # Add NPCs to the garden to observe how normal civilians interact with plants
        civilian_names = ["Ben", "Bob", "Charl", "Muckle", "Beevo", "ZeFronk", "Grazey", "Honk", "Ivee", "Jork"]
        name_variations = ["etti", "oodle", "op", "eeky", "-eep", "uffin", "bertmo", "athur", "ubble", "uck", "ington", "sworth", "thistle", "quibble", "fizzle", "whistle", "plume", "tumble", "whisk", "glimmer", "thrax", "gloop", "splunk", "dribble", "crunch", "splorp", "quack", "splat", "grizzle", "blorp", "kins", "muff", "snuff", "puff", "whiff", "bloop", "twizzle", "flibble", "squibble", "wobble", "izzle", "oodle", "bop", "snorp", "florp", "wump", "zorp", "plonk", "squee", "boop", "doodle", "ucklebuck", "shoop"]
        
        for i in range(5):
            name_start = random.choice(civilian_names)
            name_end = random.choice(name_variations)
            name = f"{name_start}{name_end}"
            civilian = EntityFactory.create_npc(name, f"A random civilian named {name}.", "civilian")
            self.areas["garden"].add_npc(civilian)
            
            # Add items to civilian's inventory
            civilian_inventory = civilian.get_component("inventory")
            civilian_inventory.add_item(create_watering_can())
            civilian_inventory.add_item(create_seed("Carrot Seed", "A seed for growing carrot.", "carrot", 5))
            
        # Set the player's starting area
        self.player.current_area = self.areas["Home"]
        self.areas["Home"].add_entity(self.player)
    
    def run(self):
        """Run the game loop."""
        print("Welcome to Root Access v2 - Enhanced Component Version!")
        print("Type 'help' for a list of commands.")
        print()
        
        self.cmd_look([])
        
        while self.running:
            # Get player input
            command = input("> ").strip().lower()
            
            # Check if we're in targeting mode
            if self.in_targeting_mode:
                self.handle_targeting(command)
                continue
            
            # Parse the command
            parts = command.split()
            if not parts:
                continue
            
            cmd = parts[0]
            args = parts[1:]
            
            # Execute the command
            if cmd in self.commands:
                result = self.commands[cmd]['handler'](args)
                print(result)
            else:
                print(f"Unknown command: {cmd}")
            
            # Update the game state
            self.update()
    
    def update(self):
        """Update the game state."""
        self.current_turn += 1
        
        # Update all entities in all areas
        for area in self.areas.values():
            for entity in area.entities:
                entity.update(self)
            
            for obj in area.objects:
                obj.update(self)
        
        # Update the NPC coordinator
        self.npc_coordinator.update(self)
    
    def handle_targeting(self, command):
        """Handle targeting mode input."""
        if command.lower() == 'cancel':
            self.in_targeting_mode = False
            self.targeting_weapon = None
            self.targeting_npcs = None
            print("Targeting canceled.")
            return
        
        try:
            target_index = int(command) - 1
            if 0 <= target_index < len(self.targeting_npcs):
                target = self.targeting_npcs[target_index]
                
                # Check if the weapon has an effect component
                effect_component = self.targeting_weapon.get_component("effect")
                if effect_component:
                    result = effect_component.apply_effect(target, self)
                    print(result[1])
                else:
                    # Check if the weapon has a weapon component
                    weapon_component = self.targeting_weapon.get_component("weapon")
                    if weapon_component:
                        result = weapon_component.attack(target, self)
                        print(result[1])
                
                # Exit targeting mode
                self.in_targeting_mode = False
                self.targeting_weapon = None
                self.targeting_npcs = None
            else:
                print("Invalid target number. Try again or type 'cancel'.")
        except ValueError:
            print("Please enter a number or 'cancel'.")
    
    # ----------------------------- #
    # COMMAND HANDLERS              #
    # ----------------------------- #
    
    def cmd_move(self, args):
        """Move in a direction."""
        if not args:
            return "Move where? (north, south, east, west)"
        
        direction = args[0].lower()
        
        # Handle aliases
        if direction == "n":
            direction = "north"
        elif direction == "s":
            direction = "south"
        elif direction == "e":
            direction = "east"
        elif direction == "w":
            direction = "west"
        
        # Check if the player is hidden
        if hasattr(self.player, 'is_hidden') and self.player.is_hidden:
            return "You can't move while hiding. Use 'unhide' or 'emerge' first."
        
        # Check if the direction is valid
        if not self.player.current_area or direction not in self.player.current_area.connections:
            return f"You can't go {direction} from here."
        
        # Move the player
        old_area = self.player.current_area
        new_area = self.player.current_area.connections[direction]
        
        # Remove the player from the old area
        if old_area:
            old_area.remove_entity(self.player)
        
        # Add the player to the new area
        self.player.current_area = new_area
        new_area.add_entity(self.player)
        
        # Return a description of the new area
        return self.cmd_look([])
    
    def cmd_teleport(self, args):
        """Teleport to an area."""
        if not args:
            return "Teleport where? Use 'areas' to see available areas."
        
        area_name = " ".join(args).lower()
        
        # Find the area
        area = next((a for a in self.areas.values() if a.name.lower() == area_name), None)
        
        if not area:
            return f"There's no area called '{area_name}'."
        
        # Check if the player is hidden
        if hasattr(self.player, 'is_hidden') and self.player.is_hidden:
            return "You can't teleport while hiding. Use 'unhide' or 'emerge' first."
        
        # Move the player
        old_area = self.player.current_area
        
        # Remove the player from the old area
        if old_area:
            old_area.remove_entity(self.player)
        
        # Add the player to the new area
        self.player.current_area = area
        area.add_entity(self.player)
        
        # Return a description of the new area
        return self.cmd_look([])
    
    def cmd_areas(self, args):
        """List all areas."""
        return "Available areas:\n" + "\n".join([area.name for area in self.areas.values()])
    
    def cmd_look(self, args):
        """Look around the current area."""
        if not self.player.current_area:
            return "You are in a void. There's nothing here."
        
        area = self.player.current_area
        
        # Build the description
        description = [f"You are in {area.name}."]
        description.append(area.description)
        
        # List exits
        exits = list(area.connections.keys())
        if exits:
            description.append(f"Exits: {', '.join(exits)}")
        else:
            description.append("There are no exits.")
        
        # List objects
        if area.objects:
            description.append("\nObjects:")
            for obj in area.objects:
                description.append(f"- {obj}")
        
        # List items
        if area.items:
            description.append("\nItems:")
            for item in area.items:
                description.append(f"- {item}")
        
        # List NPCs
        if area.npcs:
            description.append("\nNPCs:")
            for npc in area.npcs:
                # Check if the NPC is alive
                health_component = npc.get_component("health")
                if health_component and health_component.is_alive:
                    description.append(f"- {npc}")
        
        return "\n".join(description)
    
    def cmd_inventory(self, args):
        """Show the player's inventory."""
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        if not inventory.items:
            return "Your inventory is empty."
        
        # Build the inventory list
        items = [f"- {item}" for item in inventory.items]
        
        return f"Inventory ({len(inventory.items)}/{inventory.capacity}):\n" + "\n".join(items)
    
    def cmd_take(self, args):
        """Take an item from the current area."""
        if not args:
            return "Take what?"
        
        item_name = " ".join(args).lower()
        
        if not self.player.current_area:
            return "There's nothing here to take."
        
        # Find the item in the current area
        item = next((item for item in self.player.current_area.items if item.name.lower() == item_name), None)
        
        if not item:
            return f"There's no {item_name} here."
        
        # Add the item to the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        if inventory.add_item(item):
            # Remove the item from the area
            self.player.current_area.remove_item(item)
            return f"You take the {item.name}."
        else:
            return "Your inventory is full."
    
    def cmd_drop(self, args):
        """Drop an item from the player's inventory."""
        if not args:
            return "Drop what?"
        
        item_name = " ".join(args).lower()
        
        # Find the item in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        item = inventory.get_item_by_name(item_name)
        
        if not item:
            return f"You don't have a {item_name}."
        
        # Remove the item from the player's inventory
        inventory.remove_item(item)
        
        # Add the item to the current area
        if self.player.current_area:
            self.player.current_area.add_item(item)
        
        return f"You drop the {item.name}."
    
    def cmd_use(self, args):
        """Use an item from the player's inventory."""
        if not args:
            return "Use what?"
        
        item_name = " ".join(args).lower()
        
        # Find the item in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        item = inventory.get_item_by_name(item_name)
        
        if not item:
            return f"You don't have a {item_name}."
        
        # Handle hybrid items specially
        if item.is_hybrid:
            # Check if the item has any usable components
            usable_components = []
            for component_type, component in item.components.items():
                if component_type.startswith("usable") or hasattr(component, "component_type") and component.component_type == "usable":
                    usable_components.append((component_type, component))
            
            if len(usable_components) > 1:
                # Ask the player which functionality to use
                options = []
                for i, (component_type, component) in enumerate(usable_components):
                    source = component.original_source.name if hasattr(component, "original_source") and component.original_source else "unknown"
                    options.append(f"{i+1}. Use as {source}")
                
                print(f"The {item.name} has multiple functions. Which would you like to use?")
                for option in options:
                    print(option)
                
                choice = input("Enter the number of your choice: ")
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(usable_components):
                        component_type, component = usable_components[choice_index]
                        result = component.use(self.player, self)
                        return result[1]
                    else:
                        return "Invalid choice."
                except ValueError:
                    return "Please enter a number."
            
            elif len(usable_components) == 1:
                component_type, component = usable_components[0]
                result = component.use(self.player, self)
                return result[1]
        
        # Check if the item has a usable component
        usable_component = item.get_component("usable")
        if usable_component:
            result = usable_component.use(self.player, self)
            return result[1]
        
        # Check if the item is a weapon
        weapon_component = item.get_component("weapon")
        if weapon_component:
            # Check if there are NPCs in the area to target
            if self.player.current_area and self.player.current_area.npcs:
                # Get a list of alive NPCs
                alive_npcs = []
                for npc in self.player.current_area.npcs:
                    health_component = npc.get_component("health")
                    if health_component and health_component.is_alive:
                        alive_npcs.append(npc)
                
                if alive_npcs:
                    # Set up targeting mode
                    self.targeting_weapon = item
                    self.targeting_npcs = alive_npcs
                    self.in_targeting_mode = True
                    
                    # Ask player which NPC to attack
                    npc_list = "\n".join([f"{i+1}. {npc.name}" for i, npc in enumerate(alive_npcs)])
                    return f"You ready your {item.name}.\nChoose a target:\n{npc_list}\n\nEnter the number of your target, or 'cancel' to stop."
            
            return f"There's nothing to attack with your {item.name}."
        
        # Check if the item has a watering can component
        watering_can_component = item.get_component("watering_can")
        if watering_can_component:
            # Check if we're in an area with soil
            if self.player.current_area:
                soil = next((obj for obj in self.player.current_area.objects if obj.has_tag("soil")), None)
                if soil:
                    # Get the soil component
                    soil_component = soil.get_component("soil")
                    if soil_component:
                        # Water the soil
                        result = soil_component.water_plants(item, self)
                        return result[1]
            
            return "There's nothing to water here."
        
        # Check if the item has a seed component
        seed_component = item.get_component("seed")
        if seed_component:
            # Check if we're in an area with soil
            if self.player.current_area:
                soil = next((obj for obj in self.player.current_area.objects if obj.has_tag("soil")), None)
                if soil:
                    # Get the soil component
                    soil_component = soil.get_component("soil")
                    if soil_component:
                        # Plant the seed
                        result = soil_component.plant_seed(item)
                        
                        # Remove the seed from the player's inventory if planting was successful
                        if result[0]:
                            inventory.remove_item(item)
                        
                        return result[1]
            
            return "There's no soil here to plant in."
        
        return f"You can't use the {item.name}."
    
    def cmd_interact(self, args):
        """Interact with an object in the current area."""
        if not args:
            return "Interact with what?"
        
        if not self.player.current_area:
            return "There's nothing here to interact with."
        
        object_name = " ".join(args).lower()
        
        # Find the object in the current area
        obj = next((obj for obj in self.player.current_area.objects if obj.name.lower() == object_name), None)
        
        if not obj:
            return f"There's no {object_name} here."
        
        # Check if the object has a usable component
        usable_component = obj.get_component("usable")
        if usable_component:
            result = usable_component.use(self.player, self)
            return result[1]
        
        return f"You can't interact with the {obj.name}."
    
    def cmd_npcs(self, args):
        """List all NPCs in the current area."""
        if not self.player.current_area:
            return "There are no NPCs here."
        
        # Build the NPC list
        npcs = []
        for npc in self.player.current_area.npcs:
            # Check if the NPC is alive
            health_component = npc.get_component("health")
            if health_component and health_component.is_alive:
                npcs.append(f"- {npc}")
        
        if not npcs:
            return "There are no living NPCs here."
        
        return "NPCs in this area:\n" + "\n".join(npcs)
    
    def cmd_break(self, args):
        """Break an object in the current area."""
        if not args:
            return "Break what?"
        
        if not self.player.current_area:
            return "There's nothing here to break."
        
        object_name = " ".join(args).lower()
        
        # Find the object in the current area
        obj = next((obj for obj in self.player.current_area.objects if obj.name.lower() == object_name), None)
        
        if not obj:
            return f"There's no {object_name} here."
        
        # Check if the object has a breakable component
        breakable_component = obj.get_component("breakable")
        if not breakable_component:
            return f"You can't break the {obj.name}."
        
        # Break the object
        result = breakable_component.break_glass(self.player)
        
        # If the object is a vending machine and it broke, add the items to the area
        if result[0] and len(result) > 2 and obj.has_tag("vending_machine"):
            for item in result[2]:
                self.player.current_area.add_item(item)
            
            # Clear the vending machine's inventory
            inventory = obj.get_component("inventory")
            if inventory:
                inventory.items.clear()
        
        return result[1]
    
    def cmd_attack(self, args):
        """Attack an NPC in the current area."""
        if not args:
            return "Attack who?"
        
        if not self.player.current_area:
            return "There's no one here to attack."
        
        npc_name = " ".join(args).lower()
        
        # Find the NPC in the current area
        npc = next((npc for npc in self.player.current_area.npcs if npc.name.lower() == npc_name), None)
        
        if not npc:
            return f"There's no {npc_name} here."
        
        # Check if the NPC is alive
        health_component = npc.get_component("health")
        if not health_component or not health_component.is_alive:
            return f"{npc.name} is already defeated."
        
        # Check if the player has a weapon
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        weapon = next((item for item in inventory.items if item.has_component("weapon")), None)
        
        if not weapon:
            return "You don't have a weapon."
        
        # Attack the NPC
        weapon_component = weapon.get_component("weapon")
        result = weapon_component.attack(npc, self)
        
        return result[1]
    
    def cmd_plant(self, args):
        """Plant a seed in soil."""
        if not args:
            return "Plant what?"
        
        seed_name = " ".join(args).lower()
        
        # Find the seed in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        seed = inventory.get_item_by_name(seed_name)
        
        if not seed:
            return f"You don't have a {seed_name}."
        
        # Check if the seed has a seed component or is a hybrid with seed functionality
        has_seed_component = seed.has_component("seed")
        is_hybrid_seed = seed.is_hybrid and any(parent.has_component("seed") for parent in seed.parent_entities)
        
        if not has_seed_component and not is_hybrid_seed:
            return f"You can't plant a {seed.name}."
        
        # Find a soil plot in the current area
        if not self.player.current_area:
            return "There's no soil here to plant in."
        
        soil = next((obj for obj in self.player.current_area.objects if obj.has_tag("soil")), None)
        
        if not soil:
            return "There's no soil here to plant in."
        
        # Get the soil component
        soil_component = soil.get_component("soil")
        if not soil_component:
            return "This soil can't be planted in."
        
        # Plant the seed
        result = soil_component.plant_seed(seed)
        
        # Remove the seed from the player's inventory if planting was successful
        if result[0]:
            inventory.remove_item(seed)
        
        return result[1]
    
    def cmd_water(self, args):
        """Water plants in soil."""
        if not self.player.current_area:
            return "There's nothing here to water."
        
        # Find a watering can in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        # Check for items with watering can component or hybrid items with watering can functionality
        watering_can = next((item for item in inventory.items if item.has_component("watering_can")), None)
        
        if not watering_can:
            # Check for hybrid items with watering can functionality
            watering_can = next((item for item in inventory.items if item.is_hybrid and any(parent.has_component("watering_can") for parent in item.parent_entities)), None)
            
            if not watering_can:
                return "You don't have a watering can."
        
        # Find a soil plot in the current area
        soil = next((obj for obj in self.player.current_area.objects if obj.has_tag("soil")), None)
        
        if not soil:
            return "There's no soil here to water."
        
        # Get the soil component
        soil_component = soil.get_component("soil")
        if not soil_component:
            return "This soil can't be watered."
        
        # Water the soil
        result = soil_component.water_plants(watering_can, self)
        
        return result[1]
    
    def cmd_harvest(self, args):
        """Harvest a plant from soil."""
        if not args:
            return "Harvest what?"
        
        if not self.player.current_area:
            return "There's nothing here to harvest."
        
        plant_name = " ".join(args).lower()
        
        # Find a soil plot in the current area
        soil = next((obj for obj in self.player.current_area.objects if obj.has_tag("soil")), None)
        
        if not soil:
            return "There's no soil here to harvest from."
        
        # Get the soil component
        soil_component = soil.get_component("soil")
        if not soil_component:
            return "This soil can't be harvested from."
        
        # Find the plant in the soil
        plant = next((p for p in soil_component.plants if p.name.lower() == plant_name.lower()), None)
        
        if not plant:
            return f"There's no {plant_name} in the soil."
        
        # Get the plant component
        plant_component = plant.get_component("plant")
        if not plant_component:
            return f"You can't harvest the {plant.name}."
        
        # Harvest the plant
        result = plant_component.harvest()
        
        if result[0]:
            # Remove the plant from the soil
            soil_component.plants.remove(plant)
            
            # Add the harvested item to the player's inventory
            if len(result) > 2:
                harvested = result[2]
                
                inventory = self.player.get_component("inventory")
                if inventory:
                    inventory.add_item(harvested)
                    return f"{result[1]} It's added to your inventory."
                else:
                    # Add the harvested item to the current area
                    self.player.current_area.add_item(harvested)
                    return f"{result[1]} You drop it on the ground."
        
        return result[1]
    
    def cmd_hide(self, args):
        """Hide in a hiding spot."""
        if not args:
            return "Hide where?"
        
        if not self.player.current_area:
            return "There's nowhere to hide here."
        
        spot_name = " ".join(args).lower()
        
        # Find the hiding spot in the current area
        spot = next((obj for obj in self.player.current_area.objects if obj.name.lower() == spot_name.lower() and obj.has_component("hiding")), None)
        
        if not spot:
            return f"There's no {spot_name} to hide in."
        
        # Check if the player is already hidden
        if hasattr(self.player, 'is_hidden') and self.player.is_hidden:
            return "You're already hiding."
        
        # Hide the player
        hiding_component = spot.get_component("hiding")
        result = hiding_component.hide(self.player)
        
        if result[0]:
            self.player.is_hidden = True
            self.player.hiding_spot = spot
        
        return result[1]
    
    def cmd_unhide(self, args):
        """Stop hiding."""
        # Check if the player is hidden
        if not hasattr(self.player, 'is_hidden') or not self.player.is_hidden:
            return "You're not hiding."
        
        # Unhide the player
        hiding_component = self.player.hiding_spot.get_component("hiding")
        result = hiding_component.unhide(self.player)
        
        if result[0]:
            self.player.is_hidden = False
            self.player.hiding_spot = None
        
        return result[1]
    
    def cmd_hiding_spots(self, args):
        """List all hiding spots in the current area."""
        if not self.player.current_area:
            return "There are no hiding spots here."
        
        # Build the hiding spot list
        spots = []
        for obj in self.player.current_area.objects:
            if obj.has_component("hiding"):
                spots.append(f"- {obj}")
        
        if not spots:
            return "There are no hiding spots here."
        
        return "Hiding spots in this area:\n" + "\n".join(spots)
    
    def cmd_hack(self, args):
        """Hack a target."""
        if not args:
            return "Hack what?"
        
        target_name = " ".join(args).lower()
        
        # Find the target in the current area
        if not self.player.current_area:
            return "There's nothing here to hack."
        
        # Check for objects
        target = next((obj for obj in self.player.current_area.objects if obj.name.lower() == target_name.lower()), None)
        
        if not target:
            # Check for NPCs
            target = next((npc for npc in self.player.current_area.npcs if npc.name.lower() == target_name.lower()), None)
        
        if not target:
            return f"There's no {target_name} here to hack."
        
        # Find a tech item in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        tech_item = next((item for item in inventory.items if item.has_component("tech")), None)
        
        if not tech_item:
            # Check for hybrid items with tech functionality
            tech_item = next((item for item in inventory.items if item.is_hybrid and any(parent.has_component("tech") for parent in item.parent_entities)), None)
            
            if not tech_item:
                return "You don't have a tech item to hack with."
        
        # Get the tech component
        tech_component = tech_item.get_component("tech")
        if not tech_component:
            # Try to find a tech component in the hybrid item
            for component_type, component in tech_item.components.items():
                if hasattr(component, "component_type") and component.component_type == "tech":
                    tech_component = component
                    break
            
            if not tech_component:
                return f"You can't hack with the {tech_item.name}."
        
        # Check if the target can be hacked
        if not target.has_tag("hackable") and not target.has_tag("tech"):
            return f"The {target.name} can't be hacked."
        
        # Hack the target
        energy_cost = 20
        if not tech_component.use_energy(energy_cost):
            return f"Not enough energy in your {tech_item.name} to hack the {target.name}."
        
        return f"You hack the {target.name} with your {tech_item.name}."
    
    def cmd_run_program(self, args):
        """Run a program on a tech item."""
        if len(args) < 2:
            return "Run what program on what? Usage: run [program] on [target]"
        
        # Parse the command to extract program and target
        command = " ".join(args).lower()
        
        # Check for 'on' keyword
        if " on " in command:
            parts = command.split(" on ")
            program_name = parts[0].strip()
            target_name = parts[1].strip()
        else:
            return "Run what program on what? Usage: run [program] on [target]"
        
        # Find the target in the current area
        if not self.player.current_area:
            return "There's nothing here to run a program on."
        
        # Check for objects
        target = next((obj for obj in self.player.current_area.objects if obj.name.lower() == target_name.lower()), None)
        
        if not target:
            # Check for NPCs
            target = next((npc for npc in self.player.current_area.npcs if npc.name.lower() == target_name.lower()), None)
        
        if not target:
            return f"There's no {target_name} here to run a program on."
        
        # Find a tech item in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        tech_item = next((item for item in inventory.items if item.has_component("tech")), None)
        
        if not tech_item:
            # Check for hybrid items with tech functionality
            tech_item = next((item for item in inventory.items if item.is_hybrid and any(parent.has_component("tech") for parent in item.parent_entities)), None)
            
            if not tech_item:
                return "You don't have a tech item to run a program with."
        
        # Get the tech component
        tech_component = tech_item.get_component("tech")
        if not tech_component:
            # Try to find a tech component in the hybrid item
            for component_type, component in tech_item.components.items():
                if hasattr(component, "component_type") and component.component_type == "tech":
                    tech_component = component
                    break
            
            if not tech_component:
                return f"You can't run programs with the {tech_item.name}."
        
        # Run the program
        result = tech_component.run_program(program_name, target, self)
        
        return result[1]
    
    def cmd_recharge(self, args):
        """Recharge a tech item."""
        if not args:
            return "Recharge what?"
        
        item_name = " ".join(args).lower()
        
        # Find the item in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        item = inventory.get_item_by_name(item_name)
        
        if not item:
            return f"You don't have a {item_name}."
        
        # Check if the item has a tech component
        tech_component = item.get_component("tech")
        if not tech_component:
            # Check if it's a hybrid item with tech functionality
            if item.is_hybrid:
                for component_type, component in item.components.items():
                    if hasattr(component, "component_type") and component.component_type == "tech":
                        tech_component = component
                        break
            
            if not tech_component:
                return f"You can't recharge the {item.name}."
        
        # Recharge the item
        if tech_component.energy >= tech_component.max_energy:
            return f"The {item.name} is already fully charged."
        
        tech_component.recharge(tech_component.max_energy)
        
        return f"You recharge the {item.name} to full energy."
    
    def cmd_combine(self, args):
        """Combine two items to create a hybrid item."""
        if len(args) < 2:
            return "Combine what items? Usage: combine [item1] with [item2]"
        
        # Parse the command to extract item names
        command = " ".join(args).lower()
        
        # Check for 'with' keyword
        if " with " in command:
            parts = command.split(" with ")
            item1_name = parts[0].strip()
            item2_name = parts[1].strip()
        else:
            # Try to split at the first space
            parts = command.split(" ", 1)
            if len(parts) < 2:
                return "Combine what items? Usage: combine [item1] with [item2]"
            
            item1_name = parts[0].strip()
            item2_name = parts[1].strip()
        
        # Find the items in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        item1 = inventory.get_item_by_name(item1_name)
        item2 = inventory.get_item_by_name(item2_name)
        
        if not item1:
            return f"You don't have a {item1_name}."
        
        if not item2:
            return f"You don't have a {item2_name}."
        
        # Create a hybrid item
        hybrid = combine_items(item1, item2)
        
        # Remove the original items from the inventory
        inventory.remove_item(item1)
        inventory.remove_item(item2)
        
        # Add the hybrid item to the inventory
        inventory.add_item(hybrid)
        
        return f"You combine the {item1.name} and the {item2.name} to create a {hybrid.name}!"
    
    def cmd_examine(self, args):
        """Examine an item to see its components and functionality."""
        if not args:
            return "Examine what?"
        
        item_name = " ".join(args).lower()
        
        # Find the item in the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        item = inventory.get_item_by_name(item_name)
        
        if not item:
            # Check if it's an object in the current area
            if self.player.current_area:
                item = next((obj for obj in self.player.current_area.objects if obj.name.lower() == item_name.lower()), None)
            
            if not item:
                return f"You don't have a {item_name} and there's no {item_name} here."
        
        # Build the examination text
        examination = [f"You examine the {item.name}."]
        examination.append(item.description)
        
        if item.is_hybrid:
            examination.append("\nThis is a hybrid item created from:")
            for parent in item.parent_entities:
                examination.append(f"- {parent.name}")
        
        examination.append("\nFunctionality:")
        
        # List components and their functionality
        for component_type, component in item.components.items():
            if component_type == "inventory":
                examination.append(f"- Can store items (capacity: {component.capacity})")
            elif component_type == "weapon":
                examination.append(f"- Can be used as a weapon (damage: {component.damage})")
            elif component_type == "usable":
                examination.append(f"- Can be used")
            elif component_type == "breakable":
                examination.append(f"- Can be broken")
            elif component_type == "effect":
                effect_name = component.effect_type.__name__ if component.effect_type else "unknown"
                examination.append(f"- Can apply the {effect_name} effect")
            elif component_type == "gardening":
                examination.append(f"- Can perform gardening actions")
            elif component_type == "hiding":
                examination.append(f"- Can be used as a hiding spot (effectiveness: {component.effectiveness})")
            elif component_type == "tech":
                examination.append(f"- Can perform tech actions (energy: {component.energy}/{component.max_energy})")
            elif component_type == "seed":
                examination.append(f"- Can be planted to grow a {component.plant_type} plant")
            elif component_type == "plant":
                examination.append(f"- A {component.plant_type} plant at growth stage {component.growth_stage}/{component.max_growth}")
            elif component_type == "soil":
                examination.append(f"- Can be planted in (capacity: {component.capacity})")
            elif component_type == "watering_can":
                examination.append(f"- Can water plants (water: {component.current_water}/{component.water_capacity})")
            elif component_type == "storage":
                examination.append(f"- Can store items (capacity: {component.capacity}, items: {len(component.items)})")
                if component.locked:
                    examination.append(f"  - Currently locked")
                if component.restricted_tags:
                    examination.append(f"  - Restricted to: {', '.join(component.restricted_tags)}")
            elif hasattr(component, "component_type"):
                if component.component_type == "weapon":
                    examination.append(f"- Can be used as a weapon (damage: {component.damage})")
                elif component.component_type == "usable":
                    examination.append(f"- Can be used")
                elif component.component_type == "seed":
                    examination.append(f"- Can be planted to grow a plant")
                elif component.component_type == "watering_can":
                    examination.append(f"- Can water plants")
                elif component.component_type == "storage":
                    examination.append(f"- Can store items (capacity: {component.capacity}, items: {len(component.items)})")
        
        return "\n".join(examination)
    
    
    def cmd_store(self, args):
        """Store an item in a container."""
        if not args or len(args) < 3 or args[-2].lower() != "in":
            return "Usage: store [item] in [container]"
        
        # Parse the command
        container_name = args[-1].lower()
        item_name = " ".join(args[:-2]).lower()
        
        # Get the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        # Find the item in the player's inventory
        item = inventory.get_item_by_name(item_name)
        if not item:
            return f"You don't have a {item_name}."
        
        # Find the container in the player's inventory or in the current area
        container = inventory.get_item_by_name(container_name)
        if not container:
            # Check if the container is in the current area
            container = next((obj for obj in self.player.current_area.objects if obj.name.lower() == container_name), None)
            if not container:
                container = next((i for i in self.player.current_area.items if i.name.lower() == container_name), None)
                if not container:
                    return f"You don't see a {container_name} here."
        
        # Check if the container has a storage component
        storage_component = container.get_component("storage")
        if not storage_component:
            return f"The {container.name} is not a container."
        
        # Store the item
        result = storage_component.add_item(item)
        if result[0]:
            # Remove the item from the player's inventory
            inventory.remove_item(item)
            return result[1]
        else:
            return result[1]
    
    
    def cmd_retrieve(self, args):
        """Retrieve an item from a container."""
        if not args or len(args) < 3 or args[-2].lower() != "from":
            return "Usage: retrieve [item] from [container]"
        
        # Parse the command
        container_name = args[-1].lower()
        item_name = " ".join(args[:-2]).lower()
        
        # Get the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        # Find the container in the player's inventory or in the current area
        container = inventory.get_item_by_name(container_name)
        if not container:
            # Check if the container is in the current area
            container = next((obj for obj in self.player.current_area.objects if obj.name.lower() == container_name), None)
            if not container:
                container = next((i for i in self.player.current_area.items if i.name.lower() == container_name), None)
                if not container:
                    return f"You don't see a {container_name} here."
        
        # Check if the container has a storage component
        storage_component = container.get_component("storage")
        if not storage_component:
            return f"The {container.name} is not a container."
        
        # Find the item in the container
        item = storage_component.get_item_by_name(item_name)
        if not item:
            return f"There is no {item_name} in the {container.name}."
        
        # Check if the player's inventory has space
        if len(inventory.items) >= inventory.capacity:
            return "Your inventory is full."
        
        # Remove the item from the container
        result = storage_component.remove_item(item)
        if result[0]:
            # Add the item to the player's inventory
            inventory.add_item(item)
            return result[1]
        else:
            return result[1]
    
    
    def cmd_containers(self, args):
        """List all containers in the current area and in the player's inventory."""
        # Get the player's inventory
        inventory = self.player.get_component("inventory")
        if not inventory:
            return "You don't have an inventory."
        
        # Find containers in the player's inventory
        inventory_containers = [item for item in inventory.items if item.has_component("storage")]
        
        # Find containers in the current area
        area_containers = [obj for obj in self.player.current_area.objects if hasattr(obj, 'has_component') and obj.has_component("storage")]
        area_containers += [item for item in self.player.current_area.items if hasattr(item, 'has_component') and item.has_component("storage")]
        
        # Build the result message
        result = []
        
        if inventory_containers:
            result.append("Containers in your inventory:")
            for container in inventory_containers:
                storage = container.get_component("storage")
                result.append(f"- {container.name} ({len(storage.items)}/{storage.capacity} items)")
        
        if area_containers:
            if result:
                result.append("")
            result.append("Containers in the area:")
            for container in area_containers:
                storage = container.get_component("storage")
                result.append(f"- {container.name} ({len(storage.items)}/{storage.capacity} items)")
        
        if not result:
            return "You don't see any containers."
        
        return "\n".join(result)
    
    def cmd_help(self, args):
        """Show help information."""
        if not args:
            # Group commands by category
            categories = {}
            for cmd, info in self.commands.items():
                category = info.get('category', 'misc')
                if category not in categories:
                    categories[category] = []
                categories[category].append(cmd)
            
            # Build the help text
            help_text = ["Available commands:"]
            
            for category, cmds in categories.items():
                help_text.append(f"\n{category.capitalize()} commands:")
                help_text.append(", ".join(sorted(cmds)))
            
            help_text.append("\nType 'help [command]' for more information about a specific command.")
            
            return "\n".join(help_text)
        
        # Show help for a specific command
        cmd = args[0].lower()
        
        if cmd not in self.commands:
            return f"Unknown command: {cmd}"
        
        # Build the help text for the command
        help_text = [f"Help for '{cmd}':"]
        
        if cmd == 'move':
            help_text.append("Move in a direction (north, south, east, west).")
            help_text.append("Usage: move [direction]")
            help_text.append("Aliases: go, north, south, east, west")
        elif cmd == 'look':
            help_text.append("Look around the current area.")
            help_text.append("Usage: look")
        elif cmd == 'inventory':
            help_text.append("Show your inventory.")
            help_text.append("Usage: inventory")
            help_text.append("Aliases: inv")
        elif cmd == 'take':
            help_text.append("Take an item from the current area.")
            help_text.append("Usage: take [item]")
        elif cmd == 'drop':
            help_text.append("Drop an item from your inventory.")
            help_text.append("Usage: drop [item]")
        elif cmd == 'use':
            help_text.append("Use an item from your inventory.")
            help_text.append("Usage: use [item]")
        elif cmd == 'interact':
            help_text.append("Interact with an object in the current area.")
            help_text.append("Usage: interact [object]")
        elif cmd == 'combine':
            help_text.append("Combine two items to create a hybrid item.")
            help_text.append("Usage: combine [item1] with [item2]")
            help_text.append("Aliases: craft, merge")
        elif cmd == 'examine':
            help_text.append("Examine an item to see its components and functionality.")
            help_text.append("Usage: examine [item]")
        elif cmd == 'plant':
            help_text.append("Plant a seed in soil.")
            help_text.append("Usage: plant [seed]")
        elif cmd == 'water':
            help_text.append("Water plants in soil.")
            help_text.append("Usage: water")
        elif cmd == 'harvest':
            help_text.append("Harvest a plant from soil.")
            help_text.append("Usage: harvest [plant]")
        elif cmd == 'hide':
            help_text.append("Hide in a hiding spot.")
            help_text.append("Usage: hide [spot]")
        elif cmd == 'unhide':
            help_text.append("Stop hiding.")
            help_text.append("Usage: unhide")
            help_text.append("Aliases: emerge")
        elif cmd == 'attack':
            help_text.append("Attack an NPC in the current area.")
            help_text.append("Usage: attack [npc]")
        elif cmd == 'break':
            help_text.append("Break an object in the current area.")
            help_text.append("Usage: break [object]")
            help_text.append("Aliases: smash, shoot")
        elif cmd == 'hack':
            help_text.append("Hack a target.")
            help_text.append("Usage: hack [target]")
        elif cmd == 'run':
            help_text.append("Run a program on a tech item.")
            help_text.append("Usage: run [program] on [target]")
        elif cmd == 'recharge':
            help_text.append("Recharge a tech item.")
            help_text.append("Usage: recharge [item]")
        elif cmd == 'quit':
            help_text.append("Quit the game.")
            help_text.append("Usage: quit")
        
        return "\n".join(help_text)
    
    def cmd_quit(self, args):
        """Quit the game."""
        self.running = False
        return "Thanks for playing!"


# ----------------------------- #
# MAIN FUNCTION                 #
# ----------------------------- #

def main():
    """Main function."""
    # Create the game
    game = Game()
    
    # Create the player
    game.create_player()
    
    # Create the world
    game.create_world()
    
    # Run the game
    game.run()


if __name__ == "__main__":
    main()
