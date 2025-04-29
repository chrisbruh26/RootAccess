import random
import json
import os
from effects import Effect

# ----------------------------- #
# NPC BEHAVIOR SYSTEM           #
# ----------------------------- #

class NPC:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.relationship = 0
        self.items = []
        self.location = None
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

    def apply_hazard_effect(self, hazard):
        """Default hazard effect application for NPCs that do not have specific implementation."""
        # By default, NPCs are unaffected by hazards
        return f"{self.name} is unaffected by the {hazard.name}."


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

    def attack_player(self, player):
        # Simple combat logic
        damage = random.randint(5, 15)
        player.health -= damage
        return f"The {self.gang.name} member {self.name} attacks you for {damage} damage!"

    def attack_npc(self, target_npc):
        # Simple NPC-to-NPC combat
        if not target_npc.is_alive or not self.is_alive:
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
                return f"The {self.gang.name} member {self.name} attacks {target_npc.name} for {damage} damage, defeating them!"
            
            return f"The {self.gang.name} member {self.name} attacks {target_npc.name} for {damage} damage!"
        else:
            # For NPCs without health attribute
            target_npc.is_alive = False
            return f"The {self.gang.name} member {self.name} attacks and defeats {target_npc.name}!"

    def detect_player(self, player, game):
        """Attempt to detect the player based on detection chance."""
        # Skip detection if already detected or on cooldown
        if self.has_detected_player or self.detection_cooldown > 0:
            return None
            
        # Base detection chance modified by distance, player actions, etc.
        detection_roll = random.random()
        
        if detection_roll < self.detection_chance:
            self.has_detected_player = True
            player.detected_by.add(self.gang)
            
            # Set a cooldown before the NPC can detect again if the player escapes
            self.detection_cooldown = 3
            
            return f"The {self.gang.name} member {self.name} spots you and becomes hostile!"
        
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


class BehaviorSettings:
    """Global settings for NPC behavior frequencies."""
    def __init__(self):
        # Default behavior weights
        self.default_weights = {
            BehaviorType.IDLE: 0.2,     # 20% chance for idle behavior
            BehaviorType.TALK: 0.3,     # 30% chance for talking
            BehaviorType.FIGHT: 0.1,    # 10% chance for fighting
            BehaviorType.USE_ITEM: 0.3, # 30% chance for using items
            BehaviorType.GARDENING: 0.1,# 10% chance for gardening
            BehaviorType.GIFT: 0.0,     # 0% base chance for gifting (boosted by effects)
        }
        
        # Behavior frequency multipliers (1.0 = normal frequency, 0.5 = half frequency, 0.0 = disabled)
        self.frequency_multipliers = {
            BehaviorType.IDLE: 1.0,
            BehaviorType.TALK: 1.0,
            BehaviorType.FIGHT: 1.0,
            BehaviorType.USE_ITEM: 1.0,
            BehaviorType.GARDENING: 1.0,
            BehaviorType.GIFT: 1.0,
        }
        
        # Behavior cooldowns (in turns)
        self.cooldowns = {
            BehaviorType.IDLE: 1,      # 1 turn between idle behaviors
            BehaviorType.TALK: 2,      # 2 turns between talking
            BehaviorType.FIGHT: 3,     # 3 turns between fighting
            BehaviorType.USE_ITEM: 1,  # 1 turn between using items
            BehaviorType.GARDENING: 2, # 2 turns between gardening activities
            BehaviorType.GIFT: 5,      # 5 turns between gifting
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
    def __init__(self, max_npc_actions_per_turn=5, max_actions_per_npc=1):
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
            
        # Process GangMember specific behaviors
        if isinstance(npc, GangMember):
            # Update effects
            if hasattr(npc, 'update_effects'):
                npc.update_effects()
                
            # Check for player detection
            if hasattr(npc, 'detect_player') and game.player.current_area == npc.location:
                detection_result = npc.detect_player(game.player, game)
                if detection_result:
                    return detection_result
                    
            # If player is detected, chance to attack
            if hasattr(game.player, 'detected_by') and npc.gang in game.player.detected_by:
                if random.random() < 0.7:  # 70% chance to attack if detected
                    return npc.attack_player(game.player)
                    
            # Chance to attack other gang members
            if random.random() < 0.2:  # 20% chance to check for enemies
                # Find other gang members in the same area
                other_gang_members = [other for other in npc.location.npcs 
                                     if isinstance(other, GangMember) 
                                     and other.gang != npc.gang
                                     and other.is_alive]
                                     
                if other_gang_members:
                    target = random.choice(other_gang_members)
                    return npc.attack_npc(target)
        
        # General NPC behaviors
        
        # Chance to use an item
        if hasattr(npc, 'items') and npc.items and random.random() < 0.3:
            item = random.choice(npc.items)
            return f"{npc.name} uses {item.name}."
            
        # Chance to talk to another NPC
        if npc.location.npcs and len(npc.location.npcs) > 1 and random.random() < 0.4:
            other_npcs = [other for other in npc.location.npcs if other != npc and other.is_alive]
            if other_npcs:
                other = random.choice(other_npcs)
                return f"{npc.name} talks with {other.name}."
                
        # Chance to interact with environment
        if hasattr(npc.location, 'objects') and npc.location.objects and random.random() < 0.3:
            obj = random.choice(npc.location.objects)
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
                
    def get_npc_summary(self):
        """
        Get a summary of NPC actions for the current turn.
        
        Returns:
            A string summarizing NPC actions, or None if no actions occurred.
        """
        if not self.action_messages:
            return None
            
        # Group similar actions together
        gang_actions = []
        combat_actions = []
        item_actions = []
        talk_actions = []
        other_actions = []
        
        for message in self.action_messages:
            if "attacks" in message.lower() or "damage" in message.lower():
                combat_actions.append(message)
            elif "gang" in message.lower() or "member" in message.lower():
                gang_actions.append(message)
            elif "uses" in message.lower() or "item" in message.lower():
                item_actions.append(message)
            elif "talks" in message.lower() or "chat" in message.lower():
                talk_actions.append(message)
            else:
                other_actions.append(message)
        
        # Create a natural language summary
        summary_parts = []
        
        # Start with combat actions as they're most important
        if combat_actions:
            summary_parts.extend(combat_actions)
        
        # Add connecting phrases between different action types
        connectors = ["Meanwhile, ", "At the same time, ", "Nearby, ", "Elsewhere, ", "Also, "]
        
        # Add other action types with connectors
        action_groups = [gang_actions, item_actions, talk_actions, other_actions]
        for group in action_groups:
            if group and summary_parts:
                summary_parts.append(random.choice(connectors) + group[0])
                group = group[1:]  # Remove the first item we just added
            
            # Add a few more from this group if available
            for action in group[:2]:  # Limit to 2 more actions per group
                if summary_parts:
                    summary_parts.append(random.choice(connectors) + action)
                else:
                    summary_parts.append(action)
        
        # Join everything into a single paragraph
        if not summary_parts:
            return None
            
        return " ".join(summary_parts)
