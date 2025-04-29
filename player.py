from items import Consumable
from gardening import Seed, Plant

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
