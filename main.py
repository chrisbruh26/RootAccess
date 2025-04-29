import random
import os
import json

# ----------------------------- #
# CORE GAME CLASSES AND SYSTEMS #
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


class Consumable(Item):
    def __init__(self, name, description, value, health_restore):
        super().__init__(name, description, value)
        self.health_restore = health_restore

    def __str__(self):
        return f"{self.name} (Restores: {self.health_restore} health)"
    

class Seed(Item):
    def __init__(self, name, description, crop_type, value, growth_time=3):
        super().__init__(name, description, value)
        self.crop_type = crop_type
        self.growth_time = growth_time  # Number of turns until fully grown
    
    def __str__(self):
        return f"{self.name} ({self.crop_type})"

class Plant(Item):
    def __init__(self, name, description, crop_type, value, growth_stage=0, max_growth=3):
        super().__init__(name, description, value)
        self.crop_type = crop_type
        self.growth_stage = growth_stage
        self.max_growth = max_growth
        self.effects = []  # List of effects applied to this plant
        self.watering_history = []  # Track what substances were used to water this plant
        
    def grow(self):
        if self.growth_stage < self.max_growth:
            self.growth_stage += 1
            return True
        return False
    
    def water(self, substance=None):
        """Water the plant to accelerate growth, optionally with a special substance."""
        if self.growth_stage >= self.max_growth:
            return False, f"The {self.name} is already fully grown and ready to harvest."
        
        # Track what was used to water the plant
        if (substance):
            self.watering_history.append(substance)
            
            # Apply effects from the substance to the plant
            for effect in substance.effects:
                if effect not in self.effects:
                    self.effects.append(effect)
            
            message = f"You water the {self.name} with {substance.name}."
        else:
            message = f"You water the {self.name} with regular water."
        
        # Water the plant, which advances growth by a full stage
        self.growth_stage += 1
        
        if self.is_harvestable():
            return True, f"{message} It's now fully grown and ready to harvest!"
        else:
            return True, f"{message} It grows visibly before your eyes!"
    
    def is_harvestable(self):
        return self.growth_stage >= self.max_growth
    
    def add_effect(self, effect):
        """Add an effect to this plant."""
        if effect not in self.effects:
            self.effects.append(effect)
            return True, f"The {effect.name} effect has been applied to the {self.name}."
        return False, f"The {self.name} already has the {effect.name} effect."
    
    def get_harvested_item(self):
        """Create a harvested item based on this plant, transferring any effects."""
        harvested_item = Item(
            f"{self.crop_type.capitalize()}", 
            f"A freshly harvested {self.crop_type}.", 
            self.value
        )
        
        # Transfer effects to the harvested item
        if self.effects:
            harvested_item.effects = self.effects.copy()
            effect_names = ", ".join(effect.name for effect in self.effects)
            harvested_item.description += f" It seems to have been affected by: {effect_names}."
        
        return harvested_item
    
    def __str__(self):
        stage_desc = "seedling" if self.growth_stage == 0 else \
                    "growing" if self.growth_stage < self.max_growth else \
                    "ready to harvest"
        
        base_str = f"{self.name} ({stage_desc})"
        
        if self.effects:
            effect_names = ", ".join(effect.name for effect in self.effects)
            base_str += f" [Effects: {effect_names}]"
            
        return base_str


# Plant Effects System

class PlantEffect:
    """Base class for all plant effects."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def apply_to_player(self, player, game):
        """Apply this effect to the player."""
        return f"The {self.name} effect is applied to you."
    
    def __str__(self):
        return self.name


class SupervisionEffect(PlantEffect):
    """Effect that allows the player to see hidden items."""
    def __init__(self):
        super().__init__("Supervision", "Allows you to see hidden items")
        self.duration = 3  # Number of turns the effect lasts
    
    def apply_to_player(self, player, game):
        """Apply supervision effect to player, spawning hidden items in the area."""
        # Add the effect to player's active effects
        if not hasattr(player, 'active_effects'):
            player.active_effects = {}
        
        player.active_effects[self.name] = self.duration
        
        # Spawn hidden items in the current area
        hidden_items = [
            Item("Encrypted USB", "A USB stick with encrypted data.", 50),
            Item("Strange Crystal", "A crystal that glows with an otherworldly light.", 75),
            Item("Tech Fragment", "A piece of advanced technology.", 30)
        ]
        
        # Add 1-2 random hidden items to the area
        num_items = random.randint(1, 2)
        for _ in range(num_items):
            item = random.choice(hidden_items)
            player.current_area.add_item(item)
        
        return f"Your vision shifts and warps. Suddenly, you can see things that weren't visible before. The {self.name} effect will last for {self.duration} turns."


class HackedPlantEffect(PlantEffect):
    """Effect that makes plants come alive."""
    def __init__(self):
        super().__init__("Hacked Plant", "Plants may come alive and follow commands")
    
    def apply_to_player(self, player, game):
        """Apply hacked plant effect, allowing control of plants."""
        if not hasattr(player, 'active_effects'):
            player.active_effects = {}
        
        player.active_effects[self.name] = 5  # Lasts for 5 turns
        
        return "You feel a strange connection to the plants around you. They seem to respond to your thoughts."


class Substance:
    """Base class for substances that can be used on plants."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.effects = []
    
    def add_effect(self, effect):
        """Add an effect to this substance."""
        self.effects.append(effect)
    
    def __str__(self):
        return self.name


