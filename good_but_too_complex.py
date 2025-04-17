import random

# --- Core Classes ---

class Item:
    def __init__(self, name, description, value=0):
        self.name = name
        self.description = description
        self.hacked = False
        self.value = value

    def __str__(self):
        return self.name


class Gang:
    def __init__(self, name):
        self.name = name
        self.members = []
        self.names = ["Buck", "Bubbles", "Blaze", "Bandit", "Buster"]  # Example names

    def create_members(self, count):
        for i in range(count):
            member_name = self.names[i % len(self.names)]  # Cycle through names
            member = GangMember(self, member_name)
            self.members.append(member)


class WaterType(Item):
    def __init__(self, name, description, effect=None):
        super().__init__(name, description)
        self.effect = effect


class WateringCan(Item):
    def __init__(self, name="watering can", description="A watering can for plants"):
        super().__init__(name, description)
        self.current_water_type = None  # Keep track of the current water type
        self.water_types = {
            "normal": WaterType("Normal Water", "Regular water", None),
            "hacked milk": WaterType("Hacked Milk", "Hacked milk with special properties", "supervision"),
            "Psychedelic Rainwater": WaterType("Psychedelic Rainwater", "Rainwater infused with experimental drugs. Warning: may cause falling objects", "falling objects"),
            "turnip juice": WaterType("Turnip Juice", "Juice from a turnip, rumored to turn people invisible", "invisibility")
        }
        self.possible_water_types = list(self.water_types.keys())  # Added this to track available water types

    def set_water_type(self, water_type_name):
        if water_type_name in self.water_types:
            self.current_water_type = self.water_types[water_type_name]
            return True
        return False

    def get_water_description(self):
        if self.current_water_type:
            return f"{self.current_water_type.description} (Effect: {self.current_water_type.effect or 'none'})"
        return "The watering can is empty."


class Seed(Item):
    def __init__(self, name, description):
        super().__init__(name, description)
        self.mutation = None


class Fertilizer(Item):
    def __init__(self, name, description, effect):
        super().__init__(name, description)
        self.effect = effect


class Crop(Item):
    def __init__(self, name, description, effect=None):
        super().__init__(name, description)
        self.effect = effect
        if effect:
            effect_descriptions = {
                "supervision": "reveals hidden items in the area",
                "falling objects": "causes objects to fall from the sky"
            }
            desc = effect_descriptions.get(effect, effect)
            self.description = f"{description.split('.')[0]} that {desc} when eaten."


class Plant:
    GROWTH_STAGES = [
        "seed", 
        "sprout",
        "small plant",
        "mature plant",
        "ready to harvest"
    ]

    def __init__(self, name, description, hacked=False):
        self.name = name
        self.description = description
        self.hacked = hacked
        self.growth_stage = 0
        self.water_count = 0
        self.water_history = []  # Track water types used
        self.current_effects = []  # Track active effects

    def water(self, water_type):
        self.water_count += 1
        self.water_history.append(water_type)
        
        # Apply water type effects (replace any existing effect)
        if hasattr(water_type, 'effect') and water_type.effect:
            self.current_effects = [water_type.effect]
            
        if self.water_count >= 2 and self.growth_stage < len(self.GROWTH_STAGES)-1:
            self.growth_stage += 1
            self.water_count = 0
            return f"The {self.name} grows into a {self.GROWTH_STAGES[self.growth_stage]}!"
        return f"You water the {self.name} with {water_type.name}."

    def harvest(self):
        if self.growth_stage == len(self.GROWTH_STAGES)-1:
            base_name = self.name.replace(' plant', '')
            if self.current_effects:
                effect = self.current_effects[-1]  # Use most recent effect
                return Crop(base_name, f"A {base_name} enhanced with {effect}", effect)
            return Crop(base_name, f"A fresh {base_name}")
        return None
    
    def check_special_effects(self):
        """Check if plant has any special effects from watering"""
        effects = []
        for water_type in self.water_history:
            if isinstance(water_type, str) and water_type != "normal":
                effects.append(water_type)
            elif hasattr(water_type, 'effect') and water_type.effect:
                effects.append(water_type.effect)
        return effects

    def status(self):
        stage = self.GROWTH_STAGES[self.growth_stage]
        effects = self.check_special_effects()
        effect_str = f", Effects: {', '.join(effects)}" if effects else ""
        return f"{self.name} ({stage}, Hacked: {'Yes' if self.hacked else 'No'}{effect_str})"
    

# RANDOM EVENT IDEAS:
# random events like GTA, cars falling from the sky, stuff blowing up

class random_event():
    def __init__(self, name, description, effect):
        self.name = name
        self.description = description
        self.effect = effect


class Tech():
    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value

class Data():
    def __init__(self, name, description, datatype, contents, value):
        self.name = name
        self.description = description
        self.datatype = datatype
        self.contents = contents # info inside a file, like a text file, or a plant's genetic code
        self.value = value # how much money the data would sell for on the black market or to individual NPCs
        # datatypes include: encrypted/non-encrypted file, code, program, notes
        # downloading data to smartphone/other tech means adding contents to the device's files, programs, etc

class Gadget(Tech):
    def __init__(self, name, description, gadgettype, value):
        super().__init__(name, description, gadgettype, value)

class Smartphone(Tech): # make sure tech can be in player's inventory
    def __init__(self):
        super().__init__("Smartphone", "A high-tech device with various apps and functions", 2000)

        self.files = [] # files the player can add, read, or delete
        self.apps = [] # apps the player can use
        self.hacked = False # has this device been hacked
        self.hacked = [] # hacking abilities this device has


    def add_files(self, data):
        self.files.append(data) # maybe I should make a special type of item that is digital data
        print(f"Added {data.name} to the smartphone")
        # add data objects to the smartphone
        

    def home_screen(self):
        print("Home Screen:")
        print("1. Garden management")
        print("2. Hacks")
        print("3. Random Events")
        print("4. Black Market")
        print("5. Files")
        command = input("Which app do you want to access? ")
        if command == "1":
            self.garden_management()
        elif command == "3":
            self.random_events()
        elif command == "4":
            self.black_market()
        elif command == "5" or command == "Files":
            self.files_app()
    
    def hacks(self, player):
        print("\n=== Hacking App ===")
        print("Available hacks:")
        print("1. Spawn Robotic Cow")
        print("2. Get Data")
        print("3. Hazards")
        
        # Spawn robotic cow if not already present
        if not any(npc.name == "Robotic Cow" for npc in player.current_area.npcs):
            player.current_area.npcs.append(NPC("Robotic Cow", "A robotic cow that can be hacked for milk production, among other things"))
            print("\nA Robotic Cow appears in the area!")
        
        command = input("\nSelect hack (1/2) or type command: ").strip().lower()
        
        if command == "2" or "get data" in command:
            if not any(npc.name == "Robotic Cow" for npc in player.current_area.npcs):
                print("No Robotic Cow found to hack!")
                return
                
            print("\nAccessing Robotic Cow systems...")
            Robotic_cow_data = Data(
                "Robotic Cow Data", 
                "Data extracted from robotic cow systems",
                "encrypted_file",
                "Data contents:\nBetween nowhere and nowhere else.\nLong, quiet stretch—don't miss the turn.\n\nSystem ID: COW-ROBO-42",
                750  # Black market value
            )
            self.add_files(Robotic_cow_data)
            print("\nSuccess! Downloaded Robotic Cow Data to your smartphone.")
            player.completed_tasks.add("read_robotic_cow_data")
            game.check_event_triggers()  # Check if this triggers any area reveals - not scalable method, might stick to calling this in other places
    
    def files_app(self):
        if not self.files:
            print("\nFiles App: No files available")
            return
            
        print("\n=== Files App ===")
        for i, file in enumerate(self.files):
            print(f"{i+1}. {file.name} ({file.datatype})")
            
        while True:
            command = input("\nSelect file (1-{}) or 'back': ".format(len(self.files))).strip().lower()
            if command == 'back':
                return
            if command.isdigit() and 1 <= int(command) <= len(self.files):
                selected = self.files[int(command)-1]
                print(f"\n=== {selected.name} ===")
                print(f"Type: {selected.datatype}")
                print(f"Value: ${selected.value}")
                print("\nContents:")
                print(selected.contents)
            else:
                print("Invalid selection. Try again.")
    
    def Garden_Management(self):
        pass
        # add garden management app to smartphone
        # access files containing plant data
        # add new plants to garden
        # hacking info, like genetically modified plant code



        # digital information should be added to the smartphone somehow, like instead of adding items to player inventory, add it to the smartphone's data
        # it uses the Item class but I realized it needs to be able to "hold items" or something so that it can contain digital info
        # maybe create a new class for digital items or something

