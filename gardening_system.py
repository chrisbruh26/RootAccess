"""
Gardening System for Root Access

This module provides a clean, unified approach to handling gardening actions in the game.
It ensures that gardening messages are properly displayed and that NPCs can interact with
the environment in meaningful ways.

Key Components:
--------------
1. Enhanced gardening message detection and display
2. Functional gardening actions that affect the game state
3. Integration with the message system to ensure visibility

Usage:
------
from gardening_system import initialize_gardening_system
initialize_gardening_system(game)
"""

import random
from message_system import MessageCategory, MessagePriority

def initialize_gardening_system(game):
    """
    Initialize the gardening system for the game.
    
    Args:
        game: The main game instance
    """
    print("\n=== INITIALIZING GARDENING SYSTEM ===\n")
    
    # 1. Ensure the message system always shows gardening messages
    _configure_message_system(game)
    
    # 2. Enhance NPC gardening behaviors
    _enhance_gardening_behaviors(game)
    
    # 3. Add gardening observer to track plant growth
    _add_gardening_observer(game)
    
    print("Gardening system initialized! NPCs will now perform gardening actions that affect the game state.")
    return True

def _configure_message_system(game):
    """Configure the message system to prioritize gardening messages."""
    if hasattr(game, 'message_manager'):
        # Set the display rate for gardening messages to 100%
        game.message_manager.display_rates[MessageCategory.NPC_GARDENING] = 100
        
        # Set the cooldown for gardening messages to 0
        game.message_manager.cooldown_periods[MessageCategory.NPC_GARDENING] = 0
        
        # Ensure gardening messages are shown directly
        game.message_manager.show_directly[MessageCategory.NPC_GARDENING] = True
    
    # Configure the message coordinator if available
    if hasattr(game, 'message_coordinator'):
        # Increase the max messages per type for gardening
        game.message_coordinator.max_messages_per_type['npc_gardening'] = 10
        
        # Add gardening to the allowed notification types if that attribute exists
        if hasattr(game.message_coordinator, 'allowed_notification_types'):
            if 'npc_gardening' not in game.message_coordinator.allowed_notification_types:
                game.message_coordinator.allowed_notification_types.append('npc_gardening')

def _enhance_gardening_behaviors(game):
    """Enhance NPC gardening behaviors to make them more frequent and functional."""
    from npc_behavior import BehaviorType, behavior_settings
    
    # Increase the base weight for gardening behaviors
    behavior_settings.default_weights[BehaviorType.GARDENING] = 0.3  # 30% base chance
    
    # Double the frequency multiplier for gardening behaviors
    behavior_settings.frequency_multipliers[BehaviorType.GARDENING] = 2.0
    
    # Remove cooldown for gardening behaviors
    behavior_settings.cooldowns[BehaviorType.GARDENING] = 0

def _add_gardening_observer(game):
    """Add an observer to track plant growth and generate messages about it."""
    def observe_gardening_state():
        """Observe the game state for gardening actions and generate messages."""
        # Check all areas for soil objects
        for area_id, area in game.areas.items():
            for obj in area.objects:
                # Check if this is a soil object with plants
                if hasattr(obj, 'name') and any(keyword in obj.name.lower() for keyword in ['soil', 'garden', 'dirt']):
                    if hasattr(obj, 'plants') and obj.plants:
                        # Generate a message about the plants
                        plant_names = [plant.name for plant in obj.plants]
                        if plant_names:
                            plant_list = ", ".join(plant_names)
                            message = f"The {obj.name} contains: {plant_list}"
                            
                            # Add to message manager with high priority
                            if hasattr(game, 'message_manager'):
                                game.message_manager.add_message(
                                    text=message,
                                    category=MessageCategory.ENVIRONMENT_CHANGE,
                                    priority=MessagePriority.HIGH
                                )
    
    # Hook the observer into the game's turn update system
    original_update_game_turn = game.update_game_turn
    
    def patched_update_game_turn():
        """Patched version of update_game_turn that includes gardening observation."""
        # Call the original method
        result = original_update_game_turn()
        
        # Observe gardening state
        observe_gardening_state()
        
        return result
    
    # Replace the original method
    game.update_game_turn = patched_update_game_turn

# Example usage:
# from gardening_system import initialize_gardening_system
# initialize_gardening_system(game)
