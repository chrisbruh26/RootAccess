"""
NPC module for Root Access v3.
Handles all non-player characters in the game world.
"""
import os
import json
import random
from datetime import datetime, timedelta
from .coordinates import Coordinates

class NPC:
    """NPC class representing non-player characters in the game world."""
    def __init__(self, name, description, coordinates=None, dialogue=None, personality=None, 
                 money=0, relationships=None, properties=None, inventory=None, schedule=None, gang=None):
        self.name = name
        self.description = description
        self.coordinates = coordinates if coordinates else Coordinates(0, 0, 0)
        self.location = None
        self.dialogue = dialogue if dialogue else {"default": "Hello there!"}
        self.inventory = inventory or []  # NPC's inventory
        self.personality = personality or {}  # Personality traits
        self.relationships = relationships or {}  # Relationships with other NPCs and the player
        self.schedule = schedule or {}  # Daily schedule
        self.current_activity = "idle"
        self.current_action = None  # What the NPC is currently doing (displayed to player)
        self.money = money
        self.properties = properties or {}  # Custom properties
        self.influence_level = 0  # How much the player has influenced this NPC
        self.id = f"npc_{name.lower().replace(' ', '_')}"
        self.gang = gang  # Gang affiliation
        self.behavior_type = "normal"  # Default behavior type
        
        # Action memory and continuity system
        self.action_memory = []  # List of recent actions (newest first)
        self.current_action_start_time = None  # When the current action started
        self.current_action_duration = 0  # How long the current action should last (in minutes)
        self.action_target = None  # Target of the current action (NPC, item, object)
        self.interrupted = False  # Whether the current action was interrupted

    def set_location(self, area):
        """Set the location of the NPC."""
        if self.location:
            self.location.remove_npc(self)
        self.location = area
        area.add_npc(self)
        # Update NPC coordinates to match area
        self.coordinates = Coordinates(area.coordinates.x, area.coordinates.y, area.coordinates.z)

    def remove_location(self):
        """Remove the NPC from its current location."""
        if self.location:
            self.location.remove_npc(self)
            self.location = None
    
    def talk(self, player):
        """Talk to the NPC."""
        # Check relationship with player
        relationship = self.get_relationship(player)
        
        # Determine dialogue based on relationship
        if relationship < -50:
            print(f"{self.name}: {self.dialogue.get('hostile', 'Go away! I do not want to talk to you.')}")
            return
        
        # Regular dialogue
        if relationship > 50:
            print(f"{self.name}: {self.dialogue.get('friendly', self.dialogue['default'])}")
        else:
            print(f"{self.name}: {self.dialogue['default']}")
        
        # Show interaction options
        self.show_interaction_options(player)
    
    def show_interaction_options(self, player):
        """Show interaction options for the player."""
        print("\nInteraction options:")
        print("1. Chat")
        print("2. Trade")
        print("3. Influence")
        print("4. Leave")
        
        choice = input("What would you like to do? ")
        
        if choice == "1":
            self.chat(player)
        elif choice == "2":
            self.trade(player)
        elif choice == "3":
            self.attempt_influence(player)
        elif choice == "4":
            print(f"You end your conversation with {self.name}.")
        else:
            print("Invalid choice.")
    
    def chat(self, player):
        """Chat with the NPC."""
        relationship = self.get_relationship(player)
        
        # Different chat topics based on relationship
        if relationship > 30:
            topics = ["weather", "life", "gossip", "advice"]
        else:
            topics = ["weather", "general"]
        
        print("\nChat topics:")
        for i, topic in enumerate(topics, 1):
            print(f"{i}. {topic.capitalize()}")
        
        choice = input("What would you like to chat about? ")
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(topics):
                topic = topics[index]
                self.discuss_topic(topic, player)
            else:
                print("Invalid topic.")
        except ValueError:
            print("Please enter a number.")
    
    def discuss_topic(self, topic, player):
        """Discuss a specific topic with the NPC."""
        # Get topic-specific dialogue or use default
        topic_key = f"topic_{topic}"
        response = self.dialogue.get(topic_key, f"Let's talk about {topic}.")
        print(f"{self.name}: {response}")
        
        # Small relationship boost for chatting
        self.adjust_relationship(player, 2)
        print(f"{self.name} appreciates the conversation.")
    
    def trade(self, player):
        """Trade items with the NPC."""
        if not self.inventory and player.money < 10:
            print(f"{self.name} doesn't have anything to trade, and you don't have enough money.")
            return
        
        print("\nTrading options:")
        print("1. Buy from NPC")
        print("2. Sell to NPC")
        print("3. Cancel")
        
        choice = input("What would you like to do? ")
        
        if choice == "1":
            self.buy_from_npc(player)
        elif choice == "2":
            self.sell_to_npc(player)
        elif choice == "3":
            print("You decide not to trade.")
        else:
            print("Invalid choice.")
    
    def buy_from_npc(self, player):
        """Buy items from the NPC."""
        if not self.inventory:
            print(f"{self.name} doesn't have anything to sell.")
            return
        
        print(f"\n{self.name}'s inventory:")
        for i, item in enumerate(self.inventory, 1):
            price = item.value * 1.5  # NPCs sell at a markup
            print(f"{i}. {item.name}: ${price}")
        print(f"{len(self.inventory) + 1}. Cancel")
        
        choice = input("What would you like to buy? ")
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(self.inventory):
                item = self.inventory[index]
                price = item.value * 1.5
                
                if player.money >= price:
                    player.money -= price
                    self.money += price
                    self.inventory.remove(item)
                    player.add_item(item)
                    print(f"You bought {item.name} for ${price}.")
                    
                    # Small relationship boost for trading
                    self.adjust_relationship(player, 3)
                else:
                    print(f"You don't have enough money. {item.name} costs ${price}.")
            elif index == len(self.inventory):
                print("You decide not to buy anything.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")
    
    def sell_to_npc(self, player):
        """Sell items to the NPC."""
        if not player.inventory:
            print("You don't have anything to sell.")
            return
        
        print("\nYour inventory:")
        for i, item in enumerate(player.inventory, 1):
            price = item.value * 0.7  # NPCs buy at a discount
            print(f"{i}. {item.name}: ${price}")
        print(f"{len(player.inventory) + 1}. Cancel")
        
        choice = input("What would you like to sell? ")
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(player.inventory):
                item = player.inventory[index]
                price = item.value * 0.7
                
                if self.money >= price:
                    self.money -= price
                    player.money += price
                    player.inventory.remove(item)
                    self.inventory.append(item)
                    print(f"You sold {item.name} for ${price}.")
                    
                    # Small relationship boost for trading
                    self.adjust_relationship(player, 2)
                else:
                    print(f"{self.name} doesn't have enough money to buy {item.name}.")
            elif index == len(player.inventory):
                print("You decide not to sell anything.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")
    
    def attempt_influence(self, player):
        """Player attempts to influence the NPC."""
        relationship = self.get_relationship(player)
        street_cred = player.street_cred
        
        # Calculate influence chance based on relationship and street cred
        influence_chance = 20 + relationship / 2 + street_cred / 10
        influence_chance = max(5, min(95, influence_chance))  # Cap between 5% and 95%
        
        print(f"You try to influence {self.name}...")
        
        if random.randint(1, 100) <= influence_chance:
            self.influence_level += 1
            print(f"Success! {self.name} is now more likely to do what you want.")
            
            # Show influence options
            self.show_influence_options(player)
        else:
            print(f"Failed. {self.name} isn't convinced by your persuasion.")
            
            # Relationship penalty for failed influence
            self.adjust_relationship(player, -5)
    
    def show_influence_options(self, player):
        """Show options for what the player can influence the NPC to do."""
        print("\nWhat would you like to influence the NPC to do?")
        print("1. Spend money at a specific location")
        print("2. Create a distraction")
        print("3. Follow you")
        print("4. Nothing for now")
        
        choice = input("Your choice: ")
        
        if choice == "1":
            self.influence_spending(player)
        elif choice == "2":
            self.create_distraction(player)
        elif choice == "3":
            self.follow_player(player)
        elif choice == "4":
            print("You decide not to influence the NPC right now.")
        else:
            print("Invalid choice.")
    
    def influence_spending(self, player):
        """Influence the NPC to spend money at a specific location."""
        # In a real game, this would interact with a business/economy system
        print(f"You convince {self.name} to spend money at a business of your choice.")
        print("(This would affect business values in a full implementation)")
        
        # Relationship adjustment
        self.adjust_relationship(player, -2)  # Slight negative for manipulation
    
    def create_distraction(self, player):
        """Influence the NPC to create a distraction."""
        print(f"{self.name} creates a commotion, distracting everyone in the area!")
        print("(This would affect NPC behaviors in a full implementation)")
        
        # Relationship adjustment
        self.adjust_relationship(player, -3)  # Negative for manipulation
    
    def follow_player(self, player):
        """Influence the NPC to follow the player."""
        print(f"{self.name} agrees to follow you for a while.")
        self.set_property("following_player", True)
        
        # Relationship adjustment
        self.adjust_relationship(player, -1)  # Slight negative for manipulation
    
    def add_to_inventory(self, item):
        """Add an item to the NPC's inventory."""
        self.inventory.append(item)
        
    def remove_from_inventory(self, item_name):
        """Remove an item from the NPC's inventory."""
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item:
            self.inventory.remove(item)
            return item
        return None
    
    def set_relationship(self, entity, value):
        """Set relationship value with another entity (NPC or player)."""
        self.relationships[entity.name] = value
    
    def adjust_relationship(self, entity, amount):
        """Adjust relationship value with another entity."""
        current = self.get_relationship(entity)
        self.relationships[entity.name] = max(-100, min(100, current + amount))
        
    def get_relationship(self, entity):
        """Get relationship value with another entity."""
        return self.relationships.get(entity.name, 0)
    
    def set_schedule(self, time, activity, location=None):
        """Set the NPC's schedule for a specific time."""
        self.schedule[time] = (activity, location)
    
    def update_activity(self, current_time, npc_manager=None, area_manager=None):
        """Update the NPC's activity based on the current time and move to appropriate areas."""
        # Convert time string to minutes if it's a string (HH:MM format)
        if isinstance(current_time, str) and ":" in current_time:
            try:
                hour, minute = map(int, current_time.split(":"))
                current_time_minutes = hour * 60 + minute
            except ValueError:
                # If conversion fails, default to idle
                self.current_activity = "idle"
                return
        else:
            # If it's already an integer, use it directly
            current_time_minutes = current_time if isinstance(current_time, int) else 0
        
        # Find the closest scheduled time
        scheduled_times = sorted(self.schedule.keys())
        current_activity = "idle"
        scheduled_location = None
        
        for time in scheduled_times:
            if current_time_minutes >= time:
                current_activity, scheduled_location = self.schedule[time]
            else:
                break
        
        # Set the current activity
        self.current_activity = current_activity
        
        # Determine if we need to move the NPC
        need_to_move = False
        target_location = scheduled_location
        
        # If we have a scheduled location, use it
        if scheduled_location and scheduled_location != self.location:
            need_to_move = True
        
        # If we don't have a scheduled location or if the current location is not suitable
        # for the current activity, find a suitable location
        elif npc_manager and area_manager:
            # Check if current location is suitable
            if not self.location or not npc_manager.is_area_suitable_for_npc(self, self.location.id, self.current_activity):
                # Find a suitable area using the helper method
                target_location = npc_manager.find_suitable_area_for_npc(self, area_manager, self.current_activity)
                if target_location:
                    need_to_move = True
        
        # Move the NPC if needed
        if need_to_move and target_location:
            self.set_location(target_location)
            
            # If the NPC is in the middle of an action, interrupt it
            if self.is_action_ongoing():
                self.interrupt_action()
            
        # Update the current action based on the activity
        self.update_action()
        
    def update_action(self):
        """Update the NPC's current action based on their activity."""
        # Check if current action is still valid based on duration
        if (self.current_action_start_time is not None and 
            self.current_action_duration > 0 and 
            not self.interrupted):
            # If the action is still valid, don't change it
            return
            
        activity_actions = {
            "idle": ["standing around", "looking at their phone", "waiting patiently", "daydreaming"],
            "walking": ["walking around", "strolling", "exploring the area"],
            "eating": ["eating a meal", "having a snack", "enjoying some food"],
            "shopping": ["browsing items", "shopping", "looking at merchandise"],
            "sleeping": ["sleeping", "resting", "taking a nap"],
            "working": ["working", "focusing on a task", "being productive"],
            "patrolling": ["patrolling the area", "keeping watch", "looking for trouble"],
            "guarding": ["guarding the area", "standing alert", "watching for intruders"],
            "meeting": ["in a meeting", "talking with others", "discussing plans"],
            "dealing": ["making deals", "negotiating", "exchanging goods"],
            "opening_shop": ["opening their shop", "setting up for business", "preparing for customers"],
            "selling": ["selling goods", "helping customers", "managing their shop"],
            "closing_shop": ["closing their shop", "cleaning up", "counting money"]
        }
        
        # Get possible actions for the current activity
        possible_actions = activity_actions.get(self.current_activity, ["doing something"])
        
        # Randomly select an action
        import random
        new_action = random.choice(possible_actions)
        
        # Store the previous action in memory if it's different
        if self.current_action and self.current_action != new_action:
            self.remember_action(self.current_action, self.action_target)
            
        # Set the new action
        self.current_action = new_action
        self.current_action_start_time = datetime.now()
        
        # Set a random duration between 5-15 minutes for continuity
        self.current_action_duration = random.randint(5, 15)
        self.action_target = None
        self.interrupted = False
        
    def remember_action(self, action, target=None):
        """Add an action to the NPC's memory."""
        # Create a memory entry
        memory = {
            "action": action,
            "time": datetime.now(),
            "target": target.name if hasattr(target, 'name') else target,
            "location": self.location.name if self.location else None
        }
        
        # Add to memory (keep only the last 10 actions)
        self.action_memory.insert(0, memory)
        if len(self.action_memory) > 10:
            self.action_memory.pop()
            
    def set_action(self, action, target=None, duration=10):
        """Set a specific action for the NPC with a duration."""
        # Remember the current action if it exists
        if self.current_action:
            self.remember_action(self.current_action, self.action_target)
            
        # Set the new action
        self.current_action = action
        self.current_action_start_time = datetime.now()
        self.current_action_duration = duration
        self.action_target = target
        self.interrupted = False
        
    def interrupt_action(self):
        """Interrupt the current action."""
        if self.current_action:
            self.remember_action(self.current_action, self.action_target)
            self.interrupted = True
            
    def get_action_time_remaining(self):
        """Get the time remaining for the current action in minutes."""
        if not self.current_action_start_time or self.interrupted:
            return 0
            
        elapsed = (datetime.now() - self.current_action_start_time).total_seconds() / 60
        remaining = max(0, self.current_action_duration - elapsed)
        return remaining
        
    def is_action_ongoing(self):
        """Check if the current action is still ongoing."""
        return self.get_action_time_remaining() > 0 and not self.interrupted
        
    def get_recent_actions(self, count=3):
        """Get the most recent actions from memory."""
        return self.action_memory[:count]
        
    def react_to_player_action(self, player, action_type, action_target=None):
        """React to a player action happening nearby."""
        # Skip if NPC is not in the same location as the player
        if not self.location or self.location != player.current_area:
            return None
            
        # Different reactions based on action type
        if action_type == "attack":
            # Player is attacking someone/something
            if action_target == self:
                # Player is attacking this NPC
                self.interrupt_action()
                self.set_action("defending against attack", player, 5)
                return f"{self.name} tries to defend against your attack!"
            elif isinstance(action_target, NPC) and action_target.location == self.location:
                # Player is attacking another NPC in the same area
                relationship_with_target = self.get_relationship(action_target)
                
                if relationship_with_target > 30:
                    # NPC likes the target, might help them
                    self.interrupt_action()
                    self.set_action("trying to help", action_target, 5)
                    return f"{self.name} rushes to help {action_target.name}!"
                elif relationship_with_target < -30:
                    # NPC dislikes the target, might cheer
                    self.interrupt_action()
                    self.set_action("cheering", player, 3)
                    return f"{self.name} cheers as you attack {action_target.name}!"
                else:
                    # Neutral relationship, just watch
                    self.interrupt_action()
                    self.set_action("watching nervously", None, 4)
                    return f"{self.name} backs away, watching nervously."
        
        elif action_type == "steal":
            # Player is stealing
            if random.random() < 0.5:  # 50% chance to notice
                self.interrupt_action()
                self.set_action("looking suspicious", player, 3)
                
                # Adjust relationship negatively
                self.adjust_relationship(player, -10)
                
                return f"{self.name} notices your suspicious behavior and frowns."
        
        elif action_type == "hack":
            # Player is hacking something
            if random.random() < 0.3:  # 30% chance to notice
                self.interrupt_action()
                self.set_action("watching curiously", player, 4)
                return f"{self.name} watches your hacking attempt with curiosity."
        
        elif action_type == "talk":
            # Player is talking to someone else
            if action_target and action_target != self and random.random() < 0.2:
                # Small chance to join the conversation
                self.interrupt_action()
                self.set_action("joining the conversation", action_target, 5)
                return f"{self.name} approaches to join your conversation with {action_target.name}."
        
        # No reaction
        return None
        
    def patrol(self):
        """Patrol behavior for gang members."""
        if not self.location:
            return
            
        # Move randomly within the area
        import random
        grid_x = random.randint(0, self.location.grid_width - 1)
        grid_y = random.randint(0, self.location.grid_length - 1)
        
        # Update coordinates
        self.coordinates.x = self.location.coordinates.x + grid_x
        self.coordinates.y = self.location.coordinates.y + grid_y
        
        # Update action
        self.current_action = "patrolling the area"
        
    def interact_with_environment(self):
        """Interact with the environment (for civilians)."""
        if not self.location:
            return
            
        # Possible environmental interactions
        interactions = [
            "watering plants", "picking up trash", "examining objects",
            "taking notes", "taking photos", "chatting with others",
            "sitting on a bench", "leaning against a wall", "looking at the sky"
        ]
        
        # Randomly select an interaction
        import random
        self.current_action = random.choice(interactions)
    
    def set_property(self, key, value):
        """Set a custom property for this NPC."""
        self.properties[key] = value
    
    def get_property(self, key, default=None):
        """Get a custom property for this NPC."""
        return self.properties.get(key, default)
    
    def to_dict(self):
        """Convert NPC to dictionary for serialization."""
        # Convert action memory to serializable format
        serialized_memory = []
        for memory in self.action_memory:
            serialized_memory.append({
                "action": memory["action"],
                "time": memory["time"].isoformat() if isinstance(memory["time"], datetime) else str(memory["time"]),
                "target": memory["target"].id if hasattr(memory["target"], 'id') else memory["target"],
                "location": memory["location"]
            })
            
        # Convert action target to serializable format
        action_target_id = None
        if self.action_target:
            if hasattr(self.action_target, 'id'):
                action_target_id = self.action_target.id
            elif hasattr(self.action_target, 'name'):
                action_target_id = f"name:{self.action_target.name}"
                
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "coordinates": self.coordinates.to_dict(),
            "dialogue": self.dialogue,
            "personality": self.personality,
            "relationships": self.relationships,
            "money": self.money,
            "properties": self.properties,
            "influence_level": self.influence_level,
            "schedule": {k: (v[0], v[1].id if v[1] else None) for k, v in self.schedule.items()},
            "inventory": [item.id for item in self.inventory],
            "gang": self.gang,
            "behavior_type": self.behavior_type,
            "current_action": self.current_action,
            "current_action_start_time": self.current_action_start_time.isoformat() if self.current_action_start_time else None,
            "current_action_duration": self.current_action_duration,
            "action_target": action_target_id,
            "interrupted": self.interrupted,
            "action_memory": serialized_memory
        }
    
    @classmethod
    def from_dict(cls, data, location_resolver=None, item_resolver=None, npc_resolver=None):
        """Create NPC from dictionary."""
        npc = cls(
            data["name"],
            data["description"],
            Coordinates.from_dict(data["coordinates"]),
            data["dialogue"],
            data["personality"],
            data["money"],
            data["relationships"],
            data["properties"]
        )
        npc.id = data.get("id", npc.id)
        npc.influence_level = data.get("influence_level", 0)
        npc.gang = data.get("gang", None)
        npc.behavior_type = data.get("behavior_type", "normal")
        
        # Restore action state
        npc.current_action = data.get("current_action")
        
        # Restore action start time
        start_time_str = data.get("current_action_start_time")
        if start_time_str:
            try:
                npc.current_action_start_time = datetime.fromisoformat(start_time_str)
            except (ValueError, TypeError):
                npc.current_action_start_time = None
                
        npc.current_action_duration = data.get("current_action_duration", 0)
        npc.interrupted = data.get("interrupted", False)
        
        # Action memory will be restored after all NPCs and items are loaded
        npc.action_memory = []  # Initialize empty memory to be filled later
        
        # Resolve schedule if location_resolver is provided
        if location_resolver and "schedule" in data:
            for time, (activity, location_id) in data["schedule"].items():
                if location_id:
                    location = location_resolver(location_id)
                    if location:
                        npc.schedule[time] = (activity, location)
        
        # Resolve inventory if item_resolver is provided
        if item_resolver and "inventory" in data:
            for item_id in data["inventory"]:
                item = item_resolver(item_id)
                if item:
                    npc.inventory.append(item)
        
        return npc


