import random
from effects import HallucinationEffect, ConfusionEffect

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

    def __str__(self):
        return f"{self.name} (Damage: {self.damage})"
        
    def use(self, player, game):
        """Use the weapon, handling damage to NPCs and breaking objects."""
        messages = []
        messages.append(f"You use the {self.name}!")
        
        # Check if there are NPCs in the area to target
        if player.current_area and player.current_area.npcs:
            # Get a list of alive NPCs
            alive_npcs = [npc for npc in player.current_area.npcs if hasattr(npc, 'is_alive') and npc.is_alive]
            
            if alive_npcs:
                # Ask player which NPC to attack
                npc_names = [npc.name for npc in alive_npcs]
                npc_list = ", ".join(npc_names)
                messages.append(f"You can target: {npc_list}")
                messages.append("Type the name of the NPC you want to attack, or 'cancel' to stop.")
                
                # Return a special message that the game loop will handle to get player input
                return True, "\n".join(messages), "target_selection", alive_npcs
        
        # Check for breakable objects in the area
        if player.current_area and player.current_area.objects:
            # Find a breakable object that's not already broken
            from objects import VendingMachine
            breakable_objects = [obj for obj in player.current_area.objects 
                                if hasattr(obj, 'break_glass') and not obj.is_broken]
            
            if breakable_objects and random.random() < 0.3:  # 30% chance to break something
                obj = random.choice(breakable_objects)
                method = "shoot" if "gun" in self.name.lower() else "smash"
                
                if isinstance(obj, VendingMachine):
                    result = obj.break_glass(player, method)
                    if result[0]:
                        for item in result[2]:
                            player.current_area.add_item(item)
                        obj.items.clear()
                        messages.append(result[1])
                else:
                    result = obj.break_glass(player, method)
                    if result[0]:
                        messages.append(result[1])
        
        return True, "\n".join(messages)
        
    def attack_npc(self, player, target_npc):
        """Attack a specific NPC with this weapon."""
        messages = []
        
        # Calculate damage (random value between half and full damage)
        damage = random.randint(self.damage // 2, self.damage)
        
        # Apply damage to the target
        if hasattr(target_npc, 'health'):
            target_npc.health -= damage
            
            # Check if target died
            if target_npc.health <= 0:
                target_npc.is_alive = False
                if hasattr(target_npc, 'gang'):
                    target_npc.gang.remove_member(target_npc)
                messages.append(f"You attack {target_npc.name} with your {self.name} for {damage} damage, defeating them!")
            else:
                messages.append(f"You attack {target_npc.name} with your {self.name} for {damage} damage!")
                
                # If target is a gang member, they might become hostile
                if hasattr(target_npc, 'gang') and hasattr(player, 'detected_by'):
                    player.detected_by.add(target_npc.gang)
                    messages.append(f"The {target_npc.gang.name} are now hostile toward you!")
        else:
            # For NPCs without health attribute
            target_npc.is_alive = False
            messages.append(f"You attack and defeat {target_npc.name} with your {self.name}!")
            
        return True, "\n".join(messages)
    
class EffectItem(Item):
    def __init__(self, name, description, value, effect):
        super().__init__(name, description, value)
        self.effect = effect

    def __str__(self):
        return f"{self.name} ({self.effect.name} effect)"

    def use(self, player, game):
        """Use the effect item, applying its effect to NPCs in the current area."""
        messages = []
        affected_npcs = []
        
        messages.append(f"You use the {self.name}!")
        
        # Apply effect to NPCs in the current area
        if player.current_area and player.current_area.npcs:
            for npc in player.current_area.npcs:
                # Skip dead NPCs
                if hasattr(npc, 'is_alive') and not npc.is_alive:
                    continue
                    
                # Apply the effect to the NPC
                if hasattr(npc, 'active_effects'):
                    # Create a new instance of the effect for this NPC
                    effect_copy = type(self.effect)()
                    npc.active_effects.append(effect_copy)
                    affected_npcs.append(npc)

            # Add the effect messages to the NPC coordinator
            if game and game.npc_coordinator:
                game.npc_coordinator.add_effect_messages(affected_npcs, self.effect)
            
            # Add more detailed message about affected NPCs
            if affected_npcs:
                if len(affected_npcs) == 1:
                    messages.append(f"{affected_npcs[0].name} is affected by the {self.effect.name} effect!")
                elif len(affected_npcs) <= 3:
                    npc_names = ", ".join(npc.name for npc in affected_npcs)
                    messages.append(f"{npc_names} are affected by the {self.effect.name} effect!")
                else:
                    messages.append(f"Several NPCs are affected by the {self.effect.name} effect!")
        
        return True, "\n".join(messages)


class SmokeBomb(Item):
    def __init__(self):
        super().__init__("Smoke Bomb", "A device that creates a thick cloud of smoke, allowing for escape.", 30)
        
    def __str__(self):
        return f"{self.name} (Escape tool)"
        
    def use(self, player, game):
        """Use the smoke bomb to escape detection and possibly hide."""
        messages = []
        messages.append(f"You throw the {self.name} on the ground!")
        messages.append("A thick cloud of smoke fills the area!")
        
        # Clear all detection status
        player.detected_by.clear()
        
        # Apply confusion effect to all NPCs in the area
        affected_npcs = []
        for npc in player.current_area.npcs:
            if hasattr(npc, 'active_effects') and npc.is_alive:
                # Create a confusion effect
                confusion = ConfusionEffect()
                confusion.duration = 2  # Lasts for 2 turns
                confusion.remaining_turns = 2
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
                
                # Reset detection status for gang members
                if hasattr(npc, 'has_detected_player'):
                    npc.has_detected_player = False
                    npc.detection_cooldown = 3
        
        # Add effect messages to the NPC coordinator
        if affected_npcs and game and game.npc_coordinator:
            game.npc_coordinator.add_effect_messages(affected_npcs, ConfusionEffect())
            
        # Check if there are hiding spots in the area
        hiding_spots = [obj for obj in player.current_area.objects 
                       if hasattr(obj, 'hide') and not (hasattr(obj, 'is_occupied') and obj.is_occupied)]
        
        if hiding_spots:
            # Suggest hiding spots to the player
            spot_names = [spot.name for spot in hiding_spots]
            messages.append(f"You could hide in: {', '.join(spot_names)}")
            messages.append("Use 'hide [spot name]' to hide quickly!")
        else:
            messages.append("There are no hiding spots here, but the NPCs have lost track of you for now.")
            
        # Remove the smoke bomb from inventory after use
        player.inventory.remove(self)
        
        return True, "\n".join(messages)
        
        
class Decoy(Item):
    def __init__(self):
        super().__init__("Tech Decoy", "A small device that creates noise and light to distract NPCs.", 25)
        
    def __str__(self):
        return f"{self.name} (Distraction tool)"
        
    def use(self, player, game):
        """Use the decoy to distract NPCs and potentially escape detection."""
        messages = []
        messages.append(f"You activate the {self.name} and toss it away from you!")
        messages.append("It starts emitting flashing lights and beeping sounds.")
        
        # Chance to lose detection from each gang
        gangs_distracted = []
        for gang in list(player.detected_by):
            if random.random() < 0.7:  # 70% chance to distract each gang
                player.detected_by.remove(gang)
                gangs_distracted.append(gang.name)
                
                # Reset detection status for gang members
                for npc in player.current_area.npcs:
                    if hasattr(npc, 'gang') and npc.gang == gang and hasattr(npc, 'has_detected_player'):
                        npc.has_detected_player = False
                        npc.detection_cooldown = 2
        
        if gangs_distracted:
            messages.append(f"The {', '.join(gangs_distracted)} seem distracted by the decoy and have lost track of you!")
        
        # Apply a brief confusion effect to some NPCs
        affected_npcs = []
        for npc in player.current_area.npcs:
            if hasattr(npc, 'active_effects') and npc.is_alive and random.random() < 0.5:  # 50% chance
                # Create a confusion effect
                confusion = ConfusionEffect()
                confusion.duration = 1  # Lasts for 1 turn
                confusion.remaining_turns = 1
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
        
        # Add effect messages to the NPC coordinator
        if affected_npcs and game and game.npc_coordinator:
            game.npc_coordinator.add_effect_messages(affected_npcs, ConfusionEffect())
            
        # Remove the decoy from inventory after use
        player.inventory.remove(self)
        
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
