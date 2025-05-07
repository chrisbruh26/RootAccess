import random
import json
import os
from effects import Effect, HallucinationEffect, ConfusionEffect
from objects import VendingMachine

# ----------------------------- #
# NPC BEHAVIOR SYSTEM           #
# ----------------------------- #

class NPC:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.relationship = 0
        self.items = []
        self.location = None  # Main area
        self.sub_location = None  # Sub-area within the main area
        self.is_alive = True
        self.actions_this_turn = 0  # Tracks the number of actions this NPC has taken in the current turn

    def reset_actions(self):
        """Reset the actions counter for the NPC at the start of a new turn."""
        self.actions_this_turn = 0

    def add_item(self, item):
        """Add an item to NPC's inventory, checking if it has the necessary attributes of an Item."""
        # Instead of using isinstance, check for essential Item attributes
        # This avoids circular import issues
        if hasattr(item, 'name') and hasattr(item, 'description'):
            self.items.append(item)
            return True
        else:
            # For debugging - this should rarely happen in normal gameplay
            print(f"Warning: {self.name} tried to add an invalid object to inventory: {item}")
            return False

    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
            
    def craft_item(self, crafting_system):
        """
        Attempt to craft an item using the crafting system.
        
        Args:
            crafting_system: The game's crafting system
            
        Returns:
            tuple: (bool, str, Item) - Success status, message, and the crafted item
        """
        # Check if NPC has enough items to craft anything
        if len(self.items) < 2:
            return False, f"{self.name} doesn't have enough items to craft anything.", None
        
        # First try to craft using recipes
        available_recipes = crafting_system.get_available_recipes(self.items)
        
        if available_recipes:
            # Choose a random recipe
            recipe = random.choice(available_recipes)
            
            # Craft the item
            can_craft, matching_items = recipe.can_craft(self.items)
            if can_craft:
                crafted_item = recipe.craft(matching_items)
                
                # Remove the ingredients from inventory
                for item in matching_items:
                    self.items.remove(item)
                
                # Add the crafted item to inventory
                self.add_item(crafted_item)
                
                return True, f"{self.name} crafted a {crafted_item.name}!", crafted_item
        
        # If no recipes available, try random combination
        if len(self.items) >= 2:
            # Choose two random items
            item1, item2 = random.sample(self.items, 2)
            
            # Combine the items
            result = crafting_system.combine_items(item1, item2, self.items)
            
            if result[0]:  # Success
                # Remove the original items from inventory
                self.items.remove(item1)
                self.items.remove(item2)
                
                # Add the new item to inventory
                self.add_item(result[2])
                
                return True, f"{self.name} combined {item1.name} and {item2.name} to create {result[2].name}!", result[2]
        
        return False, f"{self.name} couldn't craft anything useful.", None

    def enter_sub_area(self, sub_area_name):
        """Enter a sub-area within the current area."""
        if not self.location:
            return False, f"{self.name} is not in any area."
        
        sub_area = self.location.get_sub_area(sub_area_name)
        if not sub_area:
            return False, f"There is no sub-area called '{sub_area_name}' here."
        
        # Remove from current location (main area or sub-area)
        if self.sub_location:
            # Currently in a sub-area, remove from there
            self.sub_location.remove_npc(self)
        else:
            # Currently in main area, remove from there
            self.location.remove_npc(self)
        
        # Add to new sub-area
        sub_area.add_npc(self)
        
        return True, f"{self.name} enters the {sub_area.name}."
    
    def exit_sub_area(self):
        """Exit the current sub-area and return to the main area."""
        if not self.sub_location or not self.location:
            return False, f"{self.name} is not in a sub-area."
        
        sub_area_name = self.sub_location.name
        
        # Remove from sub-area
        self.sub_location.remove_npc(self)
        
        # Add to main area
        self.location.add_npc(self)
        
        return True, f"{self.name} exits the {sub_area_name} and returns to the main area."

    def apply_hazard_effect(self, hazard):
        """Default hazard effect application for NPCs that do not have specific implementation."""
        # By default, NPCs are unaffected by hazards
        return "nothing happens" #f"{self.name} is unaffected by the {hazard.name}."


class Civilian(NPC):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.is_injured = False
        self.is_arrested = False
        self.is_fighting = False # two NPCs will be randomly selected to fight each other during a random event
        self.emotion = None # none if feeling neutral, can be confused if weird chaos events happen
        self.needs_help = False # random events might occur where NPC needs help, such as being mugged


# Scalable Gang class to manage gang name and members
class Gang:
    def __init__(self, name):
        self.name = name
        self.members = []

    def add_member(self, gang_member):
        self.members.append(gang_member)

    def remove_member(self, gang_member):
        if gang_member in self.members:
            self.members.remove(gang_member)

    def list_members(self):
        return [member.name for member in self.members]