class Civilian(NPC):
    """A civilian NPC with normal behavior."""
    def __init__(self, name, description, coordinates=None, dialogue=None, personality=None, 
                 money=0, relationships=None, properties=None, inventory=None, schedule=None):
        super().__init__(name, description, coordinates, dialogue, personality, 
                         money, relationships, properties, inventory, schedule)
        self.behavior_type = "civilian"
    
    def interact_with_environment(self):
        """Civilians interact with the environment in various ways."""
        if not self.location:
            return
        
        # Check for soil plots to plant seeds
        for obj in self.location.objects:
            if obj.__class__.__name__ == "SoilPlot" and not obj.has_plant:
                # Look for seeds in inventory
                seed = next((item for item in self.inventory if item.__class__.__name__ == "Seed"), None)
                if seed:
                    print(f"{self.name} plants a {seed.name} in the soil plot.")
                    obj.plant(seed)
                    self.inventory.remove(seed)
                    return
        
        # Check for plants to water
        for obj in self.location.objects:
            if obj.__class__.__name__ == "SoilPlot" and obj.has_plant and obj.plant.needs_water:
                # Look for watering can in inventory
                watering_can = next((item for item in self.inventory if item.__class__.__name__ == "WateringCan"), None)
                if watering_can:
                    print(f"{self.name} waters the {obj.plant.name}.")
                    obj.water()
                    return


