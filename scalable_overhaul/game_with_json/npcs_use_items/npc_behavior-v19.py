import random
import collections
import json
import os

# Load NPC reactions JSON once at module level
npc_reactions_path = os.path.join(os.path.dirname(__file__), "npc_reactions.json")
NPC_REACTIONS = {}
try:
    with open(npc_reactions_path, "r") as f:
        NPC_REACTIONS = json.load(f)
except Exception as e:
    print(f"Error loading npc_reactions.json: {e}")

class Effect:
    """Represents a hazard effect with duration and properties"""
    def __init__(self, name, description, duration=3, stackable=False):
        self.name = name
        self.description = description
        self.duration = duration
        self.stackable = stackable
        self.remaining_turns = duration

    def update(self):
        """Decrement remaining turns and return True if expired"""
        self.remaining_turns -= 1
        return self.remaining_turns <= 0

    def __str__(self):
        return f"{self.name}"

class NPC:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.relationship = 0
        self.items = []
        self.behavior_manager = BehaviorManager(self)
        self.location = None
        self.is_alive = True

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

class Civillian(NPC):
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
        self.detection_chance = 0.05  # 10 = Base 10% chance to detect player
        self.has_detected_player = False
        self.detection_cooldown = 0
        self.active_effects = []  # List of active effects
        self.hazard_resistance = 0.05  # 0.05 = Base 5% chance to resist hazard effects
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
            return f"The {self.gang.name} member {self.name} has been defeated!"
        return None

    def attack_player(self, player):
        # Import combat descriptions
        from combat_descriptions import format_combat_message, get_death_description
        
        # Check hazard effects first
        for effect in self.active_effects:
            if effect.name == "hallucinations":
                return f"The {self.gang.name} member {self.name} is so high that they don't see you."
            if effect.name == "friendliness":
                # Get a random friendly phrase
                friendly_phrases = [
                    f"The {self.gang.name} member {self.name} smiles at you warmly.",
                    f"The {self.gang.name} member {self.name} gives you a friendly nod.",
                    f"The {self.gang.name} member {self.name} waves cheerfully in your direction.",
                    f"The {self.gang.name} member {self.name} seems unusually happy to see you.",
                    f"The {self.gang.name} member {self.name} greets you like an old friend."
                ]
                return random.choice(friendly_phrases)
            if effect.name == "gift-giving" and self.items:
                gift = random.choice(self.items)
                player.inventory.append(gift)
                self.items.remove(gift)
                
                # Get a random gift-giving phrase
                gift_phrases = [
                    f"The {self.gang.name} member {self.name} gives you {gift.name} as a gift!",
                    f"The {self.gang.name} member {self.name} insists you take their {gift.name}.",
                    f"The {self.gang.name} member {self.name} presses {gift.name} into your hands.",
                    f"The {self.gang.name} member {self.name} seems compelled to give you their {gift.name}.",
                    f"The {self.gang.name} member {self.name} offers you {gift.name} with a strange smile."
                ]
                return random.choice(gift_phrases)

        # Normal detection logic
        if not player.hidden and (self.has_detected_player or random.random() < self.detection_chance / 100):
            self.has_detected_player = True
            player.detected_by.add(self.gang)

            if self.items:
                weapon = next((i for i in self.items if hasattr(i, 'damage')), None)
                damage = weapon.damage if weapon else random.randint(3, 8)  # Unarmed damage
                weapon_name = weapon.name if weapon else None
                
                # Apply damage
                player.health -= damage
                
                # Format descriptive combat message
                if player.health <= 0:
                    # Player has been defeated
                    result = f"{get_death_description()} The {self.gang.name} member {self.name} has defeated you!"
                else:
                    # Player is still alive - use descriptive combat message
                    result = format_combat_message(f"The {self.gang.name} member {self.name}", 
                                                  damage, player.health, 100, weapon_name)
                return result
            
            # No weapon - just threats
            threat_messages = [
                f"The {self.gang.name} member {self.name} spots you and threatens you but has no weapon!",
                f"The {self.gang.name} member {self.name} sees you and shouts threats, but is unarmed.",
                f"The {self.gang.name} member {self.name} notices you and makes threatening gestures.",
                f"The {self.gang.name} member {self.name} locks eyes with you and makes intimidating motions.",
                f"The {self.gang.name} member {self.name} spots you and yells for backup!"
            ]
            return random.choice(threat_messages)

        if player.hidden:
            self.has_detected_player = False
            
            # Only generate a message very rarely (1 in 20 chance)
            if random.random() < 0.05:
                # Varied "doesn't see you" messages
                unaware_messages = [
                    f"The {self.gang.name} member {self.name} looks around but doesn't see you.",
                    f"The {self.gang.name} member {self.name} walks past your hiding spot.",
                    f"The {self.gang.name} member {self.name} seems oblivious to your presence.",
                    f"The {self.gang.name} member {self.name} fails to notice you lurking nearby.",
                    f"The {self.gang.name} member {self.name} is unaware you're watching them."
                ]
                return random.choice(unaware_messages)
            else:
                # Most of the time, don't generate any message
                return None
            
        # Not hidden but not detected
        # Only generate a message very rarely (1 in 20 chance)
        if random.random() < 0.05:
            unnoticed_messages = [
                f"The {self.gang.name} member {self.name} doesn't notice you.",
                f"The {self.gang.name} member {self.name} hasn't spotted you yet.",
                f"The {self.gang.name} member {self.name} is distracted and hasn't seen you.",
                f"The {self.gang.name} member {self.name} is looking the other way.",
                f"The {self.gang.name} member {self.name} hasn't registered your presence."
            ]
            return random.choice(unnoticed_messages)
        else:
            # Most of the time, don't generate any message
            return None

    def update_behavior(self, game):
        """Update NPC behavior each game tick - ONLY behavior, not attacks."""
        if not self.is_alive:
            return f"{self.name} is dead and cannot act."
        
        # Only update behavior, attacks are handled separately in the game loop
        if self.behavior_manager:
            return self.behavior_manager.update(game)
        
        return None

    def apply_hazard_effect(self, hazard):
        """Apply hazard effects to gang members with chance of resistance."""
        # Check if gang member resists the hazard
        if random.random() < self.hazard_resistance:
            return f"The {self.gang.name} member {self.name} resists the {hazard.name} effect!"

        # Apply different effects based on hazard type
        if hazard.effect == "hallucinations":
            # Create and add hallucination effect
            effect = Effect("hallucinations", "Causes hallucinations", duration=3)
            self.active_effects.append(effect)
            return f"{self.gang.name} member {self.name} affected:hallucinations"
        
        elif hazard.effect == "gift-giving":
            # Create and add gift-giving effect
            effect = Effect("gift-giving", "Causes compulsive gift-giving", duration=3)
            self.active_effects.append(effect)
            return f"{self.gang.name} member {self.name} affected:gift-giving"
        
        elif hazard.effect == "friendliness":
            # Create and add friendliness effect
            effect = Effect("friendliness", "Makes NPCs friendly", duration=3)
            self.active_effects.append(effect)
            return f"{self.gang.name} member {self.name} affected:friendliness"
        
        elif hazard.effect == "falling objects":
            # Create and add falling objects effect
            effect = Effect("falling objects", "Makes objects fall on NPCs", duration=1)
            self.active_effects.append(effect)
            self.health -= hazard.damage
            if self.health <= 0:
                self.die()
            return f"{self.gang.name} member {self.name} affected:falling objects"
        
        else:
            # Generic effect
            effect = Effect(hazard.effect, f"Effect from {hazard.name}", duration=3)
            self.active_effects.append(effect)
            return f"{self.gang.name} member {self.name} affected:{hazard.effect}"