# Scalable GangMember class inheriting from NPC
class GangMember(NPC):
    def __init__(self, name, description, gang):
        super().__init__(name, description)
        self.gang = gang
        self.health = 100
        self.is_alive = True
        self.detection_chance = 0.05  # 5% base chance to detect player
        self.has_detected_player = False
        self.detection_cooldown = 0
        self.active_effects = []  # List of active effects
        self.hazard_resistance = 50  # Base 50% chance to resist hazard effects
        self.gang.add_member(self)
        
        # Initialize state manager with default 'silly' state
        from npc_states import NPCStateManager
        self.state_manager = NPCStateManager(default_state='silly')

    def update_effects(self):
        """Update active effects and remove expired ones."""
        expired_effects = []
        for effect in self.active_effects:
            if effect.update():  # Returns True if expired
                expired_effects.append(effect)
        
        # Remove expired effects
        for effect in expired_effects:
            self.active_effects.remove(effect)
            
        return expired_effects

    def die(self):
        if self.health <= 0 and self.is_alive:
            self.is_alive = False
            self.gang.remove_member(self)
            return f"{self.name} has been defeated!"
        return None
        
    def set_state(self, state_name):
        """
        Manually set the NPC's behavior state.
        
        Args:
            state_name: The name of the state to set ('silly', 'aggressive', 'tech', 'gardening')
            
        Returns:
            True if successful, False if the state doesn't exist or NPC doesn't use state system
        """
        if hasattr(self, 'state_manager'):
            return self.state_manager.force_state(state_name)
        return False
        
    def get_state(self):
        """
        Get the NPC's current behavior state.
        
        Returns:
            The name of the current state, or None if NPC doesn't use state system
        """
        if hasattr(self, 'state_manager'):
            return self.state_manager.get_current_state_name()
        return None

    def attack_player(self, player):
        # If player is hidden, can't attack
        if player.hidden:
            return None
            
        # Check if NPC is hallucinating - can't attack while hallucinating
        if any(hasattr(effect, 'affects_combat') and effect.affects_combat() for effect in self.active_effects):
            # Get a hallucination message if available
            for effect in self.active_effects:
                if hasattr(effect, 'get_combat_prevention_message'):
                    return f"{self.name} {effect.get_combat_prevention_message()} instead of attacking you."
                elif hasattr(effect, 'get_hallucination_message'):
                    return f"{self.name} {effect.get_hallucination_message()} instead of attacking you."
            return f"{self.name} is too distracted to attack you."
        
        # Check if this gang has detected the player
        if self.gang not in player.detected_by:
            # Can't attack if haven't detected
            return None
            
        # Simple combat logic
        damage = random.randint(5, 15)
        player.health -= damage
        return f"{self.name} attacks you for {damage} damage!"

    def attack_npc(self, target_npc):
        # Simple NPC-to-NPC combat
        if not target_npc.is_alive or not self.is_alive:
            return None
            
        # Check if NPC is hallucinating - can't attack while hallucinating
        if any(hasattr(effect, 'affects_combat') and effect.affects_combat() for effect in self.active_effects):
            # Get a hallucination message if available
            for effect in self.active_effects:
                if hasattr(effect, 'get_combat_prevention_message'):
                    return f"{self.name} {effect.get_combat_prevention_message()} instead of attacking {target_npc.name}."
                elif hasattr(effect, 'get_hallucination_message'):
                    return f"{self.name} {effect.get_hallucination_message()} instead of attacking {target_npc.name}."
            return f"{self.name} is too distracted to attack {target_npc.name}."
        
        # check type of each npc and compare, only allowing them to attack each other if different types, like different gang
        

        # if npc is not a gang member, or target npc is not a gang member, return None. elif they're both gang members but same gang, return None
        if not isinstance(target_npc, GangMember):
            return None
        elif self.gang.name == target_npc.gang.name:
            return None

            
        damage = random.randint(5, 15)
        
        # Apply damage to target
        if hasattr(target_npc, 'health'):
            target_npc.health -= damage
            
            # Check if target died
            if target_npc.health <= 0:
                target_npc.is_alive = False
                if hasattr(target_npc, 'gang'):
                    target_npc.gang.remove_member(target_npc)
                return f"{self.name} attacks {target_npc.name} for {damage} damage, defeating them!"
            
            return f"{self.name} attacks {target_npc.name} for {damage} damage!"
        else:
            # For NPCs without health attribute
            target_npc.is_alive = False
            return f"{self.name} attacks and defeats {target_npc.name}!"

    def detect_player(self, player, game):
        """Attempt to detect the player based on detection chance."""
        # Skip detection if already detected or on cooldown
        if self.has_detected_player or self.detection_cooldown > 0:
            return None
            
        # Check if NPC is hallucinating - can't detect player while hallucinating
        if any(hasattr(effect, 'affects_combat') and effect.affects_combat() for effect in self.active_effects):
            # Get a hallucination message if available
            for effect in self.active_effects:
                if hasattr(effect, 'get_hallucination_message'):
                    return f"{self.name} {effect.get_hallucination_message()}."
            return None
        
        # If player is hidden, drastically reduce detection chance
        if player.hidden:
            # Calculate stealth bonus from hiding spot
            stealth_bonus = 0
            if player.hiding_spot:
                stealth_bonus = player.hiding_spot.stealth_bonus
                
            # Almost impossible to detect when hidden
            modified_detection_chance = self.detection_chance * (1 - stealth_bonus)
            
            # Very small chance to detect even when hidden
            if random.random() < modified_detection_chance * 0.1:  # 10% of already reduced chance
                self.has_detected_player = True
                player.detected_by.add(self.gang)
                
                # Force player out of hiding
                player.hidden = False
                if player.hiding_spot:
                    player.hiding_spot.is_occupied = False
                    player.hiding_spot.occupant = None
                player.hiding_spot = None
                
                # Set a cooldown before the NPC can detect again if the player escapes
                self.detection_cooldown = 3
                
                return f"{self.name} discovers your hiding spot and drags you out!"
            
            # Most of the time, hidden players aren't detected
            return None
            
        # Base detection chance for non-hidden players
        detection_roll = random.random()
        
        if detection_roll < self.detection_chance:
            self.has_detected_player = True
            player.detected_by.add(self.gang)
            
            # Set a cooldown before the NPC can detect again if the player escapes
            self.detection_cooldown = 3
            
            return f"{self.name} spots you and becomes hostile!"
        
        return None


