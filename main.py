# testing if version control is established

import random
from message_system import MessageManager, MessageCategory, MessagePriority


from message_system import MessageManager, MessageCategory, MessagePriority
from npc_behavior import NPCMessageManager
from message_coordinator import MessageCoordinator
from hazard_utils import Hazard
from npc_behavior_coordinator import NPCBehaviorCoordinator








        # --------------------------- #
        # NEW MESSAGE + ACTION SYSTEM #
        # --------------------------- #






def integrate_message_systems(game):
    """
    Integrate the message systems for the game.
    """
    # Step 1: Initialize the main message manager
    if not hasattr(game, 'message_manager'):
        game.message_manager = MessageManager(game)
    
    # Step 2: Initialize the NPC message manager
    npc_message_manager = NPCMessageManager()
    
    # Step 3: Create the message coordinator to connect all systems
    message_coordinator = MessageCoordinator(
        game=game,
        message_manager=game.message_manager,
        npc_message_manager=npc_message_manager
    )
    
    # Step 4: Store the coordinator in the game instance for easy access
    game.message_coordinator = message_coordinator
    
    # Step 5: Apply the direct gardening fix to ensure gardening messages are displayed
    try:
        from direct_gardening_fix import apply_direct_gardening_fix
        apply_direct_gardening_fix(game)
    except Exception as e:
        print(f"Warning: Could not apply gardening fix: {e}")
    
    return message_coordinator


def update_game_turn(game):
    """
    Update the game for a new turn, including message system reset.
    
    Args:
        game: The main game instance
    """
    # Reset message systems for the new turn
    if hasattr(game, 'message_coordinator'):
        game.message_coordinator.new_turn()
    
    # Continue with other turn update logic...

def process_npc_messages(game, npcs):
    """
    Process messages from NPCs using the improved system.
    
    Args:
        game: The main game instance
        npcs: List of NPC objects in the current area
    """
    if not hasattr(game, 'message_coordinator'):
        return
    
    # Process messages from each NPC
    for npc in npcs:
        # Update NPC behavior
        if hasattr(npc, 'behavior_manager'):
            result = npc.behavior_manager.update(game)
            
            # If the behavior produced a message, process it
            if result:
                game.message_coordinator.process_npc_message(result, npc=npc)

def display_npc_summary(game):
    """
    Display the NPC action summary at the end of the turn in a more natural language format.
    
    Args:
        game: The main game instance
    """
    if not hasattr(game, 'message_coordinator'):
        return
    
    # Get the NPC summary
    summary = game.message_coordinator.get_npc_summary()
    if summary:
        # Store the detailed summary for debug mode
        game.debug_npc_summary = summary
        
        # Get active gangs for context
        active_gangs = getattr(game.message_coordinator, 'active_gangs', set())
        
        # Convert the bulleted summary into a natural language paragraph
        natural_summary = convert_to_natural_language(summary, active_gangs)
        
        # Add the natural summary to the message manager with HIGH priority
        game.message_manager.add_message(
            text=natural_summary,
            category=MessageCategory.NPC_SUMMARY,
            priority=MessagePriority.HIGH
        )
        
        # Print the summary directly to ensure it's visible
        print("\n" + natural_summary + "\n")

def convert_to_natural_language(summary, active_gangs):
    """
    Convert the bulleted NPC summary into a more natural paragraph format.
    
    Args:
        summary: The original NPC summary with line breaks
        active_gangs: Set of active gang names for context
    
    Returns:
        A natural language paragraph describing NPC activities
    """
    # Split the summary into individual lines
    lines = summary.strip().split('\n')
    
    # Remove any header lines (those ending with a colon)
    action_lines = [line for line in lines if not line.endswith(':') and line.strip()]
    
    # If we have no action lines, return early
    if not action_lines:
        if active_gangs and len(active_gangs) == 1:
            gang_name = next(iter(active_gangs))
            return f"The {gang_name} members are quiet for now."
        else:
            return "The area is quiet for now."
    
    # Group similar actions together
    hallucination_lines = []
    friendly_lines = []
    combat_lines = []
    gardening_lines = []
    environment_lines = []  # New category for environment changes
    item_use_lines = []     # New category for item usage
    interaction_lines = []
    talking_lines = []
    reaction_lines = []     # New category for NPC reactions
    group_action_lines = [] # New category for coordinated NPC actions
    other_lines = []
    
    for line in action_lines:
        line = line.strip()
        if "hallucinating" in line.lower() or "seeing things" in line.lower():
            hallucination_lines.append(line)
        elif "friendly" in line.lower() or "smiles" in line.lower():
            friendly_lines.append(line)
        elif "attack" in line.lower() or "damage" in line.lower() or "fight" in line.lower():
            combat_lines.append(line)
        # Enhanced gardening detection with more keywords
        elif any(word in line.lower() for word in ["plant", "water", "harvest", "garden", "seed", "crop", "fertilize", "grow"]):
            gardening_lines.append(line)
        # New environment change detection
        elif any(word in line.lower() for word in ["changed", "transformed", "grew", "withered", "bloomed", "sprouted"]):
            environment_lines.append(line)
        # Enhanced item usage detection
        elif any(word in line.lower() for word in ["use", "using", "activate", "operate", "pick up", "drop"]):
            item_use_lines.append(line)
        # Original interaction detection
        elif "interact" in line.lower() or "gives" in line.lower():
            interaction_lines.append(line)
        elif "talk" in line.lower() or "chat" in line.lower() or "conversation" in line.lower() or "says" in line.lower():
            talking_lines.append(line)
        # New reaction detection
        elif any(word in line.lower() for word in ["react", "respond", "notice", "surprised", "shocked", "impressed"]):
            reaction_lines.append(line)
        # New group action detection
        elif any(word in line.lower() for word in ["together", "group", "gang", "collectively", "coordinate", "team up"]):
            group_action_lines.append(line)
        else:
            other_lines.append(line)
    
    # Build the natural language paragraph
    paragraph_parts = []
    
    # Start with combat actions as they're most important
    if combat_lines:
        paragraph_parts.extend(combat_lines)
    
    # Add connecting phrases between different action types
    connectors = ["Meanwhile, ", "At the same time, ", "Nearby, ", "Elsewhere, ", "Also, "]
    
    # Add hallucination actions
    if hallucination_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + hallucination_lines[0].lower())
            hallucination_lines = hallucination_lines[1:]
        
        # If we have multiple hallucination lines, combine them
        if len(hallucination_lines) > 1:
            # Extract NPC names from the lines
            npc_names = []
            for line in hallucination_lines:
                parts = line.split()
                if "member" in line and parts.index("member") + 1 < len(parts):
                    npc_names.append(parts[parts.index("member") + 1])
            
            if npc_names:
                if len(npc_names) <= 4:
                    npc_list = ", ".join(npc_names)
                else:
                    npc_list = f"{', '.join(npc_names[:4])} and {len(npc_names) - 4} others"
                
                paragraph_parts.append(f"while {npc_list} are seeing the walls melting.")
    
    # Add gardening actions (high priority for game focus)
    if gardening_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + gardening_lines[0].lower())
            gardening_lines = gardening_lines[1:]
        # If we have multiple gardening lines, try to include more of them
        if gardening_lines and random.random() < 0.7:  # 70% chance to include another gardening line
            paragraph_parts.append(random.choice(connectors) + gardening_lines[0].lower())
            gardening_lines = gardening_lines[1:]
    
    # Add environment change actions (high priority for game state)
    if environment_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + environment_lines[0].lower())
            environment_lines = environment_lines[1:]
    
    # Add item use actions
    if item_use_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + item_use_lines[0].lower())
            item_use_lines = item_use_lines[1:]
    
    # Add interaction actions
    if interaction_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + interaction_lines[0].lower())
            interaction_lines = interaction_lines[1:]
    
    # Add talking actions
    if talking_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + talking_lines[0].lower())
            talking_lines = talking_lines[1:]
    
    # Add reaction actions
    if reaction_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + reaction_lines[0].lower())
            reaction_lines = reaction_lines[1:]
    
    # Add group action lines
    if group_action_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + group_action_lines[0].lower())
            group_action_lines = group_action_lines[1:]
    
    # Add friendly actions
    if friendly_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + friendly_lines[0].lower())
            friendly_lines = friendly_lines[1:]
    
    # Add other actions
    if other_lines:
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + other_lines[0].lower())
            other_lines = other_lines[1:]
    
    # Combine all remaining lines of each type
    remaining_lines = (hallucination_lines + gardening_lines + environment_lines + 
                      item_use_lines + interaction_lines + talking_lines + 
                      reaction_lines + group_action_lines + friendly_lines + other_lines)
    
    # Add a few more remaining lines with connectors if we have space
    for i, line in enumerate(remaining_lines[:3]):  # Limit to 3 more lines
        if paragraph_parts:
            paragraph_parts.append(random.choice(connectors) + line.lower())
    
    # Join everything into a single paragraph
    if active_gangs and len(active_gangs) == 1:
        gang_name = next(iter(active_gangs))
        intro = f"The {gang_name} are active in the area. "
    elif active_gangs and len(active_gangs) > 1:
        gang_names = ", ".join(active_gangs)
        intro = f"Multiple gangs ({gang_names}) are active in the area. "
    else:
        intro = "NPCs are active in the area. "
    
    # Join all parts with proper spacing and capitalization
    result = intro
    
    for i, part in enumerate(paragraph_parts):
        if i == 0:
            # Capitalize the first sentence
            result += part[0].upper() + part[1:]
        else:
            # Keep the rest as is (connectors are already capitalized)
            result += part
        
        # Add period if needed
        if not result.endswith('.') and not result.endswith('!'):
            result += '.'
        
        # Add space between sentences
        if i < len(paragraph_parts) - 1:
            result += ' '
    
    return result