class NPCMessageManager:
    """Manages and summarizes NPC messages to reduce repetition."""
    def __init__(self):
        self.message_buffer = []
        self.max_buffer_size = 20
        self.summarize_threshold = 2  # Number of messages before summarizing
        self.last_summary_types = set()  # Track message types from last summary to avoid repetition
        self.last_turn_effects = {}  # Track effects reported per NPC last turn
        self.turn_counter = 0  # Track game turns
        self.npc_actions = {}  # Track actions per NPC in current turn
        
    def new_turn(self):
        """Call at the start of each game turn to update tracking.
        Modified to maintain NPC action history across turns for better variety."""
        self.turn_counter += 1
        
        # Only clear last_summary_types every 3 turns to allow for variety
        if self.turn_counter % 3 == 0:
            self.last_summary_types.clear()
        
        # Instead of clearing npc_actions completely, we'll selectively refresh it
        # to allow some NPCs to take new actions while preventing repetition
        if self.turn_counter % 3 == 0:  # Every 3 turns
            # Randomly select some NPCs to "forget" their actions
            # This allows them to take new actions while still preventing spam
            npcs_to_refresh = []
            for npc_name in self.npc_actions.keys():
                if random.random() < 0.3:  # 30% chance to refresh each NPC
                    npcs_to_refresh.append(npc_name)
            
            # Remove these NPCs from the tracking dict
            for npc_name in npcs_to_refresh:
                if npc_name in self.npc_actions:
                    del self.npc_actions[npc_name]
        
        # Keep track of effects from last turn, but clear old ones
        if self.turn_counter % 2 == 0:  # Every other turn
            self.last_turn_effects = {}
            
        # Every 5 turns, clear the message buffer completely to avoid stale messages
        if self.turn_counter % 5 == 0:
            self.message_buffer.clear()
    
    def add_message(self, message):
        """Add a message to the buffer, tracking per-NPC actions with strict deduplication."""
        # Skip certain repetitive messages based on content
        if self._should_skip_message(message):
            return None
            
        # Extract NPC name and action from message
        npc_name, action_type = self._extract_npc_info(message)
        
        # Skip if message is empty or None
        if not message:
            return None
            
        # Skip if this exact message is already in the buffer
        if message in self.message_buffer:
            return None
            
        # If we identified an NPC, track their actions
        if npc_name:
            # Initialize if this is the first action for this NPC
            if npc_name not in self.npc_actions:
                self.npc_actions[npc_name] = []
            else:
                # Strict limit: only one action per NPC (except for attacks)
                if action_type != "attack":
                    # Skip this action if NPC already has an action
                    # (except for attacks, which are always important)
                    return None
                    
                # Even for attacks, limit to one attack message per NPC
                if action_type == "attack":
                    has_attack = False
                    for existing_action_type, _ in self.npc_actions[npc_name]:
                        if existing_action_type == "attack":
                            has_attack = True
                            break
                    if has_attack:
                        return None
                
            # For detection status messages, be extremely restrictive
            if action_type in ["unnoticed", "looking_away", "distracted"]:
                # Check if we already have any detection messages for any NPC
                has_detection_message = False
                for existing_npc, existing_actions in self.npc_actions.items():
                    for existing_action_type, _ in existing_actions:
                        if existing_action_type in ["unnoticed", "looking_away", "distracted"]:
                            has_detection_message = True
                            break
                
                # If we already have a detection message, or by random chance (90% of the time)
                # skip this detection message
                if has_detection_message or random.random() > 0.1:
                    return None
            
            # For effect messages (hallucinations, friendliness, etc.), be very restrictive
            if action_type in ["hallucination", "friendly", "gift"]:
                # Check if we already have any effect messages for any NPC
                has_effect_message = False
                for existing_npc, existing_actions in self.npc_actions.items():
                    for existing_action_type, _ in existing_actions:
                        if existing_action_type in ["hallucination", "friendly", "gift"]:
                            has_effect_message = True
                            break
                
                # If we already have an effect message, limit additional ones
                if has_effect_message and random.random() > 0.3:  # 70% chance to skip
                    return None
            
            # Add this action to the NPC's actions
            self.npc_actions[npc_name].append((action_type, message))
            
        # Add to general message buffer
        self.message_buffer.append(message)
        
        # If buffer exceeds max size, summarize and clear
        if len(self.message_buffer) >= self.max_buffer_size:
            return self.get_summary(clear=True)
        return None
    
    def _extract_action_phrase(self, message):
        """Extract a key action phrase from a message for grouping similar actions."""
        # Common action phrases to look for
        action_phrases = [
            "looking the other way",
            "standing around",
            "is idle",
            "is distracted",
            "hasn't spotted you",
            "doesn't notice you",
            "doesn't see you",
            "is unaware",
            "walks past",
            "looks around",
            "seems oblivious",
            "fails to notice",
            "is talking",
            "is chatting",
            "is discussing",
            "is arguing",
            "is fighting",
            "is attacking",
            "is defending",
            "is running",
            "is hiding",
            "is searching",
            "is investigating",
            "is eating",
            "is drinking",
            "is sleeping",
            "is resting",
            "is working",
            "is building",
            "is crafting",
            "is planting",
            "is harvesting",
            "is cooking",
            "is cleaning",
            "is repairing",
            "is guarding",
            "is patrolling",
            "is watching",
            "is observing",
            "is listening",
            "is waiting",
            "is thinking",
            "is planning",
            "is confused",
            "is scared",
            "is angry",
            "is happy",
            "is sad",
            "is excited",
            "is bored",
            "is tired",
            "is injured",
            "is healing",
            "is dying",
            "is dead"
        ]
        
        # Check for each action phrase in the message
        for phrase in action_phrases:
            if phrase in message:
                return phrase
                
        # If no specific phrase is found, try to extract a verb phrase
        if " is " in message and " and " not in message:
            parts = message.split(" is ")
            if len(parts) > 1:
                verb_phrase = parts[1].split(".")[0].strip()
                if verb_phrase and len(verb_phrase.split()) <= 4:  # Limit to short phrases
                    return f"is {verb_phrase}"
                    
        return None
        
    def _extract_npc_info(self, message):
        """Extract NPC name and action type from a message."""
        # Default values
        npc_name = None
        action_type = "other"
        
        # Check for gang member references
        if "member" in message:
            parts = message.split()
            member_idx = parts.index("member") + 1 if "member" in parts else -1
            if member_idx >= 0 and member_idx < len(parts):
                npc_name = parts[member_idx]
                
                # Determine action type
                if "attacks you" in message or "damage" in message:
                    action_type = "attack"
                elif "is so high" in message or "hallucinating" in message:
                    action_type = "hallucination"
                elif "smiles at you" in message or "friendly" in message:
                    action_type = "friendly"
                elif "gives you" in message or "gift" in message:
                    action_type = "gift"
                elif "standing around" in message:
                    action_type = "idle"
                elif "is idle" in message:
                    action_type = "idle"
                elif "looking the other way" in message:
                    action_type = "looking_away"
                elif "doesn't notice you" in message or "doesn't see you" in message or "hasn't spotted you" in message:
                    action_type = "unnoticed"
                elif "talks to" in message:
                    action_type = "talk"
                elif "interacts with" in message or "uses" in message:
                    action_type = "interact"
                else:
                    # Try to extract a more specific action type
                    action_phrase = self._extract_action_phrase(message)
                    if action_phrase:
                        action_type = f"action:{action_phrase}"
        
        # Also check for "affected:" messages which have a different format
        elif "affected:" in message:
            parts = message.split()
            if len(parts) >= 3:
                npc_name = parts[2]
                action_type = "affected"
                
        return npc_name, action_type
    
    def _should_skip_message(self, message):
        """Determine if a message should be skipped to reduce spam."""
        # Extract NPC name and effect type
        npc_name, action_type = self._extract_npc_info(message)
        
        # Skip almost all "doesn't notice you" messages - they're too repetitive
        if ("doesn't notice you" in message or "doesn't see you" in message or 
            "haven't noticed you" in message or "hasn't spotted you" in message or
            "is looking the other way" in message or "looks around but doesn't see you" in message or
            "hasn't registered your presence" in message or "is unaware you're watching" in message or
            "fails to notice you" in message or "walks past your hiding spot" in message or
            "hasn't noticed you" in message):
            # Only show a tiny percentage (1 in 50 chance) - we'll summarize these later
            # This is an extreme reduction to minimize these messages
            return random.random() > 0.02
        
        # Skip most "standing around" and "distracted" messages - we'll summarize these later
        if "standing around" in message or "is idle" in message or "is distracted" in message:
            # Only keep a small percentage for summarization
            return random.random() > 0.15
            
        # Skip effect messages if we've already reported them for this NPC
        if npc_name and action_type in ["hallucination", "friendly", "gift"]:
            if npc_name in self.last_turn_effects and action_type in self.last_turn_effects[npc_name]:
                # Only show these occasionally (1 in 5 chance) if we already reported them
                return random.random() > 0.2
                
            # Track this effect for this NPC
            if npc_name not in self.last_turn_effects:
                self.last_turn_effects[npc_name] = set()
            self.last_turn_effects[npc_name].add(action_type)
                
        # Skip most mundane interaction messages
        if "talks to" in message or "interacts with" in message or "looks for" in message:
            # Only show these occasionally (1 in 5 chance)
            return random.random() > 0.2
            
        # Always show important messages (attacks, deaths, etc.)
        if "attacks you" in message or "defeated" in message or "damage" in message or "spotted you" in message:
            return False
            
        # Skip most other messages to reduce overall volume
        return random.random() > 0.25  # Only show 25% of other messages by default

    def get_summary(self, clear=False):
        """Get a summary of the current messages in the buffer."""
        if not self.message_buffer:
            return None
            
        # Always summarize if we have enough messages
        result = self._create_summary()
            
        if clear:
            # Clear both the message buffer and NPC actions to prevent duplicates
            self.message_buffer.clear()
            self.npc_actions.clear()
            
        return result
        
    def _create_summary(self):
        """Create a summary of messages by categorizing them."""
        # Track message categories for this summary
        current_summary_types = set()
        
        # Categorize messages by action type and gang
        attack_messages = []
        hallucination_messages = []
        friendly_messages = []
        gift_messages = []
        awareness_messages = []
        idle_messages = []  # Specifically for "standing around" messages
        looking_away_messages = []  # For "looking the other way" messages
        unnoticed_messages = []  # For "doesn't notice you" messages
        distracted_messages = []  # For "is distracted" messages
        interaction_messages = []  # For "interacts with" messages
        other_messages = []
        
        # Action-specific message collections
        action_specific_messages = collections.defaultdict(list)
        
        # First pass: categorize messages and extract important info
        for message in self.message_buffer:
            # Prioritize attack messages
            if "attacks you" in message or "damage" in message or "defeated" in message:
                attack_messages.append(message)
                current_summary_types.add("attack")
            # Hallucination messages
            elif "is so high" in message or "hallucinating" in message or "affected:hallucinations" in message:
                hallucination_messages.append(message)
                current_summary_types.add("hallucination")
            # Friendly messages
            elif "smiles at you" in message or "friendly" in message or "affected:friendliness" in message:
                friendly_messages.append(message)
                current_summary_types.add("friendly")
            # Gift messages
            elif "gives you" in message or "gift" in message or "affected:gift-giving" in message:
                gift_messages.append(message)
                current_summary_types.add("gift")
            # Detection-related messages - consolidate into a single category
            elif ("looking the other way" in message or 
                  "doesn't notice you" in message or 
                  "doesn't see you" in message or 
                  "hasn't spotted you" in message or
                  "hasn't noticed you" in message or
                  "is distracted" in message or 
                  "distracted" in message or
                  "hasn't registered your presence" in message or
                  "is unaware you're watching" in message or
                  "fails to notice you" in message or
                  "walks past your hiding spot" in message or
                  "seems oblivious to your presence" in message):
                
                # Extract NPC name to avoid duplicates
                npc_name, _ = self._extract_npc_info(message)
                
                # Only add this message if we haven't already added a detection message for this NPC
                if npc_name:
                    # Check if this NPC already has a detection message
                    npc_already_has_detection_message = False
                    for existing_msg in unnoticed_messages + looking_away_messages + distracted_messages:
                        existing_npc, _ = self._extract_npc_info(existing_msg)
                        if existing_npc == npc_name:
                            npc_already_has_detection_message = True
                            break
                    
                    if not npc_already_has_detection_message:
                        # Categorize based on the specific message type
                        if "looking the other way" in message:
                            looking_away_messages.append(message)
                            current_summary_types.add("looking_away")
                        elif "distracted" in message:
                            distracted_messages.append(message)
                            current_summary_types.add("distracted")
                        else:
                            unnoticed_messages.append(message)
                            current_summary_types.add("unnoticed")
            # Interaction messages
            elif "interacts with" in message or "looks for" in message:
                interaction_messages.append(message)
                current_summary_types.add("interaction")
            # Awareness messages (noticed)
            elif "spots you" in message or "noticed you" in message:
                awareness_messages.append(message)
                current_summary_types.add("awareness")
            # Idle/standing around messages
            elif "standing around" in message or "is idle" in message:
                idle_messages.append(message)
                current_summary_types.add("idle")
            # Other messages - try to categorize by common phrases
            else:
                # Extract action phrase for grouping similar actions
                action_phrase = self._extract_action_phrase(message)
                if action_phrase:
                    action_specific_messages[action_phrase].append(message)
                    current_summary_types.add(f"action:{action_phrase}")
                else:
                    other_messages.append(message)
                    current_summary_types.add("other")
        
        # Second pass: create summaries for each category
        summary_parts = []
        max_summary_parts = 10  # Limit the number of summary parts to display
        
        # Always include attack messages (most important)
        if attack_messages:
            # Don't summarize attacks - they're important
            summary_parts.extend(attack_messages)
        
        # Summarize hallucination messages
        if hallucination_messages and len(summary_parts) < max_summary_parts:
            # Extract gang members who are hallucinating
            gang_members = self._extract_gang_members(hallucination_messages)
            if gang_members:
                gang_name = next(iter(gang_members.keys()))
                members = gang_members[gang_name]
                
                if len(members) == 1:
                    hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("singular", ["is seeing things that aren't there."]))
                    summary_parts.append(f"The {gang_name} member {members[0]} {hallucination}")
                else:
                    hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("plural", ["are seeing things that aren't there."]))
                    # Only list up to 3 members by name
                    member_list = ", ".join(members[:3])
                    if len(members) > 3:
                        member_list += f" and {len(members) - 3} others"
                    summary_parts.append(f"The {gang_name} members {member_list} {hallucination}")
        
        # Summarize friendly messages
        if friendly_messages and len(summary_parts) < max_summary_parts:
            gang_members = self._extract_gang_members(friendly_messages)
            if gang_members:
                for gang_name, members in gang_members.items():
                    if len(members) == 1:
                        friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("singular", ["seems unusually friendly."]))
                        summary_parts.append(f"The {gang_name} member {members[0]} {friendlyphrase}")
                    else:
                        friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("plural", ["seem unusually friendly."]))
                        member_list = ", ".join(members[:3])
                        if len(members) > 3:
                            member_list += f" and {len(members) - 3} others"
                        summary_parts.append(f"The {gang_name} members {member_list} {friendlyphrase}")
                    
                    # Only add one friendly message summary
                    break
        
        # Summarize gift messages
        if gift_messages and len(summary_parts) < max_summary_parts:
            gang_members = self._extract_gang_members(gift_messages)
            if gang_members:
                for gang_name, members in gang_members.items():
                    if len(members) == 1:
                        summary_parts.append(f"The {gang_name} member {members[0]} is compulsively giving away items.")
                    else:
                        member_list = ", ".join(members[:3])
                        if len(members) > 3:
                            member_list += f" and {len(members) - 3} others"
                        summary_parts.append(f"The {gang_name} members {member_list} are giving away items.")
                    
                    # Only add one gift message summary
                    break
        
        # Summarize awareness messages (only if we don't have many other messages)
        if awareness_messages and len(summary_parts) < max_summary_parts:
            # Extract who has noticed the player
            noticed = []
            
            for msg in awareness_messages:
                if "spots you" in msg or "noticed you" in msg:
                    # Extract name from message
                    parts = msg.split()
                    if "member" in msg:
                        member_idx = parts.index("member") + 1 if "member" in parts else -1
                        if member_idx >= 0 and member_idx < len(parts):
                            noticed.append(parts[member_idx])
            
            # Only report if someone has noticed you (more important)
            if noticed:
                gang_name = "Bloodhounds"  # Default, should extract from message
                if len(noticed) == 1:
                    summary_parts.append(f"The {gang_name} member {noticed[0]} has spotted you!")
                else:
                    member_list = ", ".join(noticed[:3])
                    if len(noticed) > 3:
                        member_list += f" and {len(noticed) - 3} others"
                    summary_parts.append(f"The {gang_name} members {member_list} have spotted you!")
        
        # Try to combine different types of "not noticing you" messages
        unaware_members = collections.defaultdict(list)
        
        # Process unnoticed messages
        if unnoticed_messages:
            for gang_name, members in self._extract_gang_members(unnoticed_messages).items():
                unaware_members[gang_name].extend(members)
                
        # Process looking away messages
        if looking_away_messages:
            for gang_name, members in self._extract_gang_members(looking_away_messages).items():
                unaware_members[gang_name].extend(members)
                
        # Process distracted messages
        if distracted_messages:
            for gang_name, members in self._extract_gang_members(distracted_messages).items():
                unaware_members[gang_name].extend(members)
        
        # Create combined "unaware" message if we have members and space
        # Only show "unaware" messages very occasionally (1 in 10 turns) unless we have very few messages
        if unaware_members and (len(summary_parts) < 1 or random.random() < 0.1) and len(summary_parts) < max_summary_parts:
            for gang_name, members in unaware_members.items():
                # Remove duplicates while preserving order
                unique_members = []
                for member in members:
                    if member not in unique_members:
                        unique_members.append(member)
                
                # If most/all NPCs haven't noticed you, use a simpler message
                if len(unique_members) >= 5:
                    summary_parts.append(f"None of the {gang_name} members have noticed you.")
                elif len(unique_members) == 1:
                    summary_parts.append(f"The {gang_name} member {unique_members[0]} hasn't noticed you.")
                elif len(unique_members) <= 3:
                    member_list = ", ".join(unique_members)
                    summary_parts.append(f"The {gang_name} members {member_list} haven't noticed you.")
                else:
                    # For more than 3 members, summarize with count
                    sample_members = random.sample(unique_members, 3)
                    member_list = ", ".join(sample_members)
                    summary_parts.append(f"The {gang_name} members {member_list} and {len(unique_members) - 3} others haven't noticed you.")
                
                # Only add one unaware message summary
                break
        
        # Try to combine interaction and idle messages into a natural language summary
        if (interaction_messages or idle_messages) and len(summary_parts) < max_summary_parts:
            # Extract members and their actions
            interaction_members = {}
            idle_members = {}
            
            if interaction_messages:
                # Extract members and what they're interacting with
                for message in interaction_messages:
                    npc_name, action_type = self._extract_npc_info(message)
                    if npc_name:
                        # Try to extract what they're interacting with
                        if "interacts with" in message:
                            item = message.split("interacts with")[1].strip().rstrip(".")
                            interaction_members[npc_name] = f"interacts with {item}"
                        elif "looks for" in message:
                            item = message.split("looks for")[1].strip().rstrip(".")
                            interaction_members[npc_name] = f"looks for {item}"
                        else:
                            interaction_members[npc_name] = "is busy with something"
            
            if idle_messages:
                # Extract members who are idle
                gang_members = self._extract_gang_members(idle_messages)
                for gang_name, members in gang_members.items():
                    for member in members:
                        idle_members[member] = "is standing around"
            
            # Create a combined message with different actions
            if interaction_members and idle_members:
                # Pick one member from each category for a combined message
                interact_name = random.choice(list(interaction_members.keys()))
                interact_action = interaction_members[interact_name]
                
                idle_name = random.choice(list(idle_members.keys()))
                
                # Make sure we don't pick the same NPC twice
                idle_names = list(idle_members.keys())
                if len(idle_names) > 1 and idle_name == interact_name:
                    idle_names.remove(interact_name)
                    idle_name = random.choice(idle_names)
                
                # Create a combined message
                gang_name = "Bloodhounds"  # Default
                summary_parts.append(f"{interact_name} {interact_action} while {idle_name} is standing around.")
            
        # Process combined NPC actions for other types of messages
        if len(summary_parts) < max_summary_parts:
            combined_messages = self._combine_npc_actions()
            if combined_messages:
                # Only add a limited number of combined messages
                max_combined = max_summary_parts - len(summary_parts)
                if len(combined_messages) > max_combined:
                    combined_messages = random.sample(combined_messages, max_combined)
                summary_parts.extend(combined_messages)
        
        # If we still don't have enough messages, add some action-specific messages
        if len(summary_parts) < max_summary_parts and action_specific_messages:
            # Select a random action type
            action_types = list(action_specific_messages.keys())
            if action_types:
                action_type = random.choice(action_types)
                messages = action_specific_messages[action_type]
                
                gang_members = self._extract_gang_members(messages)
                for gang_name, members in gang_members.items():
                    if len(members) == 1:
                        # Just use the original message for a single NPC
                        summary_parts.append(messages[0])
                    else:
                        # Format the list of members with proper grammar
                        if len(members) <= 3:
                            member_list = ", ".join(members)
                            summary_parts.append(f"The {gang_name} members {member_list} {action_type}.")
                        else:
                            # For more than 3 members, summarize with count
                            sample_members = random.sample(members, 3)
                            member_list = ", ".join(sample_members)
                            summary_parts.append(f"The {gang_name} members {member_list} and {len(members) - 3} others {action_type}.")
                    break
        
        # If we still don't have enough messages, add some other messages
        if len(summary_parts) < max_summary_parts and other_messages:
            # Select up to 2 random other messages
            remaining_slots = max_summary_parts - len(summary_parts)
            sample_size = min(remaining_slots, len(other_messages))
            selected_messages = random.sample(other_messages, sample_size)
            summary_parts.extend(selected_messages)
        
        # Update tracking of what message types we've shown
        self.last_summary_types = current_summary_types
        
        # Return the summary
        return "\n".join(summary_parts)
        
    def _combine_npc_actions(self):
        """Combine similar actions from different NPCs and ensure each NPC only appears once in the output."""
        combined_messages = []
        
        # Track which NPCs we've mentioned in the output
        mentioned_npcs = set()
        
        # First, group NPCs by their actions to find similar behaviors
        action_to_npcs = collections.defaultdict(list)
        
        # First pass: identify NPCs with similar single actions
        for npc_name, actions in self.npc_actions.items():
            # Skip NPCs with no actions
            if len(actions) <= 0:
                continue
                
            # Get gang name (assuming format is consistent)
            gang_name = "Bloodhounds"  # Default
            for _, message in actions:
                if "member" in message and npc_name in message:
                    parts = message.split()
                    if parts[0] == "The" and "member" in parts:
                        gang_name = parts[1]
                        break
            
            # For NPCs with a single action, group them by action type
            if len(actions) == 1:
                action_type, message = actions[0]
                # Create a key that includes gang name to avoid mixing different gangs
                action_key = f"{gang_name}:{action_type}"
                action_to_npcs[action_key].append((npc_name, message))
        
        # Second pass: generate combined messages for similar actions
        for action_key, npc_messages in action_to_npcs.items():
            # Only combine if we have multiple NPCs with the same action
            if len(npc_messages) > 1:
                gang_name = action_key.split(":")[0]
                action_type = action_key.split(":")[1]
                
                # Extract all NPC names that haven't been mentioned yet
                npc_names = [name for name, _ in npc_messages if name not in mentioned_npcs]
                
                # Skip if all NPCs have already been mentioned
                if not npc_names:
                    continue
                
                # Mark these NPCs as mentioned
                for name in npc_names:
                    mentioned_npcs.add(name)
                
                # Format the list of NPCs
                if len(npc_names) <= 3:
                    npc_list = ", ".join(npc_names)
                else:
                    # For more than 3 NPCs, summarize with count
                    npc_list = ", ".join(npc_names[:3]) + f" and {len(npc_names) - 3} others"
                
                # Create appropriate message based on action type
                if action_type == "idle":
                    combined_messages.append(f"The {gang_name} members {npc_list} are standing around.")
                elif action_type == "looking_away":
                    combined_messages.append(f"The {gang_name} members {npc_list} are looking the other way.")
                elif action_type == "unnoticed":
                    combined_messages.append(f"The {gang_name} members {npc_list} don't notice you.")
                elif action_type == "hallucination":
                    hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("plural", ["are seeing things that aren't there."]))
                    combined_messages.append(f"The {gang_name} members {npc_list} {hallucination}")
                elif action_type == "friendly":
                    friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("plural", ["seem unusually friendly."]))
                    combined_messages.append(f"The {gang_name} members {npc_list} {friendlyphrase}")
                elif action_type == "gift":
                    combined_messages.append(f"The {gang_name} members {npc_list} are giving away items.")
                elif action_type == "talk":
                    combined_messages.append(f"The {gang_name} members {npc_list} are talking to others.")
                elif action_type == "interact":
                    combined_messages.append(f"The {gang_name} members {npc_list} are interacting with objects.")
                elif action_type.startswith("action:"):
                    # Extract the action phrase
                    action_phrase = action_type.split(":", 1)[1]
                    combined_messages.append(f"The {gang_name} members {npc_list} {action_phrase}.")
                else:
                    # For other action types, use the first message as a template
                    sample_message = npc_messages[0][1]
                    # Replace the NPC name with the list of NPCs
                    if f"The {gang_name} member" in sample_message:
                        combined_message = sample_message.replace(
                            f"The {gang_name} member {npc_names[0]}", 
                            f"The {gang_name} members {npc_list}"
                        )
                        # Fix verb agreement (is -> are)
                        combined_message = combined_message.replace(" is ", " are ")
                        combined_messages.append(combined_message)
                    else:
                        # If we can't properly format, just use individual messages
                        for npc_name, message in npc_messages:
                            if npc_name not in mentioned_npcs:
                                combined_messages.append(message)
                                mentioned_npcs.add(npc_name)
            else:
                # For single NPCs, just use the original message if not already mentioned
                npc_name = npc_messages[0][0]
                if npc_name not in mentioned_npcs:
                    combined_messages.append(npc_messages[0][1])
                    mentioned_npcs.add(npc_name)
        
        # Third pass: process remaining NPCs that haven't been grouped
        for npc_name, actions in self.npc_actions.items():
            # Skip NPCs we've already mentioned or with no actions
            if npc_name in mentioned_npcs or len(actions) <= 0:
                continue
                
            # Just use the first action for this NPC
            action_type, message = actions[0]
            combined_messages.append(message)
            mentioned_npcs.add(npc_name)
        
        # Limit the number of combined messages to return
        if len(combined_messages) > 5:
            return random.sample(combined_messages, 5)
        
        return combined_messages
        
    def _create_cross_npc_message(self, npc1_name, npc1_data, npc2_name, npc2_data):
        """Create a natural language message combining actions from two different NPCs."""
        # Extract action types and messages
        npc1_action_types = npc1_data['action_types']
        npc2_action_types = npc2_data['action_types']
        
        # Get gang names
        gang1_name = npc1_data['gang_name']
        gang2_name = npc2_data['gang_name']
        
        # Try to find interesting combinations
        
        # Case 1: One NPC interacting with an item while another is doing something else
        if "interact" in npc1_action_types:
            interact_message = next((msg for type, msg in npc1_data['actions'] if type == "interact"), "")
            if "interacts with" in interact_message:
                item = interact_message.split("interacts with")[1].strip().rstrip(".")
                
                # Find a contrasting action for NPC2
                if "idle" in npc2_action_types:
                    return f"{npc1_name} interacts with {item} while {npc2_name} is standing around."
                elif "looking_away" in npc2_action_types:
                    return f"{npc1_name} interacts with {item} while {npc2_name} is looking the other way."
                elif "distracted" in npc2_action_types:
                    return f"{npc1_name} interacts with {item} while {npc2_name} is distracted."
            elif "looks for" in interact_message:
                item = interact_message.split("looks for")[1].strip().rstrip(".")
                
                # Find a contrasting action for NPC2
                if "idle" in npc2_action_types:
                    return f"{npc1_name} looks for {item} while {npc2_name} is standing around."
        
        # Case 2: One NPC looking for something while another is interacting
        if "interact" in npc2_action_types and "idle" in npc1_action_types:
            interact_message = next((msg for type, msg in npc2_data['actions'] if type == "interact"), "")
            if "interacts with" in interact_message:
                item = interact_message.split("interacts with")[1].strip().rstrip(".")
                return f"{npc2_name} interacts with {item} while {npc1_name} is standing around."
            elif "looks for" in interact_message:
                item = interact_message.split("looks for")[1].strip().rstrip(".")
                return f"{npc2_name} looks for {item} while {npc1_name} is standing around."
        
        # Case 3: One NPC hallucinating while another is doing something normal
        if "hallucination" in npc1_action_types and "idle" in npc2_action_types:
            return f"{npc1_name} is hallucinating while {npc2_name} is standing around watching."
        
        # Case 4: One NPC being friendly while another is distracted
        if "friendly" in npc1_action_types and "distracted" in npc2_action_types:
            return f"{npc1_name} is being unusually friendly while {npc2_name} seems distracted."
        
        # Case 5: Both NPCs are idle/unaware
        if ("idle" in npc1_action_types or "unnoticed" in npc1_action_types or "looking_away" in npc1_action_types) and \
           ("idle" in npc2_action_types or "unnoticed" in npc2_action_types or "looking_away" in npc2_action_types):
            return f"{npc1_name} and {npc2_name} are both unaware of your presence."
        
        # No interesting combination found
        return None
    
    def _extract_gang_members(self, messages):
        """Extract gang members from a list of messages."""
        gang_members = collections.defaultdict(list)
        
        for message in messages:
            # Look for gang member references
            if "member" in message:
                # Extract gang name and member name
                parts = message.split()
                
                # Find the position of "member" in the message
                if "member" in parts:
                    member_idx = parts.index("member")
                    
                    # Gang name should be right before "member"
                    if member_idx > 1 and parts[member_idx-2] == "The":
                        gang_name = parts[member_idx-1]
                        
                        # Member name should be right after "member"
                        if member_idx + 1 < len(parts):
                            member_name = parts[member_idx + 1]
                            # Remove any punctuation from member name
                            member_name = member_name.rstrip('.,!?:;')
                            
                            # Only add unique members
                            if member_name not in gang_members[gang_name]:
                                gang_members[gang_name].append(member_name)
            
            # Also check for "affected:" messages which have a different format
            elif "affected:" in message:
                parts = message.split()
                if len(parts) >= 3:
                    gang_name = parts[0]
                    member_name = parts[2]
                    # Remove any punctuation from member name
                    member_name = member_name.rstrip('.,!?:;')
                    
                    if member_name not in gang_members[gang_name]:
                        gang_members[gang_name].append(member_name)
        
        return gang_members

