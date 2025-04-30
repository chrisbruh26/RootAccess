import random
import os
import json

# Import game modules
from items import Item, Weapon, Consumable
from gardening import Seed, Plant, SoilPlot
from effects import Effect, PlantEffect, SupervisionEffect, HackedPlantEffect, Substance, HackedMilk, HallucinationEffect, ConfusionEffect
from npc_behavior import NPC, Civilian, Gang, GangMember, BehaviorType, BehaviorSettings, NPCBehaviorCoordinator, behavior_settings
from objects import Computer
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
        
        # Add objects to areas
        soil_plot = SoilPlot()
        self.areas["garden"].add_object(soil_plot)
        self.areas["warehouse"].add_object(soil_plot)
        
        computer = Computer("Hacking Terminal", "A specialized terminal for hacking operations.")
        computer.programs = ["data_miner", "security_override", "plant_hacker"]
        self.areas["Home"].add_object(computer)
        
        # Add items to areas
        self.areas["Home"].add_item(Item("Backpack", "A sturdy backpack for carrying items.", 20))
        self.areas["garden"].add_item(Seed("Tomato Seed", "A seed for growing tomatoes.", "tomato", 5))
        self.areas["garden"].add_item(Seed("Potato Seed", "A seed for growing potatoes.", "potato", 5))
        self.areas["street"].add_item(Consumable("Energy Drink", "A caffeinated beverage that restores health.", 10, 20))
        self.areas["alley"].add_item(Weapon("Pipe", "A metal pipe that can be used as a weapon.", 15, 10))
        
        # create better weapons

        # Hacked Milk Blaster - causes hallucinations
        hacked_milk_blaster = Weapon("Hacked Milk Blaster", "A strange weapon that shoots hacked milk.", 50, 20)
        hacked_milk_blaster.add_effect(HallucinationEffect())
        self.areas["warehouse"].add_item(hacked_milk_blaster)
        
        # Confusion Ray - causes confusion
        confusion_ray = Weapon("Confusion Ray", "A device that emits waves that confuse the target.", 60, 15)
        confusion_ray.add_effect(ConfusionEffect())
        self.areas["alley"].add_item(confusion_ray)
        self.areas["Home"].add_item(hacked_milk_blaster)




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

        for i in range(5):
            name = random.choice(bloodhounds_names)
            bloodhounds_names.remove(name)
            self.areas["warehouse"].add_npc(GangMember(name, f"A member of the Bloodhounds named {name}.", self.gangs["Bloodhounds"]))
            self.areas["warehouse"].add_item(Seed("Carrot Seed", "A seed for growing carrot.", "carrot", 5))

        



        self.areas["warehouse"].add_npc(Civilian("John", "A random guy."))

        self.areas["warehouse"].add_item(Seed("Carrot Seed", "A seed for growing carrot.", "carrot", 5))




        self.areas["garden"].add_npc(Civilian("Gardener", "A friendly gardener tending to the plants."))


        # Set player's starting location
        self.player.current_area = self.areas["Home"]
        
    def process_command(self, command):
        """Process a player command."""
        command = command.lower().strip()
        parts = command.split()
        
        if not parts:
            return "Please enter a command."
        
        action = parts[0]
        
        # Movement commands
        if action in self.player.current_area.connections:
            self.player.current_area = self.player.current_area.connections[action]
            self.update_turn()
            return f"You move {action} to {self.player.current_area.name}.\n\n{self.player.current_area.get_full_description()}"
        
        # Look command
        if action == "look":
            return self.player.current_area.get_full_description()
        
        # Inventory command
        if action == "inventory" or action == "inv":
            if not self.player.inventory:
                return "Your inventory is empty."
            items = ", ".join(str(item) for item in self.player.inventory)
            return f"Inventory: {items}"
        
        # Take command
        if action == "take" and len(parts) > 1:
            item_name = " ".join(parts[1:])
            item = self.player.current_area.remove_item(item_name)
            if item:
                self.player.add_item(item)
                self.update_turn()
                return f"You take the {item.name}."
            return f"There is no {item_name} here."
        
        # Drop command
        if action == "drop" and len(parts) > 1:
            item_name = " ".join(parts[1:])
            item = self.player.remove_item(item_name)
            if item:
                self.player.current_area.add_item(item)
                self.update_turn()
                return f"You drop the {item.name}."
            return f"You don't have a {item_name}."
        
        # Use command
        if action == "use" and len(parts) > 1:
            item_name = " ".join(parts[1:])
            result = self.player.use_item(item_name, self)
            if result[0]:
                self.update_turn()
                return result[1]
            return result[1]
        
        # Interact with objects
        if action == "interact" and len(parts) > 1:
            object_name = " ".join(parts[1:])
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
        
        # Plant-specific commands
        if action == "plant" and len(parts) > 1:
            seed_name = " ".join(parts[1:])
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
        
        if action == "water":
            soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, SoilPlot)), None)
            if not soil:
                return "There are no plants here to water."
            
            result = soil.water_plants()
            if result[0]:
                self.update_turn()
            return result[1]
        
        if action == "harvest" and len(parts) > 1:
            plant_name = " ".join(parts[1:])
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
        
        # Areas command - list all available areas
        if action == "areas":
            area_list = ", ".join(sorted(self.areas.keys()))
            return f"Available areas for teleportation: {area_list}"
            
        # NPC info command - show information about NPCs in the current area
        if action == "npcs":
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
            
        # Teleport command
        if action == "teleport" and len(parts) > 1:
            area_name = " ".join(parts[1:])
            # Find the area by name (case-insensitive)
            target_area = next((area for name, area in self.areas.items() 
                               if name.lower() == area_name.lower()), None)
            
            if not target_area:
                # Try partial matching if exact match fails
                target_area = next((area for name, area in self.areas.items() 
                                   if area_name.lower() in name.lower()), None)
                
            if not target_area:
                return f"No area named '{area_name}' found. Available areas: {', '.join(sorted(self.areas.keys()))}"
            
            # Teleport the player
            self.player.current_area = target_area
            self.update_turn()
            return f"You teleport to {target_area.name}.\n\n{target_area.get_full_description()}"
        
        # Computer-specific commands
        if action == "hack":
            computer = next((obj for obj in self.player.current_area.objects if isinstance(obj, Computer)), None)
            if not computer:
                return "There's no computer here to hack."
            
            result = computer.hack(self.player)
            if result[0]:
                self.update_turn()
            return result[1]
        
        if action == "run" and len(parts) > 1:
            program_name = " ".join(parts[1:])
            computer = next((obj for obj in self.player.current_area.objects if isinstance(obj, Computer)), None)
            if not computer:
                return "There's no computer here to run programs on."
            
            result = computer.run_program(program_name, self.player, self)
            if result[0]:
                self.update_turn()
            return result[1]
        
        # Help command
        if action == "help":
            return """Available commands:
- [direction] (north, south, east, west): Move in that direction
- teleport [area]: Instantly teleport to any area by name
- areas: List all available areas for teleportation
- npcs: Show information about NPCs in the current area
- look: Look around the current area
- inventory/inv: Check your inventory
- take [item]: Take an item from the area
- drop [item]: Drop an item from your inventory
- use [item]: Use an item from your inventory
- interact [object]: Interact with an object in the area
- plant [seed]: Plant a seed in soil
- water: Water plants in soil
- harvest [plant]: Harvest a fully grown plant
- hack: Hack a computer
- run [program]: Run a program on a hacked computer
- help: Show this help message
- quit: Exit the game"""
        
        # Quit command
        if action == "quit":
            self.running = False
            return "Thanks for playing!"
        
        return "Unknown command. Type 'help' for a list of commands."
    
    def update_turn(self):
        """Update the game state for a new turn."""
        self.current_turn += 1
        
        # Update player effects
        expired_effects = self.player.update_effects()
        if expired_effects:
            print(f"Effects expired: {', '.join(expired_effects)}")
        
        # Process NPC behaviors in the current area
        npc_messages = self.npc_coordinator.process_npc_behaviors(self, self.player.current_area.npcs)
        
        # Display NPC action summary
        npc_summary = self.npc_coordinator.get_npc_summary()
        if npc_summary:
            print("\nNPC ACTIONS:")
            print(npc_summary)
            print()
            
        # Update plants in all areas
        for area_name, area in self.areas.items():
            for obj in area.objects:
                if hasattr(obj, 'plants'):
                    for plant in obj.plants:
                        if hasattr(plant, 'grow') and random.random() < 0.3:  # 30% chance to grow each turn
                            plant.grow()
    
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
                print("You have been defeated! Game over.")
                self.running = False


# ----------------------------- #
# MAIN ENTRY POINT              #
# ----------------------------- #

if __name__ == "__main__":
    game = Game()
    game.run()