def add_message(game, text, category=None, priority=None, source=None, is_npc_message=False):
    """
    Helper function to add messages using the coordinator when available.
    
    Args:
        game: The main game instance
        text: The message text
        category: Message category
        priority: Message priority
        source: Message source (usually an NPC)
        is_npc_message: Whether this is an NPC-generated message
        
    Returns:
        The result from the message system
    """
    # Use the coordinator if available
    if hasattr(game, 'message_coordinator'):
        if is_npc_message:
            return game.message_coordinator.process_npc_message(text, npc=source)
        else:
            return game.message_coordinator.process_player_message(text, priority=priority)
    
    # Fall back to direct message manager if coordinator not available
    return game.message_manager.add_message(
        text=text,
        category=category,
        priority=priority,
        source=source
    )

        # --------------------------- #
        # NEW MESSAGE + ACTION SYSTEM #
        # --------------------------- #



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
        import random
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


class WateringCan(Item):
    """A watering can that can be filled with different substances."""
    def __init__(self, name="Watering Can", description="A metal watering can for watering plants.", value=5):
        super().__init__(name, description, value)
        self.substance = None  # Default is empty/water
    
    def fill_with(self, substance):
        """Fill the watering can with a substance."""
        self.substance = substance
        return f"You fill the {self.name} with {substance.name}."
    
    def empty(self):
        """Empty the watering can."""
        if self.substance:
            substance_name = self.substance.name
            self.substance = None
            return f"You empty the {substance_name} from the {self.name}."
        return f"The {self.name} is already empty."
    
    def __str__(self):
        if self.substance:
            return f"{self.name} (filled with {self.substance.name})"
        return f"{self.name} (empty)"






            # --------------------------- #
            #    Tech class and apps      #
            # --------------------------- #

class Tech:
    """Base class for all technology items in the game."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    def use(self):
        """Default use method for tech items."""
        return f"You use the {self.name}."


class App:
    """Base class for smartphone applications."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.options = {}
        
    def run(self):
        """Run the app and return its menu."""
        return f"{self.name} - {self.description}\nOptions: {', '.join(self.options.keys())}"
        
    def execute_option(self, option, game, player):
        """Execute a specific option within the app."""
        if option in self.options:
            return self.options[option](game, player)
        return f"Invalid option: {option}"


class GardenApp(App):
    """Garden management application for smartphones."""
    def __init__(self):
        super().__init__("Garden Manager", "Manage and enhance your garden")
        self.options = {
            "status": self.garden_status,
            "instagrow": self.instagrow,
            "hack": self.hack_plant,
            "help": self.help
        }
        
    def garden_status(self, game, player):
        """Show status of all plants in the current area."""
        area = player.current_area
        plants_found = False
        status = "Garden Status:\n"
        
        for obj in area.objects:
            if isinstance(obj, Soil) and obj.plants:
                plants_found = True
                status += f"\n{obj.name}:\n"
                for plant in obj.plants:
                    growth_percent = (plant.growth_stage / plant.max_growth) * 100
                    status += f"  - {plant.name}: {growth_percent:.0f}% grown"
                    if plant.is_harvestable():
                        status += " (Ready to harvest!)"
                    status += "\n"
        
        if not plants_found:
            return "No plants found in this area."
        return status
        
    def instagrow(self, game, player):
        """Instantly grow all plants in the current area to maximum growth."""
        area = player.current_area
        plants_grown = 0
        
        for obj in area.objects:
            if isinstance(obj, Soil):
                for plant in obj.plants:
                    if not plant.is_harvestable():
                        plant.growth_stage = plant.max_growth
                        plants_grown += 1
        
        if plants_grown > 0:
            return f"HACK SUCCESSFUL: {plants_grown} plants have instantly grown to full maturity!"
        else:
            return "No plants found that needed growing."
            
    def hack_plant(self, game, player):
        """Apply a hacking effect to plants in the current area."""
        area = player.current_area
        plants_found = False
        plants_hacked = 0
        
        # Create a hacked plant effect
        hacked_effect = HackedPlantEffect()
        
        for obj in area.objects:
            if isinstance(obj, Soil) and obj.plants:
                plants_found = True
                for plant in obj.plants:
                    success, _ = plant.add_effect(hacked_effect)
                    if success:
                        plants_hacked += 1
        
        if not plants_found:
            return "No plants found in this area to hack."
        elif plants_hacked > 0:
            return f"HACK SUCCESSFUL: Applied {hacked_effect.name} effect to {plants_hacked} plants!"
        else:
            return "All plants in this area are already hacked."
    
    def help(self, game, player):
        """Show help for the garden app."""
        help_text = "Garden Manager App Help:\n"
        help_text += "  - status: View the status of all plants in your current area\n"
        help_text += "  - instagrow: Instantly grow all plants to full maturity\n"
        help_text += "  - hack: Apply hacking effects to plants in your current area\n"
        help_text += "  - help: Show this help message"
        return help_text


class Smartphone(Tech, Item):
    """A smartphone that can run various apps."""
    def __init__(self, name="Smartphone", description="A high-tech smartphone with various apps", value=50):
        Tech.__init__(self, name, description)
        Item.__init__(self, name, description, value)
        self.apps = {}
        self.current_app = None
        
        # Install default apps
        self.install_app(GardenApp())
        
    def install_app(self, app):
        """Install a new app on the smartphone."""
        self.apps[app.name.lower()] = app
        
    def use(self):
        """Use the smartphone, showing the main menu."""
        if not self.apps:
            return "Your smartphone has no apps installed."
        
        menu = "Smartphone Menu\nAvailable apps:\n"
        for app_key, app in self.apps.items():
            menu += f"  - {app.name}: {app.description}\n"
        menu += "\nUse 'use phone [app_name]' to open an app. For example: 'use phone garden'"
        return menu
        
    def open_app(self, app_name):
        """Open a specific app on the smartphone."""
        app_key = app_name.lower()
        
        # Exact match
        if app_key in self.apps:
            self.current_app = self.apps[app_key]
            return self.current_app.run()
        
        # Partial match (e.g., "garden" matches "garden manager")
        for key, app in self.apps.items():
            if app_key in key:
                self.current_app = app
                return self.current_app.run()
        
        return f"App not found: {app_name}"
        
    def execute_app_option(self, option, game, player):
        """Execute an option in the currently open app."""
        if not self.current_app:
            return "No app is currently open."
        return self.current_app.execute_option(option, game, player)
        
    def __str__(self):
        return f"{self.name}"


            # --------------------------- #
            # Object class and subclasses #
            # --------------------------- #

class Object():
        def __init__(self, name, description, portable=True, value=0):
            self.name = name
            self.description = description
            self.portable = portable
            self.value = value
            
        def __str__(self):
            return self.name
            
class Storage(Object):
    def __init__(self, name, description, capacity=10, portable=True, value=0):
        super().__init__(name, description, portable, value)
        self.items = []
        self.capacity = capacity  # Maximum number of items this storage can hold
        self.is_open = False  # Storage starts closed
        
    def open(self):
        # Open the storage to access items.
        if self.is_open:
            return False, f"The {self.name} is already open."
        self.is_open = True
        return True, f"You open the {self.name}."
        
    def close(self):
        # Close the storage.
        if not self.is_open:
            return False, f"The {self.name} is already closed."
        self.is_open = False
        return True, f"You close the {self.name}."
        
    def add_item(self, item):
        # Add an item to the storage.
        if len(self.items) >= self.capacity:
            return False, f"The {self.name} is full and cannot hold any more items."
        
        self.items.append(item)
        return True, f"You put {item.name} in the {self.name}."
        
    def remove_item(self, item_name):
        # Remove an item from the storage by name.
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return True, item
        return False, None
        
    def list_items(self):
        # List all items in the storage.
        if not self.items:
            return f"The {self.name} is empty."
        
        items_list = [f" - {item}" for item in self.items]
        return f"Items in the {self.name}:\n" + "\n".join(items_list)
        
    def __str__(self):
        status = "open" if self.is_open else "closed"
        return f"{self.name} ({status})"


class Soil(Object):
    def __init__(self, name, description, capacity=5):
        super().__init__(name, description, portable=False)
        self.plants = []
        self.capacity = capacity  # Maximum number of plants this soil can hold
    
    def add_plant(self, seed):
        """Convert a seed into a plant and add it to the soil."""
        if len(self.plants) >= self.capacity:
            return False, "This soil is already at full capacity."
        
        # Create a new plant from the seed
        plant_name = f"{seed.crop_type.capitalize()} Plant"
        plant_desc = f"A young {seed.crop_type} plant growing in the soil."
        new_plant = Plant(plant_name, plant_desc, seed.crop_type, seed.value * 2, 0, seed.growth_time)
        
        self.plants.append(new_plant)
        return True, f"You planted a {seed.crop_type} seed. Water it to help it grow!"
    
    def water_plants(self, plant_name=None, substance=None):
        """Water all plants or a specific plant in the soil, optionally with a special substance."""
        if not self.plants:
            return False, "There are no plants in this soil to water."
        
        if plant_name:
            # Water a specific plant
            plant = self.get_plant(plant_name)
            if not plant:
                return False, f"There is no plant called '{plant_name}' in this soil."
            
            success, message = plant.water(substance)
            return success, message
        else:
            # Water all plants
            results = []
            for plant in self.plants:
                success, message = plant.water(substance)
                if success:
                    results.append(message)
            
            if results:
                return True, "\n".join(results)
            else:
                return False, "All plants are already fully grown."
    
    def get_plant(self, plant_name):
        """Find a plant by name."""
        for plant in self.plants:
            if plant.name.lower() == plant_name.lower():
                return plant
        return None
    
    def remove_plant(self, plant):
        """Remove a plant from the soil."""
        if plant in self.plants:
            self.plants.remove(plant)
            return True
        return False
    
    def __str__(self):
        base_str = f"{self.name}"
        if self.plants:
            base_str += f" with {len(self.plants)} plants growing"

            return base_str
        
