"""
Player module for Root Access v3.
Handles the player character and their interactions with the game world.
"""

from .coordinates import Coordinates

class Player:
    """Player class for the Root Access game."""
    def __init__(self, name="Player"):
        self.name = name
        self.street_cred = 0
        self.inventory = []
        self.current_area = None
        self.coordinates = Coordinates(0, 0, 0)
        self.energy = 100
        self.max_energy = 100
        self.hunger = 0
        self.max_hunger = 100
        self.money = 0
        self.skills = {}  # Dictionary of skills and their levels
        self.relationships = {}  # Relationships with NPCs
        self.properties = {}  # Custom properties
        self.current_vehicle = None  # Vehicle the player is currently in
        self.investments = {}  # Dictionary mapping business IDs to investment amounts
        self.hacking_level = 1  # Player's hacking skill level
        self.stealth_level = 1  # Player's stealth skill level
        self.combat_level = 1  # Player's combat skill level
        self.is_hidden = False  # Whether the player is currently hidden
        self.current_hiding_spot = None  # The hiding spot the player is using
        
    def set_current_area(self, area, grid_x=0, grid_y=0):
        """Set the current area for the player."""
        self.current_area = area
        # Update player coordinates to match area entrance coordinates plus grid position
        self.coordinates = Coordinates(
            area.coordinates.x + grid_x,
            area.coordinates.y + grid_y,
            area.coordinates.z
        )
        print(f"You are now in {area.name}. {area.description}")
        self.look_around()
    
    def look_around(self):
        """Look around the current area."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        print(f"You are at position ({grid_x}, {grid_y}) in {self.current_area.name}.")
        
        # Display available directions for movement within the grid
        print("You can move:")
        if grid_y < self.current_area.grid_length - 1:
            print("- north/forward")
        if grid_y > 0:
            print("- south/backward")
        if grid_x < self.current_area.grid_width - 1:
            print("- east/right")
        if grid_x > 0:
            print("- west/left")
        
        # Display area connections (exits to other areas)
        if self.current_area.connections:
            print("Area exits:")
            for direction, area in self.current_area.connections.items():
                print(f"- {direction} to {area.name}")
        
        # Display objects at the current position
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        # Keep track of items and objects we've already shown to the player
        shown_items = []
        shown_objects = []
        
        if objects_here:
            items_here = [obj for obj in objects_here if hasattr(obj, 'pickupable') and obj.pickupable]
            other_objects = [obj for obj in objects_here if not hasattr(obj, 'pickupable') or not obj.pickupable]
            
            if items_here:
                print("Items within arm's reach (can be picked up):") # shows the player which items are immediately available 
                for obj in items_here:
                    print(f"- {obj.name}") # REMOVE ALL DESCRIPTIONS FROM LISTS, ONLY SHOW IF PLAYER EXAMINES (items, objects, etc.) - need examine method
                    # Add to shown items list so we don't show them again
                    shown_items.append(obj)
                    
            if other_objects:
                print("Objects at your position:")
                for obj in other_objects:
                    print(f"- {obj.name}")
                    # Add to shown objects list so we don't show them again
                    shown_objects.append(obj)
        
        # Display items in the area
        if self.current_area.items:
            # Filter out items that have already been shown
            area_items = [item for item in self.current_area.items if item not in shown_items]
            
            # Create a list of visible items with their positions
            visible_items = []
            for item in area_items:
                # Get the relative position of the item
                item_rel_x = item.coordinates.x - self.current_area.coordinates.x
                item_rel_y = item.coordinates.y - self.current_area.coordinates.y
                # Only include items that are visible (in the same area)
                if 0 <= item_rel_x < self.current_area.grid_width and 0 <= item_rel_y < self.current_area.grid_length:
                    direction = self.get_relative_direction(grid_x, grid_y, item_rel_x, item_rel_y)
                    visible_items.append((item, direction))
            
            if visible_items:  # Only print the header if there are items to show
                print("Items in this area:")
                
                # Check if there are fewer than 3 items in the area
                if len(visible_items) <= 3:
                    for item, direction in visible_items:
                        print(f"- {item.name} ({direction})") # remove description for items
                # Else, show the first 3 and add "and more" to the end
                else:
                    for item, direction in visible_items[:3]:
                        print(f"- {item.name} ({direction})")
                    print(f"- and more...")

        
        # Display NPCs in the area
        if self.current_area.npcs:
            print("People in this area:")
            for npc in self.current_area.npcs:
                # Get the relative position of the NPC
                npc_rel_x = npc.coordinates.x - self.current_area.coordinates.x
                npc_rel_y = npc.coordinates.y - self.current_area.coordinates.y
                # Only show NPCs that are visible (in the same area)
                if 0 <= npc_rel_x < self.current_area.grid_width and 0 <= npc_rel_y < self.current_area.grid_length:
                    direction = self.get_relative_direction(grid_x, grid_y, npc_rel_x, npc_rel_y)
                    print(f"- {npc.name}: ({direction})") # remove descriptions for NPCs
        
        # Display objects in the area
        if self.current_area.objects:
            # Create a list of visible objects that haven't been shown yet
            visible_objects = []
            for obj in self.current_area.objects:
                # Skip objects that have already been shown
                if obj in shown_objects:
                    continue
                    
                # Get the relative position of the object
                obj_rel_x = obj.coordinates.x - self.current_area.coordinates.x
                obj_rel_y = obj.coordinates.y - self.current_area.coordinates.y
                
                # Only show objects that are visible (in the same area)
                if 0 <= obj_rel_x < self.current_area.grid_width and 0 <= obj_rel_y < self.current_area.grid_length:
                    # Skip objects at the current position (already displayed above)
                    if obj_rel_x == grid_x and obj_rel_y == grid_y:
                        continue
                    direction = self.get_relative_direction(grid_x, grid_y, obj_rel_x, obj_rel_y)
                    visible_objects.append((obj, direction))
            
            # Only print the header if there are objects to show
            if visible_objects:
                print("Objects in this area:")
                for obj, direction in visible_objects:
                    print(f"- {obj.name}: ({direction})") # remove description for objects
    
    def get_relative_direction(self, from_x, from_y, to_x, to_y):
        """Get the relative direction from one position to another."""
        if from_x == to_x and from_y == to_y:
            return "here"
            
        directions = []
        if to_y > from_y:
            directions.append("north")
        elif to_y < from_y:
            directions.append("south")
            
        if to_x > from_x:
            directions.append("east")
        elif to_x < from_x:
            directions.append("west")
            
        distance = int(((to_x - from_x) ** 2 + (to_y - from_y) ** 2) ** 0.5)
        if distance == 1:
            proximity = "adjacent"
        elif distance <= 3:
            proximity = "nearby"
        else:
            proximity = "in the distance"
            
        return f"{' '.join(directions)} {proximity}"

    def add_item(self, item):
        """Add an item to the player's inventory."""
        self.inventory.append(item)
        print(f"You have picked up {item.name}.")

    def remove_item(self, item_name):
        """Remove an item from the player's inventory."""
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if item:
            self.inventory.remove(item)
            print(f"You have dropped {item.name}.")
            
            # Add the item to the current area
            if self.current_area:
                self.current_area.add_item(item)
        else:
            print(f"You don't have {item_name} in your inventory.")
    
    def eat(self, item_name):
        """Eat an item from inventory."""
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            print(f"You don't have {item_name} to eat.")
            return
        
        if hasattr(item, 'edible') and item.edible:
            self.hunger = max(0, self.hunger - item.nutrition)
            self.inventory.remove(item)
            print(f"You eat the {item.name}. Yum!")
            if hasattr(item, 'effect'):
                item.effect(self)
        else:
            print(f"You can't eat the {item.name}!")
            
    def get_grid_position(self):
        """Get the player's position relative to the current area's grid."""
        if not self.current_area:
            return None
        
        rel_x = self.coordinates.x - self.current_area.coordinates.x
        rel_y = self.coordinates.y - self.current_area.coordinates.y
        rel_z = self.coordinates.z - self.current_area.coordinates.z
        
        return (rel_x, rel_y, rel_z)
    
    def move(self, direction, distance=1):
        """Move the player in a direction within the current area's grid."""
        if not self.current_area:
            print("You're not in any area.")
            return False
            
        # If player is in a vehicle, use the vehicle's movement
        if self.current_vehicle:
            return self.current_vehicle.drive(self, direction, distance)
            
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        new_x, new_y = grid_x, grid_y
        
        # Calculate new position based on direction
        if direction.lower() in ["north", "forward"]:
            new_y += distance
        elif direction.lower() in ["south", "backward"]:
            new_y -= distance
        elif direction.lower() in ["east", "right"]:
            new_x += distance
        elif direction.lower() in ["west", "left"]:
            new_x -= distance
        else:
            print(f"Unknown direction: {direction}")
            return False
        
        # Check if new position is within area bounds
        if 0 <= new_x < self.current_area.grid_width and 0 <= new_y < self.current_area.grid_length:
            # Update player coordinates
            self.coordinates.x = self.current_area.coordinates.x + new_x
            self.coordinates.y = self.current_area.coordinates.y + new_y
            
            print(f"You move {direction}.")
            
            # If player was hidden, they're no longer hidden after moving
            if self.is_hidden:
                self.unhide()
            
            # Check for objects at the new position
            objects_here = self.current_area.get_objects_at(new_x, new_y, grid_z)
            if objects_here:
                print("You see:")
                for obj in objects_here:
                    print(f"- {obj.name}")
                    
            return True
        else:
            # Check if there's a connection in this direction
            if direction.lower() in self.current_area.connections:
                connected_area = self.current_area.connections[direction.lower()]
                # Determine entry point on the other side
                entry_x, entry_y = 0, 0
                if direction.lower() == "north":
                    entry_y = 0  # Enter from the south side
                    entry_x = grid_x  # Keep the same x-coordinate
                elif direction.lower() == "south":
                    entry_y = connected_area.grid_length - 1  # Enter from the north side
                    entry_x = grid_x  # Keep the same x-coordinate
                elif direction.lower() == "east":
                    entry_x = 0  # Enter from the west side
                    entry_y = grid_y  # Keep the same y-coordinate
                elif direction.lower() == "west":
                    entry_x = connected_area.grid_width - 1  # Enter from the east side
                    entry_y = grid_y  # Keep the same y-coordinate
                
                # If player was hidden, they're no longer hidden after changing areas
                if self.is_hidden:
                    self.unhide()
                
                # Move to the connected area
                self.set_current_area(connected_area, entry_x, entry_y)
                return True
            else:
                print(f"You can't go {direction} from here. You've reached the edge of {self.current_area.name}.")
                return False
    
    def interact_with(self, object_name):
        """Interact with an object in the current area."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Check for objects at the current position
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        obj = next((o for o in objects_here if o.name.lower() == object_name.lower()), None)
        
        if obj:
            obj.interact(self)
        else:
            # Check for objects in adjacent positions
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # Skip current position (already checked)
                    
                    adj_x, adj_y = grid_x + dx, grid_y + dy
                    if 0 <= adj_x < self.current_area.grid_width and 0 <= adj_y < self.current_area.grid_length:
                        objects_adj = self.current_area.get_objects_at(adj_x, adj_y, grid_z)
                        obj = next((o for o in objects_adj if o.name.lower() == object_name.lower()), None)
                        if obj:
                            print(f"You reach over to interact with the {obj.name}.")
                            obj.interact(self)
                            return
            
            print(f"You don't see a {object_name} nearby to interact with.")
    
    def pick_up(self, item_name):
        """Pick up an item from the current area."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Check for items at the current position
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        item = next((o for o in objects_here if o.name.lower() == item_name.lower() and hasattr(o, 'pickupable') and o.pickupable), None)
        
        if item:
            self.current_area.remove_item(item.name)
            self.add_item(item)
        else:
            # Check for items in the area's item list
            item = next((i for i in self.current_area.items if i.name.lower() == item_name.lower()), None)
            if item:
                # Check if the item is close enough to pick up
                item_rel_x = item.coordinates.x - self.current_area.coordinates.x
                item_rel_y = item.coordinates.y - self.current_area.coordinates.y
                
                distance = ((grid_x - item_rel_x) ** 2 + (grid_y - item_rel_y) ** 2) ** 0.5
                if distance <= 1:  # Can only pick up items within 1 grid unit
                    self.current_area.remove_item(item.name)
                    self.add_item(item)
                else:
                    print(f"The {item_name} is too far away. Move closer to pick it up.")
            else:
                print(f"You don't see a {item_name} here.")
    
    def drop(self, item_name):
        """Drop an item from inventory."""
        self.remove_item(item_name)
    
    def use(self, item_name):
        """Use an item from inventory."""
        item = next((i for i in self.inventory if i.name.lower() == item_name.lower()), None)
        if not item:
            print(f"You don't have {item_name} to use.")
            return
        
        if hasattr(item, 'use'):
            item.use(self)
        else:
            print(f"You can't figure out how to use the {item.name}.")
    
    def talk_to(self, npc_name):
        """Talk to an NPC in the current area."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Find the NPC in the current area
        npc = next((n for n in self.current_area.npcs if n.name.lower() == npc_name.lower()), None)
        if not npc:
            print(f"You don't see {npc_name} here.")
            return
        
        # Check if the NPC is close enough to talk to
        npc_rel_x = npc.coordinates.x - self.current_area.coordinates.x
        npc_rel_y = npc.coordinates.y - self.current_area.coordinates.y
        
        distance = ((grid_x - npc_rel_x) ** 2 + (grid_y - npc_rel_y) ** 2) ** 0.5
        if distance <= 2:  # Can talk to NPCs within 2 grid units
            npc.talk(self)
        else:
            print(f"{npc_name} is too far away. Move closer to talk.")
    
    def hide(self, hiding_spot_name):
        """Hide in a hiding spot."""
        if self.is_hidden:
            print("You're already hidden.")
            return
        
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Check for hiding spots at the current position
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        hiding_spot = next((o for o in objects_here if o.name.lower() == hiding_spot_name.lower() and o.__class__.__name__ == "HidingSpot"), None)
        
        if hiding_spot:
            self.is_hidden = True
            self.current_hiding_spot = hiding_spot
            print(f"You hide in/behind the {hiding_spot.name}.")
            
            # Apply stealth bonus based on hiding spot and player's stealth level
            stealth_bonus = hiding_spot.stealth_bonus * (1 + self.stealth_level * 0.1)
            print(f"Your stealth is improved by {int(stealth_bonus * 100)}%.")
        else:
            print(f"You don't see a {hiding_spot_name} here to hide in/behind.")
    
    def unhide(self):
        """Stop hiding."""
        if not self.is_hidden:
            print("You're not hidden.")
            return
        
        self.is_hidden = False
        self.current_hiding_spot = None
        print("You emerge from your hiding spot.")
    
    def hack(self, target_name):
        """Hack a target object or device."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Check for hackable objects at the current position
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        target = next((o for o in objects_here if o.name.lower() == target_name.lower() and hasattr(o, 'hack')), None)
        
        if target:
            target.hack(self)
        else:
            # Check for hackable objects in adjacent positions
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # Skip current position (already checked)
                    
                    adj_x, adj_y = grid_x + dx, grid_y + dy
                    if 0 <= adj_x < self.current_area.grid_width and 0 <= adj_y < self.current_area.grid_length:
                        objects_adj = self.current_area.get_objects_at(adj_x, adj_y, grid_z)
                        target = next((o for o in objects_adj if o.name.lower() == target_name.lower() and hasattr(o, 'hack')), None)
                        if target:
                            print(f"You attempt to hack the {target.name}.")
                            target.hack(self)
                            return
            
            print(f"You don't see a {target_name} nearby that you can hack.")
    
    def attack(self, target_name):
        """Attack a target NPC or object."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Find the target in the current area
        npc = next((n for n in self.current_area.npcs if n.name.lower() == target_name.lower()), None)
        if npc:
            # Check if the NPC is close enough to attack
            npc_rel_x = npc.coordinates.x - self.current_area.coordinates.x
            npc_rel_y = npc.coordinates.y - self.current_area.coordinates.y
            
            distance = ((grid_x - npc_rel_x) ** 2 + (grid_y - npc_rel_y) ** 2) ** 0.5
            if distance <= 1:  # Can attack NPCs within 1 grid unit
                # Check if player has a weapon
                weapon = next((i for i in self.inventory if i.__class__.__name__ == "Weapon"), None)
                if weapon:
                    damage = weapon.damage * (1 + self.combat_level * 0.1)
                    print(f"You attack {npc.name} with your {weapon.name} for {int(damage)} damage!")
                    # In a full implementation, this would affect NPC health and relationships
                    self.adjust_relationship(npc, -20)  # Attacking makes NPCs dislike you
                else:
                    damage = 5 * (1 + self.combat_level * 0.1)  # Unarmed damage
                    print(f"You attack {npc.name} with your fists for {int(damage)} damage!")
                    # In a full implementation, this would affect NPC health and relationships
                    self.adjust_relationship(npc, -10)  # Attacking makes NPCs dislike you
            else:
                print(f"{npc.name} is too far away. Move closer to attack.")
        else:
            # Check for breakable objects
            obj = next((o for o in self.current_area.objects if o.name.lower() == target_name.lower() and hasattr(o, 'break_object')), None)
            if obj:
                # Check if the object is close enough to attack
                obj_rel_x = obj.coordinates.x - self.current_area.coordinates.x
                obj_rel_y = obj.coordinates.y - self.current_area.coordinates.y
                
                distance = ((grid_x - obj_rel_x) ** 2 + (grid_y - obj_rel_y) ** 2) ** 0.5
                if distance <= 1:  # Can attack objects within 1 grid unit
                    # Check if player has a weapon
                    weapon = next((i for i in self.inventory if i.__class__.__name__ == "Weapon"), None)
                    if weapon:
                        print(f"You attack the {obj.name} with your {weapon.name}!")
                        obj.break_object(self)
                    else:
                        print(f"You attack the {obj.name} with your fists!")
                        obj.break_object(self)
                else:
                    print(f"The {obj.name} is too far away. Move closer to attack.")
            else:
                print(f"You don't see {target_name} here to attack.")
    
    def plant(self, seed_name, plot_name):
        """Plant a seed in a soil plot."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Find the seed in inventory
        seed = next((i for i in self.inventory if i.name.lower() == seed_name.lower() and i.__class__.__name__ == "Seed"), None)
        if not seed:
            print(f"You don't have a {seed_name} to plant.")
            return
        
        # Find the soil plot
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        plot = next((o for o in objects_here if o.name.lower() == plot_name.lower() and o.__class__.__name__ == "SoilPlot"), None)
        
        if not plot:
            # Check adjacent positions
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # Skip current position (already checked)
                    
                    adj_x, adj_y = grid_x + dx, grid_y + dy
                    if 0 <= adj_x < self.current_area.grid_width and 0 <= adj_y < self.current_area.grid_length:
                        objects_adj = self.current_area.get_objects_at(adj_x, adj_y, grid_z)
                        plot = next((o for o in objects_adj if o.name.lower() == plot_name.lower() and o.__class__.__name__ == "SoilPlot"), None)
                        if plot:
                            break
                if plot:
                    break
        
        if plot:
            if plot.has_plant:
                print(f"The {plot.name} already has a plant in it.")
            else:
                self.inventory.remove(seed)
                plot.plant(seed)
                print(f"You plant the {seed.name} in the {plot.name}.")
        else:
            print(f"You don't see a {plot_name} nearby to plant in.")
    
    def water(self, plot_name):
        """Water a soil plot."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Find a watering can in inventory
        watering_can = next((i for i in self.inventory if i.__class__.__name__ == "WateringCan"), None)
        if not watering_can:
            print("You don't have a watering can.")
            return
        
        # Find the soil plot
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        plot = next((o for o in objects_here if o.name.lower() == plot_name.lower() and o.__class__.__name__ == "SoilPlot"), None)
        
        if not plot:
            # Check adjacent positions
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # Skip current position (already checked)
                    
                    adj_x, adj_y = grid_x + dx, grid_y + dy
                    if 0 <= adj_x < self.current_area.grid_width and 0 <= adj_y < self.current_area.grid_length:
                        objects_adj = self.current_area.get_objects_at(adj_x, adj_y, grid_z)
                        plot = next((o for o in objects_adj if o.name.lower() == plot_name.lower() and o.__class__.__name__ == "SoilPlot"), None)
                        if plot:
                            break
                if plot:
                    break
        
        if plot:
            if not plot.has_plant:
                print(f"The {plot.name} doesn't have a plant to water.")
            else:
                if watering_can.uses > 0:
                    watering_can.uses -= 1
                    plot.water()
                    print(f"You water the {plot.plant.name} in the {plot.name}.")
                    if watering_can.uses == 0:
                        print("Your watering can is empty. You need to refill it.")
                else:
                    print("Your watering can is empty. You need to refill it.")
        else:
            print(f"You don't see a {plot_name} nearby to water.")
    
    def harvest(self, plot_name):
        """Harvest a plant from a soil plot."""
        # Get current grid position
        grid_x, grid_y, grid_z = self.get_grid_position()
        
        # Find the soil plot
        objects_here = self.current_area.get_objects_at(grid_x, grid_y, grid_z)
        plot = next((o for o in objects_here if o.name.lower() == plot_name.lower() and o.__class__.__name__ == "SoilPlot"), None)
        
        if not plot:
            # Check adjacent positions
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue  # Skip current position (already checked)
                    
                    adj_x, adj_y = grid_x + dx, grid_y + dy
                    if 0 <= adj_x < self.current_area.grid_width and 0 <= adj_y < self.current_area.grid_length:
                        objects_adj = self.current_area.get_objects_at(adj_x, adj_y, grid_z)
                        plot = next((o for o in objects_adj if o.name.lower() == plot_name.lower() and o.__class__.__name__ == "SoilPlot"), None)
                        if plot:
                            break
                if plot:
                    break
        
        if plot:
            if not plot.has_plant:
                print(f"The {plot.name} doesn't have a plant to harvest.")
            elif not plot.plant.is_mature:
                print(f"The {plot.plant.name} isn't ready to harvest yet.")
            else:
                harvested_item = plot.harvest()
                self.add_item(harvested_item)
                print(f"You harvest the {harvested_item.name} from the {plot.name}.")
        else:
            print(f"You don't see a {plot_name} nearby to harvest from.")
    
    def set_relationship(self, entity, value):
        """Set relationship value with another entity (NPC)."""
        self.relationships[entity.name] = value
    
    def adjust_relationship(self, entity, amount):
        """Adjust relationship value with another entity."""
        current = self.get_relationship(entity)
        self.relationships[entity.name] = max(-100, min(100, current + amount))
        
    def get_relationship(self, entity):
        """Get relationship value with another entity."""
        return self.relationships.get(entity.name, 0)
    
    def to_dict(self):
        """Convert player to dictionary for serialization."""
        return {
            "name": self.name,
            "street_cred": self.street_cred,
            "coordinates": self.coordinates.to_dict(),
            "current_area": self.current_area.id if self.current_area else None,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "hunger": self.hunger,
            "max_hunger": self.max_hunger,
            "money": self.money,
            "skills": self.skills,
            "relationships": self.relationships,
            "properties": self.properties,
            "inventory": [item.id for item in self.inventory],
            "hacking_level": self.hacking_level,
            "stealth_level": self.stealth_level,
            "combat_level": self.combat_level,
            "is_hidden": self.is_hidden,
            "current_hiding_spot": self.current_hiding_spot.id if self.current_hiding_spot else None,
            "current_vehicle": self.current_vehicle.id if self.current_vehicle else None,
            "investments": self.investments
        }
    
    @classmethod
    def from_dict(cls, data, area_resolver=None, item_resolver=None, object_resolver=None):
        """Create player from dictionary."""
        player = cls(data["name"])
        player.street_cred = data["street_cred"]
        player.coordinates = Coordinates.from_dict(data["coordinates"])
        player.energy = data["energy"]
        player.max_energy = data["max_energy"]
        player.hunger = data["hunger"]
        player.max_hunger = data["max_hunger"]
        player.money = data["money"]
        player.skills = data["skills"]
        player.relationships = data["relationships"]
        player.properties = data["properties"]
        player.hacking_level = data["hacking_level"]
        player.stealth_level = data["stealth_level"]
        player.combat_level = data["combat_level"]
        player.is_hidden = data["is_hidden"]
        player.investments = data["investments"]
        
        # Resolve current area if area_resolver is provided
        if area_resolver and data["current_area"]:
            player.current_area = area_resolver(data["current_area"])
        
        # Resolve inventory if item_resolver is provided
        if item_resolver and "inventory" in data:
            for item_id in data["inventory"]:
                item = item_resolver(item_id)
                if item:
                    player.inventory.append(item)
        
        # Resolve current hiding spot if object_resolver is provided
        if object_resolver and data["current_hiding_spot"]:
            player.current_hiding_spot = object_resolver(data["current_hiding_spot"])
        
        # Resolve current vehicle if object_resolver is provided
        if object_resolver and data["current_vehicle"]:
            player.current_vehicle = object_resolver(data["current_vehicle"])
        
        return player