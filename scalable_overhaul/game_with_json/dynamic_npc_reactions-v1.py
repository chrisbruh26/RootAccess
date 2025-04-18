
# To do next:
# - organize geography (area exits)
# move garden and toolbox to an outside area, like a garden
# fill areas with items and hazards, make functional
# more apps on phone
# regular NPCs
# lots of areas to explore and connect to each other
# need a lot of ideas for more items and hazards


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
        if substance:
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

class Object(): # this was initially a subclass of item, not sure if I want to keep it that way
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
        
class NPC:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.relationship = 0
        self.items = []

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)


class Civillian(NPC):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.health = 100
        self.items = []
        self.location = None
        self.is_alive = True
        self.is_injured = False
        self.is_arrested = False
        self.is_fighting = False # two NPCs will be randomly selected to fight each other during a random event
        self.emotion = None # none if feeling neutral, can be confused if weird chaos events happen
        self.needs_help = False # random events might occur where NPC needs help, such as being mugged


# New scalable Gang class to manage gang name and members
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

# New scalable GangMember class inheriting from NPC
class GangMember(NPC):
    def __init__(self, name, description, gang):
        super().__init__(name, description)
        self.gang = gang
        self.health = 100
        self.detection_chance = 10  # 10 = Base 10% chance to detect player
        self.has_detected_player = False
        self.detection_cooldown = 0
        self.active_effects = []  # List of active effects
        self.hazard_resistance = 0.05  # 0.05 = Base 5% chance to resist hazard effects
        self.gang.add_member(self)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
        return item

    def list_contents(self):
        return ", ".join(item.name for item in self.items) if self.items else "nothing"

    def apply_hazard_effect(self, hazard):
        import random
        if random.random() < self.hazard_resistance:
            return f"The {self.gang.name} member {self.name} resists the {hazard.name} effect!"

        # Select a random specific effect variant if available
        effect_variant = None
        if hasattr(hazard, 'effect_variants') and hazard.effect_variants:
            effect_variant = random.choice(hazard.effect_variants)
        else:
            effect_variant = hazard.effect if hasattr(hazard, 'effect') else None

        if effect_variant:
            self.active_effects.append(effect_variant)
            return f"{self.gang.name} member {self.name} {effect_variant}"
        else:
            return f"The {self.gang.name} member {self.name} is affected by {hazard.name}"

    def clear_effects(self):
        self.active_effects = []

    def die(self):
        if self.health <= 0:
            self.gang.remove_member(self)
            return f"The {self.gang.name} member {self.name} has been defeated!"

    def attack_player(self, player):
        import random
        # Check active effects that influence behavior
        for effect in self.active_effects:
            if effect == "hallucinations":
                return f"The {self.gang.name} member {self.name} is hallucinating and doesn't see you."
            if effect == "friendliness":
                return f"The {self.gang.name} member {self.name} smiles warmly at you."
            if effect == "gift-giving" and self.items:
                gift = random.choice(self.items)
                player.inventory.append(gift)
                self.items.remove(gift)
                return f"The {self.gang.name} member {self.name} gives you {gift.name} as a gift!"

        # Normal detection and attack logic
        if not player.hidden and (self.has_detected_player or random.random() < self.detection_chance):
            self.has_detected_player = True
            if hasattr(player, 'detected_by'):
                player.detected_by.add(self.gang)
            weapon = next((i for i in self.items if hasattr(i, 'damage')), None)
            damage = weapon.damage if weapon else 1
            player.health -= damage
            result = f"The {self.gang.name} member {self.name} spots and attacks you for {damage} damage!"
            if player.health <= 0:
                result += "\nYou have been defeated!"
            return result

        if player.hidden:
            self.has_detected_player = False
            return f"The {self.gang.name} member {self.name} looks around but doesn't see you."

        return f"The {self.gang.name} member {self.name} doesn't notice you."

    def update_effects(self):
        # Remove expired effects if they have duration (not implemented here)
        pass



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

    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)

    def describe(self):
        desc = f"{self.name}\n{self.description}\n"
        if self.items:
            desc += "You see the following items:\n"
            for item in self.items:
                desc += f" - {item.name}\n"
        if self.npcs:
            desc += "You see the following people:\n"
            for npc in self.npcs:
                desc += f" - {npc.name}\n"
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
        if next_area:
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
        result = f"You attack {target.name} with {weapon.name} for {damage} damage."

        if target.health <= 0:
            # Remove target from gang and area
            target.die()
            self.current_area.remove_npc(target)
            result += f"\nYou have defeated {target.name}!"
        else:
            result += f"\n{target.name} has {target.health} health remaining."

        return result

    def check_death_and_respawn(self, game):
        """Check if player is dead and respawn at home if so."""
        if self.health <= 0:
            home_area = game.areas.get('Home')
            if home_area:
                self.current_area = home_area
                self.health = 100
                self.active_effects.clear()
                self.hidden = False
                self.detected_by.clear()
                return "You have died and have been respawned at Home with full health."
            else:
                return "You have died and there is no Home area to respawn."
        return None


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

import json
import os
import collections
import random

# Load NPC reactions JSON once at module level
npc_reactions_path = os.path.join(os.path.dirname(__file__), "npc_reactions.json")
NPC_REACTIONS = {}
try:
    with open(npc_reactions_path, "r") as f:
        NPC_REACTIONS = json.load(f)
