"""
Grid-based Game module for Root Access game.
This module defines the GridGame class which is the main entry point for the grid-based template.
"""

import random
import os
import sys

# Import game modules
from grid_player import GridPlayer
from grid_area import GridArea, Grid
from grid_world_builder import GridWorldBuilder

class GridGame:
    """Main game class for the grid-based template of Root Access."""
    
    def __init__(self):
        """Initialize the GridGame object."""
        self.player = None
        self.areas = {}
        self.current_turn = 0
        self.running = True
        
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
            
            # Basic interaction commands
            'look': {'handler': self.cmd_look, 'category': 'interaction'},
            'inventory': {'handler': self.cmd_inventory, 'category': 'interaction'},
            'inv': {'handler': self.cmd_inventory, 'category': 'interaction'},
            'take': {'handler': self.cmd_take, 'category': 'interaction'},
            'drop': {'handler': self.cmd_drop, 'category': 'interaction'},
            'use': {'handler': self.cmd_use, 'category': 'interaction'},
            'interact': {'handler': self.cmd_interact, 'category': 'interaction'},
            'npcs': {'handler': self.cmd_npcs, 'category': 'interaction'},
            
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
        world_builder = GridWorldBuilder(self)
        world_builder.build_world()
    
    def run(self):
        """Run the game loop."""
        print("Welcome to Root Access - Grid-Based Template")
        print("Type 'help' for a list of commands.")
        
        while self.running:
            command = input("> ")
            result = self.process_command(command)
            print(result)
    
    def process_command(self, command):
        """Process a player command."""
        command = command.lower().strip()
        parts = command.split()
        
        if not parts:
            return "Please enter a command."
        
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
        
        # Update NPCs (placeholder for future implementation)
        if hasattr(self.player.current_area, 'npcs'):
            for npc in self.player.current_area.npcs:
                if hasattr(npc, 'update'):
                    npc.update(self.player)
    
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
    
    def cmd_npcs(self, args):
        """Show information about NPCs in the current area."""
        if not hasattr(self.player.current_area, 'npcs') or not self.player.current_area.npcs:
            return "There are no NPCs in this area."
        
        npc_info = []
        for npc in self.player.current_area.npcs:
            info = f"{npc.name}: {npc.description}"
            
            # Add position information if NPC has coordinates
            if hasattr(npc, 'x') and hasattr(npc, 'y'):
                info += f"\n  Position: ({npc.x}, {npc.y})"
            
            npc_info.append(info)
        
        return "NPCs in this area:\n" + "\n\n".join(npc_info)
    
    def cmd_areas(self, args):
        """List all available areas."""
        area_list = ", ".join(sorted(self.areas.keys()))
        return f"Available areas: {area_list}"
    
    def cmd_position(self, args):
        """Show the player's current position."""
        if not self.player.current_area:
            return "You're not in any area."
        
        return f"You are in {self.player.current_area.name} at position ({self.player.x}, {self.player.y})."
    
    def cmd_help(self, args):
        """Show help information."""
        help_text = "Available commands:\n"
        
        # Group commands by category
        categories = {}
        for cmd, data in self.commands.items():
            category = data.get('category', 'misc')
            if category not in categories:
                categories[category] = []
            categories[category].append(cmd)
        
        # Display commands by category
        for category, cmds in categories.items():
            help_text += f"\n{category.capitalize()}:\n"
            help_text += "  " + ", ".join(sorted(cmds)) + "\n"
        
        return help_text
    
    def cmd_quit(self, args):
        """Quit the game."""
        self.running = False
        return "Thanks for playing!"
