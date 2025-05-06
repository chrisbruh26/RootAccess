"""
Grid-based Game module for Root Access game.
This module defines the GridGame class which is the main entry point for the grid-based version.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from grid_player import GridPlayer
    from grid_area import GridArea, Region
    from grid_structure import GridStructure, LockedRoom
    from items import Item, Weapon, Consumable, EffectItem, SmokeBomb, Decoy, Drone
    from objects import VendingMachine, Computer, HidingSpot
    from gardening import Seed, Plant, SoilPlot, WateringCan
    from effects import Effect, PlantEffect, SupervisionEffect, HackedPlantEffect, Substance, HackedMilk, HallucinationEffect, ConfusionEffect
    from npc_behavior import NPC, Civilian, Gang, GangMember, BehaviorType, BehaviorSettings, NPCBehaviorCoordinator, behavior_settings
    from random_events import RandomEventManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required modules are in the same directory.")
    sys.exit(1)

class GridGame:
    """Main game class for the grid-based version of Root Access."""
    
    def __init__(self):
        """Initialize the GridGame object."""
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
            'north': {'handler': self.cmd_move_direction, 'category': 'movement'},
            'south': {'handler': self.cmd_move_direction, 'category': 'movement'},
            'east': {'handler': self.cmd_move_direction, 'category': 'movement'},
            'west': {'handler': self.cmd_move_direction, 'category': 'movement'},
            'forward': {'handler': self.cmd_move_grid, 'category': 'movement'},
            'backward': {'handler': self.cmd_move_grid, 'category': 'movement'},
            'left': {'handler': self.cmd_move_grid, 'category': 'movement'},
            'right': {'handler': self.cmd_move_grid, 'category': 'movement'},
            'move': {'handler': self.cmd_move_grid, 'category': 'movement'},
            'go': {'handler': self.cmd_move_grid, 'category': 'movement'},
            'areas': {'handler': self.cmd_areas, 'category': 'movement'},
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
            'talk': {'handler': self.cmd_talk, 'category': 'interaction'},
            
            # Breaking mechanic commands
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
            
            # Structure commands
            'enter': {'handler': self.cmd_enter, 'category': 'interaction'},
            'unlock': {'handler': self.cmd_unlock, 'category': 'interaction'},
            
            # System commands
            'help': {'handler': self.cmd_help, 'category': 'system'},
            'quit': {'handler': self.cmd_quit, 'category': 'system'},
            'position': {'handler': self.cmd_position, 'category': 'system'},
        }
    
    def create_player(self):
        """Create the player object."""
        self.player = GridPlayer()
    
    def create_world(self):
        """Create the game world."""
        # Create player first
        self.create_player()
        
        # Use the WorldBuilder to create the world
        from grid_world_builder import GridWorldBuilder
        world_builder = GridWorldBuilder(self)
        world_builder.build_world()
        
        # Initialize the event manager
        self.event_manager = RandomEventManager(self)
    
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
    
    def update_turn(self):
        """Update the game state for a new turn."""
        self.current_turn += 1
        
        # Update player effects
        expired_effects = self.player.update_effects()
        for effect in expired_effects:
            print(f"The {effect} effect has worn off.")
        
        # Update NPCs
        self.npc_coordinator.update_npcs(self.player)
        
        # Update gang activity
        if self.player.current_area:
            self.player.current_area.handle_gang_activity(self.gangs)
        
        # Trigger random events
        if self.event_manager:
            self.event_manager.trigger_random_event()
    
    # Command handlers
    def cmd_move_direction(self, args):
        """Process movement command to change areas. Usage: north, south, east, west"""
        direction = args[0] if args else None
        if not direction:
            direction = self.commands[args[0]]['name'] if args else None
        
        if not direction:
            return "Move where? Specify a direction."
        
        result = self.player.change_area(direction)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_move_grid(self, args):
        """Process movement command within the grid. Usage: move [direction] or just [direction]"""
        if not args:
            return "Move where? Specify a direction (forward, backward, left, right)."
        
        direction = args[0].lower()
        
        # No need to convert directions, the move method handles both types
        result = self.player.move(direction)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_look(self, args):
        """Look around the current area."""
        return self.player.current_area.get_full_description(self.player)
    
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
        result = self.player.take_item(item_name)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_drop(self, args):
        """Drop an item from your inventory."""
        if not args:
            return "Drop what? Specify an item."
        item_name = " ".join(args)
        result = self.player.drop_item(item_name)
        if result[0]:
            self.update_turn()
        return result[1]
    
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
    
    def cmd_interact(self, args):
        """Interact with an object in the area."""
        if not args:
            return "Interact with what? Specify an object."
        object_name = " ".join(args)
        result = self.player.interact_with_object(object_name)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_talk(self, args):
        """Talk to an NPC in the area."""
        if not args:
            return "Talk to whom? Specify an NPC."
        npc_name = " ".join(args)
        result = self.player.talk_to_npc(npc_name)
        if result[0]:
            self.update_turn()
        return result[1]
    
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
            
            # Add position information if NPC has coordinates
            if hasattr(npc, 'x') and hasattr(npc, 'y'):
                info += f"\n  Position: ({npc.x}, {npc.y})"
            
            npc_info.append(info)
        
        return "NPCs in this area:\n" + "\n\n".join(npc_info)
    
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
        
        # Check if the player is close enough to the target
        if hasattr(target, 'x') and hasattr(target, 'y') and not self.player._is_near_coordinates(target.x, target.y):
            return f"You're not close enough to {target_name} to attack them."
        
        # Use the first weapon in inventory
        weapon = weapons[0]
        result = weapon.attack_npc(self.player, target)
        
        # Update turn after attack
        self.update_turn()
        
        return result[1]
    
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
        
        # Check if the player is close enough to the soil
        if hasattr(soil, 'x') and hasattr(soil, 'y') and not self.player._is_near_coordinates(soil.x, soil.y):
            return f"You're not close enough to the soil to plant seeds."
        
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
        
        # Check if the player is close enough to the soil
        if hasattr(soil, 'x') and hasattr(soil, 'y') and not self.player._is_near_coordinates(soil.x, soil.y):
            return f"You're not close enough to the soil to water plants."
        
        # Check if the player has a watering can
        watering_can = next((i for i in self.player.inventory if isinstance(i, WateringCan)), None)
        if not watering_can:
            return "You need a watering can to water plants."
        
        result = soil.water_plants()
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_harvest(self, args):
        """Harvest plants from soil."""
        soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, SoilPlot)), None)
        if not soil:
            return "There are no plants here to harvest."
        
        # Check if the player is close enough to the soil
        if hasattr(soil, 'x') and hasattr(soil, 'y') and not self.player._is_near_coordinates(soil.x, soil.y):
            return f"You're not close enough to the soil to harvest plants."
        
        result = soil.harvest_plants(self.player)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_hide(self, args):
        """Hide in a hiding spot."""
        if not args:
            return "Hide where? Specify a hiding spot."
        hiding_spot_name = " ".join(args)
        result = self.player.hide(hiding_spot_name)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_unhide(self, args):
        """Stop hiding."""
        result = self.player.unhide()
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_hiding_spots(self, args):
        """List all hiding spots in the current area."""
        hiding_spots = [obj for obj in self.player.current_area.objects if hasattr(obj, 'is_occupied')]
        if not hiding_spots:
            return "There are no hiding spots in this area."
        
        hiding_spot_info = []
        for spot in hiding_spots:
            info = f"{spot.name}: {spot.description}"
            if hasattr(spot, 'effectiveness'):
                info += f" (Effectiveness: {spot.effectiveness * 100}%)"
            if hasattr(spot, 'is_occupied') and spot.is_occupied:
                info += " (Occupied)"
            hiding_spot_info.append(info)
        
        return "Hiding spots in this area:\n" + "\n".join(hiding_spot_info)
    
    def cmd_hack(self, args):
        """Hack an object in the area."""
        if not args:
            return "Hack what? Specify an object."
        object_name = " ".join(args)
        
        # Find the object in the current area
        obj = next((o for o in self.player.current_area.hackable_objects if o.name.lower() == object_name.lower()), None)
        if not obj:
            return f"There is no {object_name} here to hack."
        
        # Check if the player is close enough to the object
        if hasattr(obj, 'x') and hasattr(obj, 'y') and not self.player._is_near_coordinates(obj.x, obj.y):
            return f"You're not close enough to the {object_name} to hack it."
        
        # Hack the object
        if hasattr(obj, 'hack'):
            result = obj.hack()
            if result[0]:
                self.update_turn()
            return result[1]
        
        return f"You can't hack the {object_name}."
    
    def cmd_run_program(self, args):
        """Run a program on a computer."""
        if not args:
            return "Run what? Specify a program."
        program_name = " ".join(args)
        
        # Find a computer in the current area
        computer = next((o for o in self.player.current_area.objects if isinstance(o, Computer)), None)
        if not computer:
            return "There is no computer here to run programs on."
        
        # Check if the player is close enough to the computer
        if hasattr(computer, 'x') and hasattr(computer, 'y') and not self.player._is_near_coordinates(computer.x, computer.y):
            return f"You're not close enough to the computer to use it."
        
        # Run the program
        if hasattr(computer, 'run_program'):
            result = computer.run_program(program_name, self.player)
            if result[0]:
                self.update_turn()
            return result[1]
        
        return "This computer can't run programs."
    
    def cmd_recharge(self, args):
        """Recharge a device."""
        if not args:
            return "Recharge what? Specify a device."
        device_name = " ".join(args)
        
        # Find the device in the player's inventory
        device = next((i for i in self.player.inventory if i.name.lower() == device_name.lower()), None)
        if not device:
            return f"You don't have a {device_name}."
        
        # Recharge the device
        if hasattr(device, 'recharge'):
            result = device.recharge()
            if result[0]:
                self.update_turn()
            return result[1]
        
        return f"You can't recharge the {device_name}."
    
    def cmd_break(self, args):
        """Break an object in the area."""
        if not args:
            return "Break what? Specify an object."
        object_name = " ".join(args)
        
        # Find the object in the current area
        obj = next((o for o in self.player.current_area.objects if o.name.lower() == object_name.lower()), None)
        if not obj:
            return f"There is no {object_name} here to break."
        
        # Check if the player is close enough to the object
        if hasattr(obj, 'x') and hasattr(obj, 'y') and not self.player._is_near_coordinates(obj.x, obj.y):
            return f"You're not close enough to the {object_name} to break it."
        
        # Break the object
        if hasattr(obj, 'break_object'):
            result = obj.break_object(self.player)
            if result[0]:
                self.update_turn()
            return result[1]
        
        return f"You can't break the {object_name}."
    
    def cmd_enter(self, args):
        """Enter a structure in the area."""
        if not args:
            return "Enter what? Specify a structure."
        structure_name = " ".join(args)
        
        # Find the structure in the current area
        structure = next((o for o in self.player.current_area.environment_objects 
                         if isinstance(o, GridStructure) and o.name.lower() == structure_name.lower()), None)
        if not structure:
            return f"There is no {structure_name} here to enter."
        
        # Check if the player is close enough to the structure
        if not structure.is_near(self.player):
            return f"You're not close enough to the {structure_name} to enter it."
        
        # Enter the structure
        result = structure.enter(self.player)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_unlock(self, args):
        """Unlock a structure in the area."""
        if not args:
            return "Unlock what? Specify a structure."
        structure_name = " ".join(args)
        
        # Find the structure in the current area
        structure = next((o for o in self.player.current_area.environment_objects 
                         if isinstance(o, GridStructure) and o.name.lower() == structure_name.lower()), None)
        if not structure:
            return f"There is no {structure_name} here to unlock."
        
        # Unlock the structure
        result = structure.unlock(self.player)
        if result[0]:
            self.update_turn()
        return result[1]
    
    def cmd_teleport(self, args):
        """Teleport to a different area."""
        if not args:
            return "Teleport where? Specify an area."
        area_name = " ".join(args)
        
        # Find the area
        area = next((a for a_name, a in self.areas.items() if a_name.lower() == area_name.lower()), None)
        if not area:
            return f"There is no area called {area_name}."
        
        # Teleport to the area
        self.player.current_area = area
        self.player.x = 0
        self.player.y = 0
        self.update_turn()
        return f"You teleport to {area.name}.\n\n{area.get_full_description(self.player)}"
    
    def cmd_position(self, args):
        """Show the player's current position."""
        if not self.player.current_area:
            return "You're not in any area."
        return f"Your current position is ({self.player.x}, {self.player.y}) in {self.player.current_area.name}."
    
    def cmd_help(self, args):
        """Show help information."""
        help_text = "Available commands:\n"
        
        # Group commands by category
        categories = {}
        for cmd_name, cmd_info in self.commands.items():
            category = cmd_info['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd_name)
        
        # Print commands by category
        for category, cmds in categories.items():
            help_text += f"\n{category.capitalize()}:\n"
            help_text += "  " + ", ".join(sorted(cmds)) + "\n"
        
        return help_text
    
    def cmd_quit(self, args):
        """Quit the game."""
        self.running = False
        return "Thanks for playing!"
    
    def run(self):
        """Run the game loop."""
        self.create_world()
        
        print("Welcome to Root Access: Grid Edition!")
        print("Type 'help' for a list of commands.")
        print(self.player.current_area.get_full_description(self.player))
        
        while self.running:
            command = input("> ")
            result = self.process_command(command)
            print(result)


if __name__ == "__main__":
    game = GridGame()
    game.run()
