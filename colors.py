# ----------------------------- #
# ROOT ACCESS COLOR SYSTEM     #
# ----------------------------- #

"""
This module provides backward compatibility with the original colors.py
while redirecting to the new color_system.py module.

For new code, import directly from color_system instead.
"""

from color_system import colorizer, colorize, semantic, style, print_colored, print_semantic

# Legacy function for backward compatibility
def print_rgb(text, r, g, b):
    """Prints text in the specified RGB color."""
    print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")

# Legacy color map for backward compatibility
color_map = colorizer.color_map

# Legacy color variables for backward compatibility
red = color_map["red"]
light_blue = color_map["light_blue"]
light_green = color_map["light_green"]
magenta = color_map["magenta"]
orange = color_map["orange"]
blue = color_map["blue"]
purple = color_map["purple"]
cyan = color_map["cyan"]
yellow = color_map["yellow"]
gray = color_map["gray"]
light_red = color_map["light_red"]

# Legacy ColorText class for backward compatibility
class ColorText:
    """Handles ANSI color formatting for text."""
    def __init__(self):
        self.color_map = colorizer.color_map

    def colorize(self, text, color_name):
        """Returns text wrapped in ANSI color codes."""
        return colorizer.colorize(text, color_name)

# Example usage
if __name__ == "__main__":
    # Examples using the new color system
    print(colorize("This text is red", "red"))
    print(semantic("Warning: Danger ahead!", "warning"))
    print(semantic("You found a new weapon!", "success"))
    
    # Examples using legacy functions
    print_rgb("Legacy RGB coloring", 255, 100, 0)
    
    # Using the colorizer directly
    print(colorizer.styled_colorize("Bold red text", "red", "bold"))
    
    # Message formatting with colored replacements
    message = colorizer.format_message("You hit {target} with {weapon}!", {
        "target": ("the goblin", "npc"),
        "weapon": ("your sword", "weapon")
    })
    print(message)
    
    # Semantic printing for game events
    print_semantic("A gang member is attacking you!", "danger")
    print_semantic("You found a health potion!", "success")
    print_semantic("The plant has grown!", "gardening")
