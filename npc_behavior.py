"""
NPC Behavior module for Root Access game.
This module defines NPC behavior patterns and AI.
"""

import random
from enum import Enum

class BehaviorType(Enum):
    """Enum for different NPC behavior types."""
    IDLE = 0
    PATROL = 1
    FOLLOW = 2
    FLEE = 3
    ATTACK = 4
    DISTRACTED = 5


class BehaviorSettings:
    """Settings for NPC behavior."""
    
    def __init__(self, behavior_type=BehaviorType.IDLE, target=None, duration=None, path=None):
        """Initialize BehaviorSettings object."""
        self.behavior_type = behavior_type
        self.target = target  # Target object or coordinates
        self.duration = duration  # How long the behavior lasts (in turns)
        self.path = path  # List of coordinates for patrol paths
        self.current_path_index = 0


class Gang:
    """Represents a gang in the game."""
    
    def __init__(self, name):
        """Initialize a Gang object."""
        self.name = name
        self.members = []
        self.territory = None
        self.rival_gangs = []
        self.member_names = []
    
    def add_member(self, member):
        """Add a member to the gang."""
        self.members.append(member)
        member.gang = self
    
    def remove_member(self, member):
        """Remove a member from the gang."""
        if member in self.members:
            self.members.remove(member)
            member.gang = None
    
    def is_rival(self, other_gang):
        """Check if another gang is a rival."""
        return other_gang in self.rival_gangs
    
    def add_rival(self, other_gang):
        """Add a rival gang."""
        if other_gang not in self.rival_gangs:
            self.rival_gangs.append(other_gang)
            if self not in other_gang.rival_gangs:
                other_gang.add_rival(self)


