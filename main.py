import random
import os
import json

# Import game modules
from items import Item, Weapon, Consumable, EffectItem, SmokeBomb, Decoy, Drone
from objects import VendingMachine
from gardening import Seed, Plant, SoilPlot, WateringCan
from effects import Effect, PlantEffect, SupervisionEffect, HackedPlantEffect, Substance, HackedMilk, HallucinationEffect, ConfusionEffect
from npc_behavior import NPC, Civilian, Gang, GangMember, BehaviorType, BehaviorSettings, NPCBehaviorCoordinator, behavior_settings
from objects import Computer, HidingSpot
from player import Player
from area import Area
from random_events import RandomEventManager
from world_builder import WorldBuilder
from crafting import CraftingSystem, initialize_crafting_system

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
        
        # Initialize crafting system
        self.crafting_system = initialize_crafting_system()
        
        # Weapon targeting system
        self.targeting_weapon = None
        self.targeting_npcs = None
        self.in_targeting_mode = False
        
        # Crafting system variables
        self.crafting_item1 = None
        self.crafting_item2 = None
        self.in_crafting_mode = False
        
        # Hybrid item choice system
        self.hybrid_item = None
        self.in_hybrid_choice_mode = False
        
        # Store command arguments for use by other methods
        self.process_command_args = []
        
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
            
            # Sub-area commands
            'enter': {'handler': self.cmd_enter_sub_area, 'category': 'movement'},
            'exit': {'handler': self.cmd_exit_sub_area, 'category': 'movement'},
            'sub_areas': {'handler': self.cmd_list_sub_areas, 'category': 'movement'},
            
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
            
            # NPC state commands
            'npc_states': {'handler': self.cmd_npc_states, 'category': 'interaction'},
            
            # Crafting commands
            'craft': {'handler': self.cmd_craft, 'category': 'crafting'},
            'recipes': {'handler': self.cmd_recipes, 'category': 'crafting'},
            'combine': {'handler': self.cmd_combine, 'category': 'crafting'},
            
            # System commands
            'help': {'handler': self.cmd_help, 'category': 'system'},
            'quit': {'handler': self.cmd_quit, 'category': 'system'},
        }

    def create_player(self):
        self.player = Player()
        
    def create_world(self):
        """
        Create the game world using the WorldBuilder.
        This method delegates world creation to the WorldBuilder class.
        """
        # Create player first
        self.create_player()
        
        # Use the WorldBuilder to create the world
        world_builder = WorldBuilder(self)
        world_builder.build_world()
        
    def process_command(self, command):
        """Process a player command."""
        command = command.lower().strip()
        parts = command.split()
        
        if not parts:
            return "Please enter a command."
        
        # Store the command parts for potential use by other methods
        self.process_command_args = parts
        
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
        
        # Check if we're in crafting mode (selecting second item)
        if self.in_crafting_mode and self.crafting_item1:
            # If user types 'cancel', exit crafting mode
            if command.lower() == 'cancel':
                self.crafting_item1 = None
                self.in_crafting_mode = False
                return "Crafting canceled."
                
            # Try to find the second item in inventory
            item_name = command
            item2 = next((item for item in self.player.inventory if item.name.lower() == item_name.lower()), None)
            
            if item2:
                # Combine the items
                result = self.crafting_system.combine_items(self.crafting_item1, item2, self.player.inventory)
                
                if result[0]:  # Success
                    # Remove the original items from inventory
                    self.player.inventory.remove(self.crafting_item1)
                    self.player.inventory.remove(item2)
                    
                    # Add the new item to inventory
                    self.player.add_item(result[2])
                    
                    # Reset crafting mode
                    self.crafting_item1 = None
                    self.in_crafting_mode = False
                    
                    # Update turn after crafting
                    self.update_turn()
                    
                    return result[1]
                else:
                    # Reset crafting mode
                    self.crafting_item1 = None
                    self.in_crafting_mode = False
                    
                    return result[1]
            else:
                return f"You don't have a {item_name} in your inventory.\nType the name of another item to combine with {self.crafting_item1.name}, or 'cancel' to stop."
        
        # Check if we're in hybrid item choice mode
        if self.in_hybrid_choice_mode and self.hybrid_item:
            # If user types 'cancel', exit hybrid choice mode
            if command.lower() == 'cancel':
                self.hybrid_item = None
                self.in_hybrid_choice_mode = False
                return "Action canceled."
                
            # Process the choice
            if hasattr(self.hybrid_item, 'health_restore') and command.lower() == 'consume':
                # Use as consumable
                if hasattr(self.hybrid_item, 'consume'):
                    result = self.hybrid_item.consume(self.player, self)
                else:
                    # For hybrid items that don't have a specific consume method
                    self.player.health = min(self.player.max_health, 
                                           self.player.health + self.hybrid_item.health_restore)
                    result = (True, f"You consume the {self.hybrid_item.name} and restore {self.hybrid_item.health_restore} health.")
                
                # Reset hybrid choice mode
                self.hybrid_item = None
                self.in_hybrid_choice_mode = False
                
                # Update turn after using
                self.update_turn()
                
                # Handle different result formats
                if isinstance(result, tuple) and len(result) >= 2:
                    return result[1]
                else:
                    return str(result)
                    
            elif hasattr(self.hybrid_item, 'effect') and command.lower() == 'effect':
                # Use for effect
                if hasattr(self.hybrid_item, 'apply_effect'):
                    result = self.hybrid_item.apply_effect(self.player, self)
                else:
                    # For hybrid items that don't have a specific apply_effect method
                    # Try to use the effect directly
                    effect_name = self.hybrid_item.effect.name if hasattr(self.hybrid_item.effect, 'name') else "unknown"
                    
                    # Apply effect to NPCs in the current area
                    messages = []
                    affected_npcs = []
                    
                    messages.append(f"You use the {self.hybrid_item.name} to apply its effect!")
                    
                    if self.player.current_area and self.player.current_area.npcs:
                        for npc in self.player.current_area.npcs:
                            # Skip dead NPCs
                            if hasattr(npc, 'is_alive') and not npc.is_alive:
                                continue
                                
                            # Apply the effect to the NPC
                            if hasattr(npc, 'active_effects'):
                                # Create a new instance of the effect for this NPC
                                effect_copy = type(self.hybrid_item.effect)()
                                npc.active_effects.append(effect_copy)
                                affected_npcs.append(npc)
                    
                        # Add the effect messages to the NPC coordinator
                        if self.npc_coordinator:
                            self.npc_coordinator.add_effect_messages(affected_npcs, self.hybrid_item.effect)
                        
                        # Add more detailed message about affected NPCs
                        if affected_npcs:
                            if len(affected_npcs) == 1:
                                messages.append(f"{affected_npcs[0].name} is affected by the {effect_name} effect!")
                            elif len(affected_npcs) <= 3:
                                npc_names = ", ".join(npc.name for npc in affected_npcs)
                                messages.append(f"{npc_names} are affected by the {effect_name} effect!")
                            else:
                                messages.append(f"Several NPCs are affected by the {effect_name} effect!")
                    
                    result = (True, "\n".join(messages))
                
                # Reset hybrid choice mode
                self.hybrid_item = None
                self.in_hybrid_choice_mode = False
                
                # Update turn after using
                self.update_turn()
                
                # Handle different result formats
                if isinstance(result, tuple) and len(result) >= 2:
                    return result[1]
                else:
                    return str(result)
            elif command.lower() == 'attack':
                # Use as weapon
                # Get a list of alive NPCs
                alive_npcs = [npc for npc in self.player.current_area.npcs if hasattr(npc, 'is_alive') and npc.is_alive]
                
                if alive_npcs:
                    # Set up targeting mode
                    self.targeting_weapon = self.hybrid_item
                    self.targeting_npcs = alive_npcs
                    
                    # Reset hybrid choice mode
                    self.hybrid_item = None
                    self.in_hybrid_choice_mode = False
                    
                    # Show available targets
                    npc_names = [npc.name for npc in alive_npcs]
                    npc_list = ", ".join(npc_names)
                    return f"You can target: {npc_list}\nType the name of the NPC you want to attack, or 'cancel' to stop."
                else:
                    # Reset hybrid choice mode
                    self.hybrid_item = None
                    self.in_hybrid_choice_mode = False
                    
                    return "There are no NPCs to attack here."
            else:
                return f"Invalid choice. Type 'attack', 'consume', 'effect', or 'cancel'."
        
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

    def cmd_enter_sub_area(self, args):
        """Enter a sub-area within the current area."""
        if not args:
            return "Enter where? Specify a sub-area."
        
        sub_area_name = " ".join(args)
        result = self.player.enter_sub_area(sub_area_name)
        
        if result[0]:
            self.update_turn()
            # Get the sub-area description
            return f"{result[1]}\n\n{self.player.current_area.get_full_description(self.player.current_sub_area)}"
        return result[1]
    
    def cmd_exit_sub_area(self, args):
        """Exit the current sub-area and return to the main area."""
        result = self.player.exit_sub_area()
        
        if result[0]:
            self.update_turn()
            # Get the main area description
            return f"{result[1]}\n\n{self.player.current_area.get_full_description()}"
        return result[1]
    
    def cmd_list_sub_areas(self, args):
        """List all sub-areas in the current area."""
        if not self.player.current_area or not self.player.current_area.sub_areas:
            return "There are no sub-areas here."
        
        sub_area_list = []
        for name, sub_area in self.player.current_area.sub_areas.items():
            sub_area_list.append(f"{sub_area.name}: {sub_area.description}")
        
        return "Sub-areas in this area:\n" + "\n".join(sub_area_list)
    
    def cmd_look(self, args):
        """Look around the current area or sub-area."""
        if not self.player.current_area:
            return "You are nowhere."
        
        return self.player.current_area.get_full_description(self.player.current_sub_area)

    def cmd_inventory(self, args):
        """Check your inventory."""
        if not self.player.inventory:
            return "Your inventory is empty."
        items = ", ".join(str(item) for item in self.player.inventory)
        return f"Inventory: {items}"

    def cmd_take(self, args):
        """Take an item from the area or sub-area."""
        if not args:
            return "Take what? Specify an item."
        
        item_name = " ".join(args)
        
        # Check if player is in a sub-area
        if self.player.current_sub_area:
            sub_area = self.player.current_area.get_sub_area(self.player.current_sub_area)
            if not sub_area:
                return "Error: Sub-area not found."
            
            item = sub_area.remove_item(item_name)
            if item:
                self.player.add_item(item)
                self.update_turn()
                return f"You take the {item.name}."
        else:
            # Player is in the main area
            item = self.player.current_area.remove_item(item_name)
            if item:
                self.player.add_item(item)
                self.update_turn()
                return f"You take the {item.name}."
        
        return f"There is no {item_name} here."

    def cmd_drop(self, args):
        """Drop an item from your inventory into the area or sub-area."""
        if not args:
            return "Drop what? Specify an item."
        
        item_name = " ".join(args)
        item = self.player.remove_item(item_name)
        
        if item:
            # Check if player is in a sub-area
            if self.player.current_sub_area:
                sub_area = self.player.current_area.get_sub_area(self.player.current_sub_area)
                if not sub_area:
                    # If sub-area not found, add to main area
                    self.player.current_area.add_item(item)
                else:
                    sub_area.add_item(item)
            else:
                # Player is in the main area
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
                
            # Add state information if NPC uses the state system
            if hasattr(npc, 'get_state') and npc.get_state() is not None:
                state = npc.get_state()
                state_desc = {
                    'silly': "peaceful and playful",
                    'aggressive': "hostile and dangerous",
                    'tech': "focused on technology",
                    'gardening': "tending to plants"
                }.get(state, state)
                info += f"\n  Current behavior: {state_desc}"
                
            npc_info.append(info)
            
        return "NPCs in this area:\n" + "\n\n".join(npc_info)

    def cmd_plant(self, args):
        """Plant a seed in soil."""
        if not args:
            return "Plant what? Specify a seed."
        seed_name = " ".join(args)
        
        # First try to find a regular seed
        seed = next((i for i in self.player.inventory if i.name.lower() == seed_name.lower() and isinstance(i, Seed)), None)
        
        # If not found, check for hybrid items with seed functionality
        if not seed:
            # Look for hybrid items with crop_type and growth_time attributes (seed properties)
            seed = next((i for i in self.player.inventory 
                        if hasattr(i, 'is_hybrid') and i.is_hybrid and 
                        hasattr(i, 'crop_type') and hasattr(i, 'growth_time') and
                        (seed_name.lower() in i.name.lower() or
                         (hasattr(i, 'parent1') and hasattr(i.parent1, 'name') and seed_name.lower() in i.parent1.name.lower()) or
                         (hasattr(i, 'parent2') and hasattr(i.parent2, 'name') and seed_name.lower() in i.parent2.name.lower()))), None)
        
        # If still not found, try a more flexible search for hybrid items
        if not seed:
            seed = next((i for i in self.player.inventory 
                        if hasattr(i, 'is_hybrid') and i.is_hybrid and 
                        (seed_name.lower() in i.name.lower())), None)
        
        if not seed:
            return f"You don't have a {seed_name}."
        
        # Check if it's a hybrid item
        is_hybrid = hasattr(seed, 'is_hybrid') and seed.is_hybrid
        
        # If it's a hybrid but doesn't have crop_type, it can't be planted
        if is_hybrid and not hasattr(seed, 'crop_type'):
            return f"The {seed.name} cannot be planted."
        
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
            # Only remove the item if it's not a hybrid
            if not is_hybrid:
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
        """Hack a computer or use a drone to hack an NPC.
        
        Usage:
        - 'hack' - Hack a computer in the current area
        - 'hack drone' - Deploy a hacking drone if you have one
        - 'hack [number]' - When drone is deployed, hack the NPC with the corresponding number
        - 'hack [number] [hack_type]' - Execute a specific hack type on the target
        - 'hack [number] behavior [state]' - Change an NPC's behavior state
        
        Available hack types:
        - message: Send fake threatening messages to rival gangs
        - confusion: Hack target's device to cause confusion
        - item: Make the target drop or use an item
        - behavior: Temporarily change the target's behavior
        
        Available behavior states:
        - silly: Make the NPC peaceful and playful
        - aggressive: Make the NPC hostile and dangerous
        - tech: Make the NPC focus on technology
        - gardening: Make the NPC tend to plants
        """
        # Check if args are provided
        if args:
            # Check if the player wants to use a drone
            if args[0].lower() == 'drone':
                # Find a drone in the player's inventory
                drone = next((item for item in self.player.inventory if item.__class__.__name__ == 'Drone'), None)
                if not drone:
                    return "You don't have a drone in your inventory."
                
                # Use the drone
                result = drone.use(self.player, self)
                if result[0]:
                    self.update_turn()
                return result[1]
            
            # Check if the player is trying to hack a specific target with a deployed drone
            try:
                target_index = int(args[0])
                # Find a deployed drone in the player's inventory
                drone = next((item for item in self.player.inventory 
                             if item.__class__.__name__ == 'Drone' and item.is_deployed), None)
                if not drone:
                    return "You need to deploy a drone first with 'hack drone'."
                
                # Check if a specific hack type was provided
                if len(args) > 1:
                    hack_type = args[1].lower()
                    
                    # Check if the hack type is valid
                    if not hasattr(drone, 'hack_types') or hack_type not in drone.hack_types:
                        valid_types = list(drone.hack_types.keys()) if hasattr(drone, 'hack_types') else []
                        return f"Invalid hack type. Available types: {', '.join(valid_types)}"
                    
                    # Get the target
                    if not hasattr(drone, 'available_targets') or len(drone.available_targets) < target_index:
                        return "Invalid target number."
                    
                    target = drone.available_targets[target_index - 1]
                    
                    # Execute the specific hack
                    result = drone._execute_hack(target, hack_type, self.player, self)
                else:
                    # No specific hack type, use the default hack_target method
                    result = drone.hack_target(target_index, self.player, self)
                
                if result[0]:
                    self.update_turn()
                return result[1]
            except ValueError:
                # Not a number, so not trying to hack a specific target
                return "Invalid hack command. Use 'hack', 'hack drone', or 'hack [number] [hack_type]'."
        
        # No args, try to hack a computer in the area
        computer = next((obj for obj in self.player.current_area.objects if isinstance(obj, Computer)), None)
        if not computer:
            # No computer found, check if player has a drone they could use
            drone = next((item for item in self.player.inventory if item.__class__.__name__ == 'Drone'), None)
            if drone:
                return "There's no computer here to hack. Try 'hack drone' to deploy your drone."
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
        # Check if user is asking for help with a specific command
        if args:
            cmd = args[0].lower()
            if cmd in self.commands:
                handler = self.commands[cmd]['handler']
                doc = handler.__doc__ or "No documentation available."
                return f"{cmd}: {doc}"
            else:
                return f"Unknown command: {cmd}. Type 'help' for a list of commands."
        
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
        
        # Add special note about NPC state commands
        help_text.append("\nNPC State System:")
        help_text.append("  Use 'npc_states' to view the current behavior states of NPCs in the area.")
        help_text.append("  Use 'hack [target number] behavior [state]' to hack an NPC's neural interface.")
        
        # Add information about crafting
        help_text.append("\nCrafting System:")
        help_text.append("  Use 'recipes' to view available crafting recipes.")
        help_text.append("  Use 'craft [recipe name]' to craft an item using a recipe.")
        help_text.append("  Use 'combine [item name]' to combine two items into a hybrid item.")
        
        help_text.append("\nNPC States:")
        help_text.append("  Available states: silly, aggressive, tech, gardening, craft")
        help_text.append("  Note: You need a deployed hacking drone to modify NPC behavior states.")
        
        help_text.append("\nType 'help [command]' for more information about a specific command.")
        
        return "\n".join(help_text)

    def cmd_quit(self, args):
        """Exit the game."""
        self.running = False
        
    def cmd_recharge(self, args):
        """Recharge tech items like drones.
        
        Usage:
        - 'recharge' - Recharge all tech items in your inventory
        - 'recharge [item name]' - Recharge a specific tech item
        """
        # Find all tech items in the player's inventory
        tech_items = [item for item in self.player.inventory 
                     if hasattr(item, 'is_electronic') and item.is_electronic]
        
        if not tech_items:
            return "You don't have any electronic devices to recharge."
        
        # If an item name is specified, try to recharge that specific item
        if args:
            item_name = " ".join(args).lower()
            item = next((item for item in tech_items if item.name.lower() == item_name), None)
            
            if not item:
                return f"You don't have a '{item_name}' to recharge."
            
            # Recharge the item
            result = item.recharge()
            self.update_turn()
            return result
        
        # Recharge all tech items
        messages = []
        for item in tech_items:
            messages.append(item.recharge())
        
        self.update_turn()
        return "\n".join(messages)
        
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
        
        # Update drone cooldowns
        for item in self.player.inventory:
            if isinstance(item, Drone) and hasattr(item, 'update'):
                item.update()
        
        # Check for random events (10% chance per turn)
        if random.random() < 0.1 and self.event_manager:
            self.event_manager.trigger_random_event()
        
        # Process NPC behaviors in the current area
        npc_messages = self.npc_coordinator.process_npc_behaviors(self, self.player.current_area.npcs)
        
        # Display NPC action summary
        npc_summary = self.npc_coordinator.get_npc_summary()
        if npc_summary:
            # If player is hidden, add a stealth indicator
            if self.player.hidden:
                print("\n[STEALTH MODE ACTIVE]")
            
            print("\n===== NPC ACTIONS =====")
            
            # Check if there are combat actions to display separately
            combat_keywords = [
                "attack", "damage", "defeat", "fight", "hostile", "punch", 
                "kick", "shoot", "stab", "hit", "battle", "combat", "weapon",
                "threatens", "ambush", "retaliate", "defend", "drag"
            ]
            
            has_combat = any(keyword in npc_summary.lower() for keyword in combat_keywords)
            
            if has_combat:
                print("COMBAT:")
                
                # Extract and print combat-related sentences
                # Split by both period and exclamation mark
                sentences = []
                current = ""
                for char in npc_summary:
                    current += char
                    if char in ['.', '!'] and current.strip():
                        sentences.append(current.strip())
                        current = ""
                
                # Add any remaining text
                if current.strip():
                    sentences.append(current.strip())
                
                combat_sentences = []
                other_sentences = []
                
                for sentence in sentences:
                    # Clean up the sentence
                    clean_sentence = sentence.strip()
                    if not clean_sentence:
                        continue
                        
                    # Make sure it ends with proper punctuation
                    if not clean_sentence.endswith('.') and not clean_sentence.endswith('!'):
                        clean_sentence += '.'
                        
                    # Categorize as combat or other
                    if any(keyword in clean_sentence.lower() for keyword in combat_keywords):
                        combat_sentences.append(clean_sentence)
                    else:
                        other_sentences.append(clean_sentence)
                
                # Print combat sentences
                for sentence in combat_sentences:
                    print(f"- {sentence}")
                
                # Print other actions if any
                if other_sentences:
                    print("\nOTHER ACTIONS:")
                    for sentence in other_sentences:
                        print(f"- {sentence}")
            else:
                # No combat, just print the summary
                print(npc_summary)
                
            print()
        
    # Random events have been moved to random_events.py
        
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
        
        # Initialize the event manager after the world is created
        self.event_manager = RandomEventManager(self)
        
        print(self.player.current_area.get_full_description())
        
        while self.running:
            command = input("\n> ")
            result = self.process_command(command)
            print(result)
            
            # Check if player is dead
            if self.player.health <= 0:
                self.respawn_player()
                continue


    def cmd_npc_states(self, args):
        """Show the current behavior states of NPCs in the area."""
        if not self.player.current_area.npcs:
            return "There are no NPCs in this area."
            
        # Filter for NPCs that use the state system
        state_npcs = [npc for npc in self.player.current_area.npcs 
                     if hasattr(npc, 'get_state') and npc.get_state() is not None]
        
        if not state_npcs:
            return "There are no NPCs with behavior states in this area."
            
        npc_state_info = []
        for npc in state_npcs:
            state = npc.get_state()
            state_desc = {
                'silly': "peaceful and playful",
                'aggressive': "hostile and dangerous",
                'tech': "focused on technology",
                'gardening': "tending to plants"
            }.get(state, state)
            
            npc_state_info.append(f"{npc.name} is currently {state_desc}.")
            
        return "NPC States:\n" + "\n".join(npc_state_info)
    