class HackedMilk(Substance):
    """A special substance that gives plants the supervision effect."""
    def __init__(self):
        super().__init__("Hacked Milk", "A strange, glowing milk-like substance that can alter plant growth.")
        self.add_effect(SupervisionEffect())


class Player:
    def __init__(self, name):
        self.name = name
        self.inventory = []
        self.health = 100
        self.max_health = 100
        self.money = 100
        self.current_area = None
        self.active_effects = {}  # Dictionary of effect name -> turns remaining
        self.detected_by = set()  # Set of gangs that have detected the player
    
    def add_item(self, item):
        self.inventory.append(item)
    
    def remove_item(self, item_name):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item:
            self.inventory.remove(item)
            return item
        return None
    
    def use_item(self, item_name, game):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            return False, f"You don't have a {item_name}."
        
        # Handle consumables
        if isinstance(item, Consumable):
            self.health = min(self.max_health, self.health + item.health_restore)
            self.inventory.remove(item)
            return True, f"You use the {item.name} and restore {item.health_restore} health."
        
        # Handle seeds (planting)
        if isinstance(item, Seed):
            # Check if there's soil in the current area
            soil = next((obj for obj in self.current_area.objects if hasattr(obj, 'add_plant')), None)
            if not soil:
                return False, "There's no soil here to plant seeds."
            
            # Plant the seed
            plant = Plant(
                f"{item.crop_type} plant", 
                f"A young {item.crop_type} plant.", 
                item.crop_type, 
                item.value * 2
            )
            
            result = soil.add_plant(plant)
            if result[0]:
                self.inventory.remove(item)
            return result
        
        # Handle other items
        return False, f"You can't use the {item.name} right now."
    
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


class Area:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.connections = {}  # Direction -> Area
        self.items = []
        self.npcs = []
        self.objects = []  # Interactive objects like soil plots, computers, etc.
        self.hazards = []  # Environmental hazards
    
    def add_connection(self, direction, area):
        self.connections[direction] = area
    
    def add_item(self, item):
        self.items.append(item)
    
    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
            return item
        return None
    
    def add_npc(self, npc):
        self.npcs.append(npc)
        npc.location = self
    
    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)
            npc.location = None
    
    def add_object(self, obj):
        self.objects.append(obj)
    
    def add_hazard(self, hazard):
        self.hazards.append(hazard)
        hazard.location = self
    
    def remove_hazard(self, hazard):
        if hazard in self.hazards:
            self.hazards.remove(hazard)
            hazard.location = None
    
    def get_full_description(self):
        """Get a full description of the area, including items, NPCs, and exits."""
        desc = self.description + "\n"
        
        # Add exits
        if self.connections:
            exits = ", ".join(self.connections.keys())
            desc += f"\nExits: {exits}\n"
        
        # Add items
        if self.items:
            item_names = ", ".join(str(item) for item in self.items)
            desc += f"\nItems: {item_names}\n"
        
        # Add NPCs
        if self.npcs:
            npc_names = ", ".join(npc.name for npc in self.npcs if npc.is_alive)
            if npc_names:
                desc += f"\nPeople: {npc_names}\n"
        
        # Add objects
        if self.objects:
            object_names = ", ".join(str(obj) for obj in self.objects)
            desc += f"\nObjects: {object_names}\n"
        
        return desc


