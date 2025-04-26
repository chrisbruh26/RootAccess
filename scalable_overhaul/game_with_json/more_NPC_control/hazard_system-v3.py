import random
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
            return f"An NPC in the area {get_random_npc_action()}"
        
        # If we have multiple NPCs, sometimes generate an interaction between them
        if len(eligible_npcs) >= 2 and random.random() < 0.3:  # 30% chance for NPC interaction
            from RA_main import get_npc_interaction
            npc1 = random.choice(eligible_npcs)
            # Choose a different NPC for the second one
            remaining_npcs = [npc for npc in eligible_npcs if npc != npc1]
            if remaining_npcs:
                npc2 = random.choice(remaining_npcs)
                return get_npc_interaction(npc1.name, npc2.name)
        
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
            # Get a random action from our improved categorized actions
            action = get_random_npc_action()
            # Format it to look like an NPC action
            return f"An NPC in the area {action}"
        
        # Filter out empty results
        results = [r for r in results if r]
        if not results:
            from RA_main import get_random_npc_action
            # Get a random action from our improved categorized actions
            action = get_random_npc_action()
            # Format it to look like an NPC action
            return f"An NPC in the area {action}"
            
        # Group results by effect type
        hallucination_results = []
        friendly_results = []
        gift_results = []
        resistance_results = []
        other_results = []
        
        for result in results:
            if "hallucinating" in result.lower():
                hallucination_results.append(result)
            elif "friendly" in result.lower() or "smiles" in result.lower():
                friendly_results.append(result)
            elif "gift" in result.lower() or "gives" in result.lower():
                gift_results.append(result)
            elif "resisted" in result.lower():
                resistance_results.append(result)
            else:
                other_results.append(result)
        
        # Combine results into a coherent message
        final_results = []
        
        # Add hallucination results
        if hallucination_results:
            if len(hallucination_results) == 1:
                final_results.append(hallucination_results[0])
            else:
                names = []
                for result in hallucination_results[:3]:  # Limit to first 3 for readability
                    parts = result.split()
                    if parts:
                        names.append(parts[0])  # Extract the name (first word)
                
                if len(names) == 2:
                    final_results.append(f"{names[0]} and {names[1]} are hallucinating wildly.")
                elif len(names) >= 3:
                    final_results.append(f"{names[0]}, {names[1]}, and {len(hallucination_results) - 2} others are hallucinating wildly.")
        
        # Add friendly results
        if friendly_results:
            if len(friendly_results) == 1:
                final_results.append(friendly_results[0])
            else:
                names = []
                for result in friendly_results[:3]:
                    parts = result.split()
                    if parts:
                        names.append(parts[0])
                
                if len(names) == 2:
                    final_results.append(f"{names[0]} and {names[1]} become unusually friendly.")
                elif len(names) >= 3:
                    final_results.append(f"{names[0]}, {names[1]}, and {len(friendly_results) - 2} others become unusually friendly.")
        
        # Add gift results
        if gift_results:
            if len(gift_results) == 1:
                final_results.append(gift_results[0])
            else:
                names = []
                for result in gift_results[:3]:
                    parts = result.split()
                    if parts:
                        names.append(parts[0])
                
                if len(names) == 2:
                    final_results.append(f"{names[0]} and {names[1]} feel compelled to give away their possessions.")
                elif len(names) >= 3:
                    final_results.append(f"{names[0]}, {names[1]}, and {len(gift_results) - 2} others feel compelled to give away their possessions.")
        
        # Add resistance results
        if resistance_results:
            if len(resistance_results) == 1:
                final_results.append(resistance_results[0])
            else:
                names = []
                for result in resistance_results[:3]:
                    parts = result.split()
                    if parts:
                        names.append(parts[0])
                
                if len(names) == 2:
                    final_results.append(f"{names[0]} and {names[1]} resist the effects.")
                elif len(names) >= 3:
                    final_results.append(f"{names[0]}, {names[1]}, and {len(resistance_results) - 2} others resist the effects.")
        
        # Add other results
        for result in other_results[:2]:  # Limit to 2 other results for readability
            final_results.append(result)
        
        # Combine all results
        if not final_results:
            from RA_main import get_random_npc_action
            # 30% chance to show an interesting action instead of nothing
            if random.random() < 0.3:
                action = get_random_npc_action()
                return f"An NPC in the area {action}"
            else:
                # 70% chance to return None (no message at all)
                return None
        
        return " ".join(final_results)
    
    def get_affected_verb(self, count):
        """Get appropriate verb for affected members"""
        verbs = {
            "Glitter Bomb": "gets glitter bombed",
            "Pink Mist": "breathes in pink mist",
            "Hacked Milk": "steps in hacked milk"
        }
        return verbs.get(self.name, "is affected by")
