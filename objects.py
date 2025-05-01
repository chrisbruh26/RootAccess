import random
from effects import HackedPlantEffect

# ----------------------------- #
# INTERACTIVE OBJECTS           #
# ----------------------------- #

class Computer:
    def __init__(self, name="Computer", description="A computer terminal."):
        self.name = name
        self.description = description
        self.is_hacked = False
        self.programs = []
        self.data = []
        self.security_level = 1  # 1-5, with 5 being the most secure
    
    def hack(self, player):
        """Attempt to hack the computer."""
        # In a more complex implementation, this would check player skills
        if self.is_hacked:
            return False, "This computer is already hacked."
        
        # Simple hacking mechanic - 70% base chance of success, reduced by security level
        success_chance = 0.7 - (self.security_level * 0.1)
        if random.random() < success_chance:
            self.is_hacked = True
            return True, f"You successfully hack into the {self.name}!"
        else:
            return False, f"You fail to hack into the {self.name}. The security is too strong."
    
    def use(self, player):
        """Use the computer."""
        if not self.is_hacked:
            return False, f"You need to hack the {self.name} first."
        
        # Return a list of available programs
        if not self.programs:
            return True, "The computer is hacked, but there are no useful programs installed."
        
        program_list = "\n".join(f"- {program}" for program in self.programs)
        return True, f"Available programs:\n{program_list}"
    
    def run_program(self, program_name, player, game):
        """Run a specific program on the computer."""
        if not self.is_hacked:
            return False, f"You need to hack the {self.name} first."
        
        program = next((p for p in self.programs if p.lower() == program_name.lower()), None)
        if not program:
            return False, f"The program '{program_name}' is not installed on this computer."
        
        # Handle different programs
        if program == "data_miner":
            return True, "You run the data mining program and extract valuable information."
        elif program == "security_override":
            return True, "You override the security systems in the area."
        elif program == "plant_hacker":
            # Give the player the plant hacking effect
            effect = HackedPlantEffect()
            result = effect.apply_to_player(player, game)
            return True, result
        
        return True, f"You run the {program} program."
    
    def __str__(self):
        status = "hacked" if self.is_hacked else "locked"
        return f"{self.name} ({status})"

class HidingSpot:
    """A place where the player can hide from NPCs."""
    def __init__(self, name, description, stealth_bonus=0.5):
        self.name = name
        self.description = description
        self.stealth_bonus = stealth_bonus  # Reduces detection chance by this percentage
        self.is_occupied = False
        self.occupant = None
    
    def hide(self, player):
        """Player attempts to hide in this spot."""
        if self.is_occupied:
            return False, f"Someone is already hiding in the {self.name}."
        
        self.is_occupied = True
        self.occupant = player
        player.hidden = True
        player.hiding_spot = self
        
        # Clear detection status when hiding
        player.detected_by.clear()
        
        return True, f"You hide in the {self.name}. Gang members won't be able to detect you while you're hidden."
    
    def leave(self, player):
        """Player leaves the hiding spot."""
        if self.occupant != player:
            return False, "You're not hiding here."
        
        self.is_occupied = False
        self.occupant = None
        player.hidden = False
        player.hiding_spot = None
        
        return True, f"You emerge from the {self.name}."
    
    def __str__(self):
        status = "occupied" if self.is_occupied else "empty"
        return f"{self.name} ({status})"
    

class Storage:
    """A storage container for items."""
    def __init__(self, name="Storage", description="A storage container."):
        self.name = name
        self.description = description
        self.items = []
    
    def add_item(self, item):
        """Add an item to the storage."""
        self.items.append(item)
        return True, f"You add the {item.name} to the {self.name}."
    
    def remove_item(self, item_name):
        """Remove an item from the storage."""
        item = next((i for i in self.items if i.name.lower() == item_name.lower()), None)
        if not item:
            return False, f"There is no {item_name} in the {self.name}."
        
        self.items.remove(item)
        return True, f"You take the {item.name} from the {self.name}."
    
    def __str__(self):
        if not self.items:
            return f"{self.name} (empty)"
        
        item_list = "\n".join(f"- {item}" for item in self.items)
        return f"{self.name}:\n{item_list}"
    

class BreakableGlassObject:
    """Objects that have breakable glass."""
    def __init__(self, name, description="A breakable object with glass.", broken=False):
        self.name = name
        self.description = description
        self.is_broken = broken
        
    def break_glass(self, breaker=None, method=None):
        """
        Break the glass of the object.
        
        Args:
            breaker: The entity (player or NPC) breaking the glass
            method: The method used to break the glass (e.g., "smash", "shoot")
            
        Returns:
            tuple: (success, message)
        """
        if self.is_broken:
            return False, f"The {self.name} is already broken."
        
        self.is_broken = True
        
        # Generate appropriate message based on who broke it and how
        if breaker:
            # Check if breaker is the player
            from player import Player
            is_player = isinstance(breaker, Player)
            
            if method:
                if is_player:
                    message = f"You {method} the {self.name} and it shatters!"
                else:
                    message = f"{breaker.name} {method}es the {self.name} and it shatters!"
            else:
                if is_player:
                    message = f"You break the {self.name} and it shatters!"
                else:
                    message = f"{breaker.name} breaks the {self.name} and it shatters!"
        else:
            message = f"The {self.name} shatters!"
            
        return True, message
    
    def __str__(self):
        status = "broken" if self.is_broken else "intact"
        return f"{self.name} ({status})"


class VendingMachine(BreakableGlassObject):
    """A Vending Machine."""
    def __init__(self, name="Vending Machine", description="A vending machine filled with snacks and drinks."):
        super().__init__(name.lower(), description, broken=False)
        self.display_name = name  # For display purposes
        self.items = []
    
    def break_glass(self, breaker=None, method=None):
        """
        Break the glass of the vending machine and spill its contents.
        
        Args:
            breaker: The entity breaking the glass
            method: The method used to break the glass
            
        Returns:
            tuple: (success, message, spilled_items)
        """
        result = super().break_glass(breaker, method)
        
        if not result[0]:
            return False, result[1], []
            
        # Create a copy of items to spill
        spilled_items = self.items.copy()
        message = result[1]
        
        # Check if breaker is the player for appropriate messaging
        from player import Player
        is_player = isinstance(breaker, Player)
        
        if spilled_items:
            item_names = ", ".join(item.name for item in spilled_items)
            if is_player:
                message += f"\nItems spill out onto the floor: {item_names}"
            else:
                message += f"\nItems spill out onto the floor: {item_names}"
        else:
            if is_player:
                message += "\nYou find that the vending machine is empty."
            else:
                message += "\nThe vending machine is empty."
            
        return True, message, spilled_items
    
    def add_item(self, item):
        """Add an item to the vending machine."""
        self.items.append(item)
        
    def __str__(self):
        status = "broken" if self.is_broken else "intact"
        return f"{self.display_name} ({status})"
