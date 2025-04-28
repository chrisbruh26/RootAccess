"""
Message Management System for Root Access

This module provides a centralized way to manage all game messages,
controlling how and when they are displayed to the player.

Key Components:
--------------
1. MessageCategory: Enum defining different types of messages
2. MessagePriority: Enum defining importance levels for messages
3. MessageManager: Main class that processes and filters messages

Configuration Options:
--------------------
- Show/Hide Categories: Control which types of messages appear in the game
- Display Rates: Set percentage chance for a message type to be shown (0-100%)
- Cooldown Periods: Set minimum turns between messages of the same category

See MESSAGE_SYSTEM_README.md for more information on customizing the system.
"""

import enum
import time
import random
from collections import defaultdict, deque

class MessageCategory(enum.Enum):
    """Categories for game messages."""
    PLAYER_ACTION = 1  # Player's direct actions
    COMBAT = 2  # Combat messages
    CRITICAL = 3  # Critical game information
    NPC_MINOR = 4  # Minor NPC interactions
    NPC_IDLE = 5  # NPC idle behaviors
    NPC_MOVEMENT = 6  # NPC movement behaviors
    NPC_INTERACTION = 7  # NPC interactions with objects or other NPCs
    NPC_TALK = 8  # NPC talking or making sounds
    NPC_GIFT = 9  # NPC giving gifts or items
    NPC_HAZARD = 10  # NPC affected by hazards
    NPC_SUMMARY = 11  # Summary of NPC actions
    HAZARD_EFFECT = 12  # Hazard effects on NPCs/environment
    AMBIENT = 13  # Ambient/environmental messages
    TRIVIAL = 14  # Very minor events
    DEBUG = 15  # Debug information
    
    # New categories for enhanced NPC behaviors
    NPC_GARDENING = 16  # NPC gardening activities (planting, watering, harvesting)
    NPC_ITEM_USE = 17   # NPC using items with real functionality
    NPC_REACTION = 18   # NPC reactions to environment or player actions
    ENVIRONMENT_CHANGE = 19  # Changes to the environment (crops growing, etc.)
    NPC_GROUP_ACTION = 20  # Coordinated actions by multiple NPCs


class MessagePriority(enum.Enum):
    """Priority levels for messages within each category."""
    CRITICAL = 1  # Must be shown
    HIGH = 2      # Almost always shown
    MEDIUM = 3    # Shown based on settings
    LOW = 4       # Rarely shown
    MINIMAL = 5   # Almost never shown


class Message:
    """Represents a single game message."""
    def __init__(self, text, category, priority=MessagePriority.MEDIUM, 
                 source=None, target=None, timestamp=None, metadata=None):
        self.text = text
        self.category = category
        self.priority = priority
        self.source = source  # Who/what generated the message
        self.target = target  # Who/what is affected by the message
        self.timestamp = timestamp or time.time()
        self.metadata = metadata or {}  # Additional data about the message
        self.shown = False  # Whether this message has been shown to the player


