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
        self.items.append(item)

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
        self.detection_chance = 10  # 10 = Base 10% chance to detect player
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
        # Check hazard effects first
        for effect in self.active_effects:
            if effect.name == "hallucinations":
                return f"The {self.gang.name} member {self.name} is so high that they don't see you."
            if effect.name == "friendliness":
                return f"The {self.gang.name} member {self.name} smiles at you warmly."  # add random friendliness outcomes here as well as other places where it would take effect
            if effect.name == "gift-giving" and self.items:
                gift = random.choice(self.items)
                player.inventory.append(gift)
                self.items.remove(gift)
                return f"The {self.gang.name} member {self.name} gives you {gift.name} as a gift!"

        # Normal detection logic
        if not player.hidden and (self.has_detected_player or random.random() < self.detection_chance / 100):
            self.has_detected_player = True
            player.detected_by.add(self.gang)

            if self.items:
                weapon = next((i for i in self.items if hasattr(i, 'damage')), None)
                damage = weapon.damage if weapon else 1
                player.health -= damage
                result = f"The {self.gang.name} member {self.name} spots and attacks you for {damage} damage!"
                if player.health <= 0:
                    result += "\nYou have been defeated!"
                return result
            return f"The {self.gang.name} member {self.name} spots you and threatens you but has no weapon!"

        if player.hidden:
            self.has_detected_player = False
            return f"The {self.gang.name} member {self.name} looks around but doesn't see you."
        return f"The {self.gang.name} member {self.name} doesn't notice you."

    def update_behavior(self, game):
        """Update NPC behavior each game tick."""
        if not self.is_alive:
            return f"{self.name} is dead and cannot act."
        behavior_result = None
        if self.behavior_manager:
            behavior_result = self.behavior_manager.update(game)
        # After behavior update, gang member may attack player if conditions met
        if hasattr(game, 'player') and self.location == game.player.current_area and self.is_alive:
            attack_result = self.attack_player(game.player)
            if behavior_result:
                return f"{behavior_result}\n{attack_result}"
            else:
                return attack_result
        return behavior_result

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
        self.max_buffer_size = 10
        self.summarize_threshold = 3  # Number of messages before summarizing

    def add_message(self, message):
        """Add a message to the buffer."""
        self.message_buffer.append(message)
        
        # If buffer exceeds max size, summarize and clear
        if len(self.message_buffer) >= self.max_buffer_size:
            return self.get_summary(clear=True)
        return None

    def get_summary(self, clear=False):
        """Get a summary of the current messages in the buffer."""
        if not self.message_buffer:
            return None
            
        if len(self.message_buffer) < self.summarize_threshold:
            # Not enough messages to summarize, return as is
            result = "\n".join(self.message_buffer)
        else:
            # Summarize messages by type and gang
            result = self._create_summary()
            
        if clear:
            self.message_buffer.clear()
            
        return result
        
    def _create_summary(self):
        """Create a summary of messages by categorizing them."""
        # Group messages by gang and action type
        gang_actions = collections.defaultdict(lambda: collections.defaultdict(list))
        
        for message in self.message_buffer:
            # Extract gang name and member name
            if "Bloodhounds member" in message:
                gang_name = "Bloodhounds"
                # Extract member name
                parts = message.split()
                member_idx = parts.index("member") + 1 if "member" in parts else -1
                if member_idx >= 0 and member_idx < len(parts):
                    member_name = parts[member_idx]
                else:
                    member_name = "Unknown"
                
                # Categorize action
                if "doesn't notice you" in message or "doesn't see you" in message:
                    action_type = "unaware"
                elif "spots you" in message or "attacks you" in message:
                    action_type = "hostile"
                elif "hallucinating" in message:
                    action_type = "hallucinating"
                elif "smiles at you" in message or "friendly" in message:
                    action_type = "friendly"
                elif "gives you" in message:
                    action_type = "gift-giving"
                else:
                    action_type = "other"
                
                gang_actions[gang_name][action_type].append(member_name)
        
        # Create summary messages
        summary = []
        for gang, actions in gang_actions.items():
            for action_type, members in actions.items():
                if action_type == "unaware":
                    if len(members) == 1:
                        summary.append(f"The {gang} member {members[0]} hasn't noticed you.")
                    else:
                        summary.append(f"The {gang} members ({', '.join(members[:3])}{' and others' if len(members) > 3 else ''}) haven't noticed you.")
                
                elif action_type == "hostile":
                    if len(members) == 1:
                        summary.append(f"The {gang} member {members[0]} has spotted you and looks hostile!")
                    else:
                        summary.append(f"Several {gang} members ({', '.join(members[:3])}{' and others' if len(members) > 3 else ''}) have spotted you and look ready to attack!")
                
                elif action_type == "hallucinating":
                    if len(members) == 1:
                        hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("singular", ["is seeing things that aren't there."]))
                        summary.append(f"The {gang} member {members[0]} {hallucination}")
                    else:
                        hallucination = random.choice(NPC_REACTIONS.get("possible_hallucinations", {}).get("plural", ["are seeing things that aren't there."]))
                        summary.append(f"Several {gang} members ({', '.join(members[:3])}{' and others' if len(members) > 3 else ''}) {hallucination}")
                
                elif action_type == "friendly":
                    if len(members) == 1:
                        friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("singular", ["seems unusually friendly."]))
                        summary.append(f"The {gang} member {members[0]} {friendlyphrase}")
                    else:
                        friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("plural", ["seem unusually friendly."]))
                        summary.append(f"Several {gang} members ({', '.join(members[:3])}{' and others' if len(members) > 3 else ''}) {friendlyphrase}")
                
                elif action_type == "gift-giving":
                    if len(members) == 1:
                        summary.append(f"The {gang} member {members[0]} is compulsively giving away items.")
                    else:
                        summary.append(f"Several {gang} members ({', '.join(members[:3])}{' and others' if len(members) > 3 else ''}) are giving away items to anyone nearby.")
                
                else:
                    # Generic summary for other actions
                    if len(members) == 1:
                        summary.append(f"The {gang} member {members[0]} is active in the area.")
                    else:
                        summary.append(f"Several {gang} members ({', '.join(members[:3])}{' and others' if len(members) > 3 else ''}) are active in the area.")
        
        return "\n".join(summary)

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
        # NPC might look around or say something idle
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
        # Simple fight logic: reduce health, print fight message
        damage = random.randint(5, 15)
        self.target.health -= damage
        
        # Check if target is player (doesn't have name attribute)
        is_player = not hasattr(self.target, 'name')
        target_name = "you" if is_player else self.target.name
        
        if self.target.health <= 0:
            self.target.is_alive = False
            if is_player:
                result = f"{self.npc.name} has defeated you!"
            else:
                result = f"{self.npc.name} has defeated {target_name}!"
        else:
            if is_player:
                result = f"{self.npc.name} attacks you for {damage} damage. You have {self.target.health} health left."
            else:
                result = f"{self.npc.name} attacks {target_name} for {damage} damage. {target_name} has {self.target.health} health left."
        return result