class Weapon(Item):
    def __init__(self, name, description, damage):
        super().__init__(name, description)
        self.damage = damage

    def use(self, target):
        if target and isinstance(target, GangMember):
            target.health -= self.damage
            result = f"You attack the {target.gang.name} member with {self.name} for {self.damage} damage!"
            if target.health <= 0:
                result += f"\n{target.die()}"
            return result
        return "No valid target to attack!"

class Consumable(Item):
    def __init__(self, name, description, effect):
        super().__init__(name, description)
        self.effect = effect # health regeneration, damage boost, etc. Could be customizable and have different effects, harvestable with gardening and hybdrid creation like ACNH flowers



class Weapon(Item):
    def __init__(self, name, description, damage):
        super().__init__(name, description)
        self.damage = damage

    def use(self, target):
        if target and isinstance(target, GangMember):
            target.health -= self.damage
            result = f"You attack the {target.gang.name} member with {self.name} for {self.damage} damage!"
            if target.health <= 0:
                result += f"\n{target.die()}"
            return result
        return "No valid target to attack!"



class Effect:
    """Represents a hazard effect with duration and properties"""
    def __init__(self, name, description, duration=3, stackable=False):
        self.name = name
        self.description = description
        self.duration = duration
        self.stackable = stackable
        self.remaining_turns = duration

    def update(self):
        """Decrement remaining turns and return True if expired"""
        self.remaining_turns -= 1
        return self.remaining_turns <= 0

    def __str__(self):
        return f"{self.name}"


class GangMember:
    def __init__(self, gang):
        self.gang = gang
        self.health = 100
        self.name = f"{gang.name} Member"
        gang.members.append(self)
        self.items = []
        self.detection_chance = 0.05  # Base 5% chance to detect
        self.has_detected_player = False
        self.detection_cooldown = 0
        self.active_effects = []  # List of Effect objects
        self.hazard_resistance = 0.5  # 50% chance to resist effects

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
        return item

    def list_contents(self):
        return ", ".join(item.name for item in self.items) if self.items else "nothing"
    
    def apply_hazard_effect(self, hazard):
        """Apply a hazard effect to this gang member"""
        if random.random() < self.hazard_resistance:
            return f"The {self.gang.name} member {self.name} resists the {hazard.name} effect!"
            
        effect = Effect(
            name=hazard.effect,
            description=hazard.description,
            stackable=False
        )
        self.active_effects.append(effect)
        return f"The {self.gang.name} member {self.name} is affected by {hazard.name} ({effect})"
    def clear_effects(self):
        """Clear all active hazard effects"""
        self.active_effects = []

    def die(self):
        if self.health <= 0:
            self.gang.members.remove(self)
            return f"The {self.gang.name} member {self.name} has been defeated!"
        
    def attack_player(self, player):
        # Check hazard effects first
        for effect in self.active_effects:
            if effect.name == "hallucinations":
                return f"The {self.gang.name} member {self.name} is so high that they don't see you."
            if effect.name == "friendliness":
                return f"The {self.gang.name} member {self.name} smiles at you warmly." # add random friendliness outcomes here as well as other places where it would take effect
            if effect.name == "gift-giving" and self.items:
                gift = random.choice(self.items)
                player.inventory.append(gift)
                self.items.remove(gift)
                return f"The {self.gang.name} member {self.name} gives you {gift.name} as a gift!"
                
                
        # Normal detection logic
        if not player.hidden and (self.has_detected_player or random.random() < self.detection_chance):
            self.has_detected_player = True
            player.detected_by.add(self.gang)
            
            if self.items:
                weapon = next((i for i in self.items if isinstance(i, Weapon)), None)
                damage = weapon.damage if weapon else 1
                player.health -= damage
                result = f"The {self.gang.name} member {self.name} spots and attacks you for {damage} damage!"
                if player.health <= 0:
                    result += "\nYou have been defeated!"
                return result
            return f"The {self.gang.name} member {self.name} spots you and threatens you but has no weapon!"
        
        if player.hidden:
            self.has_detected_player = False
            return f"The {self.gang.name} member {self.name} looks around but doesn't see you."
        return f"The {self.gang.name} member {self.name} doesn't notice you." # add specific name here

    def update_effects(self):
        """Update all active effects and remove expired ones"""
        self.active_effects = [effect for effect in self.active_effects if not effect.update()]


class NPC:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.relationship = 0
        self.items = []
        self.vendor = False


    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)

    def buy(self, item, player):
        if item.price > player.money:
            return f"You don't have enough money to buy {item.name}."
        player.money -= item.price
        self.remove_item(item.name)
        player.add_item(item)
        return f"You bought {item.name} for {item.price} dollars."
    
    def sell(self, item, player):
        if item not in player.items:
            return f"You don't have {item.name} to sell."
        player.inventory.remove(item)

    def talk(self, player):
        if self.name == "Jack":
            if self.relationship == 0:
                print( f"{self.name} says: Hey, you look like someone who knows their way around a garden. Think you could help me out?")
                self.relationship = 1 # player has met Jack
                response = input("Do you ask about the job? Yes/no ")
                if response == "yes":
                    print(f"{self.name} says: Alright, I've got a job for you. Bring me a supervision carrot. You bring me one, I'll give you info about a Bloodhounds hideout.")
                    player.active_tasks.add("supervision_carrot")
                elif response == "no":
                    print(f"{self.name} says: Suit Yourself. ")
                else:
                    print(f"{self.name} says: huh?" )


            # IF PLAYER AND JACK KNOW EACH OTHER 
            elif self.relationship >= 1:
                if "supervision_carrot" in player.active_tasks: 
                    for item in player.inventory:
                        if item.name == "carrot":
                            if hasattr(item, 'effect') and item.effect:
                                if item.effect == "supervision":
                                    print(f"{self.name} says: Got something for me? ")
                                    give = input("Do you give Jack the supervision carrot? ")
                                    if give == "yes": 
                                        player.inventory.remove(item)
                                        self.add_item(item)
                                        print(f"You gave Jack the supervision carrot.")
                                        player.active_tasks.remove("supervision_carrot")
                                        player.completed_tasks.add("supervision_carrot")
                                        print(f"{self.name} says: Alright, I've got the info you need. The Bloodhounds have an operation going on at the abandoned farm. They've got genetically modified plants, experimental tech, hacking equipment, everything. \nIf you can get past the members, you can get the data. You'll advance your own garden-hacking skills in no time. Oh, and you might want to take this USB stick. It'll help you get what you need. ")
                                        player.inventory.append(Item("USB stick", "A USB stick, possibly useful for downloading data", 500))
                

                # if player has already given Jack the supervision carrot
                else:
                    print(f"{self.name} says: What's up?") # more dialogue and tasks in the future 


class HackingTool(Item):
    def __init__(self, name, description, effect):
        super().__init__(name, description)
        self.effect = effect

    def use_on(self, npc):
        if npc.is_gang_member:
            return f"You used {self.name} on {npc.name}. {self.effect}"
        else:
            return f"{npc.name} doesn't seem affected by the {self.name}."

class GameObject:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __str__(self):
        return self.name
    



