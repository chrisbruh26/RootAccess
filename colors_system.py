# ----------------------------- #
# ROOT ACCESS COLOR SYSTEM     #
# ----------------------------- #

"""
Color system for Root Access game.
This module provides a comprehensive color management system for the game,
allowing for consistent and semantic coloring of game elements.
"""

class ColorText:
    """
    Handles ANSI color formatting for text in the Root Access game.
    
    This class provides methods for coloring text with predefined colors
    and semantic categories for different game elements.
    """
    
    def __init__(self):
        # Base color palette - RGB values for different colors
        self.color_map = {
            # Basic colors
            "orange": (255, 100, 0),
            "blue": (50, 10, 222),
            "light_green": (150, 255, 150),
            "red": (255, 50, 50),
            "purple": (200, 50, 200),
            "magenta": (240, 22, 225),
            "cyan": (50, 200, 200),
            "yellow": (255, 255, 100),
            "gray": (180, 180, 180),
            "light_red": (255, 150, 150),
            "light_blue": (150, 150, 255),
            
            # Additional colors
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "dark_green": (0, 100, 0),
            "dark_blue": (0, 0, 139),
            "gold": (255, 215, 0),
            "silver": (192, 192, 192),
            "pink": (255, 192, 203),
            "brown": (165, 42, 42),
            "teal": (0, 128, 128),
            "lime": (50, 205, 50),
            "crimson": (220, 20, 60),
            "navy": (0, 0, 128),
            "olive": (128, 128, 0),
            "maroon": (128, 0, 0),
        }
        
        # Semantic color mapping - maps game concepts to colors
        self.semantic_colors = {
            # Status and alerts
            "danger": "red",
            "warning": "orange",
            "success": "light_green",
            "info": "light_blue",
            "system": "cyan",
            
            # Game elements
            "player": "cyan",
            "npc": "yellow",
            "gang_member": "crimson",
            "civilian": "light_blue",
            
            # Items and objects
            "weapon": "red",
            "consumable": "light_green",
            "tech": "blue",
            "plant": "lime",
            "effect": "purple",
            "object": "gray",
            
            # Areas and navigation
            "area_name": "gold",
            "direction": "light_blue",
            "connection": "blue",
            
            # Combat and status
            "damage": "light_red",
            "health": "light_green",
            "attack": "red",
            "defense": "blue",
            
            # Special events
            "hallucination": "magenta",
            "confusion": "purple",
            "hacking": "cyan",
            "gardening": "lime",
            "hiding": "gray",
        }
        
        # Text style codes
        self.styles = {
            "bold": "\033[1m",
            "italic": "\033[3m",
            "underline": "\033[4m",
            "blink": "\033[5m",
            "reverse": "\033[7m",
            "reset": "\033[0m"
        }
    
    def colorize(self, text, color_name):
        """
        Returns text wrapped in ANSI color codes.
        
        Args:
            text (str): The text to colorize
            color_name (str): The name of the color to use
            
        Returns:
            str: The colorized text
        """
        if color_name in self.color_map:
            r, g, b = self.color_map[color_name]
            return f"\033[38;2;{r};{g};{b}m{text}\033[0m"
        else:
            return text  # Return plain text if color name isn't found
    
    def semantic(self, text, category):
        """
        Colorizes text based on semantic category.
        
        Args:
            text (str): The text to colorize
            category (str): The semantic category (e.g., 'danger', 'success')
            
        Returns:
            str: The colorized text
        """
        if category in self.semantic_colors:
            color_name = self.semantic_colors[category]
            return self.colorize(text, color_name)
        else:
            return text  # Return plain text if category isn't found
    
    def style(self, text, style_name):
        """
        Applies a text style to the given text.
        
        Args:
            text (str): The text to style
            style_name (str): The name of the style to apply
            
        Returns:
            str: The styled text
        """
        if style_name in self.styles:
            return f"{self.styles[style_name]}{text}{self.styles['reset']}"
        else:
            return text
    
    def styled_colorize(self, text, color_name, style_name):
        """
        Applies both color and style to text.
        
        Args:
            text (str): The text to format
            color_name (str): The name of the color to use
            style_name (str): The name of the style to apply
            
        Returns:
            str: The formatted text
        """
        styled_text = self.style(text, style_name)
        return self.colorize(styled_text, color_name)
    
    def format_message(self, message, replacements):
        """
        Formats a message with colored replacements.
        
        Args:
            message (str): The message template with {placeholders}
            replacements (dict): Dictionary mapping placeholders to (text, category) tuples
            
        Returns:
            str: The formatted message with colored replacements
            
        Example:
            format_message("You hit {target} with {weapon}!", {
                "target": ("the goblin", "npc"),
                "weapon": ("your sword", "weapon")
            })
        """
        for key, (text, category) in replacements.items():
            colored_text = self.semantic(text, category)
            message = message.replace(f"{{{key}}}", colored_text)
        return message
    
    def print_rgb(self, text, r, g, b):
        """
        Prints text in the specified RGB color.
        
        Args:
            text (str): The text to print
            r (int): Red component (0-255)
            g (int): Green component (0-255)
            b (int): Blue component (0-255)
        """
        print(f"\033[38;2;{r};{g};{b}m{text}\033[0m")
    
    def print(self, text, color_name):
        """
        Prints text in the specified color.
        
        Args:
            text (str): The text to print
            color_name (str): The name of the color to use
        """
        print(self.colorize(text, color_name))
    
    def print_semantic(self, text, category):
        """
        Prints text in the color associated with the semantic category.
        
        Args:
            text (str): The text to print
            category (str): The semantic category
        """
        print(self.semantic(text, category))


# Create a global instance for easy access
colorizer = ColorText()


# Helper functions for common color operations
def colorize(text, color_name):
    """Shorthand for colorizer.colorize()"""
    return colorizer.colorize(text, color_name)

def semantic(text, category):
    """Shorthand for colorizer.semantic()"""
    return colorizer.semantic(text, category)

def style(text, style_name):
    """Shorthand for colorizer.style()"""
    return colorizer.style(text, style_name)

def print_colored(text, color_name):
    """Shorthand for printing colored text"""
    print(colorize(text, color_name))

def print_semantic(text, category):
    """Shorthand for printing semantically colored text"""
    print(semantic(text, category))
