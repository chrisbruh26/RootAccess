import random
from effects import HallucinationEffect, ConfusionEffect
from items import Weapon, EffectItem

# ----------------------------- #
# RANDOM EVENTS SYSTEM          #
# ----------------------------- #

class RandomEventManager:
    """Manages random events in the game."""
    def __init__(self, game):
        self.game = game
        self.event_cooldowns = {}  # Track cooldowns for specific events
        
    def trigger_random_event(self):
        """Trigger a random event in the current area."""
        # List of possible random events
        events = [
            self.event_rival_gang_appears,
            self.event_tech_malfunction,
            self.event_plant_mutation,
            self.event_mass_confusion
        ]
        
        # Choose and trigger a random event
        event = random.choice(events)
        event()
        
    def event_rival_gang_appears(self, target_gang=None, target_member=None, forced=False):
        """
        Random event: A rival gang appears and starts a fight.
        
        Args:
            target_gang: Optional specific gang to target (for player-triggered events)
            target_member: Optional specific gang member to target (for player-triggered events)
            forced: If True, bypass normal restrictions like area checks
        """
        # Only trigger in areas that make sense (not Home) unless forced
        if not forced and self.game.player.current_area.name == "Home":
            return
            
        # Get all gangs in the area
        gangs_present = set()
        for npc in self.game.player.current_area.npcs:
            if hasattr(npc, 'gang'):
                gangs_present.add(npc.gang.name)
                
        # If there's a target gang, make sure it's in the area
        if target_gang and target_gang.name not in gangs_present:
            return "The target gang is not in this area."
                
        # If there's only one or no gangs, bring in a rival (or if forced)
        if forced or len(gangs_present) <= 1:
            # Choose a rival gang that's not already present
            if target_gang:
                # Use the specified target gang's rivals
                available_gangs = [gang for gang_name, gang in self.game.gangs.items() 
                                  if gang_name != target_gang.name]
            else:
                # Choose any gang not already present
                available_gangs = [gang for gang_name, gang in self.game.gangs.items() 
                                  if gang_name not in gangs_present]
            
            if not available_gangs:
                return "No available rival gangs."
                
            rival_gang = random.choice(available_gangs)
            
            # Create 1-3 rival gang members
            num_rivals = random.randint(1, 3)
            
            # Gang member name lists
            bloodhounds_names = ["Buck", "Bubbles", "Boop", "Noodle", "Flop", "Squirt", "Squeaky", "Gus-Gus", "Puddles", "Muffin", "Binky", "Beep-Beep"]
            crimson_vipers_names = ["Vipoop", "Snakle", "Rattlesnop", "Pythirt", "Anaceaky", "Cobrus-brus", "Lizuddles", "Viperino", "Slitherpuff", "Hissypants", "Slinker", "Snakester"]
            
            # Choose appropriate name list
            if rival_gang.name == "Crimson Vipers":
                name_list = crimson_vipers_names
            else:
                name_list = bloodhounds_names
                
            # Add rival gang members
            for i in range(num_rivals):
                if name_list:
                    name = random.choice(name_list)
                    name_list.remove(name)
                else:
                    # Generate a random name if we run out
                    name = f"{rival_gang.name[0]}-{random.randint(1, 100)}"
                    
                # Create and add the gang member
                from npc_behavior import GangMember
                rival = GangMember(name, f"A member of the {rival_gang.name} named {name}.", rival_gang)
                self.game.player.current_area.add_npc(rival)
                
                # Give them weapons and items
                gun = Weapon("Gun", "A standard firearm.", 50, 20)
                rival.add_item(gun)
                
                # 50% chance to have an effect item
                if random.random() < 0.5:
                    effect_item = EffectItem("Confusion Ray", "A device that emits waves that confuse the target.", 60, ConfusionEffect())
                    rival.add_item(effect_item)
            
            event_message = f"\n*** GANG EVENT: A group of {rival_gang.name} members has appeared! ***"
            print(event_message)
            
            # Make them immediately hostile to other gangs
            for npc in self.game.player.current_area.npcs:
                if hasattr(npc, 'gang') and npc.gang != rival_gang:
                    # If there's a specific target, prioritize attacking them
                    if target_member and npc == target_member:
                        for rival_member in [n for n in self.game.player.current_area.npcs if hasattr(n, 'gang') and n.gang == rival_gang]:
                            attack_result = rival_member.attack_npc(target_member)
                            if attack_result:
                                print(attack_result)
                                break
                        break
                    # Otherwise attack any member of the target gang
                    elif target_gang and npc.gang == target_gang:
                        for rival_member in [n for n in self.game.player.current_area.npcs if hasattr(n, 'gang') and n.gang == rival_gang]:
                            attack_result = rival_member.attack_npc(npc)
                            if attack_result:
                                print(attack_result)
                                break
                        break
                    # Or just attack any other gang member
                    else:
                        for rival_member in [n for n in self.game.player.current_area.npcs if hasattr(n, 'gang') and n.gang == rival_gang]:
                            attack_result = rival_member.attack_npc(npc)
                            if attack_result:
                                print(attack_result)
                                break
                        break
            
            return event_message
        
        return "There are already multiple gangs in this area."
        
    def event_tech_malfunction(self):
        """Random event: Technology in the area malfunctions, causing distractions."""
        # Check if there are any tech objects in the area
        tech_objects = [obj for obj in self.game.player.current_area.objects 
                       if hasattr(obj, 'is_electronic') and obj.is_electronic]
        
        if not tech_objects:
            return "No tech objects to malfunction."
            
        # Choose a random tech object
        tech_object = random.choice(tech_objects)
        
        # Generate a malfunction effect
        effects = [
            f"The {tech_object.name} suddenly sparks and emits a loud noise!",
            f"The {tech_object.name} starts flashing with bright lights!",
            f"The {tech_object.name} makes a series of strange beeping sounds!"
        ]
        
        effect = random.choice(effects)
        event_message = f"\n*** RANDOM EVENT: TECH MALFUNCTION ***\n{effect}"
        print(event_message)
        
        # Distract NPCs - 50% chance for each NPC to be affected
        affected_npcs = []
        for npc in self.game.player.current_area.npcs:
            if random.random() < 0.5 and hasattr(npc, 'active_effects'):
                # Create a temporary confusion effect
                confusion = ConfusionEffect()
                confusion.remaining_turns = 1  # Only lasts 1 turn
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
                
        # If player was detected, 30% chance to lose detection
        if self.game.player.detected_by and random.random() < 0.3:
            # Choose one random gang to lose detection
            if self.game.player.detected_by:
                gang_to_forget = random.choice(list(self.game.player.detected_by))
                self.game.player.detected_by.remove(gang_to_forget)
                print(f"The {gang_to_forget.name} seem distracted by the malfunction and have lost track of you!")
        
        return event_message
        
    def event_plant_mutation(self):
        """Random event: Plants in the area mutate and release strange effects."""
        # Check if there are any soil plots with plants
        soil_plots = [obj for obj in self.game.player.current_area.objects 
                     if hasattr(obj, 'plants') and obj.plants]
        
        if not soil_plots:
            return "No plants to mutate."
            
        # Choose a random soil plot
        soil = random.choice(soil_plots)
        
        # Choose a random plant
        if not soil.plants:
            return "No plants in the soil plot."
            
        plant = random.choice(soil.plants)
        
        # Generate a mutation effect
        effects = [
            f"The {plant.name} suddenly grows to twice its size!",
            f"The {plant.name} releases a cloud of spores!",
            f"The {plant.name} starts glowing with an eerie light!",
            f"The {plant.name} makes a strange rustling sound!"
        ]
        
        effect = random.choice(effects)
        event_message = f"\n*** RANDOM EVENT: PLANT MUTATION ***\n{effect}"
        print(event_message)
        
        # Apply random effects to NPCs
        for npc in self.game.player.current_area.npcs:
            if hasattr(npc, 'active_effects') and random.random() < 0.4:  # 40% chance
                # Choose between hallucination and confusion
                if random.random() < 0.5:
                    effect = HallucinationEffect()
                else:
                    effect = ConfusionEffect()
                    
                npc.active_effects.append(effect)
                print(f"{npc.name} is affected by the plant mutation!")
                
        # 20% chance to heal the player a bit
        if random.random() < 0.2:
            heal_amount = random.randint(5, 15)
            self.game.player.health = min(self.game.player.max_health, self.game.player.health + heal_amount)
            print(f"You feel rejuvenated by the plant's energy! (+{heal_amount} health)")
        
        return event_message
        
    def event_mass_confusion(self):
        """Random event: A wave of confusion sweeps through the area."""
        # Only trigger if there are NPCs in the area
        if not self.game.player.current_area.npcs:
            return "No NPCs in the area."
            
        event_message = "\n*** RANDOM EVENT: MASS CONFUSION ***\nA strange wave of energy pulses through the area!"
        print(event_message)
        
        # Apply confusion to most NPCs
        affected_npcs = []
        for npc in self.game.player.current_area.npcs:
            if hasattr(npc, 'active_effects') and random.random() < 0.7:  # 70% chance
                confusion = ConfusionEffect()
                npc.active_effects.append(confusion)
                affected_npcs.append(npc)
                
        # If NPCs were affected, add effect messages
        if affected_npcs and self.game.npc_coordinator:
            self.game.npc_coordinator.add_effect_messages(affected_npcs, ConfusionEffect())
            
        return event_message