# ----------------------------- #
# NPC BEHAVIOR MANAGEMENT       #
# ----------------------------- #

class BehaviorType:
    """Types of NPC behaviors."""
    IDLE = "idle"
    TALK = "talk"
    FIGHT = "fight"
    USE_ITEM = "use_item"
    GARDENING = "gardening"
    GIFT = "gift"
    TECH = "tech"
    SUSPICIOUS = "suspicious"
    ENTER_SUB_AREA = "enter_sub_area"
    EXIT_SUB_AREA = "exit_sub_area"
    CRAFT = "craft"  # New behavior type for crafting


class BehaviorSettings:
    """Global settings for NPC behavior frequencies."""
    def __init__(self):
        # Default behavior weights
        self.default_weights = {
            BehaviorType.IDLE: 0.2,     # 20% chance for idle behavior
            BehaviorType.TALK: 0.3,     # 30% chance for talking
            BehaviorType.FIGHT: 0.1,    # 10% chance for fighting
            BehaviorType.USE_ITEM: 0.3, # 30% chance for using items
            BehaviorType.GARDENING: 0.3,# 10% chance for gardening
            BehaviorType.GIFT: 0.0,     # 0% base chance for gifting (boosted by effects)
            BehaviorType.ENTER_SUB_AREA: 0.2, # 20% chance for entering sub-areas
            BehaviorType.EXIT_SUB_AREA: 0.1,  # 10% chance for exiting sub-areas
            BehaviorType.CRAFT: 0.2,    # 20% chance for crafting items
        }
        
        # Behavior frequency multipliers (1.0 = normal frequency, 0.5 = half frequency, 0.0 = disabled)
        self.frequency_multipliers = {
            BehaviorType.IDLE: 1.0,
            BehaviorType.TALK: 1.0,
            BehaviorType.FIGHT: 0.1,
            BehaviorType.USE_ITEM: 1.0,
            BehaviorType.GARDENING: 5.0,
            BehaviorType.GIFT: 1.0,
            BehaviorType.ENTER_SUB_AREA: 2.0, # Higher frequency for entering sub-areas
            BehaviorType.EXIT_SUB_AREA: 1.0,  # Normal frequency for exiting sub-areas
            BehaviorType.CRAFT: 1.5,          # Higher frequency for crafting
        }
        
        # Behavior cooldowns (in turns)
        self.cooldowns = {
            BehaviorType.IDLE: 1,      # 1 turn between idle behaviors
            BehaviorType.TALK: 2,      # 2 turns between talking
            BehaviorType.FIGHT: 3,     # 3 turns between fighting
            BehaviorType.CRAFT: 4,     # 4 turns between crafting attempts
            BehaviorType.USE_ITEM: 1,  # 1 turn between using items
            BehaviorType.GARDENING: 2, # 2 turns between gardening activities
            BehaviorType.GIFT: 5,      # 5 turns between gifting
            BehaviorType.ENTER_SUB_AREA: 2, # 2 turns between entering sub-areas
            BehaviorType.EXIT_SUB_AREA: 3,  # 3 turns between exiting sub-areas
        }
        
        # Last turn each behavior was performed (per NPC)
        self.last_behavior_turn = {}
        
        # Global switch to disable all NPC behaviors
        self.npcs_enabled = True
    
    def get_adjusted_weights(self, npc):
        """Get behavior weights adjusted by frequency multipliers."""
        # Start with default weights
        weights = self.default_weights.copy()
        
        # Apply frequency multipliers
        for behavior_type, multiplier in self.frequency_multipliers.items():
            if behavior_type in weights:
                weights[behavior_type] *= multiplier
        
        return weights
    
    def can_perform_behavior(self, npc, behavior_type, current_turn):
        """Check if an NPC can perform a behavior based on cooldowns."""
        # Get the NPC's last behavior times
        npc_id = id(npc)
        if npc_id not in self.last_behavior_turn:
            self.last_behavior_turn[npc_id] = {}
        
        # If behavior has never been performed, allow it
        if behavior_type not in self.last_behavior_turn[npc_id]:
            return True
        
        # Check if cooldown has elapsed
        cooldown = self.cooldowns.get(behavior_type, 0)
        last_turn = self.last_behavior_turn[npc_id].get(behavior_type, 0)
        
        return (current_turn - last_turn) >= cooldown
    
    def record_behavior(self, npc, behavior_type, current_turn):
        """Record that an NPC performed a behavior."""
        npc_id = id(npc)
        if npc_id not in self.last_behavior_turn:
            self.last_behavior_turn[npc_id] = {}
        
        self.last_behavior_turn[npc_id][behavior_type] = current_turn
    
    def set_frequency(self, behavior_type, frequency):
        """Set the frequency multiplier for a behavior type."""
        if behavior_type in self.frequency_multipliers:
            self.frequency_multipliers[behavior_type] = frequency
    
    def set_cooldown(self, behavior_type, cooldown):
        """Set the cooldown for a behavior type."""
        if behavior_type in self.cooldowns:
            self.cooldowns[behavior_type] = cooldown