class GangMember(NPC):
    """A gang member NPC with gang-specific behavior."""
    def __init__(self, name, description, gang, coordinates=None, dialogue=None, personality=None, 
                 money=0, relationships=None, properties=None, inventory=None, schedule=None):
        super().__init__(name, description, coordinates, dialogue, personality, 
                         money, relationships, properties, inventory, schedule, gang)
        self.behavior_type = "gang_member"
        self.patrol_radius = 3  # How far the gang member patrols from their base
    
    def patrol(self):
        """Gang members patrol their territory."""
        if not self.location:
            return
        
        # Simple patrol behavior - move randomly within patrol radius
        if random.random() < 0.3:  # 30% chance to move each turn
            grid_x, grid_y, grid_z = self.location.get_relative_coordinates(self.coordinates)
            
            # Choose a random direction
            directions = ["north", "south", "east", "west"]
            direction = random.choice(directions)
            
            # Calculate new position
            new_x, new_y = grid_x, grid_y
            if direction == "north":
                new_y += 1
            elif direction == "south":
                new_y -= 1
            elif direction == "east":
                new_x += 1
            elif direction == "west":
                new_x -= 1
            
            # Check if new position is within area bounds and patrol radius
            if (0 <= new_x < self.location.grid_width and 
                0 <= new_y < self.location.grid_length and
                abs(new_x - grid_x) <= self.patrol_radius and
                abs(new_y - grid_y) <= self.patrol_radius):
                
                # Update gang member coordinates
                self.coordinates = Coordinates(
                    self.location.coordinates.x + new_x,
                    self.location.coordinates.y + new_y,
                    self.location.coordinates.z
                )
                print(f"{self.name} patrols {direction}.")


