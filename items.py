import random

# ----------------------------- #
# ITEM CLASSES                  #
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
        self.effects = []  # List of effects this weapon can apply

    def __str__(self):
        return f"{self.name} (Damage: {self.damage})"
        
    def add_effect(self, effect):
        """Add an effect to this weapon."""
        self.effects.append(effect)
        
    def use(self, player, game):
        """Use the weapon, applying its effects to NPCs in the current area."""
        messages = []
        
        # Basic attack message
        messages.append(f"You use the {self.name}!")
        
        # Apply effects to NPCs in the current area
        if self.effects and player.current_area and player.current_area.npcs:
            for effect in self.effects:
                # Create a copy of the effect for each NPC
                for npc in player.current_area.npcs:
                    # Skip dead NPCs
                    if hasattr(npc, 'is_alive') and not npc.is_alive:
                        continue
                        
                    # Apply the effect to the NPC
                    if hasattr(npc, 'active_effects'):
                        # Create a new instance of the effect for this NPC
                        effect_copy = type(effect)()
                        npc.active_effects.append(effect_copy)
                        messages.append(f"{npc.name} is affected by {effect.name}!")
        
        # Check for breakable objects in the area
        if player.current_area and player.current_area.objects:
            # Find a breakable object that's not already broken
            from objects import VendingMachine
            breakable_objects = [obj for obj in player.current_area.objects 
                               if hasattr(obj, 'break_glass') and not obj.is_broken]
            
            if breakable_objects and random.random() < 0.3:  # 30% chance to break something
                # Choose a random breakable object
                obj = random.choice(breakable_objects)
                
                # Determine the method based on weapon type
                method = "shoot" if "gun" in self.name.lower() else "smash"
                
                # Break the object
                if isinstance(obj, VendingMachine):
                    result = obj.break_glass(player, method)
                    if result[0]:
                        # Add spilled items to the area
                        for item in result[2]:
                            player.current_area.add_item(item)
                        # Clear the vending machine's items
                        obj.items.clear()
                        messages.append(result[1])
                else:
                    result = obj.break_glass(player, method)
                    if result[0]:
                        messages.append(result[1])
        
        return True, "\n".join(messages)


class Consumable(Item):
    def __init__(self, name, description, value, health_restore):
        super().__init__(name, description, value)
        self.health_restore = health_restore

    def __str__(self):
        return f"{self.name} (Restores: {self.health_restore} health)"
    

class TechItem(Item):
    def __init__(self, name, description, value, tech_type):
        super().__init__(name, description, value)
        self.tech_type = tech_type


class USBStick(TechItem):
    def __init__(self, name, description, value):
        super().__init__(name, description, value, "USB")
        # should probably have self.data = None or something to hold the data. USB sticks will usually have plant genetic code on them to hack the soil, maybe intel 
        self.data = None
        self.data_type = None  # Type of data on the USB stick (e.g., "plant genetic code", "intel")

    def __str__(self):
        return f"{self.name} (Data Type: {self.data_type})"
    
    def use(self, player, game):
        """Use the USB stick to hack the soil or access."""
        # Import here to avoid circular imports
        from gardening import SoilPlot
        
        # check if there is soil in the area by checking if isinstance of SoilPlot
        soil = next((obj for obj in player.current_area.objects if isinstance(obj, SoilPlot)), None)
        if not soil:
            return False, "There's no soil here to hack."
        # check for data on USB stick
        if not self.data:
            return False, "The USB stick is empty. You need to find data to hack the soil."
        # check if data is compatible with soil
        if self.data != "plant genetic code":
            return False, "This USB stick doesn't contain the right data to hack the soil."
        # make the soil produce a plant with special effects

        # cause the soil to produce a plant with effects based on the data on the USB stick
