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
        
        # Determine if we should remind the player about unread notifications
        should_remind = (
            self.unread_count > 0 and 
            (self.turn_counter - self.last_reminder_turn) >= self.reminder_frequency
        )
        
        if should_remind:
            self.last_reminder_turn = self.turn_counter
            return self._create_reminder()
        
        return None
    
    def add_notification(self, message, category="general", importance=1):
        """Add a new notification to the system."""
        notification = Notification(message, category, importance=importance)
        self.notifications.append(notification)
        self.unread_count += 1
        
        # Return True if this is the first unread notification
        return self.unread_count == 1
    
    def get_unread_count(self):
        """Get the number of unread notifications."""
        return self.unread_count
    
    def read_notifications(self, count=None, category=None):
        """Read and return notifications, optionally filtering by category.
        
        Args:
            count: Maximum number of notifications to return. If None, returns all.
            category: Category to filter by. If None, returns all categories.
            
        Returns:
            A tuple of (notifications_text, remaining_count)
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
        
        # Mark these notifications as read
        for notification in notifications_to_read:
            if not notification.read:
                notification.mark_as_read()
                self.unread_count -= 1
        
        # Format the notifications
        if not notifications_to_read:
            return f"No {category} notifications found.", self.unread_count
        
        # Group notifications by category for better readability
        notifications_by_category = {}
        for notification in notifications_to_read:
            if notification.category not in notifications_by_category:
                notifications_by_category[notification.category] = []
            notifications_by_category[notification.category].append(notification)
        
        # Format the output
        output = []
        output.append(f"--- Notifications ({len(notifications_to_read)}) ---")
        
        for category, notifications in notifications_by_category.items():
            output.append(f"\n[{category.upper()}]")
            for i, notification in enumerate(notifications, 1):
                output.append(f"{i}. {notification.message}")
        
        output.append(f"\nRemaining unread: {self.unread_count}")
        
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
