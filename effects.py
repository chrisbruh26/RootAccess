"""
Effects module for Root Access game.
This module defines various effects that can be applied to players and NPCs.
"""

import random

class Effect:
    """Base class for all effects in the game."""
    
    def __init__(self, name, description, duration=3):
        """Initialize an Effect object."""
        self.name = name
        self.description = description
        self.duration = duration
    
    def apply(self, target):
        """Apply the effect to a target."""
        if hasattr(target, 'active_effects'):
            target.active_effects[self.name] = self.duration
            return True, f"Applied {self.name} effect to {target.name if hasattr(target, 'name') else 'target'}."
        return False, "Target cannot have effects applied."
    
    def update(self, target):
        """Update the effect on a target."""
        return False, "Effect has no update behavior."
    
    def remove(self, target):
        """Remove the effect from a target."""
        if hasattr(target, 'active_effects') and self.name in target.active_effects:
            del target.active_effects[self.name]
            return True, f"Removed {self.name} effect from {target.name if hasattr(target, 'name') else 'target'}."
        return False, "Target does not have this effect."


class PlantEffect(Effect):
    """An effect that accelerates plant growth."""
    
    def __init__(self, duration=3):
        """Initialize a PlantEffect object."""
        super().__init__("Plant Growth", "Accelerates plant growth.", duration)
    
    def apply_to_plants(self, plants):
        """Apply the effect to plants."""
        if not plants:
            return False, "No plants to apply effect to."
        
        # Accelerate growth for all plants
        for plant_data in plants:
            plant_data['growth'] += 1
        
        return True, "The plants grow rapidly!"


class SupervisionEffect(Effect):
    """An effect that enhances the player's vision."""
    
    def __init__(self, duration=5):
        """Initialize a SupervisionEffect object."""
        super().__init__("Supervision", "Enhances vision, allowing you to see hidden objects and NPCs.", duration)
    
    def apply(self, player):
        """Apply the effect to the player."""
        result = super().apply(player)
        
        if result[0]:
            # Reveal hidden NPCs and objects in the current area
            hidden_things = []
            
            # Check for hidden NPCs
            if hasattr(player, 'current_area') and hasattr(player.current_area, 'npcs'):
                for npc in player.current_area.npcs:
                    if hasattr(npc, 'hidden') and npc.hidden:
                        hidden_things.append(f"NPC: {npc.name}")
                        npc.hidden = False
            
            # Check for hidden objects
            if hasattr(player, 'current_area') and hasattr(player.current_area, 'objects'):
                for obj in player.current_area.objects:
                    if hasattr(obj, 'hidden') and obj.hidden:
                        hidden_things.append(f"Object: {obj.name}")
                        obj.hidden = False
            
            if hidden_things:
                hidden_str = ", ".join(hidden_things)
                return True, f"Your vision is enhanced! You can now see: {hidden_str}"
            else:
                return True, "Your vision is enhanced, but there's nothing hidden to see."
        
        return result


class HackedPlantEffect(Effect):
    """An effect that causes plants to produce special items."""
    
    def __init__(self, duration=3):
        """Initialize a HackedPlantEffect object."""
        super().__init__("Hacked Plant", "Causes plants to produce special items.", duration)
    
    def apply_to_plants(self, plants):
        """Apply the effect to plants."""
        if not plants:
            return False, "No plants to apply effect to."
        
        # Modify plants to produce special items
        for plant_data in plants:
            plant_data['hacked'] = True
        
        return True, "The plants' DNA has been hacked! They will now produce special items when harvested."


class Substance:
    """A substance that can be consumed for an effect."""
    
    def __init__(self, name, description, effect):
        """Initialize a Substance object."""
        self.name = name
        self.description = description
        self.effect = effect
    
    def consume(self, target):
        """Consume the substance."""
        if self.effect:
            return self.effect.apply(target)
        return False, "The substance has no effect."


class HackedMilk(Substance):
    """A special substance that causes hallucinations."""
    
    def __init__(self):
        """Initialize a HackedMilk object."""
        super().__init__(
            "Hacked Milk",
            "A strange, glowing milk-like substance.",
            HallucinationEffect()
        )


class HallucinationEffect(Effect):
    """An effect that causes hallucinations."""
    
    def __init__(self, duration=5):
        """Initialize a HallucinationEffect object."""
        super().__init__("Hallucination", "Causes visual and auditory hallucinations.", duration)
    
    def apply(self, target):
        """Apply the effect to a target."""
        result = super().apply(target)
        
        if result[0]:
            # Generate random hallucinations
            hallucinations = [
                "You see colorful patterns swirling in the air.",
                "You hear whispers coming from nowhere.",
                "The walls seem to breathe.",
                "Objects appear to melt and reform.",
                "You see shadowy figures at the edge of your vision.",
                "Everything looks like it's made of neon light.",
                "You hear music that isn't there.",
                "The ground feels like it's moving beneath your feet."
            ]
            
            hallucination = random.choice(hallucinations)
            
            return True, f"You experience hallucinations: {hallucination}"
        
        return result
    
    def apply_to_npcs(self, npcs):
        """Apply the effect to NPCs."""
        if not npcs:
            return False, "No NPCs to apply effect to."
        
        # Make NPCs hallucinate
        hallucinating_npcs = []
        for npc in npcs:
            if hasattr(npc, 'active_effects'):
                npc.active_effects[self.name] = self.duration
                hallucinating_npcs.append(npc.name)
        
        if not hallucinating_npcs:
            return False, "No NPCs were affected."
        
        hallucinating_str = ", ".join(hallucinating_npcs)
        
        return True, f"{hallucinating_str} {'are' if len(hallucinating_npcs) > 1 else 'is'} now hallucinating!"


class ConfusionEffect(Effect):
    """An effect that causes confusion."""
    
    def __init__(self, duration=3):
        """Initialize a ConfusionEffect object."""
        super().__init__("Confusion", "Causes confusion and disorientation.", duration)
    
    def apply(self, target):
        """Apply the effect to a target."""
        result = super().apply(target)
        
        if result[0]:
            return True, "You feel confused and disoriented."
        
        return result
    
    def apply_to_npcs(self, npcs):
        """Apply the effect to NPCs."""
        if not npcs:
            return False, "No NPCs to apply effect to."
        
        # Make NPCs confused
        confused_npcs = []
        for npc in npcs:
            if hasattr(npc, 'active_effects'):
                npc.active_effects[self.name] = self.duration
                confused_npcs.append(npc.name)
        
        if not confused_npcs:
            return False, "No NPCs were affected."
        
        confused_str = ", ".join(confused_npcs)
        
        return True, f"{confused_str} {'are' if len(confused_npcs) > 1 else 'is'} now confused!"
