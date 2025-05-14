"""
NPC module for Root Access v3.
Handles all non-player characters in the game world.
"""

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
    
    def update_activity(self, current_time):
        """Update the NPC's activity based on the current time."""
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
        current_location = None
        
        for time in scheduled_times:
            if current_time_minutes >= time:
                current_activity, current_location = self.schedule[time]
            else:
                break
        
        self.current_activity = current_activity
        if current_location and current_location != self.location:
            self.set_location(current_location)
            
        # Update the current action based on the activity
        self.update_action()
        
    def update_action(self):
        """Update the NPC's current action based on their activity."""
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
        self.current_action = random.choice(possible_actions)
        
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
            "behavior_type": self.behavior_type
        }
    
    @classmethod
    def from_dict(cls, data, location_resolver=None, item_resolver=None):
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


class NPCManager:
    """Manages all NPCs in the game."""
    def __init__(self):
        self.npcs = {}  # Dictionary mapping NPC IDs to NPC objects
        self.templates = {}  # Dictionary of NPC templates
        self.gangs = {}  # Dictionary mapping gang IDs to Gang objects
    
    def add_npc(self, npc):
        """Add an NPC to the manager."""
        self.npcs[npc.id] = npc
    
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
    
    def update_all_npcs(self, current_time):
        """Update all NPCs based on the current time."""
        import random
        
        for npc in self.npcs.values():
            # Update NPC activity based on schedule
            npc.update_activity(current_time)
            
            # Execute behavior based on NPC type and activity
            if isinstance(npc, GangMember) or npc.behavior_type == "gang_member":
                # Gang members have a chance to patrol regardless of activity
                if npc.current_activity == "patrolling" or random.random() < 0.3:  # 30% chance to patrol
                    npc.patrol()
                    
            elif isinstance(npc, Civilian) or npc.behavior_type == "civilian":
                # Civilians have a chance to interact with the environment
                if random.random() < 0.4:  # 40% chance to interact with environment
                    npc.interact_with_environment()
                    
            # All NPCs have a small chance to move around randomly
            if random.random() < 0.2:  # 20% chance to move
                self.move_npc_randomly(npc)
                
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