# ----------------------------- #
# CRAFTING COMMANDS             #
# ----------------------------- #

    def cmd_craft(self, args):
        """Craft an item using a recipe."""
        if not args:
            return "Craft what? Specify a recipe name or use 'recipes' to see available recipes."
        
        recipe_name = " ".join(args)
        result = self.crafting_system.craft_item(recipe_name, self.player.inventory)
        
        if result[0]:  # Success
            # Remove the ingredients from inventory
            for recipe in self.crafting_system.recipes:
                if recipe.name.lower() == recipe_name.lower():
                    can_craft, matching_items = recipe.can_craft(self.player.inventory)
                    if can_craft:
                        for item in matching_items:
                            self.player.inventory.remove(item)
                        break
            
            # Add the crafted item to inventory
            self.player.add_item(result[2])
            
            # Update turn after crafting
            self.update_turn()
            
            return result[1]
        else:
            return result[1]
    
    def cmd_recipes(self, args):
        """Show available recipes that can be crafted with current inventory."""
        available_recipes = self.crafting_system.get_available_recipes(self.player.inventory)
        
        if not available_recipes:
            return "You don't have the ingredients for any recipes. Try finding more items!"
        
        messages = ["Available recipes:"]
        for recipe in available_recipes:
            ingredients = ", ".join(recipe.ingredients)
            messages.append(f"- {recipe.name}: {recipe.description} (Requires: {ingredients})")
        
        return "\n".join(messages)
    
    def cmd_combine(self, args):
        """Combine two items to create a hybrid item."""
        if not args:
            return "Combine what? Specify the first item to combine."
        
        item_name = " ".join(args)
        item = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
        
        if not item:
            return f"You don't have a {item_name} in your inventory."
        
        # Set up crafting mode for the second item
        self.crafting_item1 = item
        self.in_crafting_mode = True
        
        return f"You selected {item.name} as the first item. What would you like to combine it with? (Type the name of another item in your inventory, or 'cancel' to stop)"

# ----------------------------- #
# MAIN ENTRY POINT              #
# ----------------------------- #

if __name__ == "__main__":
    game = Game()
    game.run()
