"""
Enhanced Gardening System for Root Access v2

This module provides an enhanced gardening system that integrates with the component-based
architecture while maintaining flexibility and scalability. It supports hybrid items
and allows for complex interactions between gardening elements.
"""

import random
import copy
from typing import Dict, List, Any, Optional, Callable, Union, Tuple, Set

# Import the component system
from components import (
    Entity, Component, 
    SeedComponent, PlantComponent, SoilComponent, WateringCanComponent,
    EffectComponent, UsableComponent
)

# ----------------------------- #
# GARDENING EFFECT CLASSES      #
# ----------------------------- #

class GardeningEffect:
    """Base class for effects that can be applied to plants."""
    
    def __init__(self, name="Effect", description="A mysterious effect."):
        self.name = name
        self.description = description
        self.duration = 3  # Default duration in turns
        self.remaining_turns = 3
    
    def apply(self, target):
        """Apply this effect to a target."""
        pass
    
    def update(self):
        """Update this effect each turn."""
        if self.remaining_turns > 0:
            self.remaining_turns -= 1
            return True
        return False
    
    def __str__(self):
        return self.name


class GrowthBoostEffect(GardeningEffect):
    """Effect that boosts plant growth."""
    
    def __init__(self, boost_amount=1):
        super().__init__(name="Growth Boost", description="Accelerates plant growth.")
        self.boost_amount = boost_amount
    
    def apply(self, target):
        """Apply growth boost to a plant."""
        if hasattr(target, 'get_component') and target.get_component('plant'):
            plant_component = target.get_component('plant')
            plant_component.growth_stage += self.boost_amount
            return True, f"The {target.name} grows visibly!"
        return False, f"The {target.name} cannot be affected by growth boost."


class YieldBoostEffect(GardeningEffect):
    """Effect that increases the yield of a plant."""
    
    def __init__(self, yield_multiplier=1.5):
        super().__init__(name="Yield Boost", description="Increases harvest yield.")
        self.yield_multiplier = yield_multiplier
    
    def apply(self, target):
        """Apply yield boost to a plant."""
        if hasattr(target, 'get_component') and target.get_component('plant'):
            # This will be used when harvesting
            return True, f"The {target.name} looks more bountiful!"
        return False, f"The {target.name} cannot be affected by yield boost."


class QualityBoostEffect(GardeningEffect):
    """Effect that improves the quality of a plant."""
    
    def __init__(self, quality_bonus=2):
        super().__init__(name="Quality Boost", description="Improves harvest quality.")
        self.quality_bonus = quality_bonus
    
    def apply(self, target):
        """Apply quality boost to a plant."""
        if hasattr(target, 'get_component') and target.get_component('plant'):
            # This will be used when harvesting
            return True, f"The {target.name} looks healthier and more vibrant!"
        return False, f"The {target.name} cannot be affected by quality boost."


class HybridGrowthEffect(GardeningEffect):
    """Special effect for hybrid plants that gives them unique properties."""
    
    def __init__(self, special_property="mysterious"):
        super().__init__(
            name="Hybrid Growth", 
            description=f"Gives the plant {special_property} properties."
        )
        self.special_property = special_property
    
    def apply(self, target):
        """Apply hybrid growth effect to a plant."""
        if hasattr(target, 'get_component') and target.get_component('plant'):
            # Mark the plant as having special properties
            target.add_tag(f"special_{self.special_property}")
            return True, f"The {target.name} develops {self.special_property} properties!"
        return False, f"The {target.name} cannot be affected by hybrid growth."


# ----------------------------- #
# ENHANCED GARDENING COMPONENTS #
# ----------------------------- #

class EnhancedSeedComponent(SeedComponent):
    """Enhanced seed component with additional functionality."""
    
    def __init__(self, owner=None, plant_type="generic", growth_time=5, special_effects=None):
        super().__init__(owner, plant_type, growth_time, special_effects)
        self.effects = []  # List of effects that will be transferred to the plant
        self.genetic_traits = []  # Special traits that affect the grown plant
        self.hybridization_history = []  # Track hybridization history
    
    def add_effect(self, effect):
        """Add an effect to this seed."""
        if effect not in self.effects:
            self.effects.append(effect)
            return True
        return False
    
    def add_genetic_trait(self, trait):
        """Add a genetic trait to this seed."""
        if trait not in self.genetic_traits:
            self.genetic_traits.append(trait)
            return True
        return False


