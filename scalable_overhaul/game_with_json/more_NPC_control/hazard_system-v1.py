from hazard_utils import Hazard
from RA_main import GangMember

class StaticHazard(Hazard):
    def __init__(self, name, description, effect):
        super().__init__(name, description, effect, damage=40, duration=2)  # duration was None permanent static hazards, testing with 2 turns

    def affect_area(self, area):
        """Apply hazard to all gang members in area with grouped results."""
        results = []
        
        # Get a list of eligible NPCs (gang members)
        eligible_npcs = [npc for npc in area.npcs if isinstance(npc, GangMember)]
        
        # If no NPCs are affected, return a random NPC action
        if not eligible_npcs:
            from RA_main import get_random_npc_action
            return get_random_npc_action()
        
        # Apply hazard effect to selected NPCs
        for npc in eligible_npcs:
            result = npc.apply_hazard_effect(self)
            npc.update_effects()
            results.append(result)
                
        return self.group_results(results)

    def group_results(self, results):
        """Group hazard results by effect status with proper grammar and interesting details."""
        if not results:
            from RA_main import get_random_npc_action
            return get_random_npc_action()
        # ...existing code for grouping results...
    
    def get_affected_verb(self, count):
        """Get appropriate verb for affected members"""
        verbs = {
            "Glitter Bomb": "gets glitter bombed",
            "Pink Mist": "breathes in pink mist",
            "Hacked Milk": "steps in hacked milk"
        }
        return verbs.get(self.name, "is affected by")