class UseItemBehavior(Behavior):
    """NPC uses an item in the environment."""
    def __init__(self, npc, item):
        super().__init__(npc)
        self.item = item

    def perform(self, game):
        # Example: NPC uses an item, e.g., healing or weapon
        if hasattr(self.item, 'health_restore'):
            self.npc.health += self.item.health_restore
            return f"{self.npc.name} uses {self.item.name} and restores {self.item.health_restore} health."
        elif hasattr(self.item, 'damage'):
            return f"{self.npc.name} brandishes {self.item.name} menacingly."
        else:
            return f"{self.npc.name} interacts with {self.item.name}."

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
        """Randomly choose next behavior for demonstration."""
        behaviors = [IdleBehavior, TalkBehavior, FightBehavior, UseItemBehavior]
        choice = random.choice(behaviors)

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
            targets = [npc for npc in self.npc.location.npcs if npc != self.npc and npc.is_alive]
            
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
            # Pick a random item in the area
            items = self.npc.location.items if hasattr(self.npc.location, 'items') else []
            if items:
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
            max_names = 4
            if count <= max_names:
                member_list = ", ".join(members[:-1]) + " and " + members[-1] if count > 1 else members[0]
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
            else:
                # More than max_names, split into named and remainder groups
                named_members = members[:max_names]
                remainder_count = count - max_names
                remainder_members = members[max_names:]
                member_list = ", ".join(named_members[:-1]) + " and " + named_members[-1]
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

                # Add remainder message
                group_remainder_list = NPC_REACTIONS.get(f"possible_{effect_variant.replace(' ', '_')}", {}).get("group_remainder", [])
                if group_remainder_list:
                    remainder_phrase = random.choice(group_remainder_list)
                else:
                    remainder_phrase = ""
                if remainder_count == 1:
                    remainder_message = f"{remainder_members[0]} {remainder_phrase}"
                else:
                    remainder_message = f"{remainder_phrase}"
                messages.append(remainder_message)

    # Group resisted members
    if resisted:
        count = len(resisted)
        if count == 1:
            messages.append(construct_resist_message(resisted[0], count))
        else:
            member_list = ", ".join(resisted[:-1]) + " and " + resisted[-1] if count > 1 else resisted[0]
            messages.append(f"The {gang_name} members {member_list} resist the hazard effect.")

    return "\n".join(messages) if messages else f"The hazard has no effect on anyone."