class Behavior:
    """Base class for NPC behaviors."""
    def __init__(self, npc):
        self.npc = npc

    def perform(self, game):
        """Perform the behavior action. To be overridden by subclasses."""
        pass

    def __str__(self):
        return self.__class__.__name__

class IdleBehavior(Behavior):
    """NPC does nothing or simple idle actions."""
    def perform(self, game):
        # For gang members, use a consistent format to help with message grouping
        if hasattr(self.npc, 'gang'):
            # Use a very limited set of consistent idle messages for better grouping
            # This is crucial for the message summarization system to work properly
            idle_actions = [
                "is standing around",  # Most common, for better grouping
                "is looking the other way"  # Alternative for variety
            ]
            
            # Use weighted random choice to favor "standing around" for better grouping
            weights = [0.8, 0.2]  # 80% chance of "standing around"
            action = random.choices(idle_actions, weights=weights, k=1)[0]
            
            return f"The {self.npc.gang.name} member {self.npc.name} {action}."
        else:
            # For non-gang NPCs, use the original behavior
            reactions = game.NPC_REACTIONS.get("idle_phrases", ["{} is standing around."])
            reaction = random.choice(reactions)
            return reaction.format(self.npc.name)

class TalkBehavior(Behavior):
    """NPC talks to another NPC or player."""
    def __init__(self, npc, target):
        super().__init__(npc)
        self.target = target

    def perform(self, game):
        # Use npc_reactions.json talking phrases
        reactions = game.NPC_REACTIONS.get("talking_phrases", ["{} talks to {}."])
        reaction = random.choice(reactions)
        
        # Check if target is player (doesn't have name attribute)
        target_name = getattr(self.target, 'name', 'you')
        if target_name == 'you':
            # Use a player-specific format if available
            player_reactions = game.NPC_REACTIONS.get("player_talking_phrases", ["{} talks to you."])
            if player_reactions:
                reaction = random.choice(player_reactions)
                return reaction.format(self.npc.name)
        
        return reaction.format(self.npc.name, target_name)