class MessageManager:
    """Central manager for all game messages."""
    def __init__(self, game):
        self.game = game
        self.messages = deque(maxlen=1000)  # Store recent messages
        self.message_counts = defaultdict(int)  # Track message counts by category
        self.last_shown = defaultdict(int)  # Track when messages were last shown by category
        
        # Initialize dictionaries for category settings
        self.show_directly = {}
        self.display_rates = {}
        self.cooldown_periods = {}
        
        # Configure display settings for each category
        self.display_settings = {
            # Category, show_directly, throttle_rate
            MessageCategory.PLAYER_ACTION: (True, 0),  # Always show directly
            MessageCategory.COMBAT: (True, 0),  # Always show directly
            MessageCategory.CRITICAL: (True, 0),  # Always show directly
            MessageCategory.NPC_MINOR: (True, 0.7),  # Show 30% of the time
            MessageCategory.NPC_IDLE: (True, 0.9),  # Show 10% of the time
            MessageCategory.NPC_MOVEMENT: (True, 0.8),  # Show 20% of the time
            MessageCategory.NPC_INTERACTION: (True, 0.6),  # Show 40% of the time
            MessageCategory.NPC_TALK: (True, 0.5),  # Show 50% of the time
            MessageCategory.NPC_GIFT: (True, 0.2),  # Show 80% of the time
            MessageCategory.NPC_HAZARD: (True, 0.3),  # Show 70% of the time
            MessageCategory.NPC_SUMMARY: (True, 0),  # Always show NPC summaries
            MessageCategory.HAZARD_EFFECT: (True, 0.9),  # Show only 10% of the time
            MessageCategory.AMBIENT: (True, 0.8),  # Show 20% of the time
            MessageCategory.TRIVIAL: (False, 0.95),  # Show only 5% of the time
            MessageCategory.DEBUG: (False, 1.0),  # Never show (unless in debug mode)
            
            # New behavior-focused categories
            MessageCategory.NPC_GARDENING: (True, 0.2),  # Show 80% of the time - highlight gardening
            MessageCategory.NPC_ITEM_USE: (True, 0.4),  # Show 60% of the time
            MessageCategory.NPC_REACTION: (True, 0.3),  # Show 70% of the time
            MessageCategory.ENVIRONMENT_CHANGE: (True, 0.1),  # Show 90% of the time - important for game state
            MessageCategory.NPC_GROUP_ACTION: (True, 0.3),  # Show 70% of the time
        }
        
        # Initialize the individual setting dictionaries from display_settings
        for category, (show, rate) in self.display_settings.items():
            self.show_directly[category] = show
            self.display_rates[category] = int((1 - rate) * 100)  # Convert throttle rate to display percentage
            self.cooldown_periods[category] = 0  # Default cooldown is 0
        
        # Cooldown periods (in turns) for each category to prevent spam
        self.category_cooldowns = {
            MessageCategory.NPC_MINOR: 3,      # Show NPC minor actions every 3 turns at most
            MessageCategory.NPC_IDLE: 5,       # Show NPC idle behaviors every 5 turns at most
            MessageCategory.NPC_MOVEMENT: 4,   # Show NPC movement behaviors every 4 turns at most
            MessageCategory.NPC_INTERACTION: 3, # Show NPC interactions every 3 turns at most
            MessageCategory.NPC_TALK: 2,       # Show NPC talking every 2 turns at most
            MessageCategory.NPC_GIFT: 1,       # Show NPC gift-giving every turn
            MessageCategory.NPC_HAZARD: 2,     # Show NPC hazard effects every 2 turns at most
            MessageCategory.HAZARD_EFFECT: 5,  # Show hazard effects every 5 turns at most
            MessageCategory.AMBIENT: 4,        # Show ambient messages every 4 turns at most
            MessageCategory.TRIVIAL: 10,       # Show trivial messages every 10 turns at most
            
            # New behavior-focused categories with appropriate cooldowns
            MessageCategory.NPC_GARDENING: 1,  # Show gardening activities frequently
            MessageCategory.NPC_ITEM_USE: 2,   # Show item usage every 2 turns
            MessageCategory.NPC_REACTION: 1,   # Show reactions frequently
            MessageCategory.ENVIRONMENT_CHANGE: 1,  # Show environment changes every turn
            MessageCategory.NPC_GROUP_ACTION: 3,    # Show group actions every 3 turns
        }
        
        self.current_turn = 0
        self.debug_mode = False
    
    def add_message(self, text, category=None, priority=None, source=None):
        """Add a message to the system."""
        # Auto-detect category if not provided
        if category is None:
            category = self._detect_category(text)
        
        # Create the message
        message = Message(
            text=text,
            category=category,
            priority=priority,
            source=source
        )
        
        # Store the message
        self.messages.append(message)
        self.message_counts[category] += 1
        
        # Process the message according to its category
        return self._process_message(message)
    
    def _detect_category(self, text):
        """Automatically detect the category of a message based on its content."""
        text_lower = text.lower()
        
        # First check for combat messages (highest priority)
        if "attack" in text_lower or "damage" in text_lower or "fight" in text_lower:
            return MessageCategory.COMBAT
        
        # Check for gardening-related messages (high priority for game focus)
        gardening_keywords = [
            "plant", "plants", "planting", "planted",
            "water", "waters", "watering", "watered",
            "harvest", "harvests", "harvesting", "harvested",
            "grow", "grows", "growing", "grown",
            "crop", "crops", 
            "garden", "gardens", "gardening", "gardened",
            "seed", "seeds", "seeding", "seeded",
            "fertilize", "fertilizes", "fertilizing", "fertilized",
            "soil", "dirt", "compost",
            "weed", "weeds", "weeding", "weeded",
            "prune", "prunes", "pruning", "pruned",
            "flower", "flowers", "flowering", "flowered",
            "vegetable", "vegetables",
            "fruit", "fruits",
            "tomato", "tomatoes",
            "carrot", "carrots",
            "potato", "potatoes",
            "corn", "wheat"
        ]
        if any(word in text_lower for word in gardening_keywords):
            return MessageCategory.NPC_GARDENING
            
        # Check for environment changes
        if any(word in text_lower for word in ["changed", "transformed", "grew", "withered", "bloomed", "sprouted"]):
            return MessageCategory.ENVIRONMENT_CHANGE
            
        # Check for item usage
        if any(word in text_lower for word in ["use", "using", "activate", "activates", "operates", "picks up", "drops"]):
            return MessageCategory.NPC_ITEM_USE
            
        # Check for NPC reactions
        if any(word in text_lower for word in ["reacts", "responds", "notices", "surprised by", "shocked by", "impressed by"]):
            return MessageCategory.NPC_REACTION
            
        # Check for group actions
        if any(word in text_lower for word in ["together", "group", "gang", "collectively", "coordinate", "team up"]):
            return MessageCategory.NPC_GROUP_ACTION
        
        # Check for NPC-specific categories
        if "npc" in text_lower or "member" in text_lower:
            return MessageCategory.NPC_MINOR
        
        # Check for hazard effects
        if "hazard" in text_lower or "effect" in text_lower:
            return MessageCategory.HAZARD_EFFECT
            
        # Check for NPC talk
        if any(word in text_lower for word in ["says", "talks", "speaks", "shouts", "whispers", "mutters"]):
            return MessageCategory.NPC_TALK
            
        # Check for NPC movement
        if any(word in text_lower for word in ["walks", "runs", "moves", "jumps", "climbs", "sneaks"]):
            return MessageCategory.NPC_MOVEMENT
        
        # Default to trivial if no other category matches
        return MessageCategory.TRIVIAL
    
    def _process_message(self, message):
        """Process a message according to its category and settings."""
        category = message.category
        show_directly, throttle_rate = self.display_settings[category]
        
        # Check if this category is on cooldown
        cooldown = self.category_cooldowns.get(category, 0)
        on_cooldown = (self.current_turn - self.last_shown[category]) < cooldown
        
        # Apply throttling - randomly decide whether to show based on throttle rate
        throttled = random.random() < throttle_rate
        
        # Determine if message should be shown directly
        should_show = show_directly and not throttled and not on_cooldown
        
        # Override for debug mode
        if self.debug_mode and category == MessageCategory.DEBUG:
            should_show = True
        
        # Override for critical priority
        if message.priority == MessagePriority.CRITICAL or message.priority == MessagePriority.HIGH:
            should_show = True
            
        # ALWAYS show gardening and environment change messages
        if category in [MessageCategory.NPC_GARDENING, MessageCategory.ENVIRONMENT_CHANGE]:
            should_show = True
            
        # Also check message text for gardening keywords
        if not should_show and message.text:
            text_lower = message.text.lower()
            gardening_keywords = ["plant", "water", "harvest", "garden", "seed", "crop", "soil", "fertilize"]
            if any(keyword in text_lower for keyword in gardening_keywords):
                should_show = True
        
        # If message should be shown, mark it and update last shown time
        if should_show:
            message.shown = True
            self.last_shown[category] = self.current_turn
        
        return should_show, message.text
    
    def new_turn(self):
        """Start a new turn, incrementing the turn counter."""
        self.current_turn += 1
    
    def get_message_summary(self, categories=None, clear_shown=True):
        """Get a summary of messages for specified categories."""
        if categories is None:
            categories = [
                cat for cat, (show, _) in self.display_settings.items() 
                if show
            ]
        
        # Group messages by category
        category_messages = defaultdict(list)
        for message in self.messages:
            if not message.shown and message.category in categories:
                category_messages[message.category].append(message)
        
        # Build summary
        summary_parts = []
        for category in categories:
            messages = category_messages[category]
            if not messages:
                continue
            
            # Get up to 3 messages per category
            selected_messages = messages[:3]
            
            # Mark as shown if requested
            if clear_shown:
                for message in selected_messages:
                    message.shown = True
            
            # Add to summary
            for message in selected_messages:
                summary_parts.append(message.text)
        
        return "\n".join(summary_parts) if summary_parts else None
    
    def clear_messages(self, category=None):
        """Clear all messages, optionally only for a specific category."""
        if category is None:
            self.messages.clear()
            self.message_counts.clear()
        else:
            self.messages = deque([m for m in self.messages if m.category != category], 
                                 maxlen=self.messages.maxlen)
            self.message_counts[category] = 0