# Create a global instance of BehaviorSettings
behavior_settings = BehaviorSettings()


class NPCBehaviorCoordinator:
    """Manages NPC behaviors and enforces limits on actions per turn."""
    def __init__(self, max_npc_actions_per_turn=10, max_actions_per_npc=2):
        self.max_npc_actions_per_turn = max_npc_actions_per_turn
        self.max_actions_per_npc = max_actions_per_npc
        self.npc_cooldowns = {}  # Tracks cooldowns for specific NPC behaviors
        self.current_turn = 0
        self.action_messages = []  # Stores NPC action messages for the current turn
        
        # Load NPC actions from JSON file
        self.actions_data = self._load_actions_data()

    def _load_actions_data(self):
        """Load NPC actions from JSON file."""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_dir, 'npc_actions.json')
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return default actions if file not found or invalid
            return {
                "idle": {
                    "singular": ["stands around looking bored", "checks their phone"],
                    "plural": ["stand around looking bored", "check their phones"]
                },
                "talk": {
                    "singular": ["talks with someone nearby", "whispers something"],
                    "plural": ["talk with others", "whisper something"]
                },
                "fight": {
                    "singular": ["looks for trouble", "clenches their fists"],
                    "plural": ["look for trouble", "clench their fists"]
                }
            }

    def process_npc_behaviors(self, game, npcs):
        """
        Process NPC behaviors for the current turn, enforcing limits.

        Args:
            game: The main game instance.
            npcs: List of NPCs in the current area.

        Returns:
            A list of messages generated by NPC actions.
        """
        self.action_messages = []
        actions_taken = 0

        # Reset actions for all NPCs at the start of the turn
        for npc in npcs:
            if hasattr(npc, 'reset_actions'):
                npc.reset_actions()

        # Shuffle NPCs to randomize action order
        random_npcs = npcs.copy()
        random.shuffle(random_npcs)

        for npc in random_npcs:
            if actions_taken >= self.max_npc_actions_per_turn:
                break  # Stop if we've reached the max actions for this turn

            # Skip NPCs that are on cooldown or have already acted
            if self._is_on_cooldown(npc) or npc.actions_this_turn >= self.max_actions_per_npc:
                continue

            # Let the NPC take an action
            result = self._process_npc_action(npc, game)
            if result:
                self.action_messages.append(result)
                actions_taken += 1
                npc.actions_this_turn += 1

                # Apply cooldown to the NPC
                self._apply_cooldown(npc)

        # Increment turn counter
        self.current_turn += 1
        
        # Decrement cooldowns at the end of the turn
        self.decrement_cooldowns()

        return self.action_messages

    def _process_npc_action(self, npc, game):
        """Process a single NPC action based on their type and state."""
        # Skip dead NPCs
        if not npc.is_alive:
            return None
            
        # Check for behavior override from hacking
        if hasattr(npc, 'behavior_override_timer') and npc.behavior_override_timer > 0:
            # Update the behavior override timer
            if hasattr(npc, 'update_behavior_override'):
                npc.update_behavior_override()
        
        # Process GangMember specific behaviors using the state pattern
        if isinstance(npc, GangMember) and hasattr(npc, 'state_manager'):
            # Update effects first
            if hasattr(npc, 'update_effects'):
                npc.update_effects()
            
            # Use the state manager to determine behavior
            return npc.state_manager.update(npc, game)
        
        # Legacy behavior for NPCs without state manager
        elif isinstance(npc, GangMember):
            # Update effects
            if hasattr(npc, 'update_effects'):
                npc.update_effects()
                
            # Check for effects that affect behavior
            is_affected = False
            if hasattr(npc, 'active_effects'):
                for effect in npc.active_effects:
                    # Check for hallucination effect
                    if isinstance(effect, HallucinationEffect) or (hasattr(effect, 'get_hallucination_message') and hasattr(effect, 'affects_combat') and effect.affects_combat()):
                        is_affected = True
                        return f"{npc.name} {effect.get_hallucination_message()}."
                    
                    # Check for confusion effect
                    elif isinstance(effect, ConfusionEffect) or (hasattr(effect, 'get_confusion_message') and hasattr(effect, 'affects_combat')):
                        # Confusion may or may not prevent combat
                        if effect.affects_combat():
                            is_affected = True
                            return f"{npc.name} {effect.get_confusion_message()}."
            
            # If affected by an effect that prevents combat, skip combat behaviors
            if is_affected:
                return None
                
            # Check for player detection
            if hasattr(npc, 'detect_player') and game.player.current_area == npc.location:
                detection_result = npc.detect_player(game.player, game)
                if detection_result:
                    return detection_result
                    
            # If player is detected, chance to attack
            if hasattr(game.player, 'detected_by') and npc.gang in game.player.detected_by:
                if random.random() < 0.9:  # 90% chance to attack if detected
                    return npc.attack_player(game.player)
                    
            # Chance to attack other gang members
            if random.random() < 0.4:  # 40% chance to check for enemies
                # Find other gang members in the same area
                other_gang_members = [other for other in npc.location.npcs 
                                     if isinstance(other, GangMember) 
                                     and other.gang != npc.gang
                                     and other.is_alive]
                                     
                if other_gang_members:
                    target = random.choice(other_gang_members)
                    return npc.attack_npc(target)
        
        # General NPC behaviors - check for behavior_type to influence actions
        
        # Check for sub-area behaviors first
        if hasattr(npc, 'location') and npc.location:
            # Chance to enter a sub-area if NPC is in the main area
            if not npc.sub_location and npc.location.sub_areas:
                if random.random() < 0.3:  # 30% chance to enter a sub-area
                    # Choose a random sub-area
                    sub_area_name = random.choice(list(npc.location.sub_areas.keys()))
                    result = npc.enter_sub_area(sub_area_name)
                    if result[0]:
                        # If player is in the same main area, show the message
                        if game.player.current_area == npc.location and not game.player.current_sub_area:
                            return result[1]
                        return None  # Don't show message if player is not in the same area
            
            # Chance to exit a sub-area if NPC is in a sub-area
            elif npc.sub_location:
                if random.random() < 0.2:  # 20% chance to exit a sub-area
                    sub_area_name = npc.sub_location.name
                    result = npc.exit_sub_area()
                    if result[0]:
                        # If player is in the same main area, show the message
                        if game.player.current_area == npc.location and not game.player.current_sub_area:
                            return result[1]
                        # If player is in the same sub-area, show a different message
                        elif game.player.current_area == npc.location and game.player.current_sub_area == sub_area_name.lower():
                            return f"{npc.name} leaves the {sub_area_name}."
                        return None  # Don't show message if player is not in the same area
        
        # If NPC has a behavior_type, use it to influence their actions
        if hasattr(npc, 'behavior_type'):
            from npc_behavior import BehaviorType
            
            # Aggressive behavior - more likely to attack or threaten
            if npc.behavior_type == BehaviorType.FIGHT:
                # Find a target NPC in the same area or sub-area
                potential_targets = []
                
                if npc.sub_location:
                    # NPC is in a sub-area, find targets in the same sub-area
                    potential_targets = [other for other in npc.sub_location.npcs 
                                        if other != npc and other.is_alive]
                else:
                    # NPC is in the main area, find targets in the main area
                    potential_targets = [other for other in npc.location.npcs 
                                        if other != npc and other.is_alive]
                                    
                if potential_targets and random.random() < 0.7:  # 70% chance to be aggressive
                    target = random.choice(potential_targets)
                    
                    # Check if they have a weapon
                    weapons = [item for item in npc.items if hasattr(item, 'damage')]
                    if weapons:
                        weapon = random.choice(weapons)
                        return f"{npc.name} threatens {target.name} with {weapon.name}!"
                    else:
                        return f"{npc.name} aggressively confronts {target.name}!"
            
            # Tech behavior - more likely to use tech items or hack
            elif npc.behavior_type == BehaviorType.TECH:
                tech_items = [item for item in npc.items if hasattr(item, 'is_electronic') and item.is_electronic]
                if tech_items and random.random() < 0.8:  # 80% chance to use tech
                    item = random.choice(tech_items)
                    return f"{npc.name} fiddles with their {item.name}."
                else:
                    return f"{npc.name} scans the area with a small device."
                    
            # Crafting behavior - attempt to craft items
            elif npc.behavior_type == BehaviorType.CRAFT:
                if hasattr(npc, 'craft_item') and len(npc.items) >= 2:
                    # Attempt to craft an item
                    result = npc.craft_item(game.crafting_system)
                    if result[0]:  # Success
                        return result[1]
                    else:
                        # If crafting failed, show a message about the attempt
                        return f"{npc.name} tries to combine some items but fails."
            
            # Suspicious behavior - more likely to watch others or hide
            elif npc.behavior_type == BehaviorType.SUSPICIOUS:
                if random.random() < 0.7:  # 70% chance for suspicious behavior
                    if npc.location.npcs and len(npc.location.npcs) > 1:
                        other_npcs = [other for other in npc.location.npcs if other != npc]
                        if other_npcs:
                            target = random.choice(other_npcs)
                            return f"{npc.name} watches {target.name} suspiciously."
                    return f"{npc.name} looks around nervously, as if hiding something."
        
        # Chance to pick up items from the environment (30% chance)
        if hasattr(npc.location, 'items') and npc.location.items and random.random() < 0.3:
            item = random.choice(npc.location.items)
            # Remove the item from the location and add it to NPC's inventory
            npc.location.items.remove(item)
            npc.add_item(item)
            return f"{npc.name} picks up {item.name}."
        
        # Chance to use an item from inventory (60% chance)
        if hasattr(npc, 'items') and npc.items and random.random() < 0.6:
            item = random.choice(npc.items)
            
            # If it's a seed, try to plant it
            if hasattr(item, 'crop_type') and hasattr(npc.location, 'objects'):
                soil_plots = [obj for obj in npc.location.objects if hasattr(obj, 'add_plant')]
                if soil_plots:
                    soil = random.choice(soil_plots)
                    from gardening import Plant
                    plant = Plant(
                        f"{item.crop_type} plant", 
                        f"A young {item.crop_type} plant.", 
                        item.crop_type, 
                        item.value * 2
                    )
                    result = soil.add_plant(plant)
                    if result[0]:  # Successfully planted
                        npc.items.remove(item)
                        return f"{npc.name} plants {item.name} in the {soil.name}."
            
            # If it's a weapon, use it against another NPC
            if hasattr(item, 'damage'):
                # Find a target NPC in the same area
                potential_targets = [other for other in npc.location.npcs 
                                    if other != npc and other.is_alive]
                                    
                if potential_targets and random.random() < 0.6:  # 60% chance to use weapon if targets exist
                    target = random.choice(potential_targets)
                    
                    # Check if they're from different gangs (if they're gang members)
                    if (isinstance(npc, GangMember) and isinstance(target, GangMember) and 
                        npc.gang.name != target.gang.name):
                        # Apply damage to target
                        if hasattr(target, 'health'):
                            damage = random.randint(item.damage // 2, item.damage)
                            target.health -= damage
                            
                            # Check if target died
                            if target.health <= 0:
                                target.is_alive = False
                                if hasattr(target, 'gang'):
                                    target.gang.remove_member(target)
                                return f"{npc.name} uses {item.name} to attack {target.name} for {damage} damage, defeating them!"
                            
                            return f"{npc.name} uses {item.name} to attack {target.name} for {damage} damage!"
                    
                    # If they're not gang members or from the same gang, just threaten
                    elif random.random() < 0.3:  # 30% chance to threaten
                        return f"{npc.name} threatens {target.name} with {item.name}!"
            
            # If it's an effect item, use it on other NPCs (high priority)
            if hasattr(item, 'effect') and random.random() < 0.8:  # 80% chance to prioritize effect items
                affected_npcs = []
                
                # Apply effect to other NPCs in the area
                for other_npc in npc.location.npcs:
                    # Skip dead NPCs and self
                    if other_npc == npc or not other_npc.is_alive:
                        continue
                        
                    # Apply the effect to the NPC
                    if hasattr(other_npc, 'active_effects'):
                        # Create a new instance of the effect for this NPC
                        effect_copy = type(item.effect)()
                        other_npc.active_effects.append(effect_copy)
                        affected_npcs.append(other_npc)
                
                # If NPCs were affected, return a message
                if affected_npcs:
                    # Add the effect messages to the NPC coordinator
                    if game and game.npc_coordinator:
                        game.npc_coordinator.add_effect_messages(affected_npcs, item.effect)
                    
                    if len(affected_npcs) == 1:
                        return f"{npc.name} uses {item.name} on {affected_npcs[0].name}!"
                    else:
                        return f"{npc.name} uses {item.name} on several NPCs!"
            
            # If it's a consumable, use it
            if hasattr(item, 'health_restore'):
                if hasattr(npc, 'health'):
                    npc.health = min(100, npc.health + item.health_restore)
                npc.items.remove(item)
                return f"{npc.name} consumes {item.name}."
                
            # Generic item use
            return f"{npc.name} uses {item.name}."
            
        # Gardening behaviors (40% chance if there are soil plots)
        if hasattr(npc.location, 'objects') and random.random() < 0.4:
            soil_plots = [obj for obj in npc.location.objects if hasattr(obj, 'plants')]
            if soil_plots:
                soil = random.choice(soil_plots)
                
                # Water plants (60% chance if there are plants)
                if soil.plants and random.random() < 0.6:
                    result = soil.water_plants()
                    if result[0]:  # Successfully watered
                        if "gardening" in self.actions_data and "singular" in self.actions_data["gardening"]:
                            action = random.choice(self.actions_data["gardening"]["singular"])
                            return f"{npc.name} {action}."
                        return f"{npc.name} waters the plants in the {soil.name}."
                
                # Harvest plants (40% chance if there are harvestable plants)
                harvestable_plants = [p for p in soil.plants if p.is_harvestable()]
                if harvestable_plants and random.random() < 0.4:
                    plant = random.choice(harvestable_plants)
                    result = soil.harvest_plant(plant.name)
                    if result[0]:  # Successfully harvested
                        message, harvested_item = result[1]
                        npc.add_item(harvested_item)
                        return f"{npc.name} harvests {plant.name} and gets {harvested_item.name}."
        
        # Chance to talk to another NPC
        if npc.location.npcs and len(npc.location.npcs) > 1 and random.random() < 0.4:
            other_npcs = [other for other in npc.location.npcs if other != npc and other.is_alive]
            if other_npcs:
                other = random.choice(other_npcs)
                # Use the npc_interactions from JSON if available
                if "npc_interactions" in self.actions_data:
                    interaction_types = list(self.actions_data["npc_interactions"].keys())
                    interaction_type = random.choice(interaction_types)
                    if self.actions_data["npc_interactions"][interaction_type]:
                        interaction = random.choice(self.actions_data["npc_interactions"][interaction_type])
                        return interaction.format(npc1_name=npc.name, npc2_name=other.name)
                return f"{npc.name} talks with {other.name}."
                
        # Chance to interact with environment
        if hasattr(npc.location, 'objects') and npc.location.objects and random.random() < 0.3:
            obj = random.choice(npc.location.objects)
            
            # Handle breakable objects
            if hasattr(obj, 'break_glass') and not obj.is_broken and random.random() < 0.2:
                # NPC has a chance to break glass objects if they're aggressive
                if isinstance(npc, GangMember) and random.random() < 0.4:
                    # Check if NPC has a weapon
                    weapon = next((item for item in npc.items if hasattr(item, 'damage')), None)
                    
                    if weapon:
                        method = "shoot" if weapon.name.lower() == "gun" else "smash"
                        
                        # Break the object
                        if isinstance(obj, VendingMachine):
                            result = obj.break_glass(npc, method)
                            if result[0]:
                                # Add spilled items to the area
                                for item in result[2]:
                                    npc.location.add_item(item)
                                # Clear the vending machine's items
                                obj.items.clear()
                                return result[1]
                        else:
                            result = obj.break_glass(npc, method)
                            if result[0]:
                                return result[1]
            
            # Handle other object types
            if hasattr(obj, 'plants') and obj.plants:
                return f"{npc.name} examines the plants in the {obj.name}."
            elif hasattr(obj, 'is_hacked'):
                return f"{npc.name} looks at the {obj.name}."
                
        # Idle behavior - use actions from JSON if available
        if "idle" in self.actions_data and "singular" in self.actions_data["idle"]:
            idle_actions = self.actions_data["idle"]["singular"]
            if idle_actions:
                action = random.choice(idle_actions)
                return f"{npc.name} {action}."
        
        # Fallback idle actions if JSON data not available
        idle_actions = [
            f"{npc.name} stands around looking bored.",
            f"{npc.name} checks their phone.",
            f"{npc.name} looks around nervously.",
            f"{npc.name} stretches and yawns.",
            f"{npc.name} hums a tune to themselves."
        ]
        return random.choice(idle_actions)

    def _is_on_cooldown(self, npc):
        """Check if an NPC is on cooldown for their behavior."""
        return self.npc_cooldowns.get(id(npc), 0) > 0

    def _apply_cooldown(self, npc, cooldown=1):
        """Apply a cooldown to an NPC."""
        self.npc_cooldowns[id(npc)] = cooldown

    def decrement_cooldowns(self):
        """Decrement cooldowns for all NPCs."""
        for npc_id in list(self.npc_cooldowns.keys()):
            self.npc_cooldowns[npc_id] -= 1
            if self.npc_cooldowns[npc_id] <= 0:
                del self.npc_cooldowns[npc_id]
                
    def add_effect_messages(self, affected_npcs, effect):
        """Add batch effect messages to be summarized."""
        if not affected_npcs:
            return
            
        # Group NPCs by effect message for better summarization
        effect_messages = {}
        
        for npc in affected_npcs:
            message = None
            if isinstance(effect, HallucinationEffect):
                message = effect.get_hallucination_message()
            elif isinstance(effect, ConfusionEffect):
                message = effect.get_confusion_message()
                
            if message:
                if message not in effect_messages:
                    effect_messages[message] = []
                effect_messages[message].append(npc.name)
        
        # Create summarized messages
        for message, npc_names in effect_messages.items():
            if len(npc_names) > 2:
                # Group message for 3 or more NPCs
                self.action_messages.append(f"Several NPCs {message}")
            elif len(npc_names) == 2:
                # Pair message for 2 NPCs
                self.action_messages.append(f"{npc_names[0]} and {npc_names[1]} {message}")
            else:
                # Individual message for 1 NPC
                self.action_messages.append(f"{npc_names[0]} {message}")
    
    def get_npc_summary(self):
        """Get a summary of NPC actions for the current turn."""
        if not self.action_messages:
            return None
            
        # Group actions by type
        combat_actions = []
        effect_actions = []
        other_actions = []
        
        # Identify combat-related keywords for better categorization
        combat_keywords = [
            "attack", "damage", "defeat", "fight", "hostile", "punch", 
            "kick", "shoot", "stab", "hit", "battle", "combat", "weapon",
            "threatens", "ambush", "retaliate", "defend", "drag"
        ]
        
        for message in self.action_messages:
            # Check if the message contains any combat keywords
            is_combat = any(keyword in message.lower() for keyword in combat_keywords)
            
            if is_combat:
                combat_actions.append(message)
            elif "Several NPCs" in message or message.count(" and ") > 0 or "hallucinate" in message.lower() or "confused" in message.lower():
                effect_actions.append(message)
            else:
                other_actions.append(message)
        
        # Combine each type of action with appropriate punctuation
        # Combat actions first, then effects, then other actions
        summary_parts = []
        
        # Combat actions get priority and more detail
        if combat_actions:
            summary_parts.extend(self._combine_messages_with_punctuation(combat_actions, max_count=4))
        
        # Effect actions next
        if effect_actions:
            summary_parts.extend(self._combine_messages_with_punctuation(effect_actions))
        
        # Other actions last and more summarized
        if other_actions:
            summary_parts.extend(self._combine_messages_with_punctuation(other_actions, max_count=3))
            
        # Join all summaries with appropriate punctuation
        result = ""
        for i, part in enumerate(summary_parts):
            # If this is not the first part, add a space
            if i > 0:
                result += " "
                
            # Add the part to the result
            result += part
            
            # If this is not the last part, add appropriate separator
            if i < len(summary_parts) - 1:
                # If the part already ends with an exclamation mark, use that as the separator
                if part.endswith("!"):
                    result += ""
                else:
                    result += "."
        
        # Ensure the summary ends with punctuation
        if not result.endswith(".") and not result.endswith("!"):
            result += "."
            
        return result

    def _clean_message(self, message):
        """Clean and normalize message punctuation."""
        # Remove trailing periods and exclamation marks
        # This allows us to add appropriate punctuation based on context
        if message.endswith('.') or message.endswith('!'):
            message = message[:-1]
        return message

    def _combine_messages_with_punctuation(self, messages, max_count=2):
        """Combine messages with appropriate punctuation."""
        if not messages:
            return []
            
        # Clean messages first
        cleaned_messages = [self._clean_message(msg) for msg in messages]
        
        combined = []
        i = 0
        while i < len(cleaned_messages) and len(combined) < max_count:
            if i + 1 < len(cleaned_messages):
                # Choose connector based on message content
                if "attacks" in cleaned_messages[i].lower() and "attacks" in cleaned_messages[i+1].lower():
                    # Use semicolons for related combat actions
                    connector = "; "
                elif any(word in cleaned_messages[i].lower() for word in ["picks up", "uses", "examines"]):
                    # Use "while" for simultaneous non-combat actions
                    connector = ", while "
                else:
                    # Randomly choose a connector with weights
                    connector = random.choices([
                        "; ",           # semicolon
                        ", while ",     # while connector
                        " as ",         # as connector
                        ". Meanwhile, " # separate sentences
                    ], weights=[40, 30, 20, 10])[0]
                
                # Check if the combined message should have an exclamation mark
                first_msg = cleaned_messages[i]
                second_msg = cleaned_messages[i + 1]
                combined_msg = first_msg + connector + second_msg
                
                # Add exclamation mark if either message contains exciting content
                exciting_words = ["attack", "defeat", "discover", "drag", "hostile", "damage", 
                                 "fight", "break", "destroy", "crash", "explode", "yell", "scream"]
                
                if (any(word in first_msg.lower() for word in exciting_words) or 
                    any(word in second_msg.lower() for word in exciting_words)):
                    # Only add exclamation if the connector doesn't already end with punctuation
                    if not connector.strip().endswith('.'):
                        combined_msg += "!"
                
                combined.append(combined_msg)
                i += 2
            else:
                # Add appropriate punctuation based on message content
                message = cleaned_messages[i]
                
                # Check if the message should have an exclamation mark
                if any(exciting_word in message.lower() for exciting_word in 
                      ["attack", "defeat", "discover", "drag", "hostile", "damage", 
                       "fight", "break", "destroy", "crash", "explode", "yell", "scream"]):
                    # Add exclamation for exciting/dramatic actions
                    combined.append(message + "!")
                else:
                    # Keep as is for normal actions (no exclamation)
                    combined.append(message)
                i += 1
        return combined