class NPC:
    """Base class for all NPCs in the game."""
    
    def __init__(self, name, description):
        """Initialize an NPC object."""
        self.name = name
        self.description = description
        self.items = []
        self.x = None
        self.y = None
        self.location = None
        self.behavior = BehaviorSettings()
        self.active_effects = {}
        self.is_alive = True
        self.health = 100
        self.detection_ability = 1.0  # Base detection ability
    
    def place_on_grid(self, grid, x, y):
        """Place the NPC on a grid at the specified coordinates."""
        if grid.place_object(self, x, y):
            self.x = x
            self.y = y
            return True
        return False
    
    def move(self, dx, dy, grid):
        """Move the NPC by the specified delta."""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if the new position is valid
        if not grid.is_valid_coordinate(new_x, new_y):
            return False
        
        # Check if the new position is occupied
        if grid.is_cell_occupied(new_x, new_y):
            return False
        
        # Move the NPC
        grid.remove_object(self.x, self.y)
        grid.place_object(self, new_x, new_y)
        self.x = new_x
        self.y = new_y
        
        return True
    
    def move_towards(self, target_x, target_y, grid):
        """Move the NPC towards the target coordinates."""
        # Calculate direction
        dx = 0
        dy = 0
        
        if target_x > self.x:
            dx = 1
        elif target_x < self.x:
            dx = -1
        
        if target_y > self.y:
            dy = 1
        elif target_y < self.y:
            dy = -1
        
        # Try to move in the calculated direction
        if dx != 0 and dy != 0:
            # Diagonal movement - try horizontal first, then vertical
            if random.random() < 0.5:
                if not self.move(dx, 0, grid):
                    self.move(0, dy, grid)
            else:
                if not self.move(0, dy, grid):
                    self.move(dx, 0, grid)
        else:
            # Straight movement
            self.move(dx, dy, grid)
    
    def move_away_from(self, target_x, target_y, grid):
        """Move the NPC away from the target coordinates."""
        # Calculate direction (opposite of move_towards)
        dx = 0
        dy = 0
        
        if target_x > self.x:
            dx = -1
        elif target_x < self.x:
            dx = 1
        
        if target_y > self.y:
            dy = -1
        elif target_y < self.y:
            dy = 1
        
        # Try to move in the calculated direction
        if dx != 0 and dy != 0:
            # Diagonal movement - try horizontal first, then vertical
            if random.random() < 0.5:
                if not self.move(dx, 0, grid):
                    self.move(0, dy, grid)
            else:
                if not self.move(0, dy, grid):
                    self.move(dx, 0, grid)
        else:
            # Straight movement
            self.move(dx, dy, grid)
    
    def update_behavior(self, player):
        """Update the NPC's behavior based on the player and environment."""
        # Check if the NPC is affected by any effects
        if "Confusion" in self.active_effects:
            # Confused NPCs move randomly
            self.behavior.behavior_type = BehaviorType.IDLE
            return
        
        if "Hallucination" in self.active_effects:
            # Hallucinating NPCs might attack randomly
            if random.random() < 0.2:
                self.behavior.behavior_type = BehaviorType.ATTACK
                self.behavior.target = player
            else:
                self.behavior.behavior_type = BehaviorType.IDLE
            return
        
        # Default behavior is to idle
        self.behavior.behavior_type = BehaviorType.IDLE
    
    def execute_behavior(self, grid):
        """Execute the NPC's current behavior."""
        if self.behavior.behavior_type == BehaviorType.IDLE:
            # 20% chance to move randomly
            if random.random() < 0.2:
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
                self.move(dx, dy, grid)
        
        elif self.behavior.behavior_type == BehaviorType.PATROL:
            if self.behavior.path and len(self.behavior.path) > 0:
                # Move along the patrol path
                target = self.behavior.path[self.behavior.current_path_index]
                self.move_towards(target[0], target[1], grid)
                
                # Check if we've reached the target
                if self.x == target[0] and self.y == target[1]:
                    # Move to the next point in the path
                    self.behavior.current_path_index = (self.behavior.current_path_index + 1) % len(self.behavior.path)
        
        elif self.behavior.behavior_type == BehaviorType.FOLLOW:
            if self.behavior.target:
                # Get target coordinates
                target_x = self.behavior.target.x if hasattr(self.behavior.target, 'x') else self.behavior.target[0]
                target_y = self.behavior.target.y if hasattr(self.behavior.target, 'y') else self.behavior.target[1]
                
                # Move towards the target
                self.move_towards(target_x, target_y, grid)
        
        elif self.behavior.behavior_type == BehaviorType.FLEE:
            if self.behavior.target:
                # Get target coordinates
                target_x = self.behavior.target.x if hasattr(self.behavior.target, 'x') else self.behavior.target[0]
                target_y = self.behavior.target.y if hasattr(self.behavior.target, 'y') else self.behavior.target[1]
                
                # Move away from the target
                self.move_away_from(target_x, target_y, grid)
        
        elif self.behavior.behavior_type == BehaviorType.ATTACK:
            if self.behavior.target:
                # Get target coordinates
                target_x = self.behavior.target.x if hasattr(self.behavior.target, 'x') else self.behavior.target[0]
                target_y = self.behavior.target.y if hasattr(self.behavior.target, 'y') else self.behavior.target[1]
                
                # Check if we're adjacent to the target
                if abs(self.x - target_x) <= 1 and abs(self.y - target_y) <= 1:
                    # Attack the target
                    if hasattr(self, 'attack') and hasattr(self.behavior.target, 'take_damage'):
                        self.attack(self.behavior.target)
                else:
                    # Move towards the target
                    self.move_towards(target_x, target_y, grid)
        
        elif self.behavior.behavior_type == BehaviorType.DISTRACTED:
            # Do nothing while distracted
            pass
    
    def update_effects(self):
        """Update active effects and remove expired ones."""
        expired_effects = []
        for effect_name, turns_remaining in list(self.active_effects.items()):
            self.active_effects[effect_name] -= 1
            if self.active_effects[effect_name] <= 0:
                expired_effects.append(effect_name)
        
        # Remove expired effects
        for effect_name in expired_effects:
            del self.active_effects[effect_name]
        
        return expired_effects
    
    def take_damage(self, damage):
        """Take damage and update health."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()
    
    def die(self):
        """Handle the NPC's death."""
        self.is_alive = False
        self.health = 0
        
        # Drop all items
        if hasattr(self, 'location') and self.location:
            for item in self.items:
                item.x = self.x
                item.y = self.y
                self.location.add_item(item)
            self.items = []
    
    def talk(self, player):
        """Talk to the player."""
        return True, f"{self.name} says: Hello there!"
    
    def distract(self):
        """Distract the NPC."""
        self.behavior.behavior_type = BehaviorType.DISTRACTED
        self.behavior.duration = 3  # Distracted for 3 turns
        return True
    
    def distract_with_decoy(self, decoy_x, decoy_y):
        """Distract the NPC with a decoy."""
        self.behavior.behavior_type = BehaviorType.FOLLOW
        self.behavior.target = (decoy_x, decoy_y)
        self.behavior.duration = 5  # Follow the decoy for 5 turns
        return True


