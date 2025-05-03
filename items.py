import random
from effects import HallucinationEffect, ConfusionEffect
import time

# ----------------------------- #
# ITEM CLASSES                  #
# ----------------------------- #

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
        
    def use(self, player, game):
        """Use the weapon, handling damage to NPCs and breaking objects."""
        messages = []
        messages.append(f"You use the {self.name}!")
        
        # Check if there are NPCs in the area to target
        if player.current_area and player.current_area.npcs:
            # Get a list of alive NPCs
            alive_npcs = [npc for npc in player.current_area.npcs if hasattr(npc, 'is_alive') and npc.is_alive]
            
            if alive_npcs:
                # Ask player which NPC to attack
                npc_names = [npc.name for npc in alive_npcs]
                npc_list = ", ".join(npc_names)
                messages.append(f"You can target: {npc_list}")
                messages.append("Type the name of the NPC you want to attack, or 'cancel' to stop.")
                
                # Return a special message that the game loop will handle to get player input
                return True, "\n".join(messages), "target_selection", alive_npcs
        
        # Check for breakable objects in the area
        if player.current_area and player.current_area.objects:
            # Find a breakable object that's not already broken
            from objects import VendingMachine
            breakable_objects = [obj for obj in player.current_area.objects 
                                if hasattr(obj, 'break_glass') and not obj.is_broken]
            
            if breakable_objects and random.random() < 0.3:  # 30% chance to break something
                obj = random.choice(breakable_objects)
                method = "shoot" if "gun" in self.name.lower() else "smash"
                
                if isinstance(obj, VendingMachine):
                    result = obj.break_glass(player, method)
                    if result[0]:
                        for item in result[2]:
                            player.current_area.add_item(item)
                        obj.items.clear()
                        messages.append(result[1])
                else:
                    result = obj.break_glass(player, method)
                    if result[0]:
                        messages.append(result[1])
        
        return True, "\n".join(messages)
        
    def attack_npc(self, player, target_npc):
        """Attack a specific NPC with this weapon."""
        messages = []
        
        # Calculate damage (random value between half and full damage)
        damage = random.randint(self.damage // 2, self.damage)
        
        # Apply damage to the target
        if hasattr(target_npc, 'health'):
            target_npc.health -= damage
            
            # Check if target died
            if target_npc.health <= 0:
                target_npc.is_alive = False
                if hasattr(target_npc, 'gang'):
                    target_npc.gang.remove_member(target_npc)
                messages.append(f"You attack {target_npc.name} with your {self.name} for {damage} damage, defeating them!")
            else:
                messages.append(f"You attack {target_npc.name} with your {self.name} for {damage} damage!")
                
                # If target is a gang member, they might become hostile
                if hasattr(target_npc, 'gang') and hasattr(player, 'detected_by'):
                    player.detected_by.add(target_npc.gang)
                    messages.append(f"The {target_npc.gang.name} are now hostile toward you!")
        else:
            # For NPCs without health attribute
            target_npc.is_alive = False
            messages.append(f"You attack and defeat {target_npc.name} with your {self.name}!")
            
        return True, "\n".join(messages)
    
class EffectItem(Item):
    def __init__(self, name, description, value, effect):
        super().__init__(name, description, value)
        self.effect = effect

    def __str__(self):
        return f"{self.name} ({self.effect.name} effect)"

    def use(self, player, game):
        """Use the effect item, applying its effect to NPCs in the current area."""
        messages = []
        affected_npcs = []
        
        messages.append(f"You use the {self.name}!")
        
        # Apply effect to NPCs in the current area
        if player.current_area and player.current_area.npcs:
            for npc in player.current_area.npcs:
                # Skip dead NPCs
                if hasattr(npc, 'is_alive') and not npc.is_alive:
                    continue
                    
                # Apply the effect to the NPC
                if hasattr(npc, 'active_effects'):
                    # Create a new instance of the effect for this NPC
                    effect_copy = type(self.effect)()
                    npc.active_effects.append(effect_copy)
                    affected_npcs.append(npc)

            # Add the effect messages to the NPC coordinator
            if game and game.npc_coordinator:
                game.npc_coordinator.add_effect_messages(affected_npcs, self.effect)
            
            # Add more detailed message about affected NPCs
            if affected_npcs:
                if len(affected_npcs) == 1:
                    messages.append(f"{affected_npcs[0].name} is affected by the {self.effect.name} effect!")
                elif len(affected_npcs) <= 3:
                    npc_names = ", ".join(npc.name for npc in affected_npcs)
                    messages.append(f"{npc_names} are affected by the {self.effect.name} effect!")
                else:
                    messages.append(f"Several NPCs are affected by the {self.effect.name} effect!")
        
        return True, "\n".join(messages)


class SmokeBomb(Item):
    def __init__(self):
        super().__init__("Smoke Bomb", "A device that creates a thick cloud of smoke, allowing for escape.", 30)
        
    def __str__(self):
        return f"{self.name} (Escape tool)"
        
    def use(self, player, game):
        """Use the smoke bomb to escape detection and possibly hide."""
        messages = []
        messages.append(f"You throw the {self.name} on the ground!")
        messages.append("A thick cloud of smoke fills the area!")
        
        # Clear all detection status
        player.detected_by.clear()
        
        # Apply confusion effect to all NPCs in the area
        affected_npcs = []
        for npc in player.current_area.npcs:
            if hasattr(npc, 'active_effects') and npc.is_alive:
                # Create a confusion effect
                confusion = ConfusionEffect()
                confusion.duration = 2  # Lasts for 2 turns
                confusion.remaining_turns = 2
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
                
                # Reset detection status for gang members
                if hasattr(npc, 'has_detected_player'):
                    npc.has_detected_player = False
                    npc.detection_cooldown = 3
        
        # Add effect messages to the NPC coordinator
        if affected_npcs and game and game.npc_coordinator:
            game.npc_coordinator.add_effect_messages(affected_npcs, ConfusionEffect())
            
        # Check if there are hiding spots in the area
        hiding_spots = [obj for obj in player.current_area.objects 
                       if hasattr(obj, 'hide') and not (hasattr(obj, 'is_occupied') and obj.is_occupied)]
        
        if hiding_spots:
            # Suggest hiding spots to the player
            spot_names = [spot.name for spot in hiding_spots]
            messages.append(f"You could hide in: {', '.join(spot_names)}")
            messages.append("Use 'hide [spot name]' to hide quickly!")
        else:
            messages.append("There are no hiding spots here, but the NPCs have lost track of you for now.")
            
        # Remove the smoke bomb from inventory after use
        player.inventory.remove(self)
        
        return True, "\n".join(messages)
        
        
class Decoy(Item):
    def __init__(self):
        super().__init__("Tech Decoy", "A small device that creates noise and light to distract NPCs.", 25)
        
    def __str__(self):
        return f"{self.name} (Distraction tool)"
        
    def use(self, player, game):
        """Use the decoy to distract NPCs and potentially escape detection."""
        messages = []
        messages.append(f"You activate the {self.name} and toss it away from you!")
        messages.append("It starts emitting flashing lights and beeping sounds.")
        
        # Chance to lose detection from each gang
        gangs_distracted = []
        for gang in list(player.detected_by):
            if random.random() < 0.7:  # 70% chance to distract each gang
                player.detected_by.remove(gang)
                gangs_distracted.append(gang.name)
                
                # Reset detection status for gang members
                for npc in player.current_area.npcs:
                    if hasattr(npc, 'gang') and npc.gang == gang and hasattr(npc, 'has_detected_player'):
                        npc.has_detected_player = False
                        npc.detection_cooldown = 2
        
        if gangs_distracted:
            messages.append(f"The {', '.join(gangs_distracted)} seem distracted by the decoy and have lost track of you!")
        
        # Apply a brief confusion effect to some NPCs
        affected_npcs = []
        for npc in player.current_area.npcs:
            if hasattr(npc, 'active_effects') and npc.is_alive and random.random() < 0.5:  # 50% chance
                # Create a confusion effect
                confusion = ConfusionEffect()
                confusion.duration = 1  # Lasts for 1 turn
                confusion.remaining_turns = 1
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
        
        # Add effect messages to the NPC coordinator
        if affected_npcs and game and game.npc_coordinator:
            game.npc_coordinator.add_effect_messages(affected_npcs, ConfusionEffect())
            
        # Remove the decoy from inventory after use
        player.inventory.remove(self)
        
        return True, "\n".join(messages)

class Consumable(Item):
    def __init__(self, name, description, value, health_restore):
        super().__init__(name, description, value)
        self.health_restore = health_restore

    def __str__(self):
        return f"{self.name} (Restores: {self.health_restore} health)"
    
    def use(self, player, game):
        """Use the consumable to restore health."""
        player.health = min(player.max_health, player.health + self.health_restore)
        player.inventory.remove(self)
        return True, f"You consume the {self.name} and restore {self.health_restore} health."


class TechItem(Item):
    """Base class for technology items that can be used for hacking and other tech operations."""
    def __init__(self, name, description, value, tech_type="generic"):
        super().__init__(name, description, value)
        self.tech_type = tech_type
        self.is_electronic = True
        self.battery = 100  # Battery percentage
        
    def __str__(self):
        return f"{self.name} (Tech type: {self.tech_type}, Battery: {self.battery}%)"
        
    def use_battery(self, amount):
        """Use some battery power. Returns True if successful, False if not enough battery."""
        if self.battery >= amount:
            self.battery -= amount
            return True
        return False
        
    def recharge(self, amount=100):
        """Recharge the battery by the specified amount."""
        self.battery = min(100, self.battery + amount)
        return f"{self.name} recharged to {self.battery}%."


class USBStick(TechItem):
    def __init__(self, name, description, value):
        super().__init__(name, description, value, "USB")
        # should probably have self.data = None or something to hold the data. USB sticks will usually have plant genetic code on them to hack the soil, maybe intel 
        self.data = None
        self.data_type = None  # Type of data on the USB stick (e.g., "plant genetic code", "intel")

    def __str__(self):
        return f"{self.name} (Data Type: {self.data_type})"
    
    def use(self, player, game):
        """Use the USB stick to hack the soil or access."""
        # Import here to avoid circular imports
        from gardening import SoilPlot
        
        # check if there is soil in the area by checking if isinstance of SoilPlot
        soil = next((obj for obj in player.current_area.objects if isinstance(obj, SoilPlot)), None)
        if not soil:
            return False, "There's no soil here to hack."
        # check for data on USB stick
        if not self.data:
            return False, "The USB stick is empty. You need to find data to hack the soil."
        # check if data is compatible with soil
        if self.data != "plant genetic code":
            return False, "This USB stick doesn't contain the right data to hack the soil."
        # make the soil produce a plant with special effects

        # cause the soil to produce a plant with effects based on the data on the USB stick


class Drone(TechItem):
    """A small drone that can be used for surveillance and hacking."""
    def __init__(self, name="Hacking Drone", description="A small drone equipped with hacking tools and a camera.", value=150):
        super().__init__(name, description, value, tech_type="Drone")
        self.is_deployed = False
        self.target = None
        self.cooldown = 0
        self.available_targets = []
        self.hack_types = {
            "message": {
                "name": "Fake Message Hack",
                "description": "Send fake threatening messages to rival gangs",
                "battery_cost": 20,
                "cooldown": 5
            },
            "confusion": {
                "name": "Confusion Hack",
                "description": "Hack target's device to cause confusion",
                "battery_cost": 15,
                "cooldown": 3
            },
            "item": {
                "name": "Item Manipulation Hack",
                "description": "Make the target drop or use an item",
                "battery_cost": 25,
                "cooldown": 4
            },
            "behavior": {
                "name": "Behavior Override Hack",
                "description": "Temporarily change the target's behavior",
                "battery_cost": 30,
                "cooldown": 6
            }
        }
        
    def __str__(self):
        status = "Deployed" if self.is_deployed else "Ready"
        return f"{self.name} ({status}, Battery: {self.battery}%)"
        
    def use(self, player, game):
        """Deploy the drone or recall it if already deployed."""
        if self.cooldown > 0:
            return False, f"The {self.name} is still cooling down. {self.cooldown} turns remaining."
            
        if not self.use_battery(10):
            return False, f"The {self.name} doesn't have enough battery power."
            
        if self.is_deployed:
            self.is_deployed = False
            self.target = None
            self.cooldown = 0  # Set cooldown after recalling, don't want any cooldown so 0 for now
            return True, f"You recall the {self.name}."
        else:
            self.is_deployed = True
            return True, self._deploy_drone(player, game)
            
    def _deploy_drone(self, player, game):
        """Deploy the drone and show available targets."""
        messages = []
        messages.append(f"You deploy the {self.name}.")
        messages.append("The drone hovers silently, awaiting your commands.")
        
        # Check for potential targets in the area - now includes all NPCs, not just gang members
        potential_targets = [npc for npc in player.current_area.npcs if npc.is_alive]
                       
        if not potential_targets:
            messages.append("There are no suitable targets for hacking in this area.")
            return "\n".join(messages)
            
        # List potential targets
        messages.append("\nPotential targets detected:")
        for i, npc in enumerate(potential_targets, 1):
            # Show gang affiliation if applicable
            if hasattr(npc, 'gang'):
                messages.append(f"{i}. {npc.name} ({npc.gang.name})")
            else:
                messages.append(f"{i}. {npc.name} (Civilian)")
            
        messages.append("\nUse 'hack [target number]' to hack a target.")
        
        # Store targets for later reference
        self.available_targets = potential_targets
        
        return "\n".join(messages)
        
    def hack_target(self, target_index, player, game):
        """Hack a target to trigger various effects."""
        if not self.is_deployed:
            return False, "The drone is not deployed."
            
        if not hasattr(self, 'available_targets') or not self.available_targets:
            return False, "No targets available."
            
        try:
            target_index = int(target_index) - 1
            if target_index < 0 or target_index >= len(self.available_targets):
                return False, "Invalid target number."
                
            target = self.available_targets[target_index]
            self.target = target
            
            # Show available hack types
            messages = []
            messages.append(f"Target locked: {target.name}")
            messages.append("\nAvailable hacks:")
            
            for hack_id, hack_info in self.hack_types.items():
                messages.append(f"- {hack_id}: {hack_info['name']} - {hack_info['description']} (Battery: {hack_info['battery_cost']}%)")
            
            messages.append("\nType 'hack [target number] [hack type]' to execute a specific hack.")
            messages.append("Example: 'hack 1 message' or 'hack 1 confusion'")
            
            # Show available hack options and let the main command handler deal with specific hack types
            
            # Show available hack options
            return True, "\n".join(messages)
            
        except ValueError:
            return False, "Invalid target number."
    
    def _execute_hack(self, target, hack_type, player, game):
        """Execute a specific type of hack on the target."""
        messages = []
        
        try:
            # Check if hack type exists
            if hack_type not in self.hack_types:
                return False, f"Unknown hack type: {hack_type}"
                
            hack_info = self.hack_types[hack_type]
            
            # Check battery
            if not self.use_battery(hack_info["battery_cost"]):
                return False, f"The drone doesn't have enough battery power. This hack requires {hack_info['battery_cost']}% battery."
                
            # Simulate hacking process
            messages.append(f"Executing {hack_info['name']} on {target.name}...")
            print(messages[-1])
            time.sleep(0.5)
            
            messages.append("Bypassing security...")
            print(messages[-1])
            time.sleep(0.5)
            
            # Execute the specific hack
            result = False
            
            try:
                if hack_type == "message" and hasattr(target, 'gang'):
                    result = self._execute_message_hack(target, game, messages)
                elif hack_type == "confusion":
                    result = self._execute_confusion_hack(target, game, messages)
                elif hack_type == "item":
                    result = self._execute_item_hack(target, game, messages)
                elif hack_type == "behavior":
                    result = self._execute_behavior_hack(target, game, messages)
                else:
                    messages.append("Hack failed: Incompatible target or hack type.")
                    result = False
            except Exception as e:
                messages.append(f"Hack failed: {str(e)}")
                result = False
                
            # Set cooldown
            self.cooldown = hack_info["cooldown"]
            
            # Recall the drone if hack was successful
            if result:
                self.is_deployed = False
                messages.append(f"Hack complete. {self.name} returning to you.")
            
            return result, "\n".join(messages)
            
        except Exception as e:
            # Catch any unexpected errors
            return False, f"Hack failed due to an unexpected error: {str(e)}"
    
    def _execute_message_hack(self, target, game, messages):
        """Execute a fake message hack to cause gang conflicts."""
        if not hasattr(target, 'gang'):
            messages.append("Hack failed: Target is not a gang member.")
            return False
            
        messages.append("Accessing messaging app...")
        print(messages[-1])
        time.sleep(0.5)
        
        # Find a rival gang
        rival_gangs = [gang for gang_name, gang in game.gangs.items() 
                      if gang.name != target.gang.name]
                      
        if not rival_gangs:
            messages.append("Hack failed: No rival gangs available.")
            return False
            
        rival_gang = random.choice(rival_gangs)
        
        # Send fake threatening message
        messages.append(f"Sending threatening message to {rival_gang.name} members...")
        print(messages[-1])
        time.sleep(0.5)
        
        messages.append("Message sent! The rival gang should arrive soon.")
        
        # Trigger the rival gang event
        from random_events import RandomEventManager
        event_manager = RandomEventManager(game)
        event_result = event_manager.event_rival_gang_appears(target.gang, target, forced=True)
        
        if event_result:
            messages.append(event_result)
        
        return True
    
    def _execute_confusion_hack(self, target, game, messages):
        """Execute a confusion hack to disorient the target."""
        messages.append("Accessing device settings...")
        print(messages[-1])
        time.sleep(0.5)
        
        messages.append("Overriding sensory inputs...")
        print(messages[-1])
        time.sleep(0.5)
        
        # Apply confusion effect to the target
        if hasattr(target, 'active_effects'):
            from effects import ConfusionEffect
            confusion = ConfusionEffect()
            confusion.duration = 3  # Lasts for 3 turns
            confusion.remaining_turns = 3
            target.active_effects.append(confusion)
            
            # Add effect messages to the NPC coordinator
            if game and game.npc_coordinator:
                game.npc_coordinator.add_effect_messages([target], confusion)
                
            messages.append(f"{target.name} is now confused and disoriented!")
            
            # If target is a gang member, they might lose track of the player
            if hasattr(target, 'has_detected_player'):
                target.has_detected_player = False
                target.detection_cooldown = 3
                messages.append(f"{target.name} has lost track of you.")
                
            return True
        else:
            messages.append("Hack failed: Target cannot be affected by confusion.")
            return False
    
    def _execute_item_hack(self, target, game, messages):
        """Execute an item hack to make the target use or drop an item."""
        messages.append("Accessing neural interface...")
        print(messages[-1])
        time.sleep(0.5)
        
        # Check if target has items - NPCs use 'items' attribute, not 'inventory'
        target_items = []
        if hasattr(target, 'items') and target.items:
            target_items = target.items
        elif hasattr(target, 'inventory') and target.inventory:
            target_items = target.inventory
            
        if target_items:
            # Choose a random item from the target's items
            item = random.choice(target_items)
            
            # 50% chance to make them use the item, 50% to make them drop it
            if random.random() < 0.5 and hasattr(item, 'use'):
                messages.append(f"Sending 'use item' command to {target.name}...")
                print(messages[-1])
                time.sleep(0.5)
                
                # Make the NPC use the item
                if hasattr(item, 'use'):
                    try:
                        # Try to use the item - handle different parameter requirements
                        if hasattr(item.use, '__code__') and 'game' in item.use.__code__.co_varnames:
                            result = item.use(target, game)
                        else:
                            # Try with just the target first
                            try:
                                result = item.use(target)
                            except TypeError:
                                # If that fails, try with both target and game
                                result = item.use(target, game)
                            
                        messages.append(f"{target.name} suddenly uses their {item.name}!")
                        
                        # If the item has effects, apply them
                        if hasattr(item, 'effect'):
                            # Add active_effects attribute if it doesn't exist
                            if not hasattr(target, 'active_effects'):
                                target.active_effects = []
                            
                            # Clone the effect to avoid sharing the same effect instance
                            if hasattr(item.effect, '__class__'):
                                from copy import deepcopy
                                effect_copy = deepcopy(item.effect)
                                target.active_effects.append(effect_copy)
                            else:
                                target.active_effects.append(item.effect)
                                
                            messages.append(f"{target.name} is affected by the {item.name}!")
                    except Exception as e:
                        # If there's an error using the item, provide a fallback message
                        messages.append(f"{target.name} tries to use {item.name} but something goes wrong.")
            else:
                messages.append(f"Sending 'drop item' command to {target.name}...")
                print(messages[-1])
                time.sleep(0.5)
                
                # Make the NPC drop the item
                if hasattr(target, 'items'):
                    target.items.remove(item)
                elif hasattr(target, 'inventory'):
                    target.inventory.remove(item)
                    
                # Add the item to the area - NPCs use 'location' attribute
                if hasattr(target, 'location') and target.location is not None:
                    if hasattr(target.location, 'add_item'):
                        target.location.add_item(item)
                    elif hasattr(target.location, 'items'):
                        # Fallback if add_item method doesn't exist
                        target.location.items.append(item)
                    messages.append(f"{target.name} suddenly drops their {item.name}!")
                else:
                    # If we can't determine the location, just remove the item
                    messages.append(f"{target.name} suddenly loses their {item.name}!")
                
            return True
        else:
            messages.append("Hack failed: Target has no items to manipulate.")
            return False
    
    def _execute_behavior_hack(self, target, game, messages):
        """Execute a behavior hack to temporarily change the target's behavior."""
        try:
            messages.append("Accessing behavioral subroutines...")
            print(messages[-1])
            time.sleep(0.5)
            
            messages.append("Overriding decision matrix...")
            print(messages[-1])
            time.sleep(0.5)
            
            # Import BehaviorType
            from npc_behavior import BehaviorType
            
            # Check if target has behavior settings or add them
            if not hasattr(target, 'behavior_type'):
                # If NPC doesn't have a behavior type, assign a default one
                target.behavior_type = BehaviorType.IDLE
                messages.append(f"Installing behavior module in {target.name}...")
                print(messages[-1])
                time.sleep(0.5)
            
            # Store original behavior
            original_behavior = target.behavior_type
            
            # Choose a random new behavior that's different from the current one
            available_behaviors = [BehaviorType.IDLE, BehaviorType.TALK, BehaviorType.FIGHT, 
                                  BehaviorType.USE_ITEM, BehaviorType.TECH, BehaviorType.SUSPICIOUS]
            
            # Remove current behavior from options
            if original_behavior in available_behaviors:
                available_behaviors.remove(original_behavior)
            
            new_behavior = random.choice(available_behaviors)
            
            # Apply the new behavior
            target.behavior_type = new_behavior
            
            # Set a timer to revert back (5 turns)
            if not hasattr(target, 'behavior_override_timer'):
                target.behavior_override_timer = 0
            target.behavior_override_timer = 5
            target.original_behavior = original_behavior
            
            # Get a readable name for the behavior
            behavior_names = {
                BehaviorType.IDLE: "Idle",
                BehaviorType.TALK: "Talkative",
                BehaviorType.FIGHT: "Aggressive",
                BehaviorType.USE_ITEM: "Item User",
                BehaviorType.GARDENING: "Gardener",
                BehaviorType.TECH: "Tech Expert",
                BehaviorType.SUSPICIOUS: "Suspicious"
            }
            
            behavior_name = behavior_names.get(new_behavior, new_behavior)
            messages.append(f"{target.name}'s behavior has been changed to {behavior_name}!")
            
            # Add a method to the target to revert behavior after timer expires
            def update_behavior_override(self_target):
                try:
                    if hasattr(self_target, 'behavior_override_timer') and self_target.behavior_override_timer > 0:
                        self_target.behavior_override_timer -= 1
                        if self_target.behavior_override_timer == 0 and hasattr(self_target, 'original_behavior'):
                            self_target.behavior_type = self_target.original_behavior
                            delattr(self_target, 'original_behavior')
                except Exception:
                    # Silently fail if there's an error in the update
                    pass
            
            # Add the method to the target if it doesn't already have it
            if not hasattr(target, 'update_behavior_override'):
                target.update_behavior_override = update_behavior_override.__get__(target)
                
                # Monkey patch the target's update method to call our new method
                original_update = target.update if hasattr(target, 'update') else lambda self, game: None
                
                def new_update(self, game):
                    try:
                        original_update(self, game)
                        self.update_behavior_override()
                    except Exception:
                        # Silently fail if there's an error in the update
                        pass
                
                target.update = new_update.__get__(target)
                
            # Add active_effects attribute if it doesn't exist
            if not hasattr(target, 'active_effects'):
                target.active_effects = []
                
            return True
            
        except Exception as e:
            # If anything goes wrong, provide a fallback message
            messages.append(f"Hack attempt failed: {str(e)}")
            return False
    
    def update(self):
        """Update the drone state each turn."""
        if self.cooldown > 0:
            self.cooldown -= 1