# Hazard Classes
class Hazard:
    def __init__(self, name, description, effect, damage, duration=None):
        self.name = name
        self.description = description
        self.effect = effect
        self.damage = damage
        self.active = True
        self.duration = duration  # None means permanent, number is turns remaining
        self.remaining_turns = duration

    def update(self):
        """Decrement duration and deactivate if expired"""
        if self.duration is not None:
            self.remaining_turns -= 1
            if self.remaining_turns <= 0:
                self.active = False
        return self.active

    def group_results(self, results):
        """Group hazard results by effect status with proper grammar and interesting details"""
        affected = []
        resisted = []
        gang_name = None
        member_names = {}  # Store member names and their individual results

        possible_hallucinations = [
            "sees pink elephants dancing!",
            "starts singing 'I Will Survive' at the top of their lungs!",
            "mumbles something about a carrot god commanding them.",
            "believes they're in a video game.",
            "thinks their friends are cartoon characters.",
            "sees the walls melting.",
            "claims to hear voices from the plants.",
            "starts talking to inanimate objects.",
            "believes they're a superhero.",
            "thinks they're a chicken and starts clucking.",
            "recites Shakespearean sonnets.",
            "believes they're a giant, walking eggplant.",
            "twirls around on their tiptoes as if they're a ballerina wearing a tutu.",
            "starts singing 'The Wheels on the Bus' with a bunch of made-up actions.",
            "tries to carry objects by licking them like a goat",
            "puts on a deep, monotone voice, stating,\n 'The FitnessGram PACER Test is a multistage aerobic capacity test that measures a student's ability...' and then runs back and forth across the warehouse.",
            "skips and hops around the room singing '1234! 1234! LA LA LA LA! 1234! 1234!' The safe is what these numbers are for",
        ]
        
        possible_friendly_phrases = [
            "I feel like I'm walking on sunshine!",
            "Wow, you smell great! Did you already find the awesome secret USB in the filing cabinet? Its a game-changer, just saying.",
            "Have you checked out the secret vault in the container room? It's in 4b, and it's like, totes adorbs!",
            "I was just in the tech lab, and the code is so smelly. I wouldn't wanna be around when it explodes.",
            "Dude, I was just thinking, what if we're just in a game? Nah.",
        ]

        possible_falling_reactions = [
            "pulls out their phone and begins recording.",
            "tries to take a selfie as it falls.",
            "tries to catch it, and quickly learns it is much heavier than they are.",
            "get bonked right on the head by it and sees stars circling around.",
            "tries to dodge it, but ends up getting hit by a stray falling object.", # if I want to make this one functional then it will need to add an item to gang member's items
            "pulls out their phone and says, 'hey mom can you come pick me up?'",
            "says, 'Oh my god this is it. The aliens are finally here.'"
        ]
        
        for result in results:
            parts = result.split()
            member_name = parts[3]  # Get member name
            member_names[member_name] = result
            if "resists" in result:
                resisted.append(member_name)
            else:
                affected.append(member_name)
            if not gang_name:
                gang_name = parts[1]  # Get gang name
                
        messages = []
        
        def construct_affect_message(member, effect_type):
            if effect_type == "hallucination":
                hallucination = random.choice(possible_hallucinations)
                return f"\n\nThe {gang_name} member {member} is hallucinating from the {self.name}. {member} {hallucination}"
            elif effect_type == "glitter":
                return f"\n\nThe {gang_name} member {member} gets covered in glitter and starts compulsively giving gifts!"
            elif effect_type == "pink mist":
                friendlyphrase = random.choice(possible_friendly_phrases)
                return f"\n\nThe {gang_name} member {member} breathes in the {self.name}, and looks unusually cheerful. {member} says, '{friendlyphrase}'"
            return ""

        def construct_resist_message(member, effect_type):
            if effect_type == "hacked milk":
                return f"{gang_name} member {member} carefully steps around the {self.name}, unaffected."
            elif effect_type == "glitter":
                return f"{gang_name} member {member} dodges the {self.name} with a graceful leap!"
            elif effect_type == "pink mist":
                return f"{gang_name} member {member} ducks down below the {self.name} and crawls on the floor!"
            elif effect_type == "car":
                return f"{gang_name} member {member} runs out of the way, dodging the {self.name}!"
            return f"{gang_name} member {member} resists the {self.name}."

        # Handle affected members
        if affected:
            if len(affected) == 1:
                messages.append(construct_affect_message(affected[0], self.name.lower()))
            else:
                names = ", ".join(affected[:-1]) + (" and " + affected[-1] if len(affected) > 1 else affected[0])
                if self.name == "Hacked Milk Spill":
                    hallucination1 = random.choice(possible_hallucinations)
                    hallucination2 = random.choice(possible_hallucinations)
                    messages.append(f"\n\nThe {gang_name} members {names} are hallucinating from the {self.name}. {affected[0]} {hallucination1} \nMeanwhile, {affected[1]} {hallucination2}")
                elif self.name == "Glitter Bomb":
                    messages.append(f"\n\nThe {gang_name} members {names} get covered in glitter and start a spontaneous gift exchange!")
                elif self.name == "Pink Mist":
                    friendlyphrase1 = random.choice(possible_friendly_phrases)
                    friendlyphrase2 = random.choice(possible_friendly_phrases)
                    messages.append(f"\n\nThe {gang_name} members {names} breathe in the { self.name}, and look unusually cheerful. {affected[0]} says, '{friendlyphrase1 }' \nMeanwhile, {affected[1]} says, '{friendlyphrase2}'")
                elif self.name in ["Car","Crate","Safe"]:
                    friendlyphrase1 = random.choice(possible_falling_reactions)
                    friendlyphrase2 = random.choice(possible_falling_reactions)
                    messages.append(f"\n\nThe {gang_name} members {names} look up at the { self.name} in awe, jaws dropped and eyes wide. {affected[0]} {friendlyphrase1 } \nMeanwhile, {affected[1]} {friendlyphrase2}")
                else:
                    messages.append(f"\n\nThe {gang_name} members {names} are affected by the {self.name} and are {self.effect}.")

        # Handle resisted members
        if resisted:
            if len(resisted) == 1:
                messages.append(construct_resist_message(resisted[0], self.name.lower()))
            else:
                names = ", ".join(resisted[:-1]) + (" and " + resisted[-1] if len(resisted) > 1 else resisted[0])
                messages.append(f"{gang_name} members {names} avoid the {self.name}, staying clear of its effects.")
            
        return " ".join(messages) if messages else f"The {self.name} has no effect on anyone."


class StaticHazard(Hazard):
    def __init__(self, name, description, effect):
        super().__init__(name, description, effect, damage=40, duration=None)  # Permanent static hazards



    def affect_area(self, area):
        """Apply hazard to all gang members in area with grouped results"""
        results = []
        for npc in area.npcs:
            if isinstance(npc, GangMember):
                result = npc.apply_hazard_effect(self)
                npc.update_effects()
                results.append(result)
                
        return self.group_results(results)
    
    def get_affected_verb(self, count):
        """Get appropriate verb for affected members"""
        verbs = {
            "Glitter Bomb": "gets glitter bombed",
            "Pink Mist": "breathes in pink mist",
            "Hacked Milk": "steps in hacked milk"
        }
        return verbs.get(self.name, "is affected by")




class HazardItem(Hazard):
    def __init__(self, name, description, effect):
        super().__init__(name, description, effect, damage=0)  # Hazard items may not cause damage
    
    def use(self, player):
        """Use hazard item on all gang members with grouped results"""
        
        results = []
        for npc in player.current_area.npcs:
            if isinstance(npc, GangMember):
                result = npc.apply_hazard_effect(self)
                npc.update_effects()
                results.append(result)
                
        return self.group_results(results)

    def get_affected_verb(self, count):
        """Get appropriate verb for affected members"""
        verbs = {
            "Glitter Bomb": "gets glitter bombed",
            "Pink Mist": "breathes in pink mist",
            "Hacked Milk": "steps in hacked milk"
        }
        return verbs.get(self.name, "is affected by")


