import random

# ----------------------------- #
# GARDENING SYSTEM              #
# ----------------------------- #

class Seed:
    def __init__(self, name, description, crop_type, value, growth_time=3):
        # Import here to avoid circular imports
        from items import Item
        
        # Initialize as an Item
        self.name = name
        self.description = description
        self.value = value
        
        # Seed-specific properties
        self.crop_type = crop_type
        self.growth_time = growth_time  # Number of turns until fully grown
    
    def __str__(self):
        return f"{self.name} ({self.crop_type})"


class Plant:
    def __init__(self, name, description, crop_type, value, growth_stage=0, max_growth=3):
        # Initialize basic properties
        self.name = name
        self.description = description
        self.value = value
        
        # Plant-specific properties
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
        # Import here to avoid circular imports
        from items import Item
        
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
    
        # -------------- #
        # SPECIAL PLANTS #
        # -------------- #
class SpecialPlant(Plant):
    """Base class for all special plants with unique behaviors."""
    def __init__(self, name, music_preference, allergen_level):
        super().__init__(name)
        self.is_special = True
        self.mood = "neutral"  # Mood of the plant
        self.music_preference = music_preference  # Genre they like
        self.allergen_level = allergen_level  # Severity of computer allergy effects

    def react_to_music(self, genre):
        """All special plants react to music."""
        if genre == self.music_preference:
            return f"{self.name} is thriving with {genre} music!"
        else:
            return f"{self.name} is uncomfortable with {genre} and mutates strangely."

    def trigger_allergy(self, computer):
        """All special plants have an effect on computers."""
        return f"{computer} sneezes violently as {self.name} spreads allergens nearby!"
    

class SnatcherSprout(SpecialPlant):
    """A mischievous plant that steals nearby items."""
    def __init__(self, music_preference, allergen_level):
        super().__init__("Snatcher Sprout", music_preference, allergen_level)

    def steal_item(self, target_item, npc):
        return f"{self.name} yanks {target_item} from {npc}! \"Give me back my wallet!\""
    

import random

class QuantumCactus(SpecialPlant):
    """A chaotic plant that teleports randomly."""
    def __init__(self, music_preference, allergen_level):
        super().__init__("Quantum Cactus", music_preference, allergen_level)

    def teleport(self, location_list):
        new_location = random.choice(location_list)
        return f"{self.name} teleports to {new_location} unexpectedly!"

from datetime import datetime

class TikTokVine(SpecialPlant):
    """A prophetic plant that announces the real-world time and commands NPCs."""
    def __init__(self, music_preference, allergen_level):
        super().__init__("TikTok Vine", music_preference, allergen_level)

    def announce_time(self):
        current_time = datetime.now().strftime("%I:%M %p on %A, %B %d, %Y")
        return f"{self.name} says: \"The time is {current_time}. Follow the prophecy!\""

import random

class Chatterbush(SpecialPlant):
    """A sentient plant that talks randomly."""
    def __init__(self, music_preference, allergen_level):
        super().__init__("Chatterbush", music_preference, allergen_level)
        self.dialogue_pool = [
            "Why do humans only grow one head? Weak genetics!",
            "Plants invented photosynthesis before it was cool.",
            "My roots heard a secret about the vending machine gang..."
        ]

    def talk(self):
        return f"{self.name} whispers: \"{random.choice(self.dialogue_pool)}\""


class BiohackerBloom(SpecialPlant):
    """A plant designed to hack computers and force digital allergies."""
    def __init__(self, music_preference, allergen_level):
        super().__init__("Biohacker Bloom", music_preference, allergen_level)

    def hack_computer(self, computer):
        return f"{self.name} infects {computer}, causing data corruption and system sneezing!"

            # --------------------------------- #
            # INITIALIZE SPECIAL PLANTS EXAMPLE #
            # --------------------------------- #
'''

snatcher = SnatcherSprout("Rock", 3)
quantum = QuantumCactus("Metal", 4)
tiktok = TikTokVine("Pop", 2)
chatter = Chatterbush("Indie", 3)
biohacker = BiohackerBloom("Synthwave", 5)

# Example interactions
print(snatcher.steal_item("USB stick", "NPC Bob"))
print(quantum.teleport(["Garden", "Vending Machine Alley", "Underground Bunker"]))
print(tiktok.announce_time())
print(chatter.talk())
print(biohacker.hack_computer("Mainframe PC"))
print(tiktok.react_to_music("Rock"))  # Shows plant reacting negatively to genre mismatch








'''

            





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
    
    def water_plants(self, watering_can=None, substance=None, actor_name="You"):
        """
        Water all plants in the soil plot.
        
        Args:
            watering_can: The watering can to use (required)
            substance: Optional substance to add to the water
            actor_name: Name of the actor doing the watering (for message formatting)
            
        Returns:
            Tuple of (success, message)
        """
        # Check if there are plants to water
        if not self.plants:
            return False, "There are no plants to water here."
        
        # Check if a watering can is provided
        if not watering_can:
            return False, f"{actor_name} need a watering can to water plants."
        
        # Check if the watering can has water
        if watering_can.current_water <= 0:

            return False, f"The {watering_can.name} is empty. It needs to be filled first."
        
        # Water the plants
        results = []
        for plant in self.plants:
            result = plant.water(substance)
            
            # Format the message to use the actor's name
            if result[0]:  # If watering was successful
                message = result[1].replace("You water", f"{actor_name} water")
                results.append(message)
        
        # Use water from the watering can
        water_used = min(len(self.plants), watering_can.current_water)
        watering_can.current_water -= water_used
        
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
    
class WateringCan:
    def __init__(self, name="Watering Can", description="A can for watering plants.", capacity=10):
        self.name = name
        self.description = description
        self.capacity = capacity
        self.current_water = capacity  # Start full
    
    def fill(self):
        """Fill the watering can to its maximum capacity."""
        self.current_water = self.capacity
        return True, f"You fill the {self.name} to its maximum capacity."
    
    def water(self, target, substance=None):
        """
        Use the watering can to water a target.
        
        Args:
            target: The target to water (soil plot or plant)
            substance: Optional substance to add to the water
            
        Returns:
            Tuple of (success, message)
        """
        # Check if the watering can has water
        if self.current_water <= 0:
            self.fill()
            return False, f"The {self.name} has been automatically refilled."
        
        # Handle different target types
        if hasattr(target, 'water_plants'):
            # Target is a soil plot
            return target.water_plants(self, substance)
        elif hasattr(target, 'water'):
            # Target is a plant
            result = target.water(substance)
            if result[0]:
                self.current_water -= 1
            return result
        else:
            return False, f"You can't water that with the {self.name}."
    
    def __str__(self):
        return f"{self.name} ({self.current_water}/{self.capacity} water)"