class EnhancedPlantComponent(PlantComponent):
    """Enhanced plant component with additional functionality."""
    
    def __init__(self, owner=None, plant_type="generic", growth_stage=0, max_growth=3, harvest_item=None):
        super().__init__(owner, plant_type, growth_stage, max_growth, harvest_item)
        self.effects = []  # List of effects applied to this plant
        self.watering_history = []  # Track what substances were used to water this plant
        self.genetic_traits = []  # Special traits inherited from the seed
        self.quality = 1.0  # Base quality multiplier
        self.yield_multiplier = 1.0  # Base yield multiplier
    
    def add_effect(self, effect):
        """Add an effect to this plant."""
        if effect not in self.effects:
            self.effects.append(effect)
            effect.apply(self.owner)
            return True
        return False
    
    def add_genetic_trait(self, trait):
        """Add a genetic trait to this plant."""
        if trait not in self.genetic_traits:
            self.genetic_traits.append(trait)
            return True
        return False


class EnhancedSoilComponent(SoilComponent):
    """Enhanced soil component with additional functionality."""
    
    def __init__(self, owner=None, fertility=1.0, capacity=5):
        super().__init__(owner, fertility, capacity)
        self.soil_quality = 1.0  # Base soil quality
        self.nutrients = 100  # Nutrient level
        self.moisture = 50  # Moisture level
        self.contaminants = []  # List of contaminants in the soil
    
    def add_nutrient(self, amount):
        """Add nutrients to the soil."""
        self.nutrients = min(100, self.nutrients + amount)
        return True, f"The {self.owner.name} now has {self.nutrients}% nutrients."
    
    def add_moisture(self, amount):
        """Add moisture to the soil."""
        self.moisture = min(100, self.moisture + amount)
        return True, f"The {self.owner.name} now has {self.moisture}% moisture."
    
    def add_contaminant(self, contaminant):
        """Add a contaminant to the soil."""
        if contaminant not in self.contaminants:
            self.contaminants.append(contaminant)
            return True, f"The {self.owner.name} has been contaminated with {contaminant}."
        return False, f"The {self.owner.name} is already contaminated with {contaminant}."


class EnhancedWateringCanComponent(WateringCanComponent):
    """Enhanced watering can component with additional functionality."""
    
    def __init__(self, owner=None, water_capacity=5, current_water=5):
        super().__init__(owner, water_capacity, current_water)
        self.water_quality = 1.0  # Base water quality
        self.additives = []  # List of additives in the water
    
    def add_additive(self, additive):
        """Add an additive to the water."""
        if additive not in self.additives:
            self.additives.append(additive)
            return True, f"You add {additive.name} to the {self.owner.name}."
        return False, f"The {self.owner.name} already contains {additive.name}."


# ----------------------------- #
# GARDENING FACTORY FUNCTIONS   #
# ----------------------------- #

def create_seed(name, description, plant_type, growth_time=3, value=5, effects=None, genetic_traits=None):
    """
    Create a seed entity with enhanced functionality.
    
    Args:
        name: Name of the seed
        description: Description of the seed
        plant_type: Type of plant this seed grows into
        growth_time: Number of turns until fully grown
        value: Value of the seed
        effects: List of effects that will be transferred to the grown plant
        genetic_traits: List of genetic traits that will be transferred to the grown plant
        
    Returns:
        A seed Entity
    """
    seed = Entity(name, description)
    seed.add_tag("item")
    seed.add_tag("seed")
    seed.value = value
    
    # Add enhanced seed component
    seed_component = EnhancedSeedComponent(
        plant_type=plant_type,
        growth_time=growth_time
    )
    seed.add_component("seed", seed_component)
    
    # Add effects
    if effects:
        for effect in (effects if isinstance(effects, list) else [effects]):
            seed_component.add_effect(effect)
    
    # Add genetic traits
    if genetic_traits:
        for trait in (genetic_traits if isinstance(genetic_traits, list) else [genetic_traits]):
            seed_component.add_genetic_trait(trait)
    
    # Add usable component with a function that handles planting
    def use_seed(seed, user, game):
        if not hasattr(user, 'current_area') or not user.current_area:
            return False, "You need to be in an area to plant a seed."
        
        # Find a soil plot in the current area
        soil = None
        for obj in user.current_area.objects:
            if obj.has_tag("soil"):
                soil = obj
                break
        
        if not soil:
            return False, "There's no soil here to plant in."
        
        # Get the soil component
        soil_component = soil.get_component("soil")
        if not soil_component:
            return False, "This soil can't be planted in."
        
        # Plant the seed
        result = plant_seed(seed, soil)
        
        return result
    
    seed.add_component("usable", UsableComponent(use_function=use_seed))
    
    return seed