class Gang:
    """A gang with multiple members and territory."""
    def __init__(self, name, territory=None, members=None, properties=None):
        self.name = name
        self.territory = territory or []  # List of area IDs that are gang territory
        self.members = members or []  # List of gang member IDs
        self.properties = properties or {}  # Custom properties
        self.id = f"gang_{name.lower().replace(' ', '_')}"
    
    def add_member(self, member):
        """Add a member to the gang."""
        if member.id not in self.members:
            self.members.append(member.id)
            member.gang = self.name
    
    def remove_member(self, member):
        """Remove a member from the gang."""
        if member.id in self.members:
            self.members.remove(member.id)
            if member.gang == self.name:
                member.gang = None
    
    def claim_territory(self, area):
        """Claim an area as gang territory."""
        if area.id not in self.territory:
            self.territory.append(area.id)
            area.set_property("controlling_gang", self.name)
    
    def abandon_territory(self, area):
        """Abandon an area as gang territory."""
        if area.id in self.territory:
            self.territory.remove(area.id)
            if area.get_property("controlling_gang") == self.name:
                area.set_property("controlling_gang", None)
    
    def to_dict(self):
        """Convert gang to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "territory": self.territory,
            "members": self.members,
            "properties": self.properties
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create gang from dictionary."""
        gang = cls(
            data["name"],
            data["territory"],
            data["members"],
            data["properties"]
        )
        gang.id = data.get("id", gang.id)
        return gang


class BehaviorType:
    """Types of NPC behaviors."""
    IDLE = "idle"
    TALK = "talk"
    FIGHT = "fight"
    USE_ITEM = "use_item"
    GARDENING = "gardening"
    GIFT = "gift"
    TECH = "tech"
    SUSPICIOUS = "suspicious"
    PATROL = "patrol"
    INTERACT = "interact"


