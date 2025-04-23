
"""
Message Management System for Root Access

This module provides a centralized way to manage all game messages,
controlling how and when they are displayed to the player.
"""

import enum
import time
import random
from collections import defaultdict, deque

class MessageCategory(enum.Enum):
    """Categories for game messages."""
    # Category 1: Should be notifications only
    NOTIFICATION = 1  # NPC significant interactions, special events
    
    # Category 2: Should always be shown in the game
    PLAYER_ACTION = 2  # Player's direct actions
    COMBAT = 3  # Combat messages
    CRITICAL = 4  # Critical game information
    
    # Category 3: Limited to prevent spam but shown occasionally
    NPC_MINOR = 5  # Minor NPC interactions
    NPC_IDLE = 6  # NPC idle behaviors (standing, waiting, etc.)
    NPC_MOVEMENT = 7  # NPC movement behaviors (walking, running, etc.)
    NPC_INTERACTION = 8  # NPC interactions with objects or other NPCs
    NPC_TALK = 9  # NPC talking or making sounds
    NPC_GIFT = 10  # NPC giving gifts or items
    NPC_HAZARD = 11  # NPC affected by hazards
    NPC_SUMMARY = 12  # Summary of NPC actions
    HAZARD_EFFECT = 13  # Hazard effects on NPCs/environment
    AMBIENT = 14  # Ambient/environmental messages
    
    # Category 4: Least important, rare or never shown
    TRIVIAL = 15  # Very minor events
    DEBUG = 16  # Debug information


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
        
        # Configure display settings for each category
        self.display_settings = {
            # Category, show_directly, add_to_notifications, throttle_rate
            MessageCategory.NOTIFICATION: (False, True, 0),  # Never show directly, always add to notifications
            MessageCategory.PLAYER_ACTION: (True, False, 0),  # Always show directly, never add to notifications
            MessageCategory.COMBAT: (True, False, 0),  # Always show directly, never add to notifications
            MessageCategory.CRITICAL: (True, True, 0),  # Always show directly AND add to notifications
            
            # NPC message categories with different throttle rates
            MessageCategory.NPC_MINOR: (True, False, 0.7),  # Show 30% of the time
            MessageCategory.NPC_IDLE: (True, False, 0.9),  # Show 10% of the time
            MessageCategory.NPC_MOVEMENT: (True, False, 0.8),  # Show 20% of the time
            MessageCategory.NPC_INTERACTION: (True, False, 0.6),  # Show 40% of the time
            MessageCategory.NPC_TALK: (True, False, 0.5),  # Show 50% of the time
            MessageCategory.NPC_GIFT: (True, False, 0.2),  # Show 80% of the time
            MessageCategory.NPC_HAZARD: (True, False, 0.3),  # Show 70% of the time
            MessageCategory.NPC_SUMMARY: (True, False, 0),  # Always show NPC summaries
            
            MessageCategory.HAZARD_EFFECT: (True, False, 0.9),  # Show only 10% of the time
            MessageCategory.AMBIENT: (True, False, 0.8),  # Show 20% of the time
            MessageCategory.TRIVIAL: (False, False, 0.95),  # Show only 5% of the time
            MessageCategory.DEBUG: (False, False, 1.0),  # Never show (unless in debug mode)
        }
        
        # Configure notification importance for each category
        self.notification_importance = {
            MessageCategory.NOTIFICATION: 3,  # Medium importance
            MessageCategory.CRITICAL: 5,      # Highest importance
            
            # NPC message categories with different importance levels
            MessageCategory.NPC_MINOR: 2,     # Lower importance
            MessageCategory.NPC_IDLE: 1,      # Lowest importance
            MessageCategory.NPC_MOVEMENT: 1,  # Lowest importance
            MessageCategory.NPC_INTERACTION: 2, # Lower importance
            MessageCategory.NPC_TALK: 2,      # Lower importance
            MessageCategory.NPC_GIFT: 3,      # Medium importance
            MessageCategory.NPC_HAZARD: 3,    # Medium importance
            MessageCategory.NPC_SUMMARY: 3,   # Medium importance
            
            MessageCategory.HAZARD_EFFECT: 2, # Lower importance
            MessageCategory.AMBIENT: 1,       # Lowest importance
            MessageCategory.TRIVIAL: 1,       # Lowest importance
        }
        
        # Configure notification categories for each message category
        self.notification_categories = {
            MessageCategory.NOTIFICATION: "event",
            MessageCategory.CRITICAL: "critical",
            
            # NPC message categories with different notification categories
            MessageCategory.NPC_MINOR: "npc",
            MessageCategory.NPC_IDLE: "npc-idle",
            MessageCategory.NPC_MOVEMENT: "npc-movement",
            MessageCategory.NPC_INTERACTION: "npc-interaction",
            MessageCategory.NPC_TALK: "npc-talk",
            MessageCategory.NPC_GIFT: "npc-gift",
            MessageCategory.NPC_HAZARD: "npc-hazard",
            MessageCategory.NPC_SUMMARY: "npc-summary",
            
            MessageCategory.HAZARD_EFFECT: "hazard",
            MessageCategory.AMBIENT: "ambient",
            MessageCategory.TRIVIAL: "misc",
        }
        
        # Keywords that indicate message categories
        self.category_keywords = {
            MessageCategory.NOTIFICATION: [
                "gives you", "gift", "offers you", "planting", "harvesting", 
                "watering", "item", "defeated", "died", "discovered"
            ],
            MessageCategory.COMBAT: [
                "attack", "damage", "health", "wounded", "hit", "strike", "defend",
                "block", "dodge", "evade", "kill", "defeat"
            ],
            
            # NPC message categories with different keywords
            MessageCategory.NPC_MINOR: [
                "member", "gang member", "npc", "person"
            ],
            MessageCategory.NPC_IDLE: [
                "stands", "sitting", "waiting", "idle", "resting", "sleeping",
                "leaning", "not moving", "stationary"
            ],
            MessageCategory.NPC_MOVEMENT: [
                "walks", "running", "moving", "pacing", "wandering", "strolling",
                "jogging", "sprinting", "climbing", "crawling", "sneaking"
            ],
            MessageCategory.NPC_INTERACTION: [
                "picks up", "drops", "examines", "uses", "interacts with", "touches",
                "pushes", "pulls", "opens", "closes", "activates", "deactivates"
            ],
            MessageCategory.NPC_TALK: [
                "talks", "speaks", "says", "whispers", "mutters", "shouts", "yells",
                "screams", "laughs", "cries", "sings", "hums", "grunts", "sighs"
            ],
            MessageCategory.NPC_GIFT: [
                "gives", "offers", "presents", "hands over", "donates", "shares",
                "distributes", "gifts", "bestows", "grants"
            ],
            MessageCategory.NPC_HAZARD: [
                "affected by", "suffering from", "experiencing", "under the influence of",
                "reacting to", "responding to", "hallucinating", "confused", "dizzy"
            ],
            
            MessageCategory.HAZARD_EFFECT: [
                "hallucination", "poison", "radiation", "electric",
                "burning", "freezing", "confusion", "dizziness"
            ],
            MessageCategory.AMBIENT: [
                "wind", "rain", "thunder", "lightning", "fog", "mist", "snow",
                "temperature", "weather", "atmosphere", "environment"
            ],
            MessageCategory.TRIVIAL: [
                "not detected", "ignores", "doesn't notice", "unaffected", 
                "no effect", "nothing happens"
            ]
        }
        
        # Cooldown periods (in turns) for each category to prevent spam
        self.category_cooldowns = {
            # NPC message categories with different cooldowns
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
        }
        
        self.current_turn = 0
        self.debug_mode = False
    
    def add_message(self, text, category=None, priority=MessagePriority.MEDIUM, 
                   source=None, target=None, metadata=None):
        """Add a message to the system with automatic category detection if not specified."""
        # Auto-detect category if not provided
        if category is None:
            category = self._detect_category(text)
        
        # Create the message
        message = Message(
            text=text,
            category=category,
            priority=priority,
            source=source,
            target=target,
            metadata=metadata
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
        if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.COMBAT]):
            return MessageCategory.COMBAT
        
        # Then check for notification messages (second highest priority)
        if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.NOTIFICATION]):
            return MessageCategory.NOTIFICATION
        
        # Check for NPC-specific categories
        if "member" in text_lower or "npc" in text_lower:
            # Check for NPC gift-giving
            if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.NPC_GIFT]):
                return MessageCategory.NPC_GIFT
            
            # Check for NPC hazard effects
            if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.NPC_HAZARD]):
                return MessageCategory.NPC_HAZARD
            
            # Check for NPC talking
            if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.NPC_TALK]):
                return MessageCategory.NPC_TALK
            
            # Check for NPC interactions
            if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.NPC_INTERACTION]):
                return MessageCategory.NPC_INTERACTION
            
            # Check for NPC movement
            if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.NPC_MOVEMENT]):
                return MessageCategory.NPC_MOVEMENT
            
            # Check for NPC idle behaviors
            if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.NPC_IDLE]):
                return MessageCategory.NPC_IDLE
            
            # If it's an NPC message but doesn't match any specific category, use NPC_MINOR
            return MessageCategory.NPC_MINOR
        
        # Check for hazard effects
        if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.HAZARD_EFFECT]):
            return MessageCategory.HAZARD_EFFECT
        
        # Check for ambient messages
        if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.AMBIENT]):
            return MessageCategory.AMBIENT
        
        # Check for trivial messages
        if any(keyword in text_lower for keyword in self.category_keywords[MessageCategory.TRIVIAL]):
            return MessageCategory.TRIVIAL
        
        # Default to NOTIFICATION if no category is detected
        return MessageCategory.NOTIFICATION
    
    def _process_message(self, message):
        """Process a message according to its category and settings."""
        category = message.category
        show_directly, add_to_notifications, throttle_rate = self.display_settings[category]
        
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
        if message.priority == MessagePriority.CRITICAL:
            should_show = True
        
        # If message should be shown, mark it and update last shown time
        if should_show:
            message.shown = True
            self.last_shown[category] = self.current_turn
        
        # Add to notifications if configured
        if add_to_notifications and hasattr(self.game.player, 'notification_manager'):
            importance = self.notification_importance.get(category, 1)
            notif_category = self.notification_categories.get(category, "general")
            self.game.player.notification_manager.add_notification(
                message.text,
                category=notif_category,
                importance=importance
            )
        
        return should_show, message.text
    
    def new_turn(self):
        """Start a new turn, incrementing the turn counter."""
        self.current_turn += 1
        
    # Category settings methods
    def should_show_category(self, category):
        """Check if a category should be shown directly."""
        return self.show_directly.get(category, True)
        
    def should_notify_category(self, category):
        """Check if a category should generate notifications."""
        return self.add_to_notifications.get(category, False)
        
    def get_category_rate(self, category):
        """Get the display rate for a category (0-100%)."""
        return self.display_rates.get(category, 100)
        
    def get_category_cooldown(self, category):
        """Get the cooldown period for a category."""
        return self.cooldown_periods.get(category, 0)
        
    def set_category_show(self, category, value):
        """Set whether a category should be shown directly."""
        self.show_directly[category] = value
        
    def set_category_notify(self, category, value):
        """Set whether a category should generate notifications."""
        self.add_to_notifications[category] = value
        
    def set_category_rate(self, category, value):
        """Set the display rate for a category (0-100%)."""
        self.display_rates[category] = value
        
    def set_category_cooldown(self, category, value):
        """Set the cooldown period for a category."""
        self.cooldown_periods[category] = value
    
    def get_messages(self, category=None, count=10, include_shown=False):
        """Get recent messages, optionally filtered by category."""
        result = []
        for message in reversed(self.messages):
            if len(result) >= count:
                break
            if category is not None and message.category != category:
                continue
            if not include_shown and message.shown:
                continue
            result.append(message)
        return result
    
    def get_message_summary(self, categories=None, clear_shown=True):
        """Get a summary of messages for specified categories."""
        if categories is None:
            # Default to categories that should be shown directly
            categories = [
                cat for cat, (show, _, _) in self.display_settings.items() 
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
    
    def set_debug_mode(self, enabled=True):
        """Enable or disable debug mode."""
        self.debug_mode = enabled
    
    def configure_category(self, category, show_directly=None, add_to_notifications=None, 
                          throttle_rate=None, cooldown=None, importance=None):
        """Configure display settings for a message category."""
        if show_directly is not None or add_to_notifications is not None or throttle_rate is not None:
            current = self.display_settings[category]
            self.display_settings[category] = (
                show_directly if show_directly is not None else current[0],
                add_to_notifications if add_to_notifications is not None else current[1],
                throttle_rate if throttle_rate is not None else current[2]
            )
        
        if cooldown is not None:
            self.category_cooldowns[category] = cooldown
        
        if importance is not None:
            self.notification_importance[category] = importance
    
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

def notification_message(text, priority=MessagePriority.MEDIUM, **kwargs):
    """Create a notification message."""
    return Message(text, MessageCategory.NOTIFICATION, priority, **kwargs)

def npc_minor_message(text, priority=MessagePriority.LOW, **kwargs):
    """Create a minor NPC interaction message."""
    return Message(text, MessageCategory.NPC_MINOR, priority, **kwargs)

def hazard_effect_message(text, priority=MessagePriority.LOW, **kwargs):
    """Create a hazard effect message."""
    return Message(text, MessageCategory.HAZARD_EFFECT, priority, **kwargs)