class SoilPlot:
    def __init__(self, name="Soil Plot", description="A plot of soil for planting."):
        self.name = name
        self.description = description
        self.plants = []
        self.max_plants = 5
    
    def add_plant(self, plant):
        if len(self.plants) >= self.max_plants:
            return False, "This soil plot is full. You can't plant anything else here."
        
        self.plants.append(plant)
        return True, f"You plant the {plant.name} in the {self.name}."
    
    def remove_plant(self, plant_name):
        plant = next((p for p in self.plants if p.name.lower() == plant_name.lower()), None)
        if plant:
            self.plants.remove(plant)
            return plant
        return None
    
    def water_plants(self, substance=None):
        """Water all plants in the soil plot."""
        if not self.plants:
            return False, "There are no plants to water here."
        
        results = []
        for plant in self.plants:
            result = plant.water(substance)
            results.append(result[1])
        
        return True, "\n".join(results)
    
    def harvest_plant(self, plant_name):
        """Harvest a specific plant from the soil plot."""
        plant = next((p for p in self.plants if p.name.lower() == plant_name.lower()), None)
        if not plant:
            return False, f"There is no {plant_name} in this soil plot."
        
        if not plant.is_harvestable():
            return False, f"The {plant.name} is not ready to harvest yet."
        
        # Get the harvested item
        harvested_item = plant.get_harvested_item()
        
        # Remove the plant from the soil
        self.plants.remove(plant)
        
        return True, (f"You harvest the {plant.name} and get a {harvested_item.name}.", harvested_item)
    
    def __str__(self):
        if not self.plants:
            return f"{self.name} (empty)"
        
        plant_count = len(self.plants)
        return f"{self.name} ({plant_count}/{self.max_plants} plants)"


class Computer:
    def __init__(self, name="Computer", description="A computer terminal."):
        self.name = name
        self.description = description
        self.is_hacked = False
        self.programs = []
        self.data = []
        self.security_level = 1  # 1-5, with 5 being the most secure
    
    def hack(self, player):
        """Attempt to hack the computer."""
        # In a more complex implementation, this would check player skills
        if self.is_hacked:
            return False, "This computer is already hacked."
        
        # Simple hacking mechanic - 70% base chance of success, reduced by security level
        success_chance = 0.7 - (self.security_level * 0.1)
        if random.random() < success_chance:
            self.is_hacked = True
            return True, f"You successfully hack into the {self.name}!"
        else:
            return False, f"You fail to hack into the {self.name}. The security is too strong."
    
    def use(self, player):
        """Use the computer."""
        if not self.is_hacked:
            return False, f"You need to hack the {self.name} first."
        
        # Return a list of available programs
        if not self.programs:
            return True, "The computer is hacked, but there are no useful programs installed."
        
        program_list = "\n".join(f"- {program}" for program in self.programs)
        return True, f"Available programs:\n{program_list}"
    
    def run_program(self, program_name, player, game):
        """Run a specific program on the computer."""
        if not self.is_hacked:
            return False, f"You need to hack the {self.name} first."
        
        program = next((p for p in self.programs if p.lower() == program_name.lower()), None)
        if not program:
            return False, f"The program '{program_name}' is not installed on this computer."
        
        # Handle different programs
        if program == "data_miner":
            return True, "You run the data mining program and extract valuable information."
        elif program == "security_override":
            return True, "You override the security systems in the area."
        elif program == "plant_hacker":
            # Give the player the plant hacking effect
            effect = HackedPlantEffect()
            result = effect.apply_to_player(player, game)
            return True, result
        
        return True, f"You run the {program} program."
    
    def __str__(self):
        status = "hacked" if self.is_hacked else "locked"
        return f"{self.name} ({status})"


# ----------------------------- #
# NPC BEHAVIOR SYSTEM           #
# ----------------------------- #

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
            if isinstance(obj, SoilPlot) and obj.plants:
                return f"{npc.name} examines the plants in the {obj.name}."
            elif isinstance(obj, Computer):
                return f"{npc.name} looks at the {obj.name}."
                
        # Idle behavior
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
        
    def create_player(self, name):
        self.player = Player(name)
        
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
        
        # Create gangs
        self.gangs["Crimson Vipers"] = Gang("Crimson Vipers")
        self.gangs["Bloodhounds"] = Gang("Bloodhounds")

        # add gang members to areas
        self.areas["warehouse"].add_npc(GangMember("Viper", "A member of the Crimson Vipers.", self.gangs["Crimson Vipers"]))
        


        bloodhounds_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]
        

        # add 5 NPCs from the bloodhounds_name list to the warehouse

        for i in range(5):
            name = random.choice(bloodhounds_names)
            bloodhounds_names.remove(name)
            self.areas["warehouse"].add_npc(GangMember(name, f"A member of the Bloodhounds named {name}.", self.gangs["Bloodhounds"]))

        
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
    
    def run(self):
        """Run the main game loop."""
        print("Welcome to Root Access!")
        player_name = input("Enter your name: ")
        self.create_player(player_name)
        self.create_world()
        
        print(f"\nWelcome, {self.player.name}!")
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