from npc_behavior import NPC, Gang, GangMember, NPCMessageManager



class Area:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.npcs = []
        self.objects = []
        self.exits = {}  # Dictionary to hold exits: direction -> Area

    def add_exit(self, direction, area):
        """Add an exit to another area in a given direction."""
        self.exits[direction] = area

    def get_exit(self, direction):
        """Get the area in the given direction."""
        return self.exits.get(direction, None)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def add_object(self, object):
        self.objects.append(object)

    def remove_object(self, obj):
        if obj in self.objects: # using the word item in place of object because the word "object" is a keyword
            self.objects.remove(obj)
            return True
        return False
    

    def add_npc(self, npc):
        self.npcs.append(npc)
        npc.location = self

    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)

    def describe(self, game=None):
        """Describe the area, including items, NPCs, and objects.
        
        If game is provided, uses the message system to filter NPC descriptions.
        """
        desc = f"{self.name}\n{self.description}\n"
        
        # Items
        if self.items:
            desc += "You see the following items:\n"
            for item in self.items:
                desc += f" - {item.name}\n"
        
        # NPCs
        if self.npcs:
            desc += "You see the following people:\n"
            
            # If game is provided, use message system to filter NPC descriptions
            if game and hasattr(game, 'message_manager'):
                # Get NPC display settings
                show_npc, throttle_rate = game.message_manager.display_settings[MessageCategory.NPC_MINOR]
                
                # Show all NPCs but with minimal descriptions for minor NPCs
                for npc in self.npcs:
                    # Always show the NPC name
                    npc_desc = f" - {npc.name}"
                    
                    # Add status info for important NPCs or based on settings
                    if hasattr(npc, 'is_alive') and not npc.is_alive:
                        npc_desc += " (dead)"
                    
                    # Add activity description only if settings allow
                    if show_npc and random.random() > throttle_rate:
                        if hasattr(npc, 'current_activity') and npc.current_activity:
                            npc_desc += f" - {npc.current_activity}"
                    
                    desc += npc_desc + "\n"
            else:
                # Without message system, show all NPCs with basic info
                for npc in self.npcs:
                    npc_desc = f" - {npc.name}"
                    if hasattr(npc, 'is_alive') and not npc.is_alive:
                        npc_desc += " (dead)"
                    desc += npc_desc + "\n"
        
        # Objects
        if self.objects:
            desc += "There are some objects here:\n"
            for obj in self.objects:
                desc += f" - {obj.name}\n"
                
                # If it's soil, show the plants
                if isinstance(obj, Soil) and obj.plants:
                    desc += "   Plants in this soil:\n"
                    for plant in obj.plants:
                        desc += f"   * {plant}\n"
                
                # If it's an open storage, show the items inside
                elif isinstance(obj, Storage) and obj.is_open and obj.items:
                    desc += "   Items in this storage:\n"
                    for item in obj.items:
                        desc += f"   * {item}\n"
                        
                # If it's a hazard, only show details based on settings
                elif isinstance(obj, StaticHazard) and game and hasattr(game, 'message_manager'):
                    show_hazard, throttle_rate = game.message_manager.display_settings[MessageCategory.HAZARD_EFFECT]
                    if show_hazard and random.random() > throttle_rate:
                        if hasattr(obj, 'description') and obj.description:
                            desc += f"   * {obj.description}\n"
        
        # Add exits
        if self.exits:
            desc += "Exits:\n"
            for direction, area in self.exits.items():
                desc += f" - {direction}: {area.name}\n"
                
        return desc


class Player:
    def __init__(self, starting_area, starting_items=None):
        self.current_area = starting_area
        self.inventory = starting_items or []
        self.health = 100
        self.active_effects = {}  # Dictionary of effect_name -> turns_remaining
        self.hidden = False  # Add hidden attribute for detection logic
        self.detected_by = set()  # Track gangs that detected the player
        

    def move(self, direction):
        """Move the player to the area in the given direction if possible."""
        next_area = self.current_area.get_exit(direction)
        if (next_area):
            self.current_area = next_area
            return f"You move {direction} to {self.current_area.name}."
        else:
            return "You can't go that way."

    def teleport(self, area):
        """Teleport the player to any area."""
        self.current_area = area
        return f"You teleport to {self.current_area.name}."

    def pick_up(self, item):
        if item in self.current_area.items:
            self.inventory.append(item)
            self.current_area.remove_item(item)
            return f"You picked up {item}."
        else:
            return "That item is not here."

    def drop(self, item):
        if item in self.inventory:
            self.inventory.remove(item)
            self.current_area.add_item(item)
            return f"You dropped {item}."
        else:
            return "You don't have that item."
            
    def consume(self, item, game):
        """Consume an item, applying any effects it might have."""
        if item not in self.inventory:
            return f"You don't have {item.name} in your inventory."
        
        # Remove the item from inventory
        self.inventory.remove(item)
        
        # Basic consumption message
        message = f"You consume the {item.name}."
        
        # Apply any effects the item might have
        if hasattr(item, 'effects') and item.effects:
            effect_messages = []
            for effect in item.effects:
                effect_message = effect.apply_to_player(self, game)
                effect_messages.append(effect_message)
            
            if effect_messages:
                message += "\n" + "\n".join(effect_messages)
        
        return message
    
    def update_effects(self):
        """Update active effects, reducing their duration by 1 turn."""
        expired_effects = []
        
        for effect_name, turns_remaining in self.active_effects.items():
            if turns_remaining <= 1:
                expired_effects.append(effect_name)
            else:
                self.active_effects[effect_name] = turns_remaining - 1
        
        # Remove expired effects
        for effect_name in expired_effects:
            del self.active_effects[effect_name]
            
        return expired_effects

    def attack(self, target_name, game):
        """Attack a gang member in the current area by name."""
        # Find gang member in current area
        target = None
        for npc in self.current_area.npcs:
            if npc.name.lower() == target_name.lower() and isinstance(npc, GangMember):
                target = npc
                break
        if not target:
            return f"No gang member named '{target_name}' here to attack."

        # Find weapon in inventory
        weapon = None
        for item in self.inventory:
            if isinstance(item, Weapon):
                weapon = item
                break
        if not weapon:
            return "You have no weapon to attack with."

        # Calculate damage and apply to target
        damage = weapon.damage
        target.health -= damage
        
        # Create descriptive attack message
        attack_descriptions = [
            f"You swing your {weapon.name} at {target.name}, landing a solid hit",
            f"You strike {target.name} with your {weapon.name}, connecting with force",
            f"Your {weapon.name} finds its mark as you attack {target.name}",
            f"You lunge forward, hitting {target.name} with your {weapon.name}",
            f"With practiced precision, you attack {target.name} using your {weapon.name}"
        ]
        
        # Weapon-specific descriptions
        if weapon.name == "Knife":
            knife_descriptions = [
                f"You slash at {target.name} with your knife, drawing blood",
                f"Your blade cuts through the air and into {target.name}",
                f"You thrust your knife forward, stabbing {target.name}",
                f"With a quick motion, you slice at {target.name} with your knife"
            ]
            # 50% chance to use weapon-specific description
            if random.random() < 0.5:
                attack_descriptions = knife_descriptions
        elif weapon.name == "Gun":
            gun_descriptions = [
                f"You pull the trigger, sending a round into {target.name}",
                f"Your gun barks as you fire at {target.name}",
                f"You take aim and shoot {target.name}",
                f"With steady hands, you fire your gun at {target.name}"
            ]
            # 50% chance to use weapon-specific description
            if random.random() < 0.5:
                attack_descriptions = gun_descriptions
        
        # Select a random attack description
        attack_desc = random.choice(attack_descriptions)
        
        if target.health <= 0:
            # Remove target from gang and area
            target.die()
            self.current_area.remove_npc(target)
            
            # Create descriptive defeat message
            defeat_descriptions = [
                f"{attack_desc}. {target.name} collapses to the ground, defeated!",
                f"{attack_desc}. That was the final blow - {target.name} is down!",
                f"{attack_desc}, finishing {target.name} off with a decisive strike!",
                f"{attack_desc}. {target.name} staggers and falls, no longer a threat.",
                f"{attack_desc}. Your attack proves too much for {target.name}, who crumples to the floor."
            ]
            
            return random.choice(defeat_descriptions)
        else:
            # Create descriptive damage message
            if target.health > 75:
                status_desc = f"{target.name} is barely injured and still fighting strong."
            elif target.health > 50:
                status_desc = f"{target.name} is wounded but still dangerous."
            elif target.health > 25:
                status_desc = f"{target.name} is seriously hurt and slowing down."
            else:
                status_desc = f"{target.name} is critically wounded and barely standing."
                
            return f"{attack_desc}. {status_desc}"

    def check_death_and_respawn(self, game):
        """Check if player is dead and respawn at home if so."""
        if self.health <= 0:
            # Import respawn descriptions
            from combat_descriptions import get_respawn_description
            
            home_area = game.areas.get('Home')
            if home_area:
                self.current_area = home_area
                self.health = 100
                self.active_effects.clear()
                self.hidden = False
                self.detected_by.clear()
                
                # Get a descriptive respawn message
                return f"{get_respawn_description()} You've been restored to full health."
            else:
                return "You have died and there is no Home area to respawn."
        return None





import random

from npc_behavior import NPC_REACTIONS