def create_plant(name, description, plant_type, growth_stage=0, max_growth=3, effects=None, genetic_traits=None, value=10):
    """
    Create a plant entity with enhanced functionality.
    
    Args:
        name: Name of the plant
        description: Description of the plant
        plant_type: Type of plant
        growth_stage: Current growth stage
        max_growth: Maximum growth stage
        effects: List of effects applied to this plant
        genetic_traits: List of genetic traits for this plant
        value: Base value of the plant
        
    Returns:
        A plant Entity
    """
    plant = Entity(name, description)
    plant.add_tag("object")
    plant.add_tag("plant")
    plant.value = value
    
    # Add enhanced plant component
    plant_component = EnhancedPlantComponent(
        plant_type=plant_type,
        growth_stage=growth_stage,
        max_growth=max_growth
    )
    plant.add_component("plant", plant_component)
    
    # Add effects
    if effects:
        for effect in (effects if isinstance(effects, list) else [effects]):
            plant_component.add_effect(effect)
    
    # Add genetic traits
    if genetic_traits:
        for trait in (genetic_traits if isinstance(genetic_traits, list) else [genetic_traits]):
            plant_component.add_genetic_trait(trait)
    
    return plant


def create_soil_plot(name="Soil Plot", description="A plot of soil for planting.", fertility=1.0, capacity=5):
    """
    Create a soil plot entity with enhanced functionality.
    
    Args:
        name: Name of the soil plot
        description: Description of the soil plot
        fertility: Base fertility of the soil (affects growth speed)
        capacity: Maximum number of plants this soil can hold
        
    Returns:
        A soil plot Entity
    """
    soil = Entity(name, description)
    soil.add_tag("object")
    soil.add_tag("soil")
    
    # Add enhanced soil component
    soil.add_component("soil", EnhancedSoilComponent(
        fertility=fertility,
        capacity=capacity
    ))
    
    return soil


def create_watering_can(name="Watering Can", description="A can for watering plants.", capacity=10, current_water=None):
    """
    Create a watering can entity with enhanced functionality.
    
    Args:
        name: Name of the watering can
        description: Description of the watering can
        capacity: Water capacity
        current_water: Current water level (defaults to full)
        
    Returns:
        A watering can Entity
    """
    watering_can = Entity(name, description)
    watering_can.add_tag("item")
    watering_can.add_tag("watering_can")
    watering_can.value = 15
    
    # Add enhanced watering can component
    watering_can.add_component("watering_can", EnhancedWateringCanComponent(
        water_capacity=capacity,
        current_water=capacity if current_water is None else current_water
    ))
    
    # Add usable component with a function that handles watering
    def use_watering_can(can, user, game):
        if not hasattr(user, 'current_area') or not user.current_area:
            return False, "You need to be in an area to water plants."
        
        # Find a soil plot or plant in the current area
        target = None
        for obj in user.current_area.objects:
            if obj.has_tag("soil") or obj.has_tag("plant"):
                target = obj
                break
        
        if not target:
            return False, "There's nothing here to water."
        
        # Get the watering can component
        watering_can_component = can.get_component("watering_can")
        if not watering_can_component:
            return False, "This can't be used for watering."
        
        # Water the target
        return water_target(can, target)
    
    watering_can.add_component("usable", UsableComponent(use_function=use_watering_can))
    
    return watering_can