class FightBehavior(Behavior):
    """NPC fights another NPC or player."""
    def __init__(self, npc, target):
        super().__init__(npc)
        self.target = target

    def perform(self, game):
        # Import combat descriptions
        from combat_descriptions import format_combat_message, get_death_description
        
        # Simple fight logic: reduce health, print fight message
        damage = random.randint(5, 15)
        
        # Check if NPC has a weapon for more damage and special descriptions
        weapon = None
        weapon_name = None
        if hasattr(self.npc, 'items'):
            weapon = next((item for item in self.npc.items if hasattr(item, 'damage')), None)
            if weapon:
                damage = weapon.damage
                weapon_name = weapon.name
        
        # Apply damage to target
        self.target.health -= damage
        
        # Check if target is player (doesn't have name attribute)
        is_player = not hasattr(self.target, 'name')
        target_name = "you" if is_player else self.target.name
        
        if self.target.health <= 0:
            self.target.is_alive = False
            if is_player:
                # Use descriptive death message for player
                result = f"{get_death_description()} {self.npc.name} has defeated you!"
            else:
                result = f"{self.npc.name} has defeated {target_name}!"
        else:
            if is_player:
                # Use descriptive combat message for player
                result = format_combat_message(self.npc.name, damage, self.target.health, 100, weapon_name)
            else:
                # For NPC-on-NPC combat, use simpler messages
                result = f"{self.npc.name} attacks {target_name} for {damage} damage. {target_name} has {self.target.health} health left."
        return result