except Exception as e:
    print(f"Error loading npc_reactions.json: {e}")

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
                return f"The {gang_name} member {member} is hallucinating from the {self.name}. {member} {hallucination}"
            elif effect_type == "gift-giving":
                return f"The {gang_name} member {member} gets covered in glitter and starts compulsively giving gifts!"
            elif effect_type == "friendliness":
                if count == 1:
                    friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("singular", []))
                else:
                    friendlyphrase = random.choice(NPC_REACTIONS.get("possible_friendly_phrases", {}).get("plural", []))
                return f"The {gang_name} member {member} breathes in the {self.name}, and looks unusually cheerful. {member} says, '{friendlyphrase}'"
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

        # Group resisted members
        if resisted:
            count = len(resisted)
            if count == 1:
                messages.append(construct_resist_message(resisted[0], count))
            else:
                member_list = ", ".join(resisted[:-1]) + " and " + resisted[-1] if count > 1 else resisted[0]
                messages.append(f"The {gang_name} members {member_list} resist the hazard effect.")

        return "\n".join(messages) if messages else f"The hazard has no effect on anyone."


class StaticHazard(Hazard):
    def __init__(self, name, description, effect):
        super().__init__(name, description, effect, damage=40, duration=2)  # duration was None permanent static hazards, testing with 2 turns



    def affect_area(self, area):
        """Apply hazard to all gang members in area with grouped results"""
        results = []
        for npc in area.npcs:
            if isinstance(npc, GangMember):
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
    
    def use(self, player):
        """Use hazard item on all gang members with grouped results"""
        
        results = []
        for npc in player.current_area.npcs:
            if isinstance(npc, GangMember):
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


        self.player_starting_items = []  # Initialize this before create_items
        
        self.create_items()
        self.create_areas()
        self.create_objects()
        self.create_npcs()

        self.player = Player(self.areas.get('Home'), self.player_starting_items)
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
        }
        self.is_running = True

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
        
        
        # Add smartphone and watering can to player's starting inventory
        self.player_starting_items = [smartphone, watering_can, gun]  # We'll use this in the Player initialization


    def create_objects(self):
        # Dynamically create and register objects.

        garden = Soil("Garden", "A garden full of plants.")
        
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



    def create_npcs(self):
        """Dynamically create and register NPCs."""
        # NPCs
        Jack = NPC("Jack", "The owner of Jacks Fuel, who may offer valuable intel.")
        self.npcs["Jack"] = Jack

        # Create Bloodhounds gang and members
        bloodhounds_gang = Gang("Bloodhounds")
        bloodhounds_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]

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


        self.add_npc_to_area('JacksFuel', 'Jack')
        

    def game_loop(self):
        print("Welcome to Root Access!")
        print("Type 'help' for a list of commands.\n")
        while self.is_running:
            
            print(f"\nCurrent location: {self.player.current_area.name}")
            command_input = input("> ").strip()
            if not command_input:
                continue
            parts = command_input.split()
            command = parts[0].lower()
            args = parts[1:]
            cmd_entry = self.commands.get(command)
            if cmd_entry:
                output = cmd_entry['handler'](args)
                if output:
                    print(output)
                # After player command, process hazards in current area first
                for obj in list(self.player.current_area.objects):
                    if isinstance(obj, StaticHazard) and obj.active:
                        hazard_result = obj.affect_area(self.player.current_area)
                        if hazard_result:
                            print(hazard_result)
                # Then have gang members in current area attempt to attack player
                gang_members = [npc for npc in self.player.current_area.npcs if isinstance(npc, GangMember)]
                hallucinating_members = []
                normal_attackers = []
                for member in gang_members:
                    # Check if member is hallucinating (has hallucination effect)
                    if any(effect == "hallucinations" for effect in member.active_effects):
                        hallucinating_members.append(member)
                    else:
                        normal_attackers.append(member)

                # Print grouped message for hallucinating members
                if hallucinating_members:
                    gang_name = hallucinating_members[0].gang.name if hallucinating_members else "Gang"
                    if len(hallucinating_members) == len(gang_members):
                        print(f"None of the {gang_name} see you because they are too distracted from the hallucinations.")
                    else:
                        names = ", ".join(member.name for member in hallucinating_members[:-1])
                        if len(hallucinating_members) > 1:
                            names += f" and {hallucinating_members[-1].name}"
                        else:
                            names = hallucinating_members[0].name
                        print(f"The {gang_name} members {names} don't see you because they are too distracted from hallucinating.")

                # Print attack messages for non-hallucinating members
                for attacker in normal_attackers:
                    attack_result = attacker.attack_player(self.player)
                    if attack_result:
                        print(attack_result)
                    # Check if player died and respawn
                    death_message = self.player.check_death_and_respawn(self)
                    if death_message:
                        print(death_message)
                        break
            else:
                print("Unknown command. Type 'help' for a list of commands.")

    def cmd_move(self, args):
        if not args:
            return "Move where? Specify a direction."
        direction = args[0].lower()
        return self.player.move(direction)

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
        return self.player.current_area.describe()

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
            area = self.player.current_area
        else:
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
    


if __name__ == '__main__':
    game = Game()
    game.game_loop()