def create_fertilizer(name, description, effects, value=15):
    """
    Create a fertilizer entity that can be used on plants or soil.
    
    Args:
        name: Name of the fertilizer
        description: Description of the fertilizer
        effects: List of effects this fertilizer applies
        value: Value of the fertilizer
        
    Returns:
        A fertilizer Entity
    """
    fertilizer = Entity(name, description)
    fertilizer.add_tag("item")
    fertilizer.add_tag("gardening_tool")
    fertilizer.add_tag("fertilizer")
    fertilizer.value = value
    
    # Store effects
    fertilizer.effects = effects.copy() if isinstance(effects, list) else [effects]
    
    # Add usable component with a function that handles fertilizing
    def use_fertilizer(fert, user, game):
        if not hasattr(user, 'current_area') or not user.current_area:
            return False, "You need to be in an area to use fertilizer."
        
        # Find a plant or soil in the current area
        target = None
        for obj in user.current_area.objects:
            if obj.has_tag("plant"):
                target = obj
                break
            elif obj.has_tag("soil") and not target:
                target = obj
        
        if not target:
            return False, "There are no plants or soil here to fertilize."
        
        # Apply effects to the target
        if target.has_tag("plant"):
            plant_component = target.get_component("plant")
            if not plant_component:
                return False, f"The {target.name} can't be fertilized."
            
            messages = []
            for effect in fert.effects:
                # Add effect to the plant
                if plant_component.add_effect(effect):
                    result = effect.apply(target)
                    if result[0]:
                        messages.append(result[1])
            
            if not messages:
                return False, f"The {target.name} already has all these effects."
            
            return True, "\n".join([f"You apply {fert.name} to the {target.name}."] + messages)
        
        elif target.has_tag("soil"):
            soil_component = target.get_component("soil")
            if not soil_component:
                return False, f"The {target.name} can't be fertilized."
            
            # Add nutrients to the soil
            result = soil_component.add_nutrient(25)  # Add 25% nutrients
            
            return True, f"You apply {fert.name} to the {target.name}. {result[1]}"
    
    fertilizer.add_component("usable", UsableComponent(use_function=use_fertilizer))
    
    return fertilizer


# ----------------------------- #
# GARDENING UTILITY FUNCTIONS   #
# ----------------------------- #

def plant_seed(seed, soil):
    """
    Plant a seed in soil.
    
    Args:
        seed: The seed Entity to plant
        soil: The soil Entity to plant in
        
    Returns:
        Tuple of (success, message)
    """
    # Get the soil component
    soil_component = soil.get_component("soil")
    if not soil_component:
        return False, f"The {soil.name} can't be planted in."
    
    # Check if the soil is full
    if len(soil_component.plants) >= soil_component.capacity:
        return False, f"The {soil.name} is full. You can't plant anything else here."
    
    # Get the seed component
    seed_component = seed.get_component("seed")
    if not seed_component:
        # If this is a hybrid item, check if it has a seed component
        if seed.is_hybrid and any(parent.has_component("seed") for parent in seed.parent_entities):
            # Create a custom message for hybrid items
            parent_names = seed.get_parent_names()
            plant_message = f"You plant a {seed.name} in the {soil.name}."
            
            # Create a new plant based on the seed
            plant = create_plant(
                f"{seed.name} Plant", 
                f"A strange plant growing from a {seed.name}.",
                "hybrid"
            )
            
            # Make it a hybrid plant
            plant.is_hybrid = True
            plant.parent_entities = seed.parent_entities.copy()
            
            # Transfer components from the hybrid seed to the plant
            for component_type, component in seed.components.items():
                if component_type != "seed" and not plant.has_component(component_type):
                    # Clone the component and add it to the plant
                    new_component = component.clone()
                    plant.add_component(component_type, new_component)
            
            # Add the plant to the soil
            soil_component.plants.append(plant)
            
            # Remove the seed from inventory if it's in the player's inventory
            if hasattr(seed, 'owner') and seed.owner:
                inventory = seed.owner.get_component('inventory')
                if inventory:
                    inventory.remove_item(seed)
            
            return True, plant_message
        
        return False, f"The {seed.name} isn't a valid seed."
    
    # Create a new plant
    plant_name = f"{seed_component.plant_type.capitalize()} Seedling"
    plant_desc = f"A young {seed_component.plant_type} plant just starting to grow."
    
    plant = create_plant(
        name=plant_name,
        description=plant_desc,
        plant_type=seed_component.plant_type,
        growth_stage=0,
        max_growth=seed_component.growth_time,
        effects=seed_component.effects,
        genetic_traits=seed_component.genetic_traits,
        value=seed.value * 2
    )
    
    # If the seed is a hybrid, make the plant a hybrid too
    if seed.is_hybrid:
        plant.is_hybrid = True
        plant.parent_entities = seed.parent_entities.copy()
        
        # Add a hybrid growth effect
        plant_component = plant.get_component("plant")
        hybrid_effect = HybridGrowthEffect("hybrid")
        plant_component.add_effect(hybrid_effect)
    
    # Add the plant to the soil
    soil_component.plants.append(plant)
    
    # Remove the seed from inventory if it's in the player's inventory
    if hasattr(seed, 'owner') and seed.owner:
        inventory = seed.owner.get_component('inventory')
        if inventory:
            inventory.remove_item(seed)
    
    return True, f"You plant the {seed.name} in the {soil.name}."


