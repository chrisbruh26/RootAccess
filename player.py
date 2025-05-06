from items import Consumable
from gardening import Seed, Plant

class Player:
    def __init__(self):
        self.inventory = []
        self.health = 100
        self.max_health = 100
        self.money = 100
        self.current_area = None
        self.current_sub_area = None  # The sub-area the player is currently in (if any)
        self.active_effects = {}  # Dictionary of effect name -> turns remaining
        self.detected_by = set()  # Set of gangs that have detected the player
        self.hidden = False  # Whether the player is currently hidden
        self.hiding_spot = None  # The hiding spot the player is using
    
    def add_item(self, item):
        self.inventory.append(item)
    
    def remove_item(self, item_name):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item:
            self.inventory.remove(item)
            return item
        return None
    
    def enter_sub_area(self, sub_area_name):
        """Enter a sub-area within the current area."""
        if not self.current_area:
            return False, "You are not in any area."
        
        sub_area = self.current_area.get_sub_area(sub_area_name)
        if not sub_area:
            return False, f"There is no sub-area called '{sub_area_name}' here."
        
        self.current_sub_area = sub_area_name.lower()
        return True, f"You enter the {sub_area.name}."
    
    def exit_sub_area(self):
        """Exit the current sub-area and return to the main area."""
        if not self.current_sub_area:
            return False, "You are not in a sub-area."
        
        sub_area_name = self.current_area.get_sub_area(self.current_sub_area).name
        self.current_sub_area = None
        return True, f"You exit the {sub_area_name} and return to the main area."
    
    def get_current_location_objects(self):
        """Get objects in the player's current location (main area or sub-area)."""
        if self.current_sub_area:
            sub_area = self.current_area.get_sub_area(self.current_sub_area)
            return sub_area.objects if sub_area else []
        else:
            return self.current_area.objects if self.current_area else []
    
    def get_current_location_items(self):
        """Get items in the player's current location (main area or sub-area)."""
        if self.current_sub_area:
            sub_area = self.current_area.get_sub_area(self.current_sub_area)
            return sub_area.items if sub_area else []
        else:
            return self.current_area.items if self.current_area else []
    
    def get_current_location_npcs(self):
        """Get NPCs in the player's current location (main area or sub-area)."""
        if self.current_sub_area:
            sub_area = self.current_area.get_sub_area(self.current_sub_area)
            return sub_area.npcs if sub_area else []
        else:
            return self.current_area.npcs if self.current_area else []
    
    def use_item(self, item_name, game):
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            return False, f"You don't have a {item_name}."
        