class UseItemBehavior(Behavior):
    """NPC uses an item in the environment."""
    def __init__(self, npc, item):
        super().__init__(npc)
        self.item = item

    def perform(self, game):
        # First, check if the item is a seed by name if it doesn't have a type attribute
        if (hasattr(self.item, 'name') and 
            ('seed' in self.item.name.lower() or 'seeds' in self.item.name.lower()) and 
            not hasattr(self.item, 'type')):
            # It's a seed by name, so treat it as one
            return self._plant_seed(game)
            
        # Check if the item has special interaction logic via type attribute
        if hasattr(self.item, 'type'):
            # Handle different item types
            if self.item.type == 'seed':
                return self._plant_seed(game)
            elif self.item.type == 'weapon':
                return self._pickup_weapon(game)
            elif self.item.type == 'food':
                return self._consume_food(game)
            elif self.item.type == 'hazard':
                return self._trigger_hazard(game)
            elif self.item.type == 'tool':
                # Handle tools - they might be used for various purposes
                if hasattr(self.item, 'use_function') and callable(self.item.use_function):
                    try:
                        result = self.item.use_function(self.npc, self.npc.location)
                        if result:
                            return result
                    except:
                        pass
                return f"{self.npc.name} uses the {self.item.name} to work on something in the area."
        
        # Handle items with specific attributes
        if hasattr(self.item, 'health_restore'):
            # Only use health items if NPC is injured
            if hasattr(self.npc, 'health') and self.npc.health < 100:
                old_health = self.npc.health
                self.npc.health = min(100, self.npc.health + self.item.health_restore)
                health_gained = self.npc.health - old_health
                
                # Remove the item if it's consumable
                if hasattr(self.item, 'consumable') and self.item.consumable:
                    if self.item in self.npc.location.items:
                        self.npc.location.items.remove(self.item)
                    elif hasattr(self.npc, 'items') and self.item in self.npc.items:
                        self.npc.items.remove(self.item)
                
                return f"{self.npc.name} uses {self.item.name} and restores {health_gained} health."
            else:
                return f"{self.npc.name} looks at the {self.item.name} but doesn't need healing right now."
        elif hasattr(self.item, 'damage'):
            # Pick up the weapon if NPC doesn't already have it
            if hasattr(self.npc, 'items') and self.item not in self.npc.items and hasattr(self.npc, 'add_item'):
                if self.item in self.npc.location.items:
                    self.npc.location.items.remove(self.item)
                self.npc.add_item(self.item)
                return f"{self.npc.name} picks up the {self.item.name}."
            return f"{self.npc.name} brandishes {self.item.name} menacingly."
        
        # Check for special items by name
        item_name_lower = self.item.name.lower() if hasattr(self.item, 'name') else ""
        
        # Handle water-related items
        if 'water' in item_name_lower or 'watering' in item_name_lower:
            # Look for plants to water
            plants_watered = False
            plant_messages = []
            
            # Check for objects that might be plants
            for obj in self.npc.location.objects:
                if hasattr(obj, 'water') and callable(obj.water):
                    try:
                        result = obj.water()
                        if result:
                            plants_watered = True
                            plant_messages.append(f"{self.npc.name} waters the {obj.name}.")
                    except:
                        pass
                elif hasattr(obj, 'name') and ('plant' in obj.name.lower() or 
                                              'flower' in obj.name.lower() or 
                                              'tree' in obj.name.lower() or
                                              'garden' in obj.name.lower()):
                    # It looks like a plant but doesn't have a water method
                    plants_watered = True
                    plant_messages.append(f"{self.npc.name} waters the {obj.name}.")
            
            if plants_watered:
                return random.choice(plant_messages)
            else:
                return f"{self.npc.name} looks for plants to water with the {self.item.name}."
        
        # Handle fertilizer
        elif 'fertilizer' in item_name_lower or 'compost' in item_name_lower:
            # Look for plants to fertilize
            for obj in self.npc.location.objects:
                if hasattr(obj, 'name') and ('plant' in obj.name.lower() or 
                                            'flower' in obj.name.lower() or 
                                            'tree' in obj.name.lower() or
                                            'garden' in obj.name.lower() or
                                            'soil' in obj.name.lower()):
                    # Remove fertilizer if it's in the location
                    if self.item in self.npc.location.items:
                        self.npc.location.items.remove(self.item)
                    elif hasattr(self.npc, 'items') and self.item in self.npc.items:
                        self.npc.items.remove(self.item)
                        
                    return f"{self.npc.name} applies {self.item.name} to the {obj.name}."
            
            return f"{self.npc.name} looks for plants to fertilize with the {self.item.name}."
                
        # For generic items, decide whether to pick up the item or just examine it
        # NPCs should have a chance to pick up valuable or interesting items
        should_pickup = False
        
        # Check if the item has value
        if hasattr(self.item, 'value') and self.item.value > 0:
            # Higher value items are more likely to be picked up
            pickup_chance = min(0.8, self.item.value / 100)  # Cap at 80% chance
            should_pickup = random.random() < pickup_chance
        
        # If NPC decides to pick up the item
        if should_pickup and hasattr(self.npc, 'items') and hasattr(self.npc, 'add_item'):
            # IMPORTANT: Check if the item is STILL in the location right before attempting to pick it up
            # This ensures we don't have multiple NPCs picking up the same item
            if self.item in self.npc.location.items:
                # Try to add the item to NPC's inventory - add_item will check if it's a valid Item
                if self.npc.add_item(self.item):
                    # Only remove from location if successfully added to inventory
                    # This is the critical step - remove the item from the area immediately
                    self.npc.location.items.remove(self.item)
                    
                    pickup_messages = [
                        f"{self.npc.name} examines the {self.item.name} carefully and decides to keep it.",
                        f"{self.npc.name} picks up the {self.item.name} and puts it in their pocket.",
                        f"{self.npc.name} takes the {self.item.name} after looking around.",
                        f"{self.npc.name} claims the {self.item.name} for themselves."
                    ]
                    return random.choice(pickup_messages)
                else:
                    # If add_item failed (not a valid Item), just interact with it
                    return f"{self.npc.name} examines the {self.item.name} but doesn't know what to do with it."
            else:
                # Item is no longer in the location
                return f"{self.npc.name} looks for the {self.item.name}, but it's no longer there."
        
        # If the item is still in the area, mark it as being examined
        # This will prevent other NPCs from examining the same item in this turn
        if hasattr(self.item, '_being_examined_by'):
            # Item is already being examined by another NPC
            return None
        else:
            # Mark the item as being examined by this NPC
            setattr(self.item, '_being_examined_by', self.npc.name)
            
            # Schedule the item to be "released" at the end of the turn
            if not hasattr(game, '_items_to_release'):
                game._items_to_release = []
            game._items_to_release.append(self.item)
            
            # Generic interaction for items without special logic
            interaction_messages = [
                f"{self.npc.name} examines the {self.item.name} carefully.",
                f"{self.npc.name} fiddles with the {self.item.name}.",
                f"{self.npc.name} picks up the {self.item.name} briefly before putting it back down.",
                f"{self.npc.name} seems interested in the {self.item.name}.",
                f"{self.npc.name} interacts with the {self.item.name}."
            ]
            return random.choice(interaction_messages)
        
    def _plant_seed(self, game):
        """NPC attempts to plant a seed if soil is available."""
        # Check if the seed is already being used by another NPC
        if hasattr(self.item, '_being_examined_by') and self.item._being_examined_by != self.npc.name:
            # Seed is already being used by another NPC
            return None
            
        # Look for soil in the current area
        soil = None
        for obj in self.npc.location.objects:
            if hasattr(obj, 'add_plant'):  # Simple check for soil-like objects
                soil = obj
                break
                
        if soil:
            # Try to plant the seed
            seed = self.item
            success = False
            message = "the soil is not suitable"
            
            # Mark the seed as being used by this NPC
            setattr(seed, '_being_examined_by', self.npc.name)
            
            # Schedule the seed to be "released" at the end of the turn if planting fails
            if not hasattr(game, '_items_to_release'):
                game._items_to_release = []
            game._items_to_release.append(seed)
            
            # Call add_plant if it exists and has the right signature
            if hasattr(soil, 'add_plant'):
                try:
                    result = soil.add_plant(seed)
                    if isinstance(result, tuple) and len(result) == 2:
                        success, message = result
                    elif isinstance(result, bool):
                        success = result
                        message = "planting succeeded" if success else "planting failed"
                except Exception as e:
                    message = f"an error occurred: {str(e)}"
            
            if success:
                # IMPORTANT: Check if the seed is STILL in the location right before removing it
                if seed in self.npc.location.items:
                    # First check if it's a valid Item (for consistency)
                    if self.npc.add_item(seed):
                        # Remove from location immediately
                        self.npc.location.items.remove(seed)
                        # Remove from NPC's inventory (since it's been planted)
                        self.npc.items.remove(seed)
                    else:
                        # If it's not a valid item, just remove it from the location
                        self.npc.location.items.remove(seed)
                elif hasattr(self.npc, 'items') and seed in self.npc.items:
                    self.npc.items.remove(seed)
                    
                # Remove the seed from the items to release since it's been planted
                if hasattr(game, '_items_to_release') and seed in game._items_to_release:
                    game._items_to_release.remove(seed)
                    
                # Create a custom message
                planting_messages = [
                    f"{self.npc.name} carefully plants the {seed.name} in the {soil.name}.",
                    f"{self.npc.name} digs a small hole in the {soil.name} and plants the {seed.name}.",
                    f"{self.npc.name} decides to grow something and plants the {seed.name}.",
                    f"{self.npc.name} adds the {seed.name} to the {soil.name}, patting the soil gently.",
                    f"{self.npc.name} successfully plants the {seed.name}, looking satisfied with their gardening."
                ]
                return random.choice(planting_messages)
            else:
                # Soil might be full or incompatible
                return f"{self.npc.name} tries to plant the {seed.name}, but {message.lower()}"
        else:
            # Look for soil-like objects by name as a fallback
            potential_soil = None
            soil_keywords = ['soil', 'dirt', 'garden', 'plot', 'planter', 'pot']
            
            # Check objects in the location
            for obj in self.npc.location.objects:
                if hasattr(obj, 'name') and any(keyword in obj.name.lower() for keyword in soil_keywords):
                    potential_soil = obj
                    break
            
            # If we found a potential soil object but it doesn't have add_plant method,
            # we'll simulate planting by removing the seed and returning a message
            if potential_soil:
                # IMPORTANT: Check if the seed is STILL in the location right before removing it
                if self.item in self.npc.location.items:
                    # First check if it's a valid Item (for consistency)
                    if self.npc.add_item(self.item):
                        # Remove from location immediately
                        self.npc.location.items.remove(self.item)
                        # Remove from NPC's inventory (since it's been planted)
                        self.npc.items.remove(self.item)
                        
                        planting_messages = [
                            f"{self.npc.name} carefully plants the {self.item.name} in the {potential_soil.name}.",
                            f"{self.npc.name} digs a small hole in the {potential_soil.name} and plants the {self.item.name}.",
                            f"{self.npc.name} decides to grow something and plants the {self.item.name}.",
                            f"{self.npc.name} adds the {self.item.name} to the {potential_soil.name}, patting it gently."
                        ]
                        return random.choice(planting_messages)
                    else:
                        # If it's not a valid item, just remove it from the location
                        self.npc.location.items.remove(self.item)
                        
                        planting_messages = [
                            f"{self.npc.name} carefully plants the {self.item.name} in the {potential_soil.name}.",
                            f"{self.npc.name} digs a small hole in the {potential_soil.name} and plants the {self.item.name}.",
                            f"{self.npc.name} decides to grow something and plants the {self.item.name}.",
                            f"{self.npc.name} adds the {self.item.name} to the {potential_soil.name}, patting it gently."
                        ]
                        return random.choice(planting_messages)
                elif hasattr(self.npc, 'items') and self.item in self.npc.items:
                    self.npc.items.remove(self.item)
                    
                    planting_messages = [
                        f"{self.npc.name} carefully plants the {self.item.name} in the {potential_soil.name}.",
                        f"{self.npc.name} digs a small hole in the {potential_soil.name} and plants the {self.item.name}.",
                        f"{self.npc.name} decides to grow something and plants the {self.item.name}.",
                        f"{self.npc.name} adds the {self.item.name} to the {potential_soil.name}, patting it gently."
                    ]
                    return random.choice(planting_messages)
                else:
                    # Item is no longer in the location
                    return f"{self.npc.name} looks for the {self.item.name}, but it's no longer there."
            
            # No soil found
            return f"{self.npc.name} looks at the {self.item.name} and seems to be searching for soil to plant it in."
            
    def _pickup_weapon(self, game):
        """NPC attempts to pick up a weapon."""
        # Only gang members should pick up weapons
        if not isinstance(self.npc, GangMember):
            return f"{self.npc.name} looks at the {self.item.name} but decides not to touch it."
            
        # Check if NPC already has a similar or better weapon
        has_better_weapon = False
        for item in self.npc.items:
            if hasattr(item, 'damage') and item.damage >= getattr(self.item, 'damage', 0):
                has_better_weapon = True
                break
                
        if not has_better_weapon:
            # Pick up the weapon
            # IMPORTANT: Check if the weapon is STILL in the location right before attempting to pick it up
            if self.item in self.npc.location.items:
                # Try to add the item to NPC's inventory - add_item will check if it's a valid Item
                if self.npc.add_item(self.item):
                    # Only remove from location if successfully added to inventory
                    # This is the critical step - remove the item from the area immediately
                    self.npc.location.items.remove(self.item)
                    
                    pickup_messages = [
                        f"{self.npc.name} grabs the {self.item.name} and adds it to their arsenal.",
                        f"{self.npc.name} picks up the {self.item.name}, looking pleased with the find.",
                        f"{self.npc.name} examines the {self.item.name} before deciding to keep it.",
                        f"{self.npc.name} takes the {self.item.name}, testing its weight and balance."
                    ]
                    return random.choice(pickup_messages)
                else:
                    # If add_item failed (not a valid Item), just interact with it
                    return f"{self.npc.name} examines the {self.item.name} but doesn't know what to do with it."
            else:
                # Weapon is no longer in the location
                return f"{self.npc.name} looks for the {self.item.name}, but it's no longer there."
        else:
            # Already has a better weapon
            return f"{self.npc.name} looks at the {self.item.name} but decides their current weapon is better."
            
    def _consume_food(self, game):
        """NPC attempts to consume food."""
        # Check if the food has healing properties
        healing = getattr(self.item, 'healing', 0)
        
        # Only consume if NPC is injured
        if hasattr(self.npc, 'health') and self.npc.health < 100 and healing > 0:
            # IMPORTANT: Check if the food is STILL in the location right before attempting to consume it
            if self.item in self.npc.location.items:
                # First add to inventory temporarily (to ensure it's a valid Item)
                if self.npc.add_item(self.item):
                    # Remove from location immediately
                    self.npc.location.items.remove(self.item)
                    # Then remove from inventory (consumed)
                    self.npc.items.remove(self.item)
                    
                    # Apply healing
                    self.npc.health = min(100, self.npc.health + healing)
                    
                    consume_messages = [
                        f"{self.npc.name} eats the {self.item.name} and looks healthier.",
                        f"{self.npc.name} consumes the {self.item.name}, recovering some health.",
                        f"{self.npc.name} quickly devours the {self.item.name}, feeling better afterward.",
                        f"{self.npc.name} takes a moment to eat the {self.item.name}."
                    ]
                    return random.choice(consume_messages)
                else:
                    # Not a valid Item
                    return f"{self.npc.name} examines the {self.item.name} but doesn't know how to use it."
            else:
                # Food is no longer in the location
                return f"{self.npc.name} looks for the {self.item.name}, but it's no longer there."
        else:
            # Not injured or item doesn't heal
            return f"{self.npc.name} examines the {self.item.name} but decides not to eat it right now."
            
    def _trigger_hazard(self, game):
        """NPC accidentally triggers a hazard."""
        # Only non-gang members or confused NPCs should trigger hazards
        if isinstance(self.npc, GangMember) and not any(effect.name == "hallucinations" for effect in self.npc.active_effects):
            return f"{self.npc.name} carefully avoids the {self.item.name}, recognizing it as dangerous."
            
        # Trigger the hazard
        if hasattr(self.item, 'activate'):
            try:
                self.item.activate()
                
                trigger_messages = [
                    f"{self.npc.name} accidentally activates the {self.item.name}!",
                    f"{self.npc.name} triggers the {self.item.name} without realizing what it does!",
                    f"{self.npc.name} curiously pokes at the {self.item.name}, setting it off!",
                    f"Not knowing any better, {self.npc.name} activates the {self.item.name}!"
                ]
                return random.choice(trigger_messages)
            except:
                # Activation failed
                pass
                
        # Item doesn't have an activate method or activation failed
        return f"{self.npc.name} fiddles with the {self.item.name} but nothing happens."