def water_target(watering_can, target, substance=None):
    """
    Water a target (soil plot or plant) with a watering can.
    
    Args:
        watering_can: The watering can Entity
        target: The target Entity (soil or plant)
        substance: Optional substance to add to the water
        
    Returns:
        Tuple of (success, message)
    """
    # Get the watering can component
    watering_can_component = watering_can.get_component("watering_can")
    if not watering_can_component:
        return False, f"The {watering_can.name} can't be used for watering."
    
    # Check if the watering can has water
    if watering_can_component.current_water <= 0:
        return False, f"The {watering_can.name} is empty. It needs to be filled first."
    
    # Handle different target types
    if target.has_tag("soil"):
        # Target is a soil plot
        return water_soil_plot(watering_can, target, substance)
    elif target.has_tag("plant"):
        # Target is a plant
        return water_plant(watering_can, target, substance)
    else:
        return False, f"You can't water the {target.name}."


def water_soil_plot(watering_can, soil, substance=None):
    """
    Water all plants in a soil plot.
    
    Args:
        watering_can: The watering can Entity
        soil: The soil plot Entity
        substance: Optional substance to add to the water
        
    Returns:
        Tuple of (success, message)
    """
    # Get the soil component
    soil_component = soil.get_component("soil")
    if not soil_component:
        return False, f"The {soil.name} can't be watered."
    
    # Check if there are plants to water
    if not soil_component.plants:
        # If no plants, just add moisture to the soil
        soil_component.add_moisture(25)  # Add 25% moisture
        
        # Get the watering can component
        watering_can_component = watering_can.get_component("watering_can")
        watering_can_component.current_water -= 1
        
        return True, f"You water the {soil.name}, increasing its moisture level."
    
    # Get the watering can component
    watering_can_component = watering_can.get_component("watering_can")
    
    # Water the plants
    results = []
    for plant in soil_component.plants:
        # Check if we have enough water
        if watering_can_component.current_water <= 0:
            results.append(f"The {watering_can.name} runs out of water.")
            break
        
        # Water the plant
        result = water_plant(watering_can, plant, substance, decrement_water=False)
        if result[0]:  # If watering was successful
            results.append(result[1])
            watering_can_component.current_water -= 1
    
    # Also add moisture to the soil
    soil_component.add_moisture(10)  # Add 10% moisture
    
    if not results:
        return False, f"No plants could be watered."
    
    return True, "\n".join(results)