# create a subclass of Hazard, for objects that fall
class FallingObject(Hazard):
    def __init__(self, name, description, effect, items):
        super().__init__(name, description, effect, damage=0)  # Hazard items may
        self.fall_distance = 3  # distance the object falls before landing - player turns before it's on the ground
        self.fall_damage = 10  
        self.fall_effect = effect  # effect the object has when it lands
        self.items = items # goods found inside object when it lands


        possible_effects = ["explodes", "crashes into ground", "hovers above ground", "reveals area"] # "reveals area" means the impact from falling damages the ground and exposes something underground



    def deactivate(self): # still present but no effect
        """make object no longer have effect"""
        self.active = False
        self.effect = None
        

    def open(self):
        
        return ", ".join(item.name for item in self.items) if self.items else "nothing"
    
    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
        return item
    
    def empty(self, player):
        """Transfer all items from this FallingObject to the current area"""
        for item in self.items:
            player.current_area.add_item(item)
        self.items.clear()

    def remove_hazard(self, player):
        """Remove this hazard from the area"""
        player.current_area.remove_object(self)


    

    def affect_area(self, area):
        """Apply hazard to all gang members in area with grouped results"""
        results = []
        for npc in area.npcs:
            if isinstance(npc, GangMember):
                result = npc.apply_hazard_effect(self)
                npc.update_effects()
                results.append(result)

                

        return self.group_results(results)
    
    
    

class Soil(GameObject):
    def __init__(self):
        super().__init__("Soil", "Dirt that can be used to grow plants")
        self.plants = []
        self.fertilizer = None
        self.effects = None
        self.USB_inserted = []  # List to track inserted USB sticks
        self.water_type = None  # Track current water type applied to soil

    def insert_usb(self, usb_item):
        """Insert a USB stick into the soil"""
        if usb_item.name.lower() == "usb stick":
            self.USB_inserted.append(usb_item)
            return f"You inserted the {usb_item.name} into the soil."
        return "You can only insert USB sticks into soil."

    def plant_seed(self, seed):
        """Plant a seed in this soil and return the new plant"""
        base_name = seed.name.replace(' seed', '')
        plant = Plant(f"{base_name} plant", f"A growing {base_name} plant")
        self.plants.append(plant)
        return plant

    def get_plants(self):
        """Return list of plants in this soil"""
        return self.plants

    def water_plants(self, water_type):
        """Water all plants in this soil with given water type"""
        self.water_type = water_type
        results = []
        for plant in self.plants:
            results.append(plant.water(water_type))
        return results

    def harvest_plants(self, player):
        """Harvest all ready plants from this soil and add crops to player's inventory"""
        harvested = []
        remaining_plants = []
        
        for plant in self.plants:
            crop = plant.harvest()
            if crop:
                player.inventory.append(crop)
                harvested.append(crop)
            else:
                remaining_plants.append(plant)
                
        self.plants = remaining_plants
        return harvested

    def describe(self):
        """Return description of plants in this soil"""
        if not self.plants:
            return "This soil has no plants growing in it."
            
        desc = f"This soil contains:\n"
        for plant in self.plants:
            desc += f"- {plant.status()}\n"
        return desc



class Storage(GameObject):
    def __init__(self, name, description, portable=False, locked=False):
        super().__init__(name, description)
        self.portable = portable
        self.items = []
        self.locked = False

    def unlock(self):
        self.locked = False

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
        return item

    def list_contents(self):
        return ", ".join(item.name for item in self.items) if self.items else "nothing"
    

class Structure(GameObject):
    def __init__(self, name, description, hideable = False):
        super().__init__(name, description)
        self.items = []
        self.hideable = hideable

    def add_item(self, items):
        self.items.append(items)

    def remove_item(self, items):
        self.items.remove(items)

    def hide(self, player):
        if self.hideable:
            player.hidden = not player.hidden
            if player.hidden:
                return f"You hide behind the {self.name}. NPCs can't see you now."
            return f"You come out from behind the {self.name}. NPCs might see you again."
        return "You can't hide behind this object."

class Area:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.items = []
        self.npcs = []
        self.objects = []
        self.garden_plants = []  # Special list for plants that can't be taken
        self.discoverable = False # does the player need to discover this area on their own, because if so, it will not be listed in nearby areas


    def add_object(self, objects):
        self.objects.append(objects)


    def remove_object(self, objects):
        self.objects.remove(objects)

    def add_npc(self, npc):
        self.npcs.append(npc)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item_name):
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if item:
            self.items.remove(item)
        return item

    def list_items(self):
        return ", ".join(item.name for item in self.items) if self.items else "nothing"

    def describe(self):
        desc = f"You are in {self.name}. {self.description}\n"
        if self.items:
            # Group items by name and count duplicates
            item_counts = {}
            for item in self.items:
                item_counts[item.name] = item_counts.get(item.name, 0) + 1
            item_list = []
            for name, count in item_counts.items():
                if count > 1:
                    item_list.append(f"{count} {name}s")
                else:
                    item_list.append(name)
            desc += "Items on the ground: " + ", ".join(item_list) + "\n"
        if self.npcs:
            people = []
            for npc in self.npcs:
                if hasattr(npc, 'name'):
                    people.append(npc.name)
                elif hasattr(npc, 'gang'):
                    people.append(f"{npc.gang} Member")
            desc += "People here: " + ", ".join(people) + "\n"
        if self.objects:
            desc += "Objects here: " + ", ".join(obj.name for obj in self.objects) + "\n"
        if self.garden_plants:
            desc += "Plants growing: " + ", ".join(p.name for p in self.garden_plants) + "\n"
        return desc


class Player:
    def __init__(self, starting_area):
        self.current_area = starting_area
        self.inventory = []
        self.health = 100
        self.stealth = 50
        self.hidden = False
        self.equipped_weapon = None
        self.active_tasks = set()
        self.completed_tasks = set()
        self.detected_by = set()  # Tracks which gangs have detected the player


    


    def hide(self):
        """Legacy method - hiding is now handled by Structure.hide()"""
        self.hidden = True

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return "You have been defeated!"
        return f"You took {amount} damage! Health: {self.health}"

    def heal(self, amount):
        self.health = min(100, self.health + amount)
        return f"Recovered {amount} health. Current health: {self.health}"
    


