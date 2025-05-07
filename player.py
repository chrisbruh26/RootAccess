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
        # First check for exact item name match
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        
        # If not found, check if it's a hybrid item by looking for partial matches
        if not item:
            # Check if any hybrid items contain this name as part of their name
            item = next((i for i in self.inventory if hasattr(i, 'is_hybrid') and 
                        (item_name.lower() in i.name.lower() or 
                         (hasattr(i, 'parent1') and hasattr(i.parent1, 'name') and item_name.lower() == i.parent1.name.lower()) or
                         (hasattr(i, 'parent2') and hasattr(i.parent2, 'name') and item_name.lower() == i.parent2.name.lower()))), None)
        
        # If still not found, try a more flexible search for hybrid items
        if not item:
            # Check if any hybrid items contain this name as part of their parent names
            item = next((i for i in self.inventory if hasattr(i, 'is_hybrid') and 
                        ((hasattr(i, 'parent1') and hasattr(i.parent1, 'name') and item_name.lower() in i.parent1.name.lower()) or
                         (hasattr(i, 'parent2') and hasattr(i.parent2, 'name') and item_name.lower() in i.parent2.name.lower()))), None)
        
        if not item:
            return False, f"You don't have a {item_name}."
        
        # Check if this is a hybrid item
        is_hybrid = hasattr(item, 'is_hybrid') and item.is_hybrid
        
        # Handle seeds (planting) - special case for both regular and hybrid seeds
        if isinstance(item, Seed) or (is_hybrid and hasattr(item, 'crop_type') and hasattr(item, 'growth_time')):
            # Check if there's soil in the current location (area or sub-area)
            objects = self.get_current_location_objects()
            soil = next((obj for obj in objects if hasattr(obj, 'add_plant')), None)
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
            if result[0] and not is_hybrid:
                # Only remove the item if it's not a hybrid
                self.inventory.remove(item)
            return result
        
        # Handle consumables
        if isinstance(item, Consumable) and not is_hybrid:
            self.health = min(self.max_health, self.health + item.health_restore)
            self.inventory.remove(item)
            return True, f"You use the {item.name} and restore {item.health_restore} health."
        
        # Handle hybrid items with multiple functionalities
        if is_hybrid:
            # Determine what functionalities this hybrid has
            has_weapon = hasattr(item, 'damage')
            has_consumable = hasattr(item, 'health_restore')
            has_effect = hasattr(item, 'effect')
            
            # If it has multiple functionalities, ask the player what to do
            if (has_weapon and has_consumable) or (has_weapon and has_effect) or (has_consumable and has_effect):
                # Set up hybrid choice mode in the game
                game.hybrid_item = item
                game.in_hybrid_choice_mode = True
                
                # Create appropriate prompt based on functionalities
                if has_weapon and has_consumable:
                    return True, f"Do you want to attack with or consume {item.name}? (Type 'attack' or 'consume')", "hybrid_choice"
                elif has_weapon and has_effect:
                    return True, f"Do you want to attack with or apply the effect of {item.name}? (Type 'attack' or 'effect')", "hybrid_choice"
                elif has_consumable and has_effect:
                    return True, f"Do you want to consume or apply the effect of {item.name}? (Type 'consume' or 'effect')", "hybrid_choice"
            else:
                # If it only has one functionality, use that directly
                if has_weapon:
                    # Get a list of alive NPCs
                    alive_npcs = [npc for npc in self.current_area.npcs if hasattr(npc, 'is_alive') and npc.is_alive]
                    
                    if alive_npcs:
                        # Set up targeting mode
                        game.targeting_weapon = item
                        game.targeting_npcs = alive_npcs
                        
                        # Show available targets
                        npc_names = [npc.name for npc in alive_npcs]
                        npc_list = ", ".join(npc_names)
                        return True, f"You can target: {npc_list}\nType the name of the NPC you want to attack, or 'cancel' to stop.", "target_selection", alive_npcs
                    else:
                        return False, "There are no NPCs to attack here."
                elif has_consumable:
                    # Use as consumable
                    if hasattr(item, 'consume'):
                        return item.consume(self, game)
                    else:
                        self.health = min(self.max_health, self.health + item.health_restore)
                        return True, f"You consume the {item.name} and restore {item.health_restore} health."
                elif has_effect:
                    # Use for effect
                    if hasattr(item, 'apply_effect'):
                        return item.apply_effect(self, game)
                    else:
                        effect_name = item.effect.name if hasattr(item.effect, 'name') else "unknown"
                        return True, f"You use the {item.name} and apply the {effect_name} effect."
        
        # Handle weapons and other items with use method
        if hasattr(item, 'use'):
            return item.use(self, game)
        
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