class NPCBehaviorCoordinator:
    """Coordinates and manages NPC behaviors."""
    def __init__(self, max_npc_actions_per_turn=10, max_actions_per_npc=2):
        self.max_npc_actions_per_turn = max_npc_actions_per_turn
        self.max_actions_per_npc = max_actions_per_npc
        self.current_turn = 0
        self.action_messages = []  # Stores NPC action messages for the current turn
        
        # Load NPC actions from JSON file or use defaults
        self.actions_data = self._load_actions_data()
        
        # Track NPC actions this turn
        self.npc_actions_this_turn = {}
        
        # Behavior cooldowns (in turns)
        self.cooldowns = {
            BehaviorType.IDLE: 1,      # 1 turn between idle behaviors
            BehaviorType.TALK: 2,      # 2 turns between talking
            BehaviorType.FIGHT: 3,     # 3 turns between fighting
            BehaviorType.USE_ITEM: 1,  # 1 turn between using items
            BehaviorType.GARDENING: 2, # 2 turns between gardening activities
            BehaviorType.GIFT: 5,      # 5 turns between gifting
            BehaviorType.PATROL: 1,    # 1 turn between patrol actions
            BehaviorType.INTERACT: 2,  # 2 turns between interactions
        }
        
        # Last turn each behavior was performed (per NPC)
        self.last_behavior_turn = {}
    
    def _load_actions_data(self):
        """Load NPC actions from JSON file or use defaults."""
        try:
            data_dir = "data"
            file_path = os.path.join(data_dir, 'npc_actions.json')
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
            
        # Return default actions if file not found or invalid
        return {
            "idle": {
                "singular": ["stands around looking bored", "checks their phone", "daydreams", "stretches", "yawns"],
                "plural": ["stand around looking bored", "check their phones", "daydream", "stretch", "yawn"]
            },
            "talk": {
                "singular": ["talks with someone nearby", "whispers something", "tells a joke", "shares gossip", "complains about the weather"],
                "plural": ["talk with others", "whisper something", "tell jokes", "share gossip", "complain about the weather"]
            },
            "fight": {
                "singular": ["looks for trouble", "clenches their fists", "threatens someone", "shows off their weapon", "cracks their knuckles"],
                "plural": ["look for trouble", "clench their fists", "threaten others", "show off their weapons", "crack their knuckles"]
            },
            "use_item": {
                "singular": ["uses an item", "examines something in their hands", "fiddles with a gadget", "plays with a tech device"],
                "plural": ["use items", "examine things in their hands", "fiddle with gadgets", "play with tech devices"]
            },
            "gardening": {
                "singular": ["tends to plants", "waters a plant", "plants a seed", "checks soil moisture", "removes weeds"],
                "plural": ["tend to plants", "water plants", "plant seeds", "check soil moisture", "remove weeds"]
            },
            "gift": {
                "singular": ["offers a gift to someone", "shares something with a friend", "gives away an item"],
                "plural": ["offer gifts to others", "share things with friends", "give away items"]
            },
            "patrol": {
                "singular": ["patrols the area", "keeps watch", "looks for intruders", "guards their territory"],
                "plural": ["patrol the area", "keep watch", "look for intruders", "guard their territory"]
            },
            "interact": {
                "singular": ["interacts with the environment", "examines surroundings", "investigates something interesting"],
                "plural": ["interact with the environment", "examine surroundings", "investigate interesting things"]
            }
        }
    
    def can_perform_behavior(self, npc, behavior_type):
        """Check if an NPC can perform a behavior based on cooldowns."""
        # Get the NPC's last behavior times
        npc_id = npc.id
        if npc_id not in self.last_behavior_turn:
            self.last_behavior_turn[npc_id] = {}
        
        # If behavior has never been performed, allow it
        if behavior_type not in self.last_behavior_turn[npc_id]:
            return True
        
        # Check if cooldown has elapsed
        cooldown = self.cooldowns.get(behavior_type, 0)
        last_turn = self.last_behavior_turn[npc_id].get(behavior_type, 0)
        
        return (self.current_turn - last_turn) >= cooldown
    
    def record_behavior(self, npc, behavior_type):
        """Record that an NPC performed a behavior."""
        npc_id = npc.id
        if npc_id not in self.last_behavior_turn:
            self.last_behavior_turn[npc_id] = {}
        
        self.last_behavior_turn[npc_id][behavior_type] = self.current_turn
    
    def process_npc_behaviors(self, game, npcs):
        """
        Process NPC behaviors for the current turn, enforcing limits.
        
        Args:
            game: The main game instance.
            npcs: List of NPCs in the current area.
            
        Returns:
            A formatted string of NPC action messages.
        """
        self.action_messages = []
        self.npc_actions_this_turn = {}
        actions_taken = 0
        
        # Shuffle NPCs to randomize action order
        random_npcs = list(npcs)
        random.shuffle(random_npcs)
        
        # Group NPCs by type for more natural behavior patterns
        civilians = [npc for npc in random_npcs if isinstance(npc, Civilian) or npc.behavior_type == "civilian"]
        gang_members = [npc for npc in random_npcs if isinstance(npc, GangMember) or npc.behavior_type == "gang_member"]
        
        # Process gang members first (they're more active)
        for npc in gang_members:
            if actions_taken >= self.max_npc_actions_per_turn:
                break  # Stop if we've reached the max actions for this turn
                
            # Get actions for this NPC
            npc_actions = self.get_npc_actions(npc, game)
            if npc_actions:
                self.action_messages.extend(npc_actions)
                actions_taken += 1
        
        # Then process civilians
        for npc in civilians:
            if actions_taken >= self.max_npc_actions_per_turn:
                break  # Stop if we've reached the max actions for this turn
                
            # Get actions for this NPC
            npc_actions = self.get_npc_actions(npc, game)
            if npc_actions:
                self.action_messages.extend(npc_actions)
                actions_taken += 1
        
        # Increment turn counter
        self.current_turn += 1
        
        # Group and format the action messages
        return self.format_action_messages()
    
    def get_npc_actions(self, npc, game):
        """Get actions for a specific NPC based on their type, state, and action continuity."""
        actions = []
        
        # Skip dead NPCs
        if hasattr(npc, 'is_alive') and not npc.is_alive:
            return actions
            
        # Check if NPC has already acted this turn
        if npc.id in self.npc_actions_this_turn and self.npc_actions_this_turn[npc.id] >= self.max_actions_per_npc:
            return actions
            
        # Initialize action count for this NPC
        if npc.id not in self.npc_actions_this_turn:
            self.npc_actions_this_turn[npc.id] = 0
            
        # Check if the NPC is continuing an ongoing action
        if npc.is_action_ongoing():
            # Continue the current action
            if npc.action_target and hasattr(npc.action_target, 'name'):
                # Action with a target
                actions.append(f"{npc.name} continues {npc.current_action} with {npc.action_target.name}.")
            else:
                # Action without a specific target
                actions.append(f"{npc.name} continues {npc.current_action}.")
                
            self.npc_actions_this_turn[npc.id] += 1
            return actions
            
        # Process gang member behaviors
        if isinstance(npc, GangMember) or npc.behavior_type == "gang_member":
            # Patrol behavior
            if npc.current_activity == "patrolling" and self.can_perform_behavior(npc, BehaviorType.PATROL):
                # Get patrol action
                patrol_action = self.get_patrol_action(npc)
                if patrol_action:
                    actions.append(patrol_action)
                    self.record_behavior(npc, BehaviorType.PATROL)
                    
                    # Set the action with a duration
                    direction = patrol_action.split(" ")[-1].rstrip(".")
                    npc.set_action(f"patrolling {direction}", None, random.randint(5, 10))
                    
                    self.npc_actions_this_turn[npc.id] += 1
            
            # Fighting behavior
            elif random.random() < 0.3 and self.can_perform_behavior(npc, BehaviorType.FIGHT):
                # Find potential targets in the same area
                if npc.location and hasattr(npc.location, 'npcs'):
                    potential_targets = [other for other in npc.location.npcs 
                                        if other != npc and 
                                        (not hasattr(other, 'is_alive') or other.is_alive)]
                                        
                    if potential_targets:
                        target = random.choice(potential_targets)
                        
                        # Check if they're from different gangs
                        if (isinstance(target, GangMember) or target.behavior_type == "gang_member") and target.gang != npc.gang:
                            fight_action = f"{npc.name} threatens {target.name} with a menacing gesture."
                            actions.append(fight_action)
                            self.record_behavior(npc, BehaviorType.FIGHT)
                            
                            # Set the action with a duration and target
                            npc.set_action("threatening", target, random.randint(5, 8))
                            
                            # Also set a reaction for the target
                            if random.random() < 0.7:  # 70% chance to react
                                target.set_action("looking nervous", npc, random.randint(3, 6))
                            
                            self.npc_actions_this_turn[npc.id] += 1
        
        # Process civilian behaviors
        elif isinstance(npc, Civilian) or npc.behavior_type == "civilian":
            # Gardening behavior
            if random.random() < 0.4 and self.can_perform_behavior(npc, BehaviorType.GARDENING):
                gardening_action = self.get_gardening_action(npc)
                if gardening_action:
                    actions.append(gardening_action)
                    self.record_behavior(npc, BehaviorType.GARDENING)
                    
                    # Set the action with a duration
                    action_text = gardening_action.split(" ", 1)[1].rstrip(".")
                    npc.set_action(action_text, None, random.randint(8, 15))  # Gardening takes time
                    
                    self.npc_actions_this_turn[npc.id] += 1
            
            # Talking behavior
            elif random.random() < 0.5 and self.can_perform_behavior(npc, BehaviorType.TALK):
                # Find other NPCs to talk to
                if npc.location and hasattr(npc.location, 'npcs'):
                    other_npcs = [other for other in npc.location.npcs if other != npc]
                    if other_npcs:
                        other_npc = random.choice(other_npcs)
                        
                        # Check if the other NPC is already engaged
                        if not other_npc.is_action_ongoing() or random.random() < 0.3:  # 30% chance to interrupt
                            talk_topics = ["local gossip", "the weather", "recent events", "their day", "funny stories"]
                            topic = random.choice(talk_topics)
                            
                            talk_action = f"{npc.name} chats with {other_npc.name} about {topic}."
                            actions.append(talk_action)
                            self.record_behavior(npc, BehaviorType.TALK)
                            
                            # Set the action with a duration and target for both NPCs
                            talk_duration = random.randint(5, 12)
                            npc.set_action(f"chatting about {topic}", other_npc, talk_duration)
                            
                            # Set the other NPC to also be chatting
                            other_npc.set_action(f"chatting about {topic}", npc, talk_duration)
                            
                            self.npc_actions_this_turn[npc.id] += 1
        
        # General behaviors for all NPCs
        
        # Item usage behavior
        if not actions and random.random() < 0.3 and self.can_perform_behavior(npc, BehaviorType.USE_ITEM):
            item_action = self.get_item_usage_action(npc)
            if item_action:
                actions.append(item_action)
                self.record_behavior(npc, BehaviorType.USE_ITEM)
                
                # Set the action with a duration
                action_text = item_action.split(" ", 1)[1].rstrip(".")
                
                # Extract item name if possible
                item_name = None
                if "their " in action_text:
                    item_name = action_text.split("their ")[1].split(" ")[0]
                
                # Find the actual item in inventory if possible
                item_obj = None
                if item_name and npc.inventory:
                    for item in npc.inventory:
                        if item_name.lower() in item.name.lower():
                            item_obj = item
                            break
                
                npc.set_action(action_text, item_obj, random.randint(3, 8))
                self.npc_actions_this_turn[npc.id] += 1
        
        # Environment interaction behavior
        elif not actions and random.random() < 0.3 and self.can_perform_behavior(npc, BehaviorType.INTERACT):
            interact_action = self.get_environment_interaction(npc)
            if interact_action:
                actions.append(interact_action)
                self.record_behavior(npc, BehaviorType.INTERACT)
                
                # Set the action with a duration
                action_text = interact_action.split(" ", 1)[1].rstrip(".")
                
                # Extract object name if possible
                obj_name = None
                if "the " in action_text:
                    obj_name = action_text.split("the ")[1].split(" ")[0]
                
                # Find the actual object if possible
                obj = None
                if obj_name and npc.location and hasattr(npc.location, 'objects'):
                    for location_obj in npc.location.objects:
                        if hasattr(location_obj, 'name') and obj_name.lower() in location_obj.name.lower():
                            obj = location_obj
                            break
                
                npc.set_action(action_text, obj, random.randint(5, 10))
                self.npc_actions_this_turn[npc.id] += 1
                
        # If no specific actions, use current action from NPC
        if not actions and npc.current_action:
            actions.append(f"{npc.name} {npc.current_action}.")
            
        return actions
    
    def get_patrol_action(self, npc):
        """Get a patrol action for a gang member."""
        if not hasattr(npc, 'patrol') or not npc.location:
            return None
            
        # Choose a random direction
        directions = ["north", "south", "east", "west"]
        direction = random.choice(directions)
        
        # Get a random patrol action
        patrol_actions = [
            f"patrols {direction}",
            f"keeps watch to the {direction}",
            f"guards the {direction} entrance",
            f"surveys the {direction} area"
        ]
        
        action = random.choice(patrol_actions)
        return f"{npc.name} {action}."
    
    def get_gardening_action(self, npc):
        """Get a gardening action for an NPC."""
        if not npc.location:
            return None
            
        # Check for gardening opportunities
        soil_plots = [obj for obj in npc.location.objects if hasattr(obj, 'add_plant') or hasattr(obj, 'water')]
        
        if not soil_plots:
            return None
            
        soil_plot = random.choice(soil_plots)
        
        # Check for seeds in inventory
        seeds = [item for item in npc.inventory if hasattr(item, 'plant_type')]
        
        if seeds and hasattr(soil_plot, 'add_plant') and not getattr(soil_plot, 'has_plant', True):
            seed = random.choice(seeds)
            gardening_actions = [
                f"plants a {seed.name} in the soil",
                f"carefully places a {seed.name} in the ground",
                f"digs a small hole and plants a {seed.name}"
            ]
            return f"{npc.name} {random.choice(gardening_actions)}."
            
        # Check for watering can
        watering_cans = [item for item in npc.inventory if hasattr(item, 'uses') and getattr(item, 'tool_type', '') == 'watering']
        
        if watering_cans and hasattr(soil_plot, 'water'):
            watering_can = watering_cans[0]
            gardening_actions = [
                f"waters the plants with a {watering_can.name}",
                f"sprinkles water on the soil",
                f"carefully waters each plant"
            ]
            return f"{npc.name} {random.choice(gardening_actions)}."
            
        return None
    
    def get_item_usage_action(self, npc):
        """Get an item usage action for an NPC."""
        if not npc.inventory:
            return None
            
        # Choose a random item from inventory
        item = random.choice(npc.inventory)
        
        # Different actions based on item type
        if hasattr(item, 'damage'):  # Weapon
            actions = [
                f"examines their {item.name} carefully",
                f"polishes their {item.name}",
                f"practices with their {item.name}"
            ]
        elif hasattr(item, 'effect_type'):  # Tech or effect item
            actions = [
                f"fiddles with their {item.name}",
                f"configures their {item.name}",
                f"tests their {item.name}"
            ]
        elif hasattr(item, 'nutrition'):  # Consumable
            actions = [
                f"consumes a {item.name}",
                f"enjoys a {item.name}",
                f"quickly eats a {item.name}"
            ]
        else:  # Generic item
            actions = [
                f"examines their {item.name}",
                f"shows off their {item.name}",
                f"checks their {item.name}"
            ]
            
        return f"{npc.name} {random.choice(actions)}."
    
    def get_environment_interaction(self, npc):
        """Get an environment interaction for an NPC."""
        if not npc.location:
            return None
            
        # Check for interactive objects in the environment
        interactive_objects = [obj for obj in npc.location.objects 
                              if hasattr(obj, 'interact') or 
                              type(obj).__name__ in ['Computer', 'VendingMachine', 'HidingSpot']]
        
        if interactive_objects:
            obj = random.choice(interactive_objects)
            obj_type = type(obj).__name__
            
            if obj_type == 'Computer':
                actions = [
                    f"types on the {obj.name}",
                    f"checks emails on the {obj.name}",
                    f"runs a program on the {obj.name}"
                ]
            elif obj_type == 'VendingMachine':
                actions = [
                    f"buys something from the {obj.name}",
                    f"examines the options in the {obj.name}",
                    f"inserts money into the {obj.name}"
                ]
            elif obj_type == 'HidingSpot':
                actions = [
                    f"peeks inside the {obj.name}",
                    f"checks behind the {obj.name}",
                    f"looks around the {obj.name}"
                ]
            else:
                actions = [
                    f"interacts with the {obj.name}",
                    f"examines the {obj.name}",
                    f"shows interest in the {obj.name}"
                ]
                
            return f"{npc.name} {random.choice(actions)}."
            
        # Generic environment interactions if no specific objects
        generic_actions = [
            "looks around curiously",
            "examines the surroundings",
            "takes in the scenery",
            "observes the area carefully"
        ]
        
        return f"{npc.name} {random.choice(generic_actions)}."
    
    def format_action_messages(self):
        """Format action messages into a readable summary with improved readability."""
        if not self.action_messages:
            return None
            
        # Group similar actions
        action_groups = {}
        
        for message in self.action_messages:
            # Extract NPC name and action
            parts = message.split(" ", 1)
            if len(parts) < 2:
                continue
                
            npc_name = parts[0]
            action = parts[1]
            
            # Remove trailing period for grouping
            if action.endswith("."):
                action = action[:-1]
                
            # Group by action
            if action not in action_groups:
                action_groups[action] = []
            action_groups[action].append(npc_name)
        
        # Categorize actions by type for better organization
        action_categories = {
            "combat": [],      # Fighting, threatening, etc.
            "patrol": [],      # Patrolling, guarding, etc.
            "social": [],      # Talking, chatting, etc.
            "item_use": [],    # Using items, examining objects, etc.
            "movement": [],    # Walking, exploring, etc.
            "other": []        # Everything else
        }
        
        # Limit to a maximum of 5 different action groups for readability
        sorted_groups = sorted(action_groups.items(), key=lambda x: len(x[1]), reverse=True)
        if len(sorted_groups) > 5:
            sorted_groups = sorted_groups[:5]
            
        # Format each action group and categorize it
        for action, npc_names in sorted_groups:
            # Format the message based on number of NPCs
            if len(npc_names) == 1:
                # Single NPC
                formatted_msg = f"{npc_names[0]} {action}."
            elif len(npc_names) == 2:
                # Two NPCs
                formatted_msg = f"{npc_names[0]} and {npc_names[1]} {action}."
            elif len(npc_names) == 3:
                # Three NPCs - list all names
                formatted_msg = f"{npc_names[0]}, {npc_names[1]}, and {npc_names[2]} {action}."
            else:
                # More than three NPCs - list first three and summarize the rest
                others_count = len(npc_names) - 3
                formatted_msg = f"{npc_names[0]}, {npc_names[1]}, {npc_names[2]} and {others_count} others {action}."
            
            # Categorize the message
            action_lower = action.lower()
            if any(word in action_lower for word in ["fight", "attack", "threaten", "punch", "kick", "shoot"]):
                action_categories["combat"].append(formatted_msg)
            elif any(word in action_lower for word in ["patrol", "guard", "watch", "survey"]):
                action_categories["patrol"].append(formatted_msg)
            elif any(word in action_lower for word in ["talk", "chat", "discuss", "whisper", "gossip"]):
                action_categories["social"].append(formatted_msg)
            elif any(word in action_lower for word in ["use", "examine", "hold", "carry", "eat", "drink"]):
                action_categories["item_use"].append(formatted_msg)
            elif any(word in action_lower for word in ["walk", "move", "stroll", "explore"]):
                action_categories["movement"].append(formatted_msg)
            else:
                action_categories["other"].append(formatted_msg)
        
        # Combine messages by category with appropriate connectors
        result_parts = []
        
        # Process combat messages first (they're most important)
        if action_categories["combat"]:
            combat_msg = self._combine_category_messages(action_categories["combat"], "Suddenly, ")
            result_parts.append(combat_msg)
            
        # Then patrol messages
        if action_categories["patrol"]:
            patrol_msg = self._combine_category_messages(action_categories["patrol"], "Meanwhile, ")
            result_parts.append(patrol_msg)
            
        # Then social interactions
        if action_categories["social"]:
            social_msg = self._combine_category_messages(action_categories["social"], "Nearby, ")
            result_parts.append(social_msg)
            
        # Then item usage
        if action_categories["item_use"]:
            item_msg = self._combine_category_messages(action_categories["item_use"])
            result_parts.append(item_msg)
            
        # Then movement
        if action_categories["movement"]:
            movement_msg = self._combine_category_messages(action_categories["movement"])
            result_parts.append(movement_msg)
            
        # Finally other actions
        if action_categories["other"]:
            other_msg = self._combine_category_messages(action_categories["other"])
            result_parts.append(other_msg)
        
        # Join all parts with paragraph breaks for better readability
        return "\n".join(result_parts)
        
    def _combine_category_messages(self, messages, first_connector=""):
        """Combine messages within a category."""
        if not messages:
            return ""
            
        result = first_connector + messages[0]
        
        # Add remaining messages with appropriate connectors
        for i in range(1, len(messages)):
            if i == len(messages) - 1 and len(messages) > 1:
                # Last message
                result += f" while {messages[i][0].lower()}{messages[i][1:]}"
            else:
                # Middle messages
                connectors = [" At the same time, ", " Also, ", " Nearby, "]
                result += f"{random.choice(connectors)}{messages[i]}"
                
        return result