def water_plant(watering_can, plant, substance=None, decrement_water=True):
    """
    Water a single plant.
    
    Args:
        watering_can: The watering can Entity
        plant: The plant Entity
        substance: Optional substance to add to the water
        decrement_water: Whether to decrement the water in the watering can
        
    Returns:
        Tuple of (success, message)
    """
    # Get the plant component
    plant_component = plant.get_component("plant")
    if not plant_component:
        return False, f"The {plant.name} can't be watered."
    
    # Get the watering can component
    watering_can_component = watering_can.get_component("watering_can")
    
    # Check if the plant is fully grown
    if plant_component.growth_stage >= plant_component.max_growth:
        return False, f"The {plant.name} is already fully grown and ready to harvest."
    
    # Check if the watering can has water
    if watering_can_component.current_water <= 0:
        return False, f"The {watering_can.name} is empty. It needs to be filled first."
    
    # Track what was used to water the plant
    if substance:
        plant_component.watering_history.append(substance)
        
        # Apply effects from the substance to the plant
        if hasattr(substance, 'effects'):
            for effect in substance.effects:
                plant_component.add_effect(effect)
        
        message = f"You water the {plant.name} with {substance.name}."
    else:
        # Check if the watering can has additives
        if hasattr(watering_can_component, 'additives') and watering_can_component.additives:
            additives_str = ", ".join(a.name for a in watering_can_component.additives)
            message = f"You water the {plant.name} with water containing {additives_str}."
            
            # Apply effects from the additives to the plant
            for additive in watering_can_component.additives:
                if hasattr(additive, 'effects'):
                    for effect in additive.effects:
                        plant_component.add_effect(effect)
        else:
            message = f"You water the {plant.name} with regular water."
    
    # Water the plant, which advances growth by a stage
    plant_component.growth_stage += 1
    
    # We don't track parent-child relationships in the current system
    # So we'll skip the soil fertility boost for now
    
    # Decrement water if needed
    if decrement_water:
        watering_can_component.current_water -= 1
    
    if plant_component.growth_stage >= plant_component.max_growth:
        return True, f"{message} It's now fully grown and ready to harvest!"
    else:
        return True, f"{message} It grows visibly before your eyes!"


def harvest_plant(plant):
    """
    Harvest a plant to get an item.
    
    Args:
        plant: The plant Entity to harvest
        
    Returns:
        Tuple of (success, message, harvested_item)
    """
    # Get the plant component
    plant_component = plant.get_component("plant")
    if not plant_component:
        return False, f"The {plant.name} can't be harvested."
    
    # Check if the plant is ready to harvest
    if plant_component.growth_stage < plant_component.max_growth:
        return False, f"The {plant.name} is not ready to harvest yet."
    
    # Create a harvested item
    harvested_name = f"{plant_component.plant_type.capitalize()}"
    harvested_desc = f"A freshly harvested {plant_component.plant_type}."
    
    harvested_item = Entity(harvested_name, harvested_desc)
    harvested_item.add_tag("item")
    harvested_item.add_tag("food")
    harvested_item.value = plant.value
    
    # Apply yield boost effects if any
    for effect in plant_component.effects:
        if isinstance(effect, YieldBoostEffect):
            harvested_item.value = int(harvested_item.value * effect.yield_multiplier)
    
    # Apply quality boost effects if any
    quality_bonus = 0
    for effect in plant_component.effects:
        if isinstance(effect, QualityBoostEffect):
            quality_bonus += effect.quality_bonus
    
    if quality_bonus > 0:
        harvested_item.value += quality_bonus
        harvested_desc += f" It looks particularly high quality."
    
    # If this is a hybrid plant, make the harvested item a hybrid too
    if plant.is_hybrid:
        harvested_item.is_hybrid = True
        harvested_item.parent_entities = plant.parent_entities.copy()
        harvested_desc += f" It has unusual properties from its hybrid nature."
    
    # Transfer effects to the harvested item
    if plant_component.effects:
        # Create an effect component for the harvested item
        effect_component = EffectComponent()
        harvested_item.add_component("effect", effect_component)
        
        # Transfer effects
        effect_component.effects = plant_component.effects.copy()
        
        # Update description
        effect_names = ", ".join(effect.name for effect in plant_component.effects)
        harvested_item.description += f" It seems to have been affected by: {effect_names}."
    
    # Make the item usable (edible)
    def eat_item(item, user, game):
        # Apply effects when eaten
        if hasattr(item, 'get_component') and item.get_component('effect'):
            effect_component = item.get_component('effect')
            for effect in effect_component.effects:
                if hasattr(user, 'active_effects'):
                    user.active_effects.append(effect)
        
        # Heal the user if they have health
        if hasattr(user, 'get_component') and user.get_component('health'):
            health_component = user.get_component('health')
            health_amount = 5 + quality_bonus  # Base healing + quality bonus
            health_component.heal(health_amount)
            return True, f"You eat the {item.name} and feel refreshed. (+{health_amount} health)"
        
        return True, f"You eat the {item.name}. It's delicious!"
    
    harvested_item.add_component("usable", UsableComponent(use_function=eat_item))
    
    return True, f"You harvest the {plant.name} and get a {harvested_item.name}.", harvested_item


