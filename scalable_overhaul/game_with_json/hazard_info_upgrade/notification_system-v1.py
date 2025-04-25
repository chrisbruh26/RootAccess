import random
import time
from collections import deque

class Notification:
    """Represents a single notification in the game."""
    def __init__(self, message, category="general", timestamp=None, importance=1):
        self.message = message
        self.category = category  # e.g., "item", "npc", "event", "combat"
        self.timestamp = timestamp or time.time()
        self.importance = importance  # 1-5 scale, 5 being most important
        self.read = False
    
    def mark_as_read(self):
        """Mark this notification as read."""
        self.read = True
    
    def __str__(self):
        return self.message


class NotificationManager:
    """Manages game notifications to reduce spam and improve player experience."""
    def __init__(self, max_notifications=50, reminder_frequency=5):
        self.notifications = deque(maxlen=max_notifications)  # Use deque with max size to auto-remove old notifications
        self.unread_count = 0
        self.last_reminder_turn = 0
        self.reminder_frequency = reminder_frequency  # How often to remind player about unread notifications
        self.turn_counter = 0
    
    def new_turn(self):
        """Update turn counter and check if we should remind the player about notifications."""
        self.turn_counter += 1
        
        # We'll no longer create notification reminders automatically
        # This prevents recursive notification issues
        # The game will show the notification count in the UI instead
        
        return None
    
    def add_notification(self, message, category="general", importance=1):
        """Add a new notification to the system."""
        # Prevent "hazard has no effect" messages from being added
        if "hazard has no effect" in message.lower():
            from RA_main import get_random_npc_action
            message = get_random_npc_action()
        
        # Check for duplicate notifications (same message and category)
        # to prevent spam
        for existing in self.notifications:
            if existing.message == message and existing.category == category:
                # If we already have this exact notification, don't add it again
                # Just update the timestamp if it's already read
                if existing.read:
                    existing.timestamp = time.time()
                    existing.read = False
                    self.unread_count += 1
                return False
        
        # If it's a new notification, add it
        notification = Notification(message, category, importance=importance)
        self.notifications.append(notification)
        self.unread_count += 1
        
        # Return True if this is the first unread notification
        return self.unread_count == 1
    
    def get_unread_count(self):
        """Get the number of unread notifications."""
        return self.unread_count
    
    def read_and_clear_notifications(self, count=None, category=None):
        """Read and clear notifications, optionally filtering by category.
        
        Args:
            count: Maximum number of notifications to return. If None, returns all.
            category: Category to filter by. If None, returns all categories.
            
        Returns:
            A string of notifications text.
        """
        if not self.notifications:
            return "You have no notifications.", 0
        
        # Filter notifications by category if specified
        if category:
            filtered_notifications = [n for n in self.notifications if n.category == category]
        else:
            filtered_notifications = list(self.notifications)
        
        # Sort by importance (highest first) and then by timestamp (newest first)
        filtered_notifications.sort(key=lambda n: (-n.importance, -n.timestamp))
        
        # Limit to requested count if specified
        if count and count < len(filtered_notifications):
            notifications_to_read = filtered_notifications[:count]
        else:
            notifications_to_read = filtered_notifications
        
        # Format the notifications
        if not notifications_to_read:
            return f"No {category} notifications found.", 0
        
        output = []
        for notification in notifications_to_read:
            output.append(notification.message)
        
        # Remove the read notifications from the list
        self.notifications = [n for n in self.notifications if n not in notifications_to_read]
        self.unread_count = len(self.notifications)
        
        return "\n".join(output), self.unread_count
    
    def clear_notifications(self):
        """Clear all notifications and reset unread count."""
        self.notifications.clear()
        self.unread_count = 0
        return "All notifications cleared."
    
    def add_test_notification(self):
        """Add a test notification for debugging purposes."""
        test_categories = ["item", "npc", "hazard", "effect", "general"]
        test_category = random.choice(test_categories)
        test_importance = random.randint(1, 5)
        
        test_messages = [
            "This is a test notification.",
            "Testing the notification system.",
            "Notification system check.",
            "This notification was added for testing purposes.",
            f"Test notification with importance {test_importance}."
        ]
        
        self.add_notification(
            random.choice(test_messages),
            category=test_category,
            importance=test_importance
        )
        
        return f"Added test notification (Category: {test_category}, Importance: {test_importance})."
    
    def _create_reminder(self):
        """Create a reminder message about unread notifications."""
        if self.unread_count == 0:
            return None
        
        # Create different messages based on number of unread notifications
        if self.unread_count == 1:
            return f"You have 1 unread notification. Type 'notifications' to view it."
        elif self.unread_count <= 5:
            return f"You have {self.unread_count} unread notifications. Type 'notifications' to view them."
        else:
            return f"You have {self.unread_count} unread notifications! Type 'notifications' to view them."