class Game:
    def __init__(self):
        self.areas = self.create_world()
        self.player = Player(self.areas['Home']['Front Lawn'])
        self.running = True
        self.alias_map = self.create_alias_map() # set an attribute by calling a function





        


    def create_alias_map(self):
        return {
            "bh": "Bloodhounds' Territory",
            "bloodhounds": "Bloodhounds' Territory",
            "bloodhounds' territory": "Bloodhounds' Territory",

            "home": "Home",
            "house": "Home",
            "living room": "Living Room",
            "lr": "Living Room",

            "Tech room": "Tech gadget room", 
            "Computer lab": "Tech Gadgets Room",
            "Bh tech": "Tech Gadgets Room",
            "Bh secret room": "Tech Gadgets Room",

            "Jack's Fuel": "Jacks Fuel",
            "gas station": "Jacks Fuel",
        }

    def create_world(self):
        home_living_room = Area('Living Room', 'A comfortable space with high-tech furniture and potted plants.')

            # ------- #
            # STORAGE #
            # ------- #
            
        desk = Storage("Desk", "A sleek metal desk with blinking lights and a terminal.")
        home_living_room.objects.append(desk)
        desk.add_item(Smartphone())
        
        # Create and add shovel to front lawn
        front_lawn = Area('Front Lawn', 'You stand just outside your cozy little house.')

        bh_techstorage = Area("Bloodhounds' Tech Gadgets Room", "A room filled with high-tech gadgets and computers.")
        

        

        # ------------------------------------------------ #
        # SET UP ITEMS FOR PLAYER TO FIND WITH SUPERVISION #
        # ------------------------------------------------ #
        
        # add value attribute to items for ability to sell them

        drone = Item("Drone", "A small drone that can be used for surveillance", 450)
        cash_bundle = Item("A bundle of cash", "A bundle of cash that can be used to buy items", 1000)
        blueprints = Item("Blueprints", "Mysterious blueprints, possibly for hacking tools", 800)
        
        
        robot_cow = NPC("A Robotic Cow", "A robotic cow that can be hacked for milk production, among other things")
        drone_powered_chicken = NPC("Drone-Powered Chicken", "A chicken with drones strapped to its wings, giving it the ability to hover precariously above the ground")

        Tony = NPC("Tony", "A shady character who may have information in exchange for goods. ")

        # Create gang and members

        bloodhounds_gang = Gang("Bloodhounds")
        self.bloodhounds = [GangMember(bloodhounds_gang) for _ in range(12)]
        
        # give each bloodhound member a different name
        self.bloodhounds[0].name = "Buck"
        self.bloodhounds[1].name = "Bubbles"
        self.bloodhounds[2].name = "Boop"
        self.bloodhounds[3].name = "Noodle"
        self.bloodhounds[4].name = "Flop"
        self.bloodhounds[5].name = "Squirt"
        self.bloodhounds[6].name = "Squeaky"
        self.bloodhounds[7].name = "Gus-Gus"
        self.bloodhounds[8].name = "Puddles"
        self.bloodhounds[9].name = "Muffin"
        self.bloodhounds[10].name = "Binky"
        self.bloodhounds[11].name = "Beep-Beep"
        
        
        
        # --------------------------- #
        # GANG MEMBER INVENTORY SETUP #
        # --------------------------- #


        knife = Weapon("Knife", "A small, sharp knife for close combat (Damage: 25)", 25)


        for member in self.bloodhounds:
            member.add_item(Weapon("gun", "A gun for self-defense", 10))
            member.add_item(knife)
            # items that the gang members could give the player as a gift when under the gift-giving hazard effect
            member.add_item(Item("USB stick", "a small USB stick with some files on it", 50))
            

        

        warehouse_entrance = Area("Bloodhounds' territory entrance", "The looming entrance to the Bloodhound-controlled warehouse.")

        # Add weapons
        warehouse_entrance.add_item(knife)


        container1 = Structure("Red Construction Container", "A large, red construction container that provides good cover from enemies.", True)
        
        container_maze = Area("Container Maze", "A long series of paths surrounded by containers, creating a makeshift hideout.")
        for member in self.bloodhounds:
            container_maze.npcs.append(member)


        container_maze.objects.append(container1)



        warehouse_main_area = Area("Warehouse Main Area", "A large, open space with crates and boxes scattered about.")
        for member in self.bloodhounds:
            warehouse_main_area.npcs.append(member)


        
    
        return {
            'Home': {
                'Front Lawn': front_lawn,
                'Living Room': home_living_room,
                'Garden': Area("Home Garden", "A patch of dirt on your front lawn. You can plant and care for seeds here."),
                 
            },

            "Bloodhounds' Territory": {
                'Entrance': warehouse_entrance,
                'Warehouse Main Area': warehouse_main_area,
                'Container Maze': container_maze,
                'Tech Gadget Room': bh_techstorage
            },

            "Backroads": {
                'Echo Road': Area("Echo Road", "In a mist of fog, a long stretch of road leads to the unknown."),
                'abandoned warehouse': Area("Abandoned Warehouse", 'a large, abandoned warehouse with broken windows and a creaky door'),
                'Jacks Fuel': Area("Jacks Fuel", 'A small gas station with a small store and a large parking lot'),
                'old diner': Area("Old Diner", 'a small, rundown diner with a neon sign that still flickers to life at night')
            },

            "The Farm": {
                'Courtyard': Area("Courtyard", "Just inside the chain-link fence that surrounds the farm, a large courtyard with untamed grass and weeds."),
                'The Fields': Area("The Fields", "Rows of crops wave lazily in the breeze, their uniform movement unnerving. There may be something sinister deep below the soil."),
                'The Farmhouse Entrance': Area("The Farmhouse Entrance", "The farmhouse appears ordinary—faded shutters, a broken weather vane spinning aimlessly. Inside, the cozy facade vanishes; harsh fluorescent lights buzz above sterile desks cluttered with computers, monitors displaying genetic sequences like hieroglyphics")

            },

            "The Farmhouse": {
                'Command Center': Area("Command Center", "The main room glows with screens, each cycling through surveillance footage of the fields and labs below."),
                'Living Quarters': Area("Living Quarters", "Bloodhounds sleep here. Scattered papers litter the floor."),
                'Storage Closet': Area("Storage Closet", "Disguised as an ordinary storage closet, this seemingly small space reveals a staircase leading down."),
                'Stairs': Area("The stairs", "A narrow staircase descends into darkness."),
                'Plant Lab': Area("Plant Lab", "A small room filled with rows of plants, each one genetically modified to produce a different effect."),
                'Data Storage': Area("Data Storage Room", "A small room filled with rows of servers, humming with data."),
            },
        

        }
    

    def check_event_triggers(self):
        """Check for completed tasks that should trigger game events.
        Uses a dictionary for scalable event triggers."""
        event_triggers = {
            "read_robotic_cow_data": {
                "action": lambda: setattr(self.areas["Backroads"]["Jacks Fuel"], 'discoverable', False),
            }
            # Add new triggers here in the format:
            # "task_name": {
            #    "action": lambda: code_to_execute,
            #    "message": "Feedback message"
            # }
        }
        
        for task, trigger in event_triggers.items():
            if task in self.player.completed_tasks:
                trigger["action"]()
                # Remove from completed_tasks so we don't keep triggering
                self.player.completed_tasks.remove(task)
            
    def setup_areas(self):
        setattr(self.areas["Backroads"]["Jacks Fuel"], 'discoverable', True) # make areas discoverable at the beginning 

        # Create NPC Jack
        Jack = NPC("Jack", "The owner of the gas station who might offer intel.")



        # ADD JACK TO JACKS FUEL
        self.areas["Backroads"]["Jacks Fuel"].add_npc(Jack)

        # create garden area


        # ---------------------- #
        # SET UP GARDENING ITEMS #
        # ---------------------- #

        watering_can = WateringCan("watering can", "A watering can for watering plants")

        shovel = Item("shovel", "A sturdy shovel for digging")

        
        seed_box = Storage("Seed Box", "A small wooden box containing seeds for your garden.", False)


        # create seeds

        carrot_seed = Seed("carrot seed", "A seed for planting carrots")
        tomato_seed = Seed("tomato seed", "A seed for planting tomatoes")
        lettuce_seed = Seed("lettuce seed", "A seed for planting lettuce")
        blueberry_seed = Seed("blueberry seed", "A seed for planting blueberries")
        
        # a seed must become a crop. A crop is the item that the player recieves when they harvest the plant. 

        carrot = Crop("carrot", "a carrot")



        seed_box.add_item(carrot_seed)
        seed_box.add_item(tomato_seed)
        seed_box.add_item(lettuce_seed)
        seed_box.add_item(blueberry_seed)
    

        watering_can.set_water_type("hacked milk")

        # home_garden_soil.set_soil_type("clay") # oh my god soil type? maybe consider later
        home_garden_soil = Soil()

        front_lawn_soil = Soil()

        gas_station__soil = Soil()


        USB_stick = Item("USB stick", "A small USB stick. Might be possible to stick into the soil.")

        self.areas["Home"]["Garden"].add_item(watering_can)
        self.areas["Home"]["Garden"].add_object(seed_box)
        self.areas["Home"]["Garden"].add_item(shovel)
        self.areas["Home"]["Garden"].add_object(home_garden_soil)
        self.areas["Home"]["Garden"].add_item(USB_stick)

        self.areas["Home"]["Front Lawn"].add_object(front_lawn_soil)
        self.areas["Backroads"]["Jacks Fuel"].add_object(gas_station__soil) # plant a carrot in the immediate area of the gas station where player talks to Jack. Add even more places for player to plant, more open-world that way



        container2 = Storage("Container 4B", "A large, yellow construction container. It might have valuable items inside.")

        farm_note = Item("A pink note", "A note that reads: Take the backroads.", 0)
        tomato_note = Item("A blue note", "A note that reads: Use the smelly code.", 0)
        smelly_USB = Item("USB stick", "a small USB stick with some files on it", 50)

        container2.add_item(farm_note)
        container2.add_item(tomato_note)
        container2.add_item(smelly_USB) 
        safe = Storage("Safe", "A safe that can be opened with the right combination", False, True)


        self.areas["Bloodhounds' Territory"]["Container Maze"].add_object(container2)
        self.areas["Bloodhounds' Territory"]["Warehouse Main Area"].add_object(safe)
        


    def setup_hazards(self):
        

        glitter_bomb = HazardItem("Glitter Bomb", "A small, shiny bomb that explodes into glitter.", "gift-giving")
        for i in range (2):
            self.player.inventory.append(glitter_bomb)

        self.areas["Bloodhounds' Territory"]["Warehouse Main Area"].add_object(StaticHazard("Hacked Milk Spill", "A puddle of hacked milk.", "hallucinations"))
        #self.areas["Bloodhounds' Territory"]["Warehouse Main Area"].add_object(StaticHazard("Pink Mist", "A pink mist floats through the air.", "friendliness"))


                  # ----------------------------- #
                  # SET UP FALLING OBJECT HAZARDS #
                  # ----------------------------- #

    def setup_falling_hazards(self):    

        falling_objects = [ # falling objects that have items inside them 
        FallingObject("Car", "A standard 4-door car", "crashes into ground", [ # some regular items might need to be changed to tech items
            Item("Laptop", "A slightly damaged but functional laptop", 300),
            Crop("Tomato", "A tomato", 5),
            Item("A note", "The note reads: Need smelly code.", 0) # notes might need to become "intel" subclass or something
        ]),
        FallingObject("Crate", "A large crate with a sign that reads special ingredients.","crashes into ground", [
            Item("Spare computer part", "Could be useful for fixing old tech", 10), # might make crafting table so players can combine these ingredients
            Item("Glitter jar", "A jar full of sparkly glitter.", 20),
            Item("Batteries", "Could be useful", 20),
            Item("A ball", "A hollow plastic ball", 300)
        ]),
        FallingObject("Safe", "A locked safe", "crashes into ground", [
            Item("Berry Bag", "A bag of unusual shiny berries.", 800),
            Item("Keycard", "Access card with unknown purpose", 300)
        ])
    ]
        
        falling_object = random.choice(falling_objects)
        return falling_object


    def __init__(self):
        self.areas = self.create_world()
        self.player = Player(self.areas['Home']['Front Lawn'])
        self.running = True
        self.alias_map = self.create_alias_map()
        self.command_history = []
        self.colors = {
            'error': '\033[91m',
            'success': '\033[92m',
            'warning': '\033[93m',
            'info': '\033[94m',
            'reset': '\033[0m'
        }

    def print_color(self, text, color='info'):
        """Print colored text using ANSI escape codes"""
        print(f"{self.colors.get(color, '')}{text}{self.colors['reset']}")

    def start(self):
        self.setup_areas()
        hazard_items = self.setup_hazards()
        # might need to also call setup_falling_hazards here  

        self.print_color("=== Welcome to Root Access! ===", 'info')
        self.print_color("Type 'help' for a list of commands", 'info')
        print(self.player.current_area.describe())

        while self.running:
            command = input("\n> ").strip().lower()
            self.command_history.append(command)
            self.handle_command(command)
            
            # Check for static hazards affecting gang members
            for obj in self.player.current_area.objects:
                if isinstance(obj, StaticHazard):
                    print(obj.affect_area(self.player.current_area))

            # check for falling hazards affecting gang members
            for obj in self.player.current_area.objects:
                if isinstance(obj, FallingObject):
                    print(obj.affect_area(self.player.current_area))
                    obj.active = False
                    obj.effect = None
                    obj.empty(self.player)
                    obj.remove_hazard(self.player)
            
            # Check for gang member attack after each command
            if not self.player.hidden:
                # Find first armed gang member in area
                attacker = next((npc for npc in self.player.current_area.npcs 
                               if isinstance(npc, GangMember) and 
                               any(isinstance(i, Weapon) for i in npc.items)), None)
                if attacker:
                    print(attacker.attack_player(self.player))
                    if self.player.health <= 0:
                        print("You were defeated! Waking up back at home...")
                        self.player.current_area = self.areas['Home']['Front Lawn']
                        self.player.health = 100
                        self.player.hidden = False


    def teleport(self, destination):
        for region, subareas in self.areas.items():
            if destination == region:
                self.player.current_area = list(subareas.values())[0]                 
                print(f"You travel to {region}.") 
                return
            for name, area in subareas.items():
                if destination == area.name:
                    self.player.current_area = area
                    print(f"You move to {area.name}.")
                    print(self.player.current_area.describe())
                    return
        print("That location doesn't exist.")
        

    def handle_command(self, command):
        # Check for event triggers before processing commands
        self.check_event_triggers()
        
        # Try each handler in order, return if command was processed
        if self.handle_movement_commands(command):
            return
        if self.handle_system_commands(command):
            return
        if self.handle_interaction_commands(command):
            return
        if self.handle_garden_commands(command):
            return
        if self.handle_combat_commands(command):
            return
        if self.handle_cheat_commands(command):
            return
        if self.handle_NPC_commands(command):
            return
        if self.handle_hacking_commands(command):
            return
        if self.handle_testing_commands(command):
            return   
        if self.handle_chaos_commands(command):
            return
        if self.handle_hazard_commands(command):
            return
        print("Command not recognized.")

    def handle_movement_commands(self, command):
        if command.startswith("go to"):
            target = command[6:].strip().lower()
            destination = self.alias_map.get(target, target.title())
            self.teleport(destination)
            return True
        return False

    def handle_system_commands(self, command):
        if "inventory" in command:
            if self.player.inventory:
                self.print_color("=" * 20, 'info')
                self.print_color("Your Inventory:", 'info')
                self.print_color("=" * 20, 'info')
                # Group inventory items by name and count duplicates
                item_counts = {}
                for item in self.player.inventory:
                    item_counts[item.name] = item_counts.get(item.name, 0) + 1
                for name, count in item_counts.items():
                    if count > 1:
                        print(f"- {count} {name}s")
                    else:
                        print(f"- {name}")
            else:
                self.print_color("Your inventory is empty.", 'warning')
            return True
            
        elif "look" in command:
            print(self.player.current_area.describe())
            return True
            
        elif command == "quit":
            self.running = False
            return True
            
        elif command == "help":
            self.print_color("\nAvailable Commands:", 'info')
            self.print_color("------------------", 'info')
            self.print_color("Movement: go to [location]", 'info')
            self.print_color("Inventory: inventory, take [item], drop [item]", 'info')
            self.print_color("Combat: attack, hide", 'info')
            self.print_color("Hazards: throw [hazard], create hazard", 'info')
            self.print_color("Gardening: plant [seed], water [plant], harvest [plant]", 'info')
            self.print_color("System: look, help, history, quit", 'info')
            return True
            
        elif command == "history":
            self.print_color("\nCommand History:", 'info')
            for i, cmd in enumerate(self.command_history[-10:], 1):
                print(f"{i}. {cmd}")
            return True
            
        return False

    def handle_interaction_commands(self, command):
        if command.startswith("open "):
            storage_name = command[5:].strip().lower()
            storage = next((obj for obj in self.player.current_area.objects 
                          if obj.name.lower() == storage_name), None)
            if storage and isinstance(storage, Storage):
                if storage.locked:
                    if storage.name == "Safe":
                        code = input("Enter the code: ")
                        if code == "1234":
                            storage.locked = False
                            print(f"You open the {storage.name}. Inside you see: {storage.list_contents()}")
                            return True
                        else:
                            print("Incorrect code.")
                            return True
                    print(f"You open the {storage.name}. Inside you see: {storage.list_contents()}")
                    return True
                
            elif storage and isinstance(storage, FallingObject):
            
                print(storage.open())

                

            else:
                print(f"You don't see anything here that can be opened.") # expanding this to handle multiple objects with items inside them
            return True
        
            
        elif command.startswith("take ") and " from " in command:
            parts = command[5:].split(" from ")
            if len(parts) == 2:
                item_name = parts[0].strip()
                storage_name = parts[1].strip().lower()
                storage = next((obj for obj in self.player.current_area.objects 
                              if obj.name.lower() == storage_name), None)
                if storage and isinstance(storage, Storage):
                    item = storage.remove_item(item_name)
                    if item:
                        self.player.inventory.append(item)
                        print(f"You take the {item.name} from the {storage.name}.")
                    else:
                        print(f"The {storage.name} doesn't contain a {item_name}.")
                elif storage and isinstance(storage, FallingObject): # might be too much code duplication here, might want to consider falling object to be storage 
                    item = storage.remove_item(item_name)
                    if item:
                        self.player.inventory.append(item)
                        print(f"You take the {item.name} from the {storage.name}.")
                else:
                    print(f"You don't see anything to take items from here.")
            else:
                print("Usage: take [item] from [storage]")
            return True
            
        elif command.startswith("put ") and " in " in command:
            parts = command[4:].split(" in ")
            if len(parts) == 2:
                item_name = parts[0].strip()
                storage_name = parts[1].strip().lower()
                item = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
                if item:
                    storage = next((obj for obj in self.player.current_area.objects 
                                  if obj.name.lower() == storage_name), None)
                    if storage and isinstance(storage, Storage):
                        storage.add_item(item)
                        self.player.inventory.remove(item)
                        print(f"You put the {item.name} in the {storage.name}.")
                    else:
                        print(f"You don't see a {storage_name} here.")
                else:
                    print(f"You don't have a {item_name} in your inventory.")
            else:
                print("Usage: put [item] in [storage]")
            return True
            
        elif command.startswith("take "):
            item_name = command[5:].strip().lower()
            item = self.player.current_area.remove_item(item_name)
            if item:
                self.player.inventory.append(item)
                print(f"You pick up the {item.name}.")
            else:
                print(f"You don't see a {item_name} here.")
            return True
            
        elif command.startswith("drop "):
            item_name = command[5:].strip().lower()
            item = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
            if item:
                self.player.current_area.add_item(item)
                self.player.inventory.remove(item)
                print(f"You drop the {item.name}.")
            else:
                print(f"You don't have a {item_name} in your inventory.")
            return True
            
        elif command.startswith("examine "):
            item_name = command[8:].strip().lower()
            item = next((i for i in self.player.inventory if i.name.lower() == item_name.lower()), None)
            if item:
                print(f"{item.name}: {item.description}")
                if hasattr(item, 'effect') and item.effect:
                    print(f"Special effect: {item.effect}")
            else:
                print(f"You don't have a {item_name} in your inventory.")
            return True
        
            
        return False
    

    def handle_garden_commands(self, command):
        if command.startswith("insert usb"):
            usb_item = next((i for i in self.player.inventory if i.name.lower() == "usb stick"), None)
            if not usb_item:
                print("You don't have a USB stick!")
                return True
                
            soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, Soil)), None)
            if soil:
                print(soil.insert_usb(usb_item))
                self.player.inventory.remove(usb_item)
            else:
                print("There's no soil here to insert the USB into!")
            return True

        if command == "fill watering can":
            watering_can = next((i for i in self.player.inventory if isinstance(i, WateringCan)), None)
            if not watering_can:
                print("You need a watering can!")
                return True

            print("Available water types:")
            for water_type in watering_can.possible_water_types:  # Updated to use possible_water_types
                print(f"- {water_type}")

            choice = input("Select water type: ").strip()
            if watering_can.set_water_type(choice):
                print(f"Filled with {choice} water")
            else:
                print("Invalid water type selected.")
            return True
    
        elif command == "dig":
            shovel = next((i for i in self.player.inventory if i.name.lower() == "shovel"), None)
            soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, Soil)), None)
            if shovel and soil:
                print("You prepare the soil for planting.")
            elif not shovel:
                print("You need a shovel to dig!")
            else:
                print("There's no soil here to dig!")
            return True
            
        elif command.startswith("plant "):
            seed_name = command[6:].strip().lower()
            seed = next((i for i in self.player.inventory if isinstance(i, Seed) and i.name.lower() == seed_name), None)
            if seed:
                soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, Soil)), None)
                if soil:
                    plant = soil.plant_seed(seed)
                    self.player.inventory.remove(seed)
                    print(f"You planted {seed.name}. Now water it to help it grow!")
                else:
                    print("There's no soil here to plant in!")
            else:
                print(f"You don't have {seed_name} seeds in your inventory.")
            return True
            
        elif command.startswith("water "):
            plant_name = command[6:].strip().lower()
            watering_can = next((i for i in self.player.inventory if i.name.lower() == "watering can"), None)
            if not watering_can:
                print("You need a watering can!")
                return True
            
            soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, Soil)), None)
            if soil:
                plant = next((p for p in soil.get_plants() if p.name.lower() == plant_name), None)
                if plant:
                    if watering_can.current_water_type:
                        results = soil.water_plants(watering_can.current_water_type)
                        print("\n".join(results))
                    else:
                        print("Your watering can is empty!")
                else:
                    print(f"You don't see a {plant_name} plant here.")
            else:
                print("There's no soil here to water!")
            return True
        

        elif command == "get water type":
            if self.player.inventory:
                for item in self.player.inventory:
                    if isinstance(item, WateringCan):
                    
                        print(f"Your watering can contains: {item.get_water_description()}")
                    else:
                        print("no watering can found")
            else:
                print("inventory empty")
            return True

            
        elif command == "instagrow":
            soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, Soil)), None)
            if soil:
                if soil.get_plants():
                    for plant in soil.get_plants():
                        plant.growth_stage = len(plant.GROWTH_STAGES)-1
                    print("All plants in the soil instantly grew to harvest-ready size!")
                else:
                    print("No plants found in the soil to grow instantly.")
            else:
                print("There's no soil here to grow plants in!")
            return True
        
        elif command == "plants":
            soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, Soil)), None)
            if soil:
                plants = soil.get_plants()
                if plants:
                    print("Plants in the soil:")
                    for plant in plants:
                        print(f"- {plant.name} ({plant.GROWTH_STAGES[plant.growth_stage]})")
                else:
                    print("No plants growing in this soil.")
            else:
                print("There's no soil here to check for plants!")
            return True

        elif command.startswith("harvest "):
            plant_name = command[8:].strip().lower()
            soil = next((obj for obj in self.player.current_area.objects if isinstance(obj, Soil)), None)
            if soil:
                plant = next((p for p in soil.get_plants() if p.name.lower() == plant_name), None)
                if plant:
                    harvested = soil.harvest_plants(self.player)
                    if harvested:
                        for crop in harvested:
                            if crop.effect:
                                print(f"You harvested a {crop.name}! (Effect: {crop.effect})")
                            else:
                                print(f"You harvested a {crop.name}!")
                    else:
                        print(f"The {plant.name} isn't ready to harvest yet.")
                else:
                    print(f"You don't see a {plant_name} plant here.")
            else:
                print("There's no soil here to harvest from!")
            return True
        
        elif command.startswith("eat"):
            food_name = command[4:].strip().lower()
            food = next((f for f in self.player.inventory if f.name.lower() == food_name), None)
            if food:
                self.player.inventory.remove(food)
                if food.effect:
                    result = self.apply_effect(food.effect, self.player)
                    print(f"You ate a {food.name}! {result}")
                else:
                    print(f"You ate a {food.name}!")
                return True

            
        return False

    def apply_effect(self, effect_name, player):
        """Handle all crop effects in a centralized way"""
        effect_handlers = {
            "supervision": self.effect_supervision,
            "falling objects": self.effect_falling_objects,
            "invisibility": self.effect_invisibility
        }
        
        handler = effect_handlers.get(effect_name)
        if handler:
            return handler(player)
        return f"Unknown effect: {effect_name}"

    def effect_supervision(self, player):
        """Handle supervision effect - adds random items/NPCs to area"""
        possible_items = [
            Item("Drone", "A small drone that can be used for surveillance", 450),
            Item("Hacked Smartphone", "A smartphone that has been hacked", 600)
        ]
        possible_npcs = [
            NPC("A Robotic Cow", "A robotic cow that can be hacked for milk production"),
            NPC("Drone-Powered Chicken", "A chicken with drones strapped to its wings")
        ]

        # Add 1-3 random items
        added_items = random.sample(possible_items, k=random.randint(1, 3))
        for item in added_items:
            player.current_area.add_item(item)

        # 50% chance to add an NPC
        if random.random() > 0.5:
            npc = random.choice(possible_npcs)
            player.current_area.npcs.append(npc)
            added_items.append(npc)

        item_names = ", ".join(i.name for i in added_items)
        return f"Your senses expand! You notice: {item_names}"
    
    def effect_falling_objects(self, player):
        """Handle falling objects effect - cars fall from sky with items"""
        pass # VERY IMPORTANT CODE EXAMPLE TO STILL USE - also not updated to use FallingObject class
        #num_cars = random.randint(1, 3)
        #cars = [ChaosObject() for _ in range(num_cars)]
        
        #for car in cars:
        #    player.current_area.objects.append(car)
            
        #car_names = ", ".join(c.name for c in cars)
        #return f"BOOM! {car_names} crash down around you! Try 'smash [car]' to break them open."
    
    def effect_invisibility(self, player):
        """Handle invisibility effect - player becomes invisible"""
        player.invisible = True
        # add more layers to this, like invisibility but also being able to pickpocket, add items into a gang member's inventory without being seen, which could cause more chaos 


    def handle_NPC_commands(self, command):
        player = self.player
        if command == "pickpocket":
            gang_member = next((npc for npc in self.player.current_area.npcs if isinstance(npc, GangMember)), None)
            if gang_member:
                if gang_member.items:
                    item = random.choice(gang_member.items)
                    gang_member.items.remove(item)
                    self.player.inventory.append(item)
                    print(f"You successfully pickpocketed a {item.name} from the {gang_member.gang.name} member.")
                else:
                    print(f"The {gang_member.gang.name} member doesn't have any items to steal.")
            else:
                print("There's no gang member here to pickpocket.")
            return True
        elif "talk" in command:
            npc_name = input("Who do you talk to? ") # must figure out a way to have npc names handled in command
            npc = next((npc for npc in self.player.current_area.npcs if npc.name.lower() == npc_name.lower()), None)
            if npc:
                npc.talk(player)
                return True
            else:
                print("There's no one here by that name.")
                return True
        return False



    def handle_combat_commands(self, command):
        if command == "stab" or command.startswith("attack"):
            weapon = next((i for i in self.player.inventory if isinstance(i, Weapon)), None)
            if not weapon:
                print("You don't have a weapon equipped!")
                return True
                
            gang_member = next((npc for npc in self.player.current_area.npcs if isinstance(npc, GangMember)), None)
            if gang_member:
                result = weapon.use(gang_member)
                if gang_member.health <= 0:
                    self.player.current_area.npcs.remove(gang_member)
                print(result)
            else:
                print(f"There's no gang member here to {command}!")
            return True
            
        elif command.startswith("hide"):
            if not any(obj for obj in self.player.current_area.objects if isinstance(obj, Structure) and obj.hideable):
                print("There's nothing here you can hide behind.")
            else:
                structure = next((obj for obj in self.player.current_area.objects 
                                if isinstance(obj, Structure) and obj.hideable), None)
                if structure:
                    print(structure.hide(self.player))
                else:
                    print("You can't hide here.")
            return True
        return False
        


    def handle_cheat_commands(self, command):
        if command == "protection":
            if self.player.hidden:
                self.player.hidden = False
                print("Protection disabled.")
            else:
                self.player.health = 100
                self.player.hidden = True
                print(f"Your health: {self.player.health}")
                print(f"Hidden: {self.player.hidden}")
            return True

        return False


    def handle_testing_commands(self, command):
        if "where" in command:
            print(f"Current area: {self.player.current_area.name}")
            return True
        elif command == "show nearby areas":
            current_area_name = self.player.current_area.name
            current_region = None
            for region, areas in self.areas.items():
                if current_area_name in areas:
                    current_region = region            
                    if current_region:
                        nearby_areas = [area for area in self.areas[current_region] if area != current_area_name]
                        print(f"You are in {current_area_name}, in {current_region}.")
                        print(f"Nearby areas: {', '.join(nearby_areas)}")
                        return True
            else:
                print("Unable to determine current region.")
                return True
        elif command == "falling object":
                falling_object = self.setup_falling_hazards() # trying to capture return value from function that defines falling objects and chooses a random one
                self.player.current_area.add_object(falling_object) # add randomly chosen falling object, from setup function, to current area
                print("Falling object added.")
                return True

        

        elif command == "give phone":
            self.player.inventory.append(Smartphone())
            self.player.inventory.append(WateringCan)
            return True
                        
                        
        return False
                # tells players what area they are in using the dictionary. The player's general area is a key, like "The Farm" is a key and "The Fields" is a value, so if player's current area is "The Fields" then it will print "You are in the fields, at the farm."

               
    def handle_hacking_commands(self, command):
        if command == "hack":
            smartphone = next((i for i in self.player.inventory if isinstance(i, Smartphone)), None)
            if smartphone:
                smartphone.hacks(self.player)
                return True
            print("You need a smartphone to hack!")
            return True
            
        elif command in ["use phone", "turn on phone"]:
            smartphone = next((i for i in self.player.inventory if isinstance(i, Smartphone)), None)
            if smartphone:
                smartphone.home_screen()
                return True
            print("You don't have a smartphone!")
            return True
            
        return False
    
    def handle_chaos_commands(self, command):
        if command == "create hazard":
            print("\n\nHazard choices: ")
            print("1. hacked milk puddle")
            print("2. pink mist")
            print("3. falling objects")
            print("4. dancing robots (coming soon)")
            hazards = input("Which hazard do you want to activate? ")
            if hazards == "1":
                self.player.current_area.add_object(StaticHazard("Hacked milk spill", "A puddle of hacked milk.","hallucination"))
                print("There is a puddle of hacked milk on the floor.")
                return True
            elif hazards == "2":
                pink_mist = StaticHazard("Pink Mist", "A pink mist floating through the air from the vents", "friendliness")
                self.player.current_area.add_object(pink_mist)
                print("There is a pink mist floating through the air.")
                return True
            elif hazards == "3":
                print("falling objects should be called here") # need falling object to be called here

                num_objs = random.randint(1, 3)
                objs = [game.setup_falling_hazards() for _ in range(num_objs)]
                for obj in objs:
                    self.player.current_area.objects.append(obj)
                obj_names = ", ".join(obj.name for obj in objs)
                return f"BOOM! {obj_names} crash down around you!", True

            elif hazards == "4":
                print("dancing robots coming soon.")
        return False
    
    def handle_hazard_commands(self, command):
        
        if command == "throw":
            hazards = [i for i in self.player.inventory if isinstance(i, HazardItem)]
            if hazards:
                print("Available hazard items to throw:")
                for i, hazard in enumerate(hazards, 1):
                    print(f"{i}. {hazard.name} - {hazard.description}")
                choice = input("Which hazard do you want to throw? (1-{}) ".format(len(hazards)))
                if choice.isdigit() and 1 <= int(choice) <= len(hazards):
                    hazard = hazards[int(choice)-1]
                    result = hazard.use(self.player)
                    self.player.inventory.remove(hazard)
                    print(result)
                else:
                    print("Invalid selection.")
            else:
                print("You don't have any hazard items to throw!")
            return True
            
        return False



if __name__ == '__main__':
    game = Game()
    game.start()