# ----------------------------- #
# PREDEFINED GARDENING ITEMS    #
# ----------------------------- #

def create_tomato_seed():
    """Create a tomato seed."""
    return create_seed(
        name="Tomato Seed",
        description="A seed that grows into a tomato plant.",
        plant_type="tomato",
        growth_time=3,
        value=5
    )


def create_carrot_seed():
    """Create a carrot seed."""
    return create_seed(
        name="Carrot Seed",
        description="A seed that grows into a carrot plant.",
        plant_type="carrot",
        growth_time=2,
        value=4
    )


def create_potato_seed():
    """Create a potato seed."""
    return create_seed(
        name="Potato Seed",
        description="A seed that grows into a potato plant.",
        plant_type="potato",
        growth_time=4,
        value=3
    )


def create_basic_fertilizer():
    """Create a basic fertilizer."""
    return create_fertilizer(
        name="Basic Fertilizer",
        description="A simple fertilizer that boosts plant growth.",
        effects=[GrowthBoostEffect(boost_amount=1)],
        value=10
    )


def create_premium_fertilizer():
    """Create a premium fertilizer."""
    return create_fertilizer(
        name="Premium Fertilizer",
        description="A high-quality fertilizer that significantly improves plant growth and yield.",
        effects=[
            GrowthBoostEffect(boost_amount=2),
            YieldBoostEffect(yield_multiplier=2.0)
        ],
        value=25
    )


def create_quality_booster():
    """Create a quality booster."""
    return create_fertilizer(
        name="Quality Booster",
        description="A special solution that improves the quality of harvested crops.",
        effects=[QualityBoostEffect(quality_bonus=5)],
        value=20
    )


def create_hybrid_seed(parent_seed1, parent_seed2):
    """
    Create a hybrid seed by combining two parent seeds.
    
    Args:
        parent_seed1: The first parent seed
        parent_seed2: The second parent seed
        
    Returns:
        A hybrid seed Entity
    """
    # Get the seed components
    seed_component1 = parent_seed1.get_component("seed")
    seed_component2 = parent_seed2.get_component("seed")
    
    if not seed_component1 or not seed_component2:
        return None
    
    # Create a new hybrid seed
    hybrid_name = f"Hybrid {seed_component1.plant_type.capitalize()}-{seed_component2.plant_type.capitalize()} Seed"
    hybrid_desc = f"A hybrid seed created by crossing {seed_component1.plant_type} and {seed_component2.plant_type}."
    
    hybrid_seed = create_seed(
        name=hybrid_name,
        description=hybrid_desc,
        plant_type=f"hybrid_{seed_component1.plant_type}_{seed_component2.plant_type}",
        growth_time=max(seed_component1.growth_time, seed_component2.growth_time) - 1,  # Slightly faster growth
        value=parent_seed1.value + parent_seed2.value,
        effects=[HybridGrowthEffect(f"{seed_component1.plant_type}-{seed_component2.plant_type}")]
    )
    
    # Make it a hybrid
    hybrid_seed.is_hybrid = True
    hybrid_seed.parent_entities = [parent_seed1, parent_seed2]
    
    # Combine effects from both parents
    hybrid_seed_component = hybrid_seed.get_component("seed")
    if hasattr(seed_component1, 'effects'):
        for effect in seed_component1.effects:
            hybrid_seed_component.add_effect(copy.deepcopy(effect))
    
    if hasattr(seed_component2, 'effects'):
        for effect in seed_component2.effects:
            hybrid_seed_component.add_effect(copy.deepcopy(effect))
    
    # Combine genetic traits from both parents
    if hasattr(seed_component1, 'genetic_traits'):
        for trait in seed_component1.genetic_traits:
            hybrid_seed_component.add_genetic_trait(trait)
    
    if hasattr(seed_component2, 'genetic_traits'):
        for trait in seed_component2.genetic_traits:
            hybrid_seed_component.add_genetic_trait(trait)
    
    return hybrid_seed