class Hazard:
    def __init__(self, name, description, effect, damage, duration=None):
        self.name = name
        self.description = description
        self.effect = effect
        self.damage = damage
        self.active = True
        self.duration = duration  # None means permanent, number is turns remaining
        self.remaining_turns = duration

    def update(self):
        """Decrement duration and deactivate if expired"""
        if self.duration is not None:
            self.remaining_turns -= 1
            if self.remaining_turns <= 0:
                self.active = False
        return self.active

    def group_results(self, results):
        """Group hazard results by effect status with proper grammar and interesting details"""
        from npc_behavior import group_hazard_results
        return group_hazard_results(self, results)


class StaticHazard(Hazard):
    def __init__(self, name, description, effect):
        super().__init__(name, description, effect, damage=40, duration=2)  # duration was None permanent static hazards, testing with 2 turns



    def affect_area(self, area):
        """Apply hazard to all gang members in area with grouped results"""
        results = []
        
        # Get a list of eligible NPCs (gang members)
        eligible_npcs = [npc for npc in area.npcs if isinstance(npc, GangMember)]
        
        # If we have a lot of NPCs, only affect a random subset
        # This prevents the same NPCs from being affected by multiple hazards
        if len(eligible_npcs) > 3:
            # Affect between 1 and 3 NPCs, or up to 1/3 of the total NPCs
            max_affected = min(3, len(eligible_npcs) // 3 + 1)
            eligible_npcs = random.sample(eligible_npcs, max_affected)
        
        # Apply hazard effect to selected NPCs
        for npc in eligible_npcs:
            result = npc.apply_hazard_effect(self)
            npc.update_effects()
            results.append(result)
                
        return self.group_results(results)
    
    def get_affected_verb(self, count):
        """Get appropriate verb for affected members"""
        verbs = {
            "Glitter Bomb": "gets glitter bombed",
            "Pink Mist": "breathes in pink mist",
            "Hacked Milk": "steps in hacked milk"
        }
        return verbs.get(self.name, "is affected by")




class HazardItem(Hazard):
    def __init__(self, name, description, effect):
        super().__init__(name, description, effect, damage=0)  # Hazard items may not cause damage
        self.type = 'hazard'  # Add type attribute for easier identification
    
    def use(self, player):
        """Use hazard item on a subset of gang members with grouped results"""
        
        results = []
        
        # Get a list of eligible NPCs (gang members)
        eligible_npcs = [npc for npc in player.current_area.npcs if isinstance(npc, GangMember)]
        
        # If we have a lot of NPCs, only affect a random subset
        # This prevents the same NPCs from being affected by multiple hazards
        if len(eligible_npcs) > 3:
            # Affect between 1 and 3 NPCs, or up to 1/3 of the total NPCs
            max_affected = min(3, len(eligible_npcs) // 3 + 1)
            eligible_npcs = random.sample(eligible_npcs, max_affected)
        
        # Apply hazard effect to selected NPCs
        for npc in eligible_npcs:
            result = npc.apply_hazard_effect(self)
            npc.update_effects()
            results.append(result)
                
        return self.group_results(results)
        
    def activate(self):
        """Activate the hazard item - this method is called when an NPC triggers the item"""
        # This method exists to be called by NPCs when they trigger the hazard
        # The actual effect is applied through apply_hazard_effect
        # We could add additional effects here if needed
        return True

    def get_affected_verb(self, count):
        """Get appropriate verb for affected members"""
        verbs = {
            "Glitter Bomb": "gets glitter bombed",
            "Pink Mist": "breathes in pink mist",
            "Hacked Milk": "steps in hacked milk"
        }
        return verbs.get(self.name, "is affected by")


# create a subclass of Hazard, for objects that fall
class FallingObject(Hazard):
    def __init__(self, name, description, effect, items):
        super().__init__(name, description, effect, damage=0)  # Hazard items may
        self.fall_distance = 3  # distance the object falls before landing - player turns before it's on the ground
        self.fall_damage = 10  
        self.fall_effect = effect  # effect the object has when it lands
        self.items = items # goods found inside object when it lands


        possible_effects = ["explodes", "crashes into ground", "hovers above ground", "reveals area"] # "reveals area" means the impact from falling damages the ground and exposes something underground



    def deactivate(self): # still present but no effect
        """make object no longer have effect"""
        self.active = False
        self.effect = None
        

    def open(self):
        
        return ", ".join(item.name for item in self.items) if self.items else "nothing"
    
    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
        return item
    
    def empty(self, player):
        """Transfer all items from this FallingObject to the current area"""
        for item in self.items:
            player.current_area.add_item(item)
        self.items.clear()

    def remove_hazard(self, player):
        """Remove this hazard from the area"""
        player.current_area.remove_object(self)


    

    def affect_area(self, area):
        """Apply hazard to all gang members in area with grouped results"""
        results = []
        for npc in area.npcs:
            if isinstance(npc, GangMember):
                result = npc.apply_hazard_effect(self)
                npc.update_effects()
                results.append(result)

                

        return self.group_results(results)
    


    

class Game:
    def __init__(self):
        self.areas = {}
        self.items = {}  # Centralized item registry
        self.objects = {}  # Centralized object registry
        self.npcs = {}  # Centralized NPC registry

        self.NPC_REACTIONS = NPC_REACTIONS
        self.npc_message_manager = NPCMessageManager()  # For summarizing NPC messages
        self.message_manager = None  # Will be initialized after player is created
        self.message_coordinator = None  # Will be initialized after message_manager
        self.npc_behavior_coordinator = NPCBehaviorCoordinator(
            max_npc_actions_per_turn=5,  # Limit total NPC actions per turn
            max_actions_per_npc=1       # Limit actions per NPC per turn
        )

        self.player_starting_items = []  # Initialize this before create_items
        
        self.create_items()
        self.create_areas()
        self.create_objects()
        self.create_npcs()

        

        self.player = Player(self.areas.get('Home'), self.player_starting_items)
        
        # Initialize the message manager after player is created
        self.message_manager = MessageManager(self)
        
        # Initialize the message coordinator to connect all message systems
        self.message_coordinator = MessageCoordinator(
            game=self,
            message_manager=self.message_manager,
            npc_message_manager=self.npc_message_manager
        )
        self.commands = {
            'move': {'handler': self.cmd_move, 'category': 'movement'},
            'go': {'handler': self.cmd_move, 'category': 'movement'},
            'teleport': {'handler': self.cmd_teleport, 'category': 'movement'},
            'tp': {'handler': self.cmd_teleport, 'category': 'movement'},
            'look': {'handler': self.cmd_look, 'category': 'system'},
            'inventory': {'handler': self.cmd_inventory, 'category': 'system'},
            'inv': {'handler': self.cmd_inventory, 'category': 'system'},
            'pickup': {'handler': self.cmd_pick_up, 'category': 'interaction'},
            'take': {'handler': self.cmd_pick_up, 'category': 'interaction'},
            'drop': {'handler': self.cmd_drop, 'category': 'interaction'},
            'quit': {'handler': self.cmd_quit, 'category': 'system'},
            'exit': {'handler': self.cmd_exit, 'category': 'system'},
            'help': {'handler': self.cmd_help, 'category': 'system'},
            'plant': {'handler': self.cmd_plant, 'category': 'interaction'},
            'harvest': {'handler': self.cmd_harvest, 'category': 'interaction'},
            'water': {'handler': self.cmd_water, 'category': 'interaction'},
            # New storage-related commands
            'open': {'handler': self.cmd_open, 'category': 'interaction'},
            'close': {'handler': self.cmd_close, 'category': 'interaction'},
            'put': {'handler': self.cmd_put_in, 'category': 'interaction'},
            'look in': {'handler': self.cmd_look_in, 'category': 'interaction'},
            # Smartphone commands
            'use': {'handler': self.cmd_use, 'category': 'tech'},
            'app': {'handler': self.cmd_app, 'category': 'tech'},
            # Consumption commands
            'eat': {'handler': self.cmd_eat, 'category': 'interaction'},
            'consume': {'handler': self.cmd_eat, 'category': 'interaction'},
            # Watering can commands
            'fill': {'handler': self.cmd_fill, 'category': 'interaction'},
            'empty': {'handler': self.cmd_empty, 'category': 'interaction'},
            # Combat commands
            'attack': {'handler': self.cmd_attack, 'category': 'combat'},
            'stab': {'handler': self.cmd_attack, 'category': 'combat'},
            # Throw command for hazard items
            'throw': {'handler': self.cmd_throw, 'category': 'interaction'},
            'message-settings': {'handler': self.cmd_message_settings, 'category': 'system'},
            'messages': {'handler': self.cmd_message_settings, 'category': 'system'},
            'behavior-settings': {'handler': self.cmd_behavior_settings, 'category': 'system'},
            'npc-settings': {'handler': self.cmd_behavior_settings, 'category': 'system'},
        }
        self.is_running = True
        self.behavior_settings = {
            "idle": {"enabled": True, "frequency": 50, "cooldown": 5},
            "talk": {"enabled": True, "frequency": 50, "cooldown": 5},
            "fight": {"enabled": True, "frequency": 50, "cooldown": 5},
            "use-item": {"enabled": True, "frequency": 50, "cooldown": 5},
            "gardening": {"enabled": True, "frequency": 50, "cooldown": 5},
            "gift": {"enabled": True, "frequency": 50, "cooldown": 5},
        }

    def add_item_to_area(self, area_name, item_name):
        """Add an item to a specified area."""
        area = self.areas.get(area_name)
        item = self.items.get(item_name)
        if area and item:
            area.add_item(item)
            return f"Added {item.name} to {area.name}."
        return "Area or item not found."
    

    def add_object_to_area(self, area_name, object_name):
        """Add an object to a specified area."""
        area = self.areas.get(area_name)
        object = self.objects.get(object_name)
        if area and object:
            area.add_object(object)
            return f"Added {object.name} to {area.name}."
        return "Area or item not found."
    

    def add_npc_to_area(self, area_name, npc_name):
        """Add an NPC to a specified area."""
        area = self.areas.get(area_name)
        npc = self.npcs.get(npc_name)
        if area and npc:
            area.add_npc(npc)
            return f"Added {npc.name} to {area.name}."
        return "Area or NPC not found."


    def create_items(self):
        """Dynamically create and register items."""

        # regular items
        shovel = Item("Shovel", "A shovel for digging.", 5)

        
        # weapons
        knife = Weapon("Knife","A sharp blade.", 10, 20)
        gun = Weapon("Gun", "A firearm.", 20, 50)
        
        usb_stick = Item("USB stick", "A USB stick with data on it.", 10)
        farm_note = Item("Note", "An old, crumbled up piece of paper with some scribbled writing on it: Take the backroads. You'll find what you're looking for up north.", 10)

        glitter_bomb = HazardItem("Glitter Bomb", "A small, shiny bomb that explodes into glitter.", "gift-giving")



        # Register items in the centralized item registry
        self.items["Shovel"] = shovel
        self.items["Knife"] = knife
        self.items["USB stick"] = usb_stick  # item.name is also a valid key
        self.items["Note"] = farm_note  # need to organize this better for multiple notes


        self.items["Glitter Bomb"] = glitter_bomb


        carrot_seed = Seed("Carrot Seed", "A seed for planting carrots.", "carrot", 5)
        tomato_seed = Seed("Tomato Seed", "A seed for planting tomatoes.", "tomato", 5)
        grape_seed = Seed("Grape Seed", "A seed for planting grapes.", "grape", 5)



        self.items["Carrot Seed"] = carrot_seed
        self.items["Tomato Seed"] = tomato_seed
        self.items["Grape Seed"] = grape_seed
        
        # Create smartphone
        smartphone = Smartphone("Smartphone", "A high-tech smartphone with various apps", 100)
        self.items["Smartphone"] = smartphone
        
        # Create watering can
        watering_can = WateringCan()
        self.items["Watering Can"] = watering_can

        hackedmilk = HackedMilk()

        watering_can.fill_with(hackedmilk) # not sure if this works
        
        
        # Add smartphone and watering can to player's starting inventory
        self.player_starting_items = [smartphone, watering_can, gun, carrot_seed, tomato_seed]  # We'll use this in the Player initialization

    def create_objects(self):
        # Dynamically create and register objects.

        garden = Soil("Garden", "A garden full of plants.")

        soil_box = Soil("Soil Box", "A box filled with soil.")
        self.objects["Soil Box"] = soil_box
        
        # Create a storage object for the player's home
        toolbox = Storage("Toolbox", "A sturdy metal toolbox for storing garden tools.", capacity=5)
        
        # Create a watering can for gardening
        watering_can = Item("Watering Can", "A metal watering can for watering plants.", 5)
        self.items["Watering Can"] = watering_can
        
        # Register objects in the centralized object registry
        self.objects["Garden"] = garden
        self.objects["Toolbox"] = toolbox
        
        # Add objects to areas
        self.add_object_to_area('Home', 'Garden')
        self.add_object_to_area('Home', 'Toolbox')
        
        # Add the watering can to the toolbox
        toolbox.add_item(watering_can)


        # Create hacked milk
        hacked_milk = StaticHazard("Hacked Milk", "A container of milk that has been tampered with.", "hallucinations")
        self.objects["Hacked Milk"] = hacked_milk
        
        self.add_object_to_area('Warehouse', 'Hacked Milk')
        self.add_object_to_area('Warehouse', 'Soil Box')



    def create_npcs(self):
        """Dynamically create and register NPCs."""
        # NPCs
        Jack = NPC("Jack", "The owner of Jacks Fuel, who may offer valuable intel.")
        self.npcs["Jack"] = Jack

        # Create Bloodhounds gang and members
        bloodhounds_gang = Gang("Bloodhounds")
        bloodhounds_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]


        # CHANGING NAMES IN A WACKY WAY

        name_variations = ["etti", "oodle", "op", "eeky", "-eep", "uffin", "bertmo", "athur", "ubble", "uck"]

        def generate_name_variations(names, variations):
            """Replaces last character in each name with a random variation."""
            new_names = []
            for name in names:
                variation = random.choice(variations)  # Pick a random suffix
                modified_name = name[:-1] + variation  # Remove last character and append new one
                new_names.append(modified_name)
            return new_names

        # Generate modified gang names
        modified_bloodhound_names = generate_name_variations(bloodhounds_names, name_variations)

        # Print new gang member names
        for name in modified_bloodhound_names:
            bloodhounds_names.append(name)



        for name in bloodhounds_names:
            member = GangMember(name, f"A member of the {bloodhounds_gang.name} gang.", bloodhounds_gang)
            # Add default items to each gang member
            knife = self.items.get("Knife")
            if knife:
                member.add_item(knife)
            member.add_item(self.items.get("USB stick"))
            self.npcs[name] = member

        # Add gang members to Warehouse area NPC list
        warehouse_area = self.areas.get("Warehouse")
        if warehouse_area:
            for name in bloodhounds_names:
                member = self.npcs.get(name)
                if member:
                    warehouse_area.add_npc(member)




    def create_areas(self):
        """Create and connect areas in a scalable way."""
        Suburbs = Area("Suburbs", "A quiet suburban neighborhood.")
        Downtown = Area("Downtown", "A bustling city area.")
        Warehouse = Area("Warehouse", "An abandoned warehouse with construction containers lining the walls, stacked up to the ceiling, run by the Bloodhounds.")
        Backroads = Area("Backroads", "A foggy, long stretch of road leads to the unknown.")
        JacksFuel = Area("Jack's Fuel Station", "On the side of the road, a small fuel station with a sign that reads 'Jack's Fuel'.")
        Farm = Area("The Farm", "A seemingly abandoned farm taken over by the Bloodhounds.")


        Home = Area("Home", "In the entrance to your house. The living room is to the north. The suburbs are outside.")
        Home_Living_Room = Area("Living Room", "A room with a couch, a TV, and a coffee table.")
        Home_Kitchen = Area("Kitchen", "A room with a sink, a fridge, and cabinets.")
        Home_Study = Area("Study", "A room with a desk, a computer, and a chair.")


        # Connect areas


        Home.add_exit("east", Warehouse)
        Home.add_exit("outside", Suburbs)

        Downtown.add_exit("south", Suburbs)
        Downtown.add_exit("east", Warehouse)

        Warehouse.add_exit("west", Downtown)
        Warehouse.add_exit("north", Backroads)

        Backroads.add_exit("North", Farm)
        Backroads.add_exit("west", JacksFuel)
        # add a road that goes east, leads to abandoned train tracks with a tunnel and a maintenance building inside the tunnel (more weapons and other item discoveries, maybe intel)




        Suburbs.add_exit("north", Downtown)
        Suburbs.add_exit("inside", Home)

        # Add areas to the dictionary
        self.areas['Home'] = Home
        self.areas['Downtown'] = Downtown
        self.areas['Warehouse'] = Warehouse
        self.areas['Backroads'] = Backroads
        self.areas['JacksFuel'] = JacksFuel
        self.areas['Farm'] = Farm

        # Add items to areas
        self.add_item_to_area('Home', 'Shovel')
        self.add_item_to_area('Downtown', 'Knife')
        self.add_item_to_area('Warehouse', 'USB stick')
        self.add_item_to_area('Warehouse', 'Note')
        self.add_item_to_area('Backroads', 'Carrot Seed')

        self.add_item_to_area('Warehouse', 'Glitter Bomb')
        self.add_item_to_area('Warehouse', 'Carrot Seed')
        self.add_item_to_area('Warehouse', 'Carrot Seed')
        self.add_item_to_area('Warehouse', 'Tomato Seed')
        self.add_item_to_area('Warehouse', 'Grape Seed')
        self.add_item_to_area('Warehouse', 'Shovel')
        self.add_item_to_area('Warehouse', 'Watering Can')




        self.add_npc_to_area('JacksFuel', 'Jack')
        

    def game_loop(self):
        print("Welcome to Root Access!")
        print("Type 'help' for a list of commands.\n")
        while self.is_running:
            # Start a new turn for the message systems
            if hasattr(self, 'message_coordinator'):
                self.message_coordinator.new_turn()
            else:
                self.message_manager.new_turn()

            # Decrement NPC cooldowns
            self.npc_behavior_coordinator.decrement_cooldowns()

            # Get the current location
            location_text = f"\nCurrent location: {self.player.current_area.name}"
            print(location_text)



                # Get an NPC in the current area
            npc = game.player.current_area.npcs[0] if game.player.current_area.npcs else None
            if npc:
                from npc_behavior import UseItemBehavior
                # Find a seed
                seed = None
                for item in game.player.current_area.items:
                    if "seed" in item.name.lower():
                        seed = item
                        break
                if seed:
                    # Create a behavior to plant the seed
                    behavior = UseItemBehavior(npc, seed)
                    # Execute the behavior
                    result = behavior._plant_seed(game)
                    print(f"Planting result: {result}")
                
        


            command_input = input("> ").strip()
            if not command_input:
                continue
            parts = command_input.split()
            command = parts[0].lower()
            args = parts[1:]
            cmd_entry = self.commands.get(command)
            if cmd_entry:
                # Process player command
                output = cmd_entry['handler'](args)
                if output:
                    if hasattr(self, 'message_coordinator'):
                        should_show = self.message_coordinator.process_player_message(
                            output, 
                            priority=MessagePriority.HIGH
                        )
                    else:
                        should_show, _ = self.message_manager.add_message(
                            output, 
                            category=MessageCategory.PLAYER_ACTION,
                            priority=MessagePriority.HIGH
                        )
                    if should_show:
                        print(output)

                # Process hazards in the current area
                for obj in list(self.player.current_area.objects):
                    if isinstance(obj, StaticHazard) and obj.active:
                        hazard_result = obj.affect_area(self.player.current_area)
                        if hazard_result:
                            if hasattr(self, 'message_coordinator'):
                                self.message_coordinator.process_system_message(
                                    hazard_result, 
                                    category=MessageCategory.HAZARD_EFFECT,
                                    priority=MessagePriority.HIGH
                                )
                            else:
                                self.message_manager.add_message(
                                    hazard_result, 
                                    category=MessageCategory.HAZARD_EFFECT
                                )

                # Process NPCs in the current area using the coordinator
                npc_actions = []
                for npc in self.player.current_area.npcs:
                    if hasattr(npc, 'is_alive') and not npc.is_alive:
                        continue
                    if hasattr(npc, 'update_behavior'):
                        behavior_result = npc.update_behavior(self)
                        if behavior_result:
                            behavior_type = self.npc_behavior_coordinator._get_behavior_type(
                                npc.behavior_manager.current_behavior
                            )
                            npc_actions.append((npc.name, behavior_type, behavior_result))

                # Summarize NPC actions
                if hasattr(self, 'message_coordinator'):
                    npc_summary = self.message_coordinator.summarize_npc_actions(npc_actions)
                    if npc_summary:
                        print(npc_summary)

                # Get message summary for this turn
                message_summary = self.message_manager.get_message_summary(
                    categories=[
                        MessageCategory.NPC_MINOR,
                        MessageCategory.HAZARD_EFFECT,
                        MessageCategory.AMBIENT,
                        MessageCategory.NPC_SUMMARY
                    ]
                )
                if message_summary:
                    print(message_summary)
            else:
                print("Unknown command. Type 'help' for a list of commands.")

    def cmd_move(self, args):
        if not args:
            return "Move where? Specify a direction."
        direction = args[0].lower()
        return self.player.move(direction)

    def _release_examined_items(self):
        """Release all items that were being examined this turn."""
        if hasattr(self, '_items_to_release'):
            for item in self._items_to_release:
                if hasattr(item, '_being_examined_by'):
                    delattr(item, '_being_examined_by')
            self._items_to_release = []
    
    def cmd_teleport(self, args):
        if not args:
            return "Teleport where? Specify an area name."
        area_name = " ".join(args).lower()
        # Search for area ignoring case
        for key, area in self.areas.items():
            if key.lower() == area_name or area.name.lower() == area_name:
                return self.player.teleport(area)
        return f"No such area: {' '.join(args)}"

    def cmd_look(self, args):
        """Look around the current area.
        
        Usage: look
        
        This command shows a description of your current location,
        including items, NPCs, and objects in the area.
        """
        return self.player.current_area.describe(self)

    def cmd_inventory(self, args):
        if self.player.inventory:
            return "You have:\n" + "\n".join(f" - {item}" for item in self.player.inventory)
        else:
            return "Your inventory is empty."

    def cmd_pick_up(self, args):
        if not args:
            return "pick up what? Specify an item name."
            
        # Check if this is a "take from storage" command
        if "from" in args:
            return self.cmd_take_from(args)
            
        item_name = " ".join(args)
        # Find item in current area by name
        for item in self.player.current_area.items:
            if item.name.lower() == item_name.lower():
                return self.player.pick_up(item)
        return f"No such item here: {item_name}"

    def cmd_drop(self, args):
        if not args:
            return "Drop what? Specify an item name."
        item_name = " ".join(args)
        # Find item in inventory by name
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                return self.player.drop(item)
        return f"You don't have that item: {item_name}"

    def cmd_quit(self, args):
        self.is_running = False
        return "Thanks for playing! Goodbye."

    def cmd_attack(self, args):
        """Player attack command handler. Usage: attack [gang member name]"""
        if not args:
            return "Attack whom? Specify a gang member's name."
        target_name = " ".join(args)
        result = self.player.attack(target_name, self)
        # Check if player died during combat
        death_message = self.player.check_death_and_respawn(self)
        if death_message:
            result += f"\n{death_message}"
        return result

    def cmd_throw(self, args):
        """Throw a hazard item to affect gang members. Usage: throw [item name]"""
        if not args:
            return "Throw what? Specify an item name."
        item_name = " ".join(args).lower()
        # Find item in inventory
        item = None
        for inv_item in self.player.inventory:
            if inv_item.name.lower() == item_name:
                item = inv_item
                break
        if not item:
            return f"You don't have a {item_name} in your inventory."
        # Check if item is a HazardItem
        if not isinstance(item, HazardItem):
            return f"You can't throw the {item.name}."
        # Use the hazard item effect
        result = item.use(self.player)
        # Remove the item from inventory after throwing
        self.player.inventory.remove(item)
        return result

    def cmd_exit(self, args):
        """List exits for current area or specified area."""
        if not args:
            return "Usage: exit [area name]"
        area_name = " ".join(args)
        area = self.areas.get(area_name)
        if not area:
            return f"No such area: {area_name}"
        exits = area.exits
        if not exits:
            return f"{area.name} has no exits."
        exit_list = ", ".join(f"{direction} -> {dest.name}" for direction, dest in exits.items())
        return f"Exits for {area.name}: {exit_list}"

    def cmd_help(self, args):
        import sys
        if args:
            # Detailed help for a specific command
            cmd = args[0].lower()
            if cmd in self.commands:
                handler = self.commands[cmd]['handler']
                doc = handler.__doc__ or "No documentation available."
                return f"Help for '{cmd}':\n{doc}"
            else:
                return f"Unknown command: {cmd}"
        
        # General help listing all commands by category with pagination
        categories = {}
        for cmd, info in self.commands.items():
            cat = info['category']
            categories.setdefault(cat, []).append(cmd)
        
        category_keys = sorted(categories.keys())
        for i, cat in enumerate(category_keys):
            cmds = ", ".join(sorted(categories[cat]))
            print(f"\n{cat.capitalize()} commands:\n  {cmds}\n")
            
            # Add special sections for storage, smartphone, and plant effects only on first page
            if i == 0:
                print("Storage-related commands:")
                print("  open [storage] - Open a storage object")
                print("  close [storage] - Close a storage object")
                print("  look in [storage] - View items in an open storage")
                print("  take [item] from [storage] - Take an item from storage")
                print("  put [item] in [storage] - Put an item into storage\n")
                
                print("Smartphone commands:")
                print("  use phone - View available apps on your smartphone")
                print("  use phone garden - Open the Garden Manager app")
                print("  app [option] - Execute an option in the currently open app (e.g., app status, app instagrow, app hack)\n")
                
                print("Plant effects commands:")
                print("  fill [watering can] with [substance] - Fill a watering can with a substance")
                print("  empty [watering can] - Empty a watering can")
                print("  water [plant/soil] - Water using your watering can (requires a watering can in inventory)")
                print("  water [plant/soil] with [watering can] - Water using a specific watering can")
                print("  eat [item] - Consume an item, applying any effects it might have\n")
                
                                
                print("Message System:")
                print("  The game includes a message management system that controls what messages are shown.")
                print("  Messages are categorized by type and can be configured to your preferences.")
                print("  Commands:")
                print("    message-settings or messages - View current message display settings")
                print("    message-settings [category] [setting] [value] - Configure message settings")
                print("  Categories:")
                print("    npc - NPC minor interactions (idle actions, talking)")
                print("    hazard - Hazard effects on NPCs and environment")
                print("    ambient - Ambient/environmental messages")
                print("    all - All message categories at once")
                print("  Settings:")
                print("    show - Whether to show messages directly (on/off)")
                print("    rate - How often to show messages (0-100%)")
                print("    cooldown - Turns between messages (number)")
                print("  Examples:")
                print("    'message-settings hazard rate 5' - Show only 5% of hazard effect messages")
                print("    'message-settings npc show off' - Don't show minor NPC interactions directly")
                print("    'message-settings all cooldown 10' - Set cooldown for all categories to 10 turns\n")
            
            if i < len(category_keys) - 1:
                user_input = input("Press Enter to see more commands or 'q' to quit help: ").strip().lower()
                if user_input == 'q':
                    break
        
        return "End of help."
    
    def cmd_plant(self, args):
        """Plant a seed in soil. Usage: plant [seed name] in [soil name]"""
        if not args:
            return "Plant what? Usage: plant [seed name] in [soil name]"
        
        # Check if the command includes "in" to specify the soil
        if "in" in args:
            in_index = args.index("in")
            seed_name = " ".join(args[:in_index])
            soil_name = " ".join(args[in_index+1:])
        else:
            seed_name = " ".join(args)
            soil_name = None  # Will try to find any soil in the area
        
        # Find seed in inventory
        seed = None
        for item in self.player.inventory:
            if item.name.lower() == seed_name.lower() and isinstance(item, Seed):
                seed = item
                break
        
        if not seed:
            return f"You don't have a seed called '{seed_name}' in your inventory."
        
        # Find soil in the current area
        soil = None
        if soil_name:
            # Look for specific soil
            for obj in self.player.current_area.objects:
                if isinstance(obj, Soil) and obj.name.lower() == soil_name.lower():
                    soil = obj
                    break
            if not soil:
                return f"There is no soil called '{soil_name}' in this area."
        else:
            # Look for any soil
            for obj in self.player.current_area.objects:
                if isinstance(obj, Soil):
                    soil = obj
                    break
            if not soil:
                return "There is no soil in this area to plant seeds in."
        
        # Plant the seed in the soil
        success, message = soil.add_plant(seed)
        if success:
            self.player.inventory.remove(seed)
            return message
        else:
            return message
        
    def cmd_harvest(self, args):
        """Harvest a plant from soil. Usage: harvest [plant name] from [soil name]"""
        if not args:
            return "Harvest what? Usage: harvest [plant name] from [soil name]"
        
        # Check if the command includes "from" to specify the soil
        if "from" in args:
            from_index = args.index("from")
            plant_name = " ".join(args[:from_index])
            soil_name = " ".join(args[from_index+1:])
        else:
            plant_name = " ".join(args)
            soil_name = None  # Will try to find the plant in any soil
        
        # Find soil and plant
        for obj in self.player.current_area.objects:
            if isinstance(obj, Soil):
                if soil_name and obj.name.lower() != soil_name.lower():
                    continue  # Skip this soil if we're looking for a specific one
                
                plant = obj.get_plant(plant_name)
                if plant:
                    if plant.is_harvestable():
                        # Get a harvested item with any effects transferred
                        harvested_item = plant.get_harvested_item()
                        
                        # Add to inventory and remove from soil
                        self.player.inventory.append(harvested_item)
                        obj.remove_plant(plant)
                        
                        # Check if the harvested item has effects
                        if hasattr(harvested_item, 'effects') and harvested_item.effects:
                            effect_names = ", ".join(effect.name for effect in harvested_item.effects)
                            return f"You harvested a {plant.crop_type} from the {obj.name}. It seems to have been affected by: {effect_names}."
                        else:
                            return f"You harvested a {plant.crop_type} from the {obj.name}."
                    else:
                        return f"The {plant.name} is not ready to harvest yet."
        
        if soil_name:
            return f"Could not find a plant called '{plant_name}' in the '{soil_name}'."
        else:
            return f"Could not find a plant called '{plant_name}' in any soil in this area."



    def cmd_open(self, args):
        # Open a storage object. Usage: open [storage name]
        if not args:
            return "Open what? Specify a storage object name."
        
        storage_name = " ".join(args)
        
        # Find storage object in current area
        for obj in self.player.current_area.objects:
            if isinstance(obj, Storage) and obj.name.lower() == storage_name.lower():
                success, message = obj.open()
                return message
        
        return f"There is no storage named '{storage_name}' here."
    
    def cmd_close(self, args):
        # Close a storage object. Usage: close [storage name]
        if not args:
            return "Close what? Specify a storage object name."
        
        storage_name = " ".join(args)
        
        # Find storage object in current area
        for obj in self.player.current_area.objects:
            if isinstance(obj, Storage) and obj.name.lower() == storage_name.lower():
                success, message = obj.close()
                return message
        
        return f"There is no storage named '{storage_name}' here."
    
    def cmd_take_from(self, args):
        # Take an item from a storage object. Usage: take [item name] from [storage name]
        if not args or "from" not in args:
            return "Usage: take [item name] from [storage name]"
        
        from_index = args.index("from")
        item_name = " ".join(args[:from_index])
        storage_name = " ".join(args[from_index+1:])
        
        # Find storage object in current area
        for obj in self.player.current_area.objects:
            if isinstance(obj, Storage) and obj.name.lower() == storage_name.lower():
                if not obj.is_open:
                    return f"The {obj.name} is closed. You need to open it first."
                
                success, item = obj.remove_item(item_name)
                if success:
                    self.player.inventory.append(item)
                    return f"You take the {item.name} from the {obj.name}."
                else:
                    return f"There is no {item_name} in the {obj.name}."
        
        return f"There is no storage named '{storage_name}' here."
    
    def cmd_put_in(self, args):
        # Put an item into a storage object. Usage: put [item name] in [storage name]
        if not args or "in" not in args:
            return "Usage: put [item name] in [storage name]"
        
        in_index = args.index("in")
        item_name = " ".join(args[:in_index])
        storage_name = " ".join(args[in_index+1:])
        
        # Find item in player's inventory
        item = None
        for inv_item in self.player.inventory:
            if inv_item.name.lower() == item_name.lower():
                item = inv_item
                break
        
        if not item:
            return f"You don't have a {item_name} in your inventory."
        
        # Find storage object in current area
        for obj in self.player.current_area.objects:
            if isinstance(obj, Storage) and obj.name.lower() == storage_name.lower():
                if not obj.is_open:
                    return f"The {obj.name} is closed. You need to open it first."
                
                self.player.inventory.remove(item)
                success, message = obj.add_item(item)
                return message
        
        return f"There is no storage named '{storage_name}' here."
    
    def cmd_look_in(self, args):
        # Look inside a storage object. Usage: look in [storage name]
        if not args or "in" not in args:
            return "Usage: look in [storage name]"
        
        in_index = args.index("in")
        storage_name = " ".join(args[in_index+1:])
        
        # Find storage object in current area
        for obj in self.player.current_area.objects:
            if isinstance(obj, Storage) and obj.name.lower() == storage_name.lower():
                if not obj.is_open:
                    return f"The {obj.name} is closed. You need to open it first."
                
                return obj.list_items()
        
            return f"There is no storage named '{storage_name}' here."
        
        
            
    def cmd_water(self, args):
        """Water plants in soil. Usage: water [plant name] in [soil name] with [watering can]"""
        # Parse arguments
        plant_name = None
        soil_name = None
        watering_can = None
        substance = None
        
        # First, check if the player has a watering can in their inventory
        has_watering_can = False
        default_watering_can = None
        
        for item in self.player.inventory:
            if isinstance(item, WateringCan):
                has_watering_can = True
                default_watering_can = item
                break
        
        if not has_watering_can:
            return "You need a watering can to water plants. Find one or craft one."
        
        # Check if using a specific watering can with a substance
        if "with" in args:
            with_index = args.index("with")
            watering_can_name = " ".join(args[with_index+1:])
            args = args[:with_index]  # Remove the "with watering can" part
            
            # Find the specified watering can in inventory
            watering_can = None
            for item in self.player.inventory:
                if isinstance(item, WateringCan) and item.name.lower() == watering_can_name.lower():
                    watering_can = item
                    substance = item.substance
                    break
            
            if not watering_can:
                return f"You don't have a {watering_can_name} in your inventory."
        else:
            # Use the default watering can found earlier
            watering_can = default_watering_can
            substance = watering_can.substance
        
        if not args:
            # Water all plants in any soil
            pass
        elif "in" in args:
            # Format: water [plant name] in [soil name]
            in_index = args.index("in")
            if in_index > 0:
                plant_name = " ".join(args[:in_index])
            soil_name = " ".join(args[in_index+1:])
        else:
            # Format could be just a soil name or just a plant name
            arg_str = " ".join(args)
            
            # Check if it's a soil name first
            soil_found = False
            for obj in self.player.current_area.objects:
                if isinstance(obj, Soil) and obj.name.lower() == arg_str.lower():
                    soil_name = arg_str
                    soil_found = True
                    break
            
            # If not a soil, assume it's a plant name
            if not soil_found:
                plant_name = arg_str
        
        # Find soil(s) to water
        watered_something = False
        messages = []
        
        for obj in self.player.current_area.objects:
            if isinstance(obj, Soil):
                if soil_name and obj.name.lower() != soil_name.lower():
                    continue  # Skip this soil if we're looking for a specific one
                
                success, message = obj.water_plants(plant_name, substance)
                if success:
                    watered_something = True
                    messages.append(message)
                    
                    # Add a message about which watering can was used
                    if substance:
                        messages.append(f"You used your {watering_can.name} filled with {substance.name}.")
                    else:
                        messages.append(f"You used your {watering_can.name} with regular water.")
        
        if watered_something:
            return "\n".join(messages)
        elif soil_name:
            return f"Could not find a soil called '{soil_name}' in this area."
        elif plant_name:
            return f"Could not find a plant called '{plant_name}' in any soil in this area."
        else:
            return "There are no plants to water in this area."
    
    def cmd_use(self, args):
        """Use an item from your inventory. Usage: use [item name]"""
        if not args:
            return "Use what? Specify an item name."
        
        item_name = args[0].lower()
        
        # Special case for smartphone
        if item_name == "phone" or item_name == "smartphone":
            # Find smartphone in inventory
            for item in self.player.inventory:
                if isinstance(item, Smartphone):
                    # If additional args are provided, try to open that app
                    if len(args) > 1:
                        app_name = args[1].lower()
                        return item.open_app(app_name)
                    else:
                        # Just show the main menu
                        return item.use()
            return "You don't have a smartphone in your inventory."
        
        # Handle other usable items
        for item in self.player.inventory:
            if item.name.lower() == item_name:
                if hasattr(item, 'use') and callable(item.use):
                    return item.use()
                else:
                    return f"You can't use the {item.name} that way."
        
        return f"You don't have a {item_name} in your inventory."
    
    def cmd_app(self, args):
        """Execute an app function on your smartphone. Usage: app [option]"""
        if not args:
            return "Specify an app option to execute."
        
        option = args[0].lower()
        
        # Find smartphone in inventory
        for item in self.player.inventory:
            if isinstance(item, Smartphone):
                if not item.current_app:
                    return "No app is currently open. Use 'use phone [app_name]' first."
                return item.execute_app_option(option, self, self.player)
        
        return "You don't have a smartphone in your inventory."
        
    def cmd_eat(self, args):
        """Eat/consume an item from your inventory. Usage: eat [item name]"""
        if not args:
            return "Eat what? Specify an item name."
        
        item_name = " ".join(args)
        
        # Find item in inventory
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                return self.player.consume(item, self)
        
        return f"You don't have a {item_name} in your inventory."
    
    def cmd_fill(self, args):
        """Fill a watering can with a substance. Usage: fill [watering can] with [substance]"""
        if not args or "with" not in args:
            return "Usage: fill [watering can] with [substance]"
        
        with_index = args.index("with")
        can_name = " ".join(args[:with_index])
        substance_name = " ".join(args[with_index+1:])
        
        # Find watering can in inventory
        watering_can = None
        for item in self.player.inventory:
            if isinstance(item, WateringCan) and item.name.lower() == can_name.lower():
                watering_can = item
                break
        
        if not watering_can:
            return f"You don't have a {can_name} in your inventory."
        
        # Find substance in inventory
        substance = None
        for item in self.player.inventory:
            if isinstance(item, Substance) and item.name.lower() == substance_name.lower():
                substance = item
                break
        
        if not substance:
            return f"You don't have {substance_name} in your inventory."
        
        # Fill the watering can
        return watering_can.fill_with(substance)
    
    def cmd_empty(self, args):
        """Empty a watering can. Usage: empty [watering can]"""
        if not args:
            return "Empty what? Specify a watering can name."
        
        can_name = " ".join(args)
        
        # Find watering can in inventory
        for item in self.player.inventory:
            if isinstance(item, WateringCan) and item.name.lower() == can_name.lower():
                return item.empty()
        
        return f"You don't have a {can_name} in your inventory."
    
    def cmd_message_settings(self, args):
        """Configure message display settings.
        
        Usage: 
          message-settings - Show current settings
          message-settings [category] [setting] [value] - Configure a setting
        
        Categories:
          npc - NPC minor messages
          npc-idle - NPC idle behaviors (standing, waiting, etc.)
          npc-movement - NPC movement behaviors (walking, running, etc.)
          npc-interaction - NPC interactions with objects or other NPCs
          npc-talk - NPC talking or making sounds
          npc-gift - NPC giving gifts or items
          npc-hazard - NPC affected by hazards
          all-npc - All NPC categories
          
          hazard - Hazard effect messages
          ambient - Ambient/environmental messages
          trivial - Trivial messages
          all - All message categories
        
        Settings:
          show - Whether to show messages directly (on/off)
          rate - How often to show messages (0-100%)
          cooldown - Turns between messages (number)
        
        Examples:
          message-settings - Show all current settings
          message-settings npc show off - Turn off direct display of minor NPC messages
          message-settings npc-idle rate 0 - Never show NPC idle behaviors
          message-settings all-npc cooldown 5 - Set cooldown for all NPC messages to 5 turns
          message-settings hazard rate 5 - Show only 5% of hazard effect messages
          message-settings ambient cooldown 10 - Set ambient message cooldown to 10 turns
        """
        if not args:
            # Show current settings
            settings = []
            settings.append("Message Display Settings:")
            
            # Get settings for each category
            categories = {
                # NPC categories
                "npc": MessageCategory.NPC_MINOR,
                "npc-idle": MessageCategory.NPC_IDLE,
                "npc-movement": MessageCategory.NPC_MOVEMENT,
                "npc-interaction": MessageCategory.NPC_INTERACTION,
                "npc-talk": MessageCategory.NPC_TALK,
                "npc-gift": MessageCategory.NPC_GIFT,
                "npc-hazard": MessageCategory.NPC_HAZARD,
                
                # Other categories
                "hazard": MessageCategory.HAZARD_EFFECT,
                "ambient": MessageCategory.AMBIENT,
                "trivial": MessageCategory.TRIVIAL
            }
            
            # Display current settings for each category
            for name, category in categories.items():
                settings.append(f"  {name}:")
                settings.append(f"    show: {self.message_manager.should_show_category(category)}")
                settings.append(f"    rate: {self.message_manager.get_category_rate(category)}%")
                settings.append(f"    cooldown: {self.message_manager.get_category_cooldown(category)} turns")
            
            return "\n".join(settings)
            
        # Handle command with arguments
        if len(args) < 3:
            return "Invalid arguments. Usage: message-settings [category] [setting] [value]"
            
        category_name = args[0].lower()
        setting_name = args[1].lower()
        value = args[2].lower()
        
        # Map category name to enum
        categories = {
            # NPC categories
            "npc": MessageCategory.NPC_MINOR,
            "npc-idle": MessageCategory.NPC_IDLE,
            "npc-movement": MessageCategory.NPC_MOVEMENT,
            "npc-interaction": MessageCategory.NPC_INTERACTION,
            "npc-talk": MessageCategory.NPC_TALK,
            "npc-gift": MessageCategory.NPC_GIFT,
            "npc-hazard": MessageCategory.NPC_HAZARD,
            
            # Other categories
            "hazard": MessageCategory.HAZARD_EFFECT,
            "ambient": MessageCategory.AMBIENT,
            "trivial": MessageCategory.TRIVIAL,
            
            # Special categories
            "all-npc": None,
            "all": None
        }
        
        if category_name not in categories:
            valid_categories = ", ".join(sorted(categories.keys()))
            return f"Unknown category: {category_name}. Valid categories: {valid_categories}"
            
        # Handle special categories
        if category_name == "all-npc":
            target_categories = [
                MessageCategory.NPC_MINOR,
                MessageCategory.NPC_IDLE,
                MessageCategory.NPC_MOVEMENT,
                MessageCategory.NPC_INTERACTION,
                MessageCategory.NPC_TALK,
                MessageCategory.NPC_GIFT,
                MessageCategory.NPC_HAZARD
            ]
        elif category_name == "all":
            target_categories = list(MessageCategory)
        else:
            target_categories = [categories[category_name]]
            
        # Apply setting to each category
        for category in target_categories:
            if setting_name == "show":
                if value.lower() in ["on", "true", "yes", "1"]:
                    self.message_manager.set_category_show(category, True)
                elif value.lower() in ["off", "false", "no", "0"]:
                    self.message_manager.set_category_show(category, False)
                else:
                    return f"Invalid value for 'show': {value}. Use 'on' or 'off'."
            
                if setting_name == "rate":
                    try:
                        rate = int(value)
                        if rate < 0 or rate > 100:
                            return "Rate must be between 0 and 100."
                        self.message_manager.set_category_rate(category, rate)
                    except ValueError:
                        return f"Invalid value for 'rate': {value}. Must be a number between 0 and 100."
            elif setting_name == "cooldown":
                try:
                    cooldown = int(value)
                    if cooldown < 0:
                        return "Cooldown must be a non-negative integer."
                    self.message_manager.set_category_cooldown(category, cooldown)
                except ValueError:
                    return f"Invalid value for 'cooldown': {value}. Must be a non-negative integer."
            else:
                return f"Unknown setting: {setting_name}. Valid settings: show, rate, cooldown"
                
        category_desc = category_name
        return f"Updated {setting_name} setting for {category_desc}"
        
    def cmd_behavior_settings(self, args):
        """Configure NPC behavior settings.
        
        Usage: 
          behavior-settings - Show current settings
          behavior-settings [behavior] [setting] [value] - Configure a setting
          behavior-settings [behavior] [on/off] - Enable or disable a behavior
          behavior-settings all [on/off] - Enable or disable all behaviors
        
        Behaviors:
          idle - NPC idle behaviors (standing, waiting, etc.)
          talk - NPC talking behaviors
          fight - NPC fighting behaviors
          use-item - NPC item interaction behaviors
          gardening - NPC planting, watering, and harvesting behaviors
          gift - NPC gift-giving behaviors
          all - All behavior types
        
        Settings:
          frequency - How often NPCs perform this behavior (0-100%)
          cooldown - Turns between behaviors (number)
        
        Examples:
          behavior-settings - Show all current settings
          behavior-settings idle frequency 50 - Set idle behavior frequency to 50%
          behavior-settings talk cooldown 5 - Set talk behavior cooldown to 5 turns
          behavior-settings all off - Disable all NPC behaviors
        """
        if not args:
            # Show current settings
            settings = ["NPC Behavior Settings:"]
            for behavior, config in self.behavior_settings.items():
                status = "enabled" if config["enabled"] else "disabled"
                settings.append(
                    f"  {behavior}: {status}, frequency={config['frequency']}%, cooldown={config['cooldown']} turns"
                )
            return "\n".join(settings)
        
        behavior = args[0].lower()
        if behavior not in self.behavior_settings and behavior != "all":
            valid_behaviors = ", ".join(self.behavior_settings.keys()) + ", all"
            return f"Unknown behavior: {behavior}. Valid behaviors: {valid_behaviors}"
        
        if len(args) == 2 and args[1].lower() in ["on", "off"]:
            # Enable or disable behavior
            enabled = args[1].lower() == "on"
            if (behavior == "all"):
                for config in self.behavior_settings.values():
                    config["enabled"] = enabled
                return f"All behaviors {'enabled' if enabled else 'disabled'}."
            else:
                self.behavior_settings[behavior]["enabled"] = enabled
                return f"{behavior.capitalize()} behavior {'enabled' if enabled else 'disabled'}."
        
        if len(args) == 3:
            # Update frequency or cooldown
            setting = args[1].lower()
            value = args[2]
            if setting not in ["frequency", "cooldown"]:
                return "Invalid setting. Valid settings: frequency, cooldown."
            
            try:
                value = int(value)
                if setting == "frequency" and (value < 0 or value > 100):
                    return "Frequency must be between 0 and 100."
                if setting == "cooldown" and value < 0:
                    return "Cooldown must be a non-negative integer."
                if behavior == "all":
                    for config in self.behavior_settings.values():
                        config[setting] = value
                    return f"Set {setting} for all behaviors to {value}."
                else:
                    self.behavior_settings[behavior][setting] = value
                    return f"Set {setting} for {behavior} behavior to {value}."
            except ValueError:
                return f"Invalid value for {setting}. Must be an integer."
        
        return "Invalid arguments. Usage: behavior-settings [behavior] [setting] [value] or behavior-settings [behavior] [on/off]."
    

# Import NPC action functions from npc_behavior.py
from npc_behavior import get_random_npc_action, get_npc_interaction

if __name__ == '__main__':
    game = Game()
    game.game_loop()