# Helper functions for common message types

def player_action_message(text, priority=MessagePriority.MEDIUM, **kwargs):
    """Create a player action message."""
    return Message(text, MessageCategory.PLAYER_ACTION, priority, **kwargs)

def combat_message(text, priority=MessagePriority.HIGH, **kwargs):
    """Create a combat message."""
    return Message(text, MessageCategory.COMBAT, priority, **kwargs)



def npc_minor_message(text, priority=MessagePriority.LOW, **kwargs):
    """Create a minor NPC interaction message."""
    return Message(text, MessageCategory.NPC_MINOR, priority, **kwargs)

def hazard_effect_message(text, priority=MessagePriority.LOW, **kwargs):
    """Create a hazard effect message."""
    return Message(text, MessageCategory.HAZARD_EFFECT, priority, **kwargs)

# Helper functions for new message categories

def npc_gardening_message(text, priority=MessagePriority.MEDIUM, **kwargs):
    """Create a message about NPC gardening activities."""
    return Message(text, MessageCategory.NPC_GARDENING, priority, **kwargs)

def npc_item_use_message(text, priority=MessagePriority.MEDIUM, **kwargs):
    """Create a message about NPC item usage."""
    return Message(text, MessageCategory.NPC_ITEM_USE, priority, **kwargs)

def npc_reaction_message(text, priority=MessagePriority.MEDIUM, **kwargs):
    """Create a message about NPC reactions to events."""
    return Message(text, MessageCategory.NPC_REACTION, priority, **kwargs)

def environment_change_message(text, priority=MessagePriority.HIGH, **kwargs):
    """Create a message about changes in the environment."""
    return Message(text, MessageCategory.ENVIRONMENT_CHANGE, priority, **kwargs)

def npc_group_action_message(text, priority=MessagePriority.MEDIUM, **kwargs):
    """Create a message about coordinated actions by multiple NPCs."""
    return Message(text, MessageCategory.NPC_GROUP_ACTION, priority, **kwargs)
