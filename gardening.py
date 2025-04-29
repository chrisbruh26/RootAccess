import random
from items import Item

# ----------------------------- #
# GARDENING SYSTEM              #
# ----------------------------- #

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