class BehaviorManager:
    """Manages NPC behaviors and transitions."""
    def __init__(self, npc):
        self.npc = npc
        self.current_behavior = IdleBehavior(npc)

    def update(self, game):
        """Update NPC behavior each tick."""
        if not self.npc.is_alive:
            return f"{self.npc.name} is dead and cannot act."

        # Perform current behavior
        result = self.current_behavior.perform(game)

        # Decide next behavior (simple random for now)
        self.choose_next_behavior(game)

        return result

    def choose_next_behavior(self, game):
        """Choose next behavior based on NPC type, state, and environment."""
        # Base behaviors
        behaviors = [IdleBehavior, TalkBehavior, FightBehavior, UseItemBehavior]
        
        # Adjust behavior weights based on NPC type and environment
        behavior_weights = [0.4, 0.3, 0.1, 0.2]  # Default weights: 40% idle, 30% talk, 10% fight, 20% use item
        
        # Gang members are more aggressive
        if isinstance(self.npc, GangMember):
            behavior_weights = [0.1, 0.1, 0.1, 0.7]  # 20% idle, 20% talk, 30% fight, 30% use item
            
            # If player is detected, even more aggressive
            if hasattr(game, 'player') and hasattr(game.player, 'detected_by') and self.npc.gang in game.player.detected_by:
                behavior_weights = [0.1, 0.1, 0.5, 0.3]  # 10% idle, 10% talk, 50% fight, 30% use item
                
            # If hallucinating, less fighting, more item interaction
            if any(effect.name == "hallucinations" for effect in self.npc.active_effects):
                behavior_weights = [0.1, 0.1, 0.1, 0.7]  # 30% idle, 20% talk, 10% fight, 40% use item
                
            # If friendly effect, more talking, no fighting
            if any(effect.name == "friendliness" for effect in self.npc.active_effects):
                behavior_weights = [0.1, 0.4, 0.0, 0.6]  # 30% idle, 50% talk, 0% fight, 20% use item
                
            # If gift-giving effect, more item interaction
            if any(effect.name == "gift-giving" for effect in self.npc.active_effects):
                behavior_weights = [0.0, 0.2, 0.0, 0.8]  # 20% idle, 20% talk, 0% fight, 60% use item
        
        # If there are interesting items in the area, increase chance of item interaction
        items = self.npc.location.items if hasattr(self.npc.location, 'items') else []
        if items:
            # Check for special items
            has_weapons = any(hasattr(item, 'damage') for item in items)
            has_healing = any(hasattr(item, 'healing') or 
                             (hasattr(item, 'type') and item.type == 'food') for item in items)
            
            # Check for seeds both by type and by name
            has_seeds = any((hasattr(item, 'type') and item.type == 'seed') or 
                           (hasattr(item, 'name') and 'seed' in item.name.lower()) for item in items)
            
            has_hazards = any(hasattr(item, 'type') and item.type == 'hazard' for item in items)
            
            # Check for gardening tools
            has_gardening_tools = any(hasattr(item, 'name') and 
                                     any(tool in item.name.lower() for tool in 
                                        ['water', 'watering', 'fertilizer', 'compost', 'shovel', 'trowel', 'rake']) 
                                     for item in items)
            
            # If there are special items, increase item interaction chance
            if has_weapons or has_healing or has_seeds or has_hazards or has_gardening_tools:
                # Increase UseItemBehavior weight by taking from other behaviors
                behavior_weights = [w * 0.7 for w in behavior_weights]  # Reduce all weights by 30%
                behavior_weights[3] += 0.3  # Add 30% to UseItemBehavior
                
                # If there are seeds and soil in the same area, make planting even more likely
                if has_seeds:
                    # Check for soil in the area
                    has_soil = False
                    for obj in self.npc.location.objects:
                        if (hasattr(obj, 'add_plant') or 
                            (hasattr(obj, 'name') and 
                             any(soil_word in obj.name.lower() for soil_word in 
                                ['soil', 'dirt', 'garden', 'plot', 'planter', 'pot']))):
                            has_soil = True
                            break
                    
                    if has_soil:
                        # Further increase UseItemBehavior weight for seed planting
                        behavior_weights = [w * 0.8 for w in behavior_weights]  # Reduce all weights by another 20%
                        behavior_weights[3] += 0.2  # Add another 20% to UseItemBehavior
        
        # Choose behavior based on weights
        choice = random.choices(behaviors, weights=behavior_weights, k=1)[0]

        if choice == IdleBehavior:
            self.current_behavior = IdleBehavior(self.npc)
        elif choice == TalkBehavior:
            # Pick a random NPC or player in the same area to talk to
            targets = [npc for npc in self.npc.location.npcs if npc != self.npc and npc.is_alive]
            
            # Add player as potential target if in same area
            player_in_area = False
            if hasattr(game, 'player') and game.player.current_area == self.npc.location:
                player_in_area = True
                # Only add player as target if not already fighting with gang members
                if not isinstance(self.npc, GangMember) or not game.player.detected_by or self.npc.gang not in game.player.detected_by:
                    targets.append(game.player)
            
            if targets:
                target = random.choice(targets)
                self.current_behavior = TalkBehavior(self.npc, target)
            else:
                self.current_behavior = IdleBehavior(self.npc)
        elif choice == FightBehavior:
            # Pick a random NPC or player to fight
            targets = []
            
            # Filter potential NPC targets
            for npc in self.npc.location.npcs:
                # Skip self and dead NPCs
                if npc == self.npc or not npc.is_alive:
                    continue
                    
                # Gang members don't attack members of the same gang
                if isinstance(self.npc, GangMember) and isinstance(npc, GangMember) and self.npc.gang == npc.gang:
                    continue
                    
                targets.append(npc)
            
            # Add player as potential target if in same area and already detected by this gang
            if hasattr(game, 'player') and game.player.current_area == self.npc.location:
                # Only gang members who have detected the player will fight them
                if isinstance(self.npc, GangMember) and hasattr(game.player, 'detected_by') and self.npc.gang in game.player.detected_by:
                    # Higher chance to target player if detected
                    if random.random() < 0.7:  # 70% chance to target player if detected
                        targets = [game.player]
                    else:
                        targets.append(game.player)
            
            if targets:
                target = random.choice(targets)
                self.current_behavior = FightBehavior(self.npc, target)
            else:
                self.current_behavior = IdleBehavior(self.npc)
        elif choice == UseItemBehavior:
            # Pick an item in the area that makes sense for the NPC to interact with
            items = self.npc.location.items if hasattr(self.npc.location, 'items') else []
            
            if items:
                # Prioritize certain items based on NPC type and state
                prioritized_items = []
                
                # Gang members prioritize weapons when healthy, healing items when injured
                if isinstance(self.npc, GangMember):
                    if self.npc.health < 50:  # Injured
                        # Look for healing items
                        healing_items = [item for item in items if hasattr(item, 'healing') or 
                                        (hasattr(item, 'type') and item.type == 'food')]
                        prioritized_items.extend(healing_items)
                    else:  # Healthy
                        # Look for weapons
                        weapon_items = [item for item in items if hasattr(item, 'damage') or 
                                       (hasattr(item, 'type') and item.type == 'weapon')]
                        prioritized_items.extend(weapon_items)
                
                # All NPCs might be interested in seeds if there's soil nearby
                has_soil = any(hasattr(obj, 'add_plant') for obj in self.npc.location.objects)
                if has_soil:
                    seed_items = [item for item in items if hasattr(item, 'type') and item.type == 'seed']
                    prioritized_items.extend(seed_items)
                
                # If hallucinating, might interact with hazards
                is_hallucinating = isinstance(self.npc, GangMember) and any(effect.name == "hallucinations" for effect in self.npc.active_effects)
                if is_hallucinating:
                    hazard_items = [item for item in items if hasattr(item, 'type') and item.type == 'hazard']
                    prioritized_items.extend(hazard_items)
                
                # Choose an item, prioritizing the ones we've identified
                if prioritized_items and random.random() < 0.7:  # 70% chance to pick a prioritized item
                    item = random.choice(prioritized_items)
                else:
                    item = random.choice(items)
                    
                self.current_behavior = UseItemBehavior(self.npc, item)
            else:
                self.current_behavior = IdleBehavior(self.npc)