class NPCManager:
    """Manages all NPCs in the game."""
    def __init__(self):
        self.npcs = {}  # Dictionary mapping NPC IDs to NPC objects
        self.templates = {}  # Dictionary of NPC templates
        self.gangs = {}  # Dictionary mapping gang IDs to Gang objects
        self.behavior_coordinator = NPCBehaviorCoordinator()  # Coordinates NPC behaviors
        
        # Define restricted areas where NPCs shouldn't spawn
        self.restricted_areas = ["home"]  # Player's home is off-limits for NPCs
        
        # Define appropriate areas for different NPC types and activities
        self.area_suitability = {
            "civilian": {
                "idle": ["plaza", "garden", "street"],
                "walking": ["street", "plaza", "garden", "alley"],
                "shopping": ["street"],
                "eating": ["plaza", "street"],
                "working": ["street", "office_floor"],
                "sleeping": [],  # Will be filled with homes/apartments when implemented
                "gardening": ["garden"]
            },
            "gang_member": {
                "idle": [],  # Will be filled with gang territories
                "patrolling": [],  # Will be filled with gang territories
                "guarding": [],  # Will be filled with gang territories
                "meeting": [],  # Will be filled with gang territories
                "dealing": ["alley", "construction_site"],
                "fighting": []  # Can be anywhere, but preferably in territories
            },
            "shopkeeper": {
                "idle": ["street"],
                "opening_shop": ["street"],
                "selling": ["street"],
                "closing_shop": ["street"]
            }
        }
    
    def add_npc(self, npc):
        """Add an NPC to the manager."""
        self.npcs[npc.id] = npc
        
    def is_area_suitable_for_npc(self, npc, area_id, activity=None):
        """Check if an area is suitable for an NPC based on their type and activity."""
        # Player's home is off-limits for NPCs
        if area_id in self.restricted_areas:
            return False
            
        # If no specific activity is provided, use the NPC's current activity
        if activity is None:
            activity = npc.current_activity
            
        # Determine NPC type
        npc_type = "civilian"
        if isinstance(npc, GangMember) or npc.behavior_type == "gang_member":
            npc_type = "gang_member"
        elif npc.name == "Shopkeeper":
            npc_type = "shopkeeper"
            
        # Check if the area is suitable for this NPC type and activity
        suitable_areas = self.area_suitability.get(npc_type, {}).get(activity, [])
        
        # Gang members can always be in their gang's territory
        if npc_type == "gang_member" and hasattr(npc, 'gang') and npc.gang:
            gang = self.gangs.get(npc.gang)
            if gang and area_id in [territory.id for territory in gang.territories]:
                return True
                
        # If no suitable areas are defined, allow any area except restricted ones
        if not suitable_areas:
            return True
            
        return area_id in suitable_areas
        
    def find_suitable_area_for_npc(self, npc, area_manager, activity=None):
        """Find a suitable area for an NPC based on their type and activity."""
        import random
        
        # If no specific activity is provided, use the NPC's current activity
        if activity is None:
            activity = npc.current_activity
            
        # Collect suitable areas
        suitable_areas = []
        
        # Determine NPC type
        npc_type = "civilian"
        if isinstance(npc, GangMember) or npc.behavior_type == "gang_member":
            npc_type = "gang_member"
        elif npc.name == "Shopkeeper":
            npc_type = "shopkeeper"
            
        # Get suitable areas for this NPC type and activity
        activity_areas = self.area_suitability.get(npc_type, {}).get(activity, [])
        suitable_areas.extend(activity_areas)
        
        # Gang members prefer their gang's territory
        if npc_type == "gang_member" and hasattr(npc, 'gang') and npc.gang:
            gang = self.gangs.get(npc.gang)
            if gang and gang.territories:
                # Add gang territories to suitable areas with higher priority
                for territory in gang.territories:
                    suitable_areas.insert(0, territory.id)  # Add at the beginning for higher priority
        
        # Remove restricted areas and duplicates
        suitable_areas = list(dict.fromkeys([area for area in suitable_areas if area not in self.restricted_areas]))
        
        # If we have suitable areas, pick one randomly
        if suitable_areas:
            # Try to find areas that exist in the area manager
            existing_areas = []
            for area_id in suitable_areas:
                area = area_manager.get_area(area_id)
                if area:
                    existing_areas.append(area)
            
            if existing_areas:
                return random.choice(existing_areas)
        
        # If no suitable areas found, return None
        return None
    
    def get_npc(self, npc_id):
        """Get an NPC by ID."""
        return self.npcs.get(npc_id)
    
    def add_template(self, template_id, template_data):
        """Add an NPC template."""
        self.templates[template_id] = template_data
    
    def create_from_template(self, template_id, **kwargs):
        """Create an NPC from a template."""
        if template_id not in self.templates:
            raise ValueError(f"Unknown NPC template: {template_id}")
        
        template = self.templates[template_id].copy()
        
        # Generate a unique name if needed
        if "name_suffix" in kwargs:
            suffix = kwargs.pop("name_suffix")
            template["name"] = f"{template['name']} {suffix}"
        
        # Override template values with provided kwargs
        for key, value in kwargs.items():
            if key in template:
                template[key] = value
        
        # Determine NPC type based on template
        if "gang" in template:
            # Create a gang member
            gang_name = template.pop("gang")
            npc = GangMember(
                template["name"],
                template["description"],
                gang_name,
                dialogue=template.get("dialogue"),
                personality=template.get("personality"),
                money=template.get("money", 0),
                relationships=template.get("relationships"),
                properties=template.get("properties"),
                inventory=template.get("inventory"),
                schedule=template.get("schedule")
            )
            
            # Add to gang if it exists
            gang = self.get_gang_by_name(gang_name)
            if gang:
                gang.add_member(npc)
        else:
            # Create a civilian
            npc = Civilian(
                template["name"],
                template["description"],
                dialogue=template.get("dialogue"),
                personality=template.get("personality"),
                money=template.get("money", 0),
                relationships=template.get("relationships"),
                properties=template.get("properties"),
                inventory=template.get("inventory"),
                schedule=template.get("schedule")
            )
        
        # Generate a unique ID if needed
        if "id" in kwargs:
            npc.id = kwargs["id"]
        
        return npc
    
    def add_gang(self, gang):
        """Add a gang to the manager."""
        self.gangs[gang.id] = gang
    
    def get_gang(self, gang_id):
        """Get a gang by ID."""
        return self.gangs.get(gang_id)
    
    def get_gang_by_name(self, gang_name):
        """Get a gang by name."""
        return next((gang for gang in self.gangs.values() if gang.name == gang_name), None)
    
    def create_gang(self, name, territory=None, members=None, properties=None):
        """Create a new gang."""
        gang = Gang(name, territory, members, properties)
        self.add_gang(gang)
        return gang
    
    def update_all_npcs(self, current_time, game=None):
        """Update all NPCs based on the current time with environment awareness."""
        import random
        
        # First, update all NPCs' activities based on their schedules and environment suitability
        for npc in self.npcs.values():
            # Skip NPCs in restricted areas (like player's home)
            if npc.location and npc.location.id in self.restricted_areas:
                # Move the NPC out of the restricted area
                if game and hasattr(game, 'area_manager'):
                    suitable_area = self.find_suitable_area_for_npc(npc, game.area_manager)
                    if suitable_area:
                        npc.set_location(suitable_area)
                        print(f"DEBUG: Moved {npc.name} from restricted area {npc.location.id} to {suitable_area.name}")
            
            # Update the NPC's activity with environment awareness
            if game and hasattr(game, 'area_manager'):
                npc.update_activity(current_time, self, game.area_manager)
            else:
                npc.update_activity(current_time)
        
        # Group NPCs by area for more efficient processing
        npcs_by_area = {}
        for npc in self.npcs.values():
            if npc.location:
                area_id = npc.location.id
                # Skip NPCs in restricted areas
                if area_id in self.restricted_areas:
                    continue
                    
                if area_id not in npcs_by_area:
                    npcs_by_area[area_id] = []
                npcs_by_area[area_id].append(npc)
        
        # Process behaviors for NPCs in each area
        npc_behavior_messages = []
        for area_id, area_npcs in npcs_by_area.items():
            # Process behaviors for this group of NPCs
            behavior_message = self.behavior_coordinator.process_npc_behaviors(game, area_npcs)
            if behavior_message:
                # Add area name to the message for context
                area_name = "Unknown Area"
                if game and hasattr(game, 'area_manager'):
                    area = game.area_manager.get_area(area_id)
                    if area:
                        area_name = area.name
                
                area_message = f"In {area_name}:\n{behavior_message}"
                npc_behavior_messages.append(area_message)
        
        # Return the behavior messages
        if npc_behavior_messages:
            return "\n\n".join(npc_behavior_messages)
        return None
                
    def move_npc_randomly(self, npc):
        """Move an NPC randomly within their current area."""
        if not npc.location:
            return
            
        # Get current grid position
        rel_x = npc.coordinates.x - npc.location.coordinates.x
        rel_y = npc.coordinates.y - npc.location.coordinates.y
        
        # Calculate new position (move 1 step in a random direction)
        import random
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # N, E, S, W
        dx, dy = random.choice(directions)
        new_x = max(0, min(npc.location.grid_width - 1, rel_x + dx))
        new_y = max(0, min(npc.location.grid_length - 1, rel_y + dy))
        
        # Update NPC coordinates
        npc.coordinates.x = npc.location.coordinates.x + new_x
        npc.coordinates.y = npc.location.coordinates.y + new_y
        
        # Update grid position in the area
        npc.location.remove_object_from_grid(npc, rel_x, rel_y)
        npc.location.place_object_at(npc, new_x, new_y)
        
        # Update action to reflect movement
        movement_actions = ["walking around", "exploring", "moving", "wandering"]
        npc.current_action = random.choice(movement_actions)
    
    def save_to_json(self, filename):
        """Save all NPCs and gangs to a JSON file."""
        data = {
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
            "gangs": {gang_id: gang.to_dict() for gang_id, gang in self.gangs.items()},
            "templates": self.templates
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    
    def load_from_json(self, filename, location_resolver=None, item_resolver=None):
        """Load NPCs and gangs from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Load templates
        self.templates = data.get("templates", {})
        
        # Load gangs first
        for gang_id, gang_data in data.get("gangs", {}).items():
            gang = Gang.from_dict(gang_data)
            self.add_gang(gang)
        
        # Load NPCs
        for npc_id, npc_data in data.get("npcs", {}).items():
            if npc_data.get("behavior_type") == "gang_member":
                gang_name = npc_data.get("gang")
                npc = GangMember(
                    npc_data["name"],
                    npc_data["description"],
                    gang_name,
                    Coordinates.from_dict(npc_data["coordinates"]),
                    npc_data["dialogue"],
                    npc_data["personality"],
                    npc_data["money"],
                    npc_data["relationships"],
                    npc_data["properties"]
                )
            else:
                npc = Civilian.from_dict(npc_data, location_resolver, item_resolver)
            
            self.add_npc(npc)
            
            # Restore action state
            npc.current_action = npc_data.get("current_action")
            
            # Restore action start time
            start_time_str = npc_data.get("current_action_start_time")
            if start_time_str:
                try:
                    npc.current_action_start_time = datetime.fromisoformat(start_time_str)
                except (ValueError, TypeError):
                    npc.current_action_start_time = None
                    
            npc.current_action_duration = npc_data.get("current_action_duration", 0)
            npc.interrupted = npc_data.get("interrupted", False)
            
            # Resolve schedule if location_resolver is provided
            if location_resolver and "schedule" in npc_data:
                for time, (activity, location_id) in npc_data["schedule"].items():
                    if location_id:
                        location = location_resolver(location_id)
                        if location:
                            npc.schedule[time] = (activity, location)
            
            # Resolve inventory if item_resolver is provided
            if item_resolver and "inventory" in npc_data:
                for item_id in npc_data["inventory"]:
                    item = item_resolver(item_id)
                    if item:
                        npc.inventory.append(item)
        
        # Second pass to restore action targets and memory
        for npc_id, npc_data in data.get("npcs", {}).items():
            npc = self.get_npc(npc_id)
            if not npc:
                continue
                
            # Restore action target
            action_target_id = npc_data.get("action_target")
            if action_target_id:
                if action_target_id.startswith("name:"):
                    # Target is identified by name
                    target_name = action_target_id[5:]
                    # Try to find an NPC with this name
                    for other_npc in self.npcs.values():
                        if other_npc.name == target_name:
                            npc.action_target = other_npc
                            break
                else:
                    # Target is identified by ID
                    # Try NPC first
                    target = self.get_npc(action_target_id)
                    if target:
                        npc.action_target = target
                    # Then try item if item_resolver is provided
                    elif item_resolver:
                        item = item_resolver(action_target_id)
                        if item:
                            npc.action_target = item
            
            # Restore action memory
            if "action_memory" in npc_data:
                for memory_data in npc_data["action_memory"]:
                    memory = {
                        "action": memory_data["action"],
                        "location": memory_data["location"],
                        "target": None
                    }
                    
                    # Convert time string back to datetime
                    try:
                        memory["time"] = datetime.fromisoformat(memory_data["time"])
                    except (ValueError, TypeError):
                        memory["time"] = datetime.now()
                    
                    # Resolve target
                    target_id = memory_data.get("target")
                    if target_id:
                        if isinstance(target_id, str):
                            if target_id.startswith("name:"):
                                # Target is identified by name
                                target_name = target_id[5:]
                                # Try to find an NPC with this name
                                for other_npc in self.npcs.values():
                                    if other_npc.name == target_name:
                                        memory["target"] = other_npc
                                        break
                            else:
                                # Target is identified by ID
                                # Try NPC first
                                target = self.get_npc(target_id)
                                if target:
                                    memory["target"] = target
                                # Then try item if item_resolver is provided
                                elif item_resolver:
                                    item = item_resolver(target_id)
                                    if item:
                                        memory["target"] = item
                    
                    npc.action_memory.append(memory)