class Civilian(NPC):
    """A civilian NPC."""
    
    def __init__(self, name, description):
        """Initialize a Civilian object."""
        super().__init__(name, description)
        self.fear_level = 0  # 0-100, affects behavior
    
    def update_behavior(self, player):
        """Update the civilian's behavior based on the player and environment."""
        # Check if the civilian is affected by any effects
        if "Confusion" in self.active_effects or "Hallucination" in self.active_effects:
            super().update_behavior(player)
            return
        
        # Check if the player is nearby
        if player and hasattr(player, 'x') and hasattr(player, 'y'):
            distance = max(abs(self.x - player.x), abs(self.y - player.y))
            
            # If the player is armed and close, flee
            has_weapon = any(hasattr(item, 'damage') for item in player.inventory)
            
            if has_weapon and distance <= 3:
                self.fear_level = min(100, self.fear_level + 20)
            elif distance <= 1:
                self.fear_level = min(100, self.fear_level + 10)
            else:
                self.fear_level = max(0, self.fear_level - 5)
            
            # Determine behavior based on fear level
            if self.fear_level >= 70:
                self.behavior.behavior_type = BehaviorType.FLEE
                self.behavior.target = player
            elif self.fear_level >= 30:
                # Move randomly, avoiding the player
                self.behavior.behavior_type = BehaviorType.IDLE
            else:
                # Normal behavior - patrol or idle
                if random.random() < 0.3:
                    self.behavior.behavior_type = BehaviorType.PATROL
                    
                    # Create a random patrol path if none exists
                    if not self.behavior.path:
                        grid_width = self.location.grid.width if hasattr(self.location, 'grid') else 20
                        grid_height = self.location.grid.height if hasattr(self.location, 'grid') else 20
                        
                        self.behavior.path = [
                            (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
                            for _ in range(3)
                        ]
                else:
                    self.behavior.behavior_type = BehaviorType.IDLE
        else:
            # Default behavior
            super().update_behavior(player)
    
    def talk(self, player):
        """Talk to the player."""
        # Different responses based on fear level
        if self.fear_level >= 70:
            return True, f"{self.name} says: Please don't hurt me! I'll do whatever you want!"
        elif self.fear_level >= 30:
            return True, f"{self.name} says: Um, hello... Can I help you with something?"
        else:
            greetings = [
                f"Hello there! Nice day, isn't it?",
                f"Oh, hi! I'm {self.name}. What's your name?",
                f"Hey! How's it going?",
                f"Well met, traveler!",
                f"Greetings! What brings you to these parts?"
            ]
            return True, f"{self.name} says: {random.choice(greetings)}"


class GangMember(NPC):
    """A gang member NPC."""
    
    def __init__(self, name, description):
        """Initialize a GangMember object."""
        super().__init__(name, description)
        self.gang = None
        self.aggression = random.randint(30, 70)  # 0-100, affects behavior
        self.status = "alive"  # "alive", "knocked out", "dead"
    
    def update_behavior(self, player):
        """Update the gang member's behavior based on the player and environment."""
        # Check if the gang member is affected by any effects
        if "Confusion" in self.active_effects or "Hallucination" in self.active_effects:
            super().update_behavior(player)
            return
        
        # Check if the gang member is knocked out or dead
        if self.status != "alive":
            self.behavior.behavior_type = BehaviorType.IDLE
            return
        
        # Check for rival gang members in the area
        if hasattr(self, 'location') and hasattr(self.location, 'gang_members'):
            rivals = [
                member for member in self.location.gang_members
                if member.gang and self.gang and member.gang != self.gang and member.status == "alive"
            ]
            
            if rivals:
                # Attack a random rival
                target = random.choice(rivals)
                self.behavior.behavior_type = BehaviorType.ATTACK
                self.behavior.target = target
                return
        
        # Check if the player is nearby and not hidden
        if player and hasattr(player, 'x') and hasattr(player, 'y') and not player.hidden:
            distance = max(abs(self.x - player.x), abs(self.y - player.y))
            
            # If the player is close, react based on aggression
            if distance <= 5:
                if self.aggression >= 70:
                    # Highly aggressive - attack the player
                    self.behavior.behavior_type = BehaviorType.ATTACK
                    self.behavior.target = player
                elif self.aggression >= 30:
                    # Moderately aggressive - follow the player
                    self.behavior.behavior_type = BehaviorType.FOLLOW
                    self.behavior.target = player
                else:
                    # Not very aggressive - patrol or idle
                    if random.random() < 0.5:
                        self.behavior.behavior_type = BehaviorType.PATROL
                        
                        # Create a random patrol path if none exists
                        if not self.behavior.path:
                            grid_width = self.location.grid.width if hasattr(self.location, 'grid') else 20
                            grid_height = self.location.grid.height if hasattr(self.location, 'grid') else 20
                            
                            self.behavior.path = [
                                (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
                                for _ in range(3)
                            ]
                    else:
                        self.behavior.behavior_type = BehaviorType.IDLE
            else:
                # Default behavior - patrol or idle
                if random.random() < 0.7:
                    self.behavior.behavior_type = BehaviorType.PATROL
                    
                    # Create a random patrol path if none exists
                    if not self.behavior.path:
                        grid_width = self.location.grid.width if hasattr(self.location, 'grid') else 20
                        grid_height = self.location.grid.height if hasattr(self.location, 'grid') else 20
                        
                        self.behavior.path = [
                            (random.randint(0, grid_width - 1), random.randint(0, grid_height - 1))
                            for _ in range(3)
                        ]
                else:
                    self.behavior.behavior_type = BehaviorType.IDLE
        else:
            # Default behavior
            super().update_behavior(player)
    
    def talk(self, player):
        """Talk to the player."""
        # Different responses based on aggression
        if self.aggression >= 70:
            threats = [
                f"What are you looking at? Get lost before I make you regret it!",
                f"You're in {self.gang.name if self.gang else 'our'} territory now. Better watch yourself.",
                f"I don't like your face. Maybe I should rearrange it for you.",
                f"You picked the wrong person to talk to. Back off!",
                f"*spits on the ground* I ain't got nothing to say to you."
            ]
            return True, f"{self.name} says: {random.choice(threats)}"
        elif self.aggression >= 30:
            warnings = [
                f"You better have a good reason for talking to me.",
                f"What do you want? Make it quick.",
                f"I'm busy. Don't waste my time.",
                f"*eyes you suspiciously* Yeah?",
                f"You're not from around here, are you? What's your business?"
            ]
            return True, f"{self.name} says: {random.choice(warnings)}"
        else:
            neutral = [
                f"Hey there. What can I do for you?",
                f"*nods* What's up?",
                f"You looking for something?",
                f"*looks around nervously* You shouldn't be seen talking to me.",
                f"Keep it down. What do you need?"
            ]
            return True, f"{self.name} says: {random.choice(neutral)}"
    
    def attack(self, target):
        """Attack a target."""
        damage = random.randint(5, 15)
        
        if hasattr(target, 'take_damage'):
            target.take_damage(damage)
            
            # Check if the target is defeated
            if hasattr(target, 'health') and target.health <= 0:
                if hasattr(target, 'die'):
                    target.die()
                return True, f"{self.name} attacks {target.name} for {damage} damage! {target.name} has been defeated!"
            
            return True, f"{self.name} attacks {target.name} for {damage} damage! {target.name}'s health: {target.health}/100"
        
        return False, f"{self.name} can't attack {target.name}."
    
    def knockout(self, player):
        """Knock out the gang member."""
        self.status = "knocked out"
        
        # Drop all items
        if hasattr(self, 'location') and self.location:
            for item in self.items:
                item.x = self.x
                item.y = self.y
                self.location.add_item(item)
            self.items = []
        
        return True, f"{self.name} has been knocked out!"
    
    def gangfight(self):
        """Initiate a gang fight with rival gang members."""
        # Check if there are rival gang members in the area
        if not hasattr(self, 'location') or not hasattr(self.location, 'gang_members'):
            return False, "No gang members to fight."
        
        rivals = [
            member for member in self.location.gang_members
            if member.gang and self.gang and member.gang != self.gang and member.status == "alive"
        ]
        
        if not rivals:
            return False, "No rival gang members to fight."
        
        # Attack a random rival
        target = random.choice(rivals)
        return self.attack(target)


class NPCBehaviorCoordinator:
    """Coordinates the behavior of all NPCs in the game."""
    
    def __init__(self):
        """Initialize an NPCBehaviorCoordinator object."""
        pass
    
    def update_npcs(self, player):
        """Update the behavior of all NPCs in the player's current area."""
        if not player or not hasattr(player, 'current_area'):
            return
        
        area = player.current_area
        
        # Update NPCs
        if hasattr(area, 'npcs'):
            for npc in area.npcs:
                if hasattr(npc, 'update_behavior'):
                    npc.update_behavior(player)
                
                if hasattr(npc, 'execute_behavior') and hasattr(area, 'grid'):
                    npc.execute_behavior(area.grid)
                
                if hasattr(npc, 'update_effects'):
                    npc.update_effects()
        
        # Update gang members
        if hasattr(area, 'gang_members'):
            for member in area.gang_members:
                if hasattr(member, 'update_behavior'):
                    member.update_behavior(player)
                
                if hasattr(member, 'execute_behavior') and hasattr(area, 'grid'):
                    member.execute_behavior(area.grid)
                
                if hasattr(member, 'update_effects'):
                    member.update_effects()


# Default behavior settings
behavior_settings = {
    "civilian": {
        "idle_chance": 0.5,
        "patrol_chance": 0.3,
        "follow_chance": 0.1,
        "flee_chance": 0.1,
        "attack_chance": 0.0
    },
    "gang_member": {
        "idle_chance": 0.3,
        "patrol_chance": 0.4,
        "follow_chance": 0.1,
        "flee_chance": 0.0,
        "attack_chance": 0.2
    }
}
