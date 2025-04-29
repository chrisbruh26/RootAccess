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
