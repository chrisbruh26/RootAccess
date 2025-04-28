"""
Enable Gardening Script for Root Access

This script enables all gardening enhancements in one go.
Run this script after the game has started to enable gardening features.
"""

def enable_gardening(game):
    """
    Enable all gardening enhancements.
    
    Args:
        game: The main game instance
    """
    print("Enabling gardening enhancements...")
    
    # Step 1: Enhance gardening behaviors
    from gardening_enhancement import enhance_gardening_behaviors, monkey_patch_behavior_manager
    enhance_gardening_behaviors()
    monkey_patch_behavior_manager()
    
    # Step 2: Enhance gardening messages
    from gardening_messages import enhance_gardening_messages
    enhance_gardening_messages(game)
    
    # Step 3: Install gardening observer
    from gardening_observer import install_gardening_observer
    install_gardening_observer(game)
    
    # Step 4: Add gardening items to the current area
    from add_gardening_items import add_gardening_items
    add_gardening_items(game)
    
    print("All gardening enhancements have been enabled!")
    print("NPCs will now garden more frequently, and you'll be notified of all gardening actions.")
    
    # Return a message to display to the player
    return "You notice some gardening supplies have appeared in the area. The NPCs seem interested in them."

# Example usage:
# from enable_gardening import enable_gardening
# enable_gardening(game)