def group_hazard_results(hazard, results):
    """Group hazard results by effect status with proper grammar and interesting details"""
    affected = collections.defaultdict(list)  # effect_variant -> list of member names
    resisted = []
    gang_name = None

    for result in results:
        if "resists" in result:
            # Example: "The Bloodhounds member Buck resists the Hacked Milk Spill effect!"
            parts = result.split()
            member_name = parts[3]
            resisted.append(member_name)
            if not gang_name:
                gang_name = parts[1]
        else:
            # Example: "Bloodhounds member Buck affected:hallucination"
            parts = result.split()
            member_name = parts[2]
            effect_variant = parts[-1]
            affected[effect_variant].append(member_name)
            if not gang_name:
                gang_name = parts[0]

    messages = []

    def construct_affect_message(member, effect_type, count):
        if effect_type == "hallucinations":
            if count == 1:
                hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("singular", []))
            else:
                hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("plural", []))
            return f"The {gang_name} member {member} is hallucinating from the {hazard.name}. {member} {hallucination}"
        elif effect_type == "gift-giving":
            return f"The {gang_name} member {member} gets covered in glitter and starts compulsively giving gifts!"
        elif effect_type == "friendliness":
            if count == 1:
                friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("singular", []))
            else:
                friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("plural", []))
            return f"The {gang_name} member {member} breathes in the {hazard.name}, and looks unusually cheerful. {member} says, '{friendlyphrase}'"
        elif effect_type == "falling objects":
            if count == 1:
                falling_reaction = random.choice(NPC_REACTIONS.get("possible_falling_reactions", {}).get("singular", []))
            else:
                falling_reaction = random.choice(NPC_REACTIONS.get("possible_falling_reactions", {}).get("plural", []))
            return f"The {gang_name} member {member} {falling_reaction}"
        else:
            return f"The {gang_name} member {member} is affected by {effect_type}."

    def construct_resist_message(member, count):
        if count == 1:
            return f"The {gang_name} member {member} resists the hazard effect."
        else:
            return f"The {gang_name} members {member} resist the hazard effect."

    # Group affected members by effect variant
    for effect_variant, members in affected.items():
        count = len(members)
        if count == 1:
            messages.append(construct_affect_message(members[0], effect_variant, count))
        else:
            # Use consistent formatting for groups of NPCs
            if count <= 3:
                member_list = ", ".join(members)
            else:
                # For more than 3 members, only list 3 and summarize the rest
                member_list = ", ".join(members[:3]) + f" and {count - 3} others"
                
            group_message = f"The {gang_name} members {member_list} are affected by {effect_variant}."
            
            # Add specific reactions for hallucinations and other effects for groups
            if effect_variant == "hallucinations":
                hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("plural", []))
                group_message += f" They {hallucination}"
            elif effect_variant == "gift-giving":
                group_message += " They get covered in glitter and start a spontaneous gift exchange!"
            elif effect_variant == "friendliness":
                friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("plural", []))
                group_message += f" They look unusually cheerful. Someone says, '{friendlyphrase}'"
            elif effect_variant == "falling objects":
                falling_reaction = random.choice(NPC_REACTIONS.get("possible_falling_reactions", {}).get("plural", []))
                group_message += f" {falling_reaction}"
                
            messages.append(group_message)

    # Group resisted members
    if resisted:
        count = len(resisted)
        if count == 1:
            messages.append(construct_resist_message(resisted[0], count))
        else:
            # Use consistent formatting for groups of NPCs
            if count <= 3:
                member_list = ", ".join(resisted)
            else:
                # For more than 3 members, only list 3 and summarize the rest
                member_list = ", ".join(resisted[:3]) + f" and {count - 3} others"
            messages.append(f"The {gang_name} members {member_list} resist the hazard effect.")

    return "\n".join(messages) if messages else f"The hazard has no effect on anyone."
