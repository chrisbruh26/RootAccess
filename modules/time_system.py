"""
Time System module for Root Access v3.
Handles the in-game time and scheduling.
"""

class TimeSystem:
    """Manages the in-game time system."""
    def __init__(self, start_hour=8, start_minute=0, start_day=1):
        self.hour = start_hour
        self.minute = start_minute
        self.day = start_day
        self.time_scale = 1  # How many real minutes pass per game minute
        self.paused = False
    
    def advance_time(self, minutes=1):
        """Advance the game time by a specified number of minutes."""
        if self.paused:
            return
        
        self.minute += minutes
        
        # Handle hour rollover
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
            
            # Handle day rollover
            if self.hour >= 24:
                self.hour -= 24
                self.day += 1
    
    def get_time_string(self):
        """Get a formatted string representation of the current time."""
        am_pm = "AM" if self.hour < 12 else "PM"
        hour_12 = self.hour % 12
        if hour_12 == 0:
            hour_12 = 12
        return f"Day {self.day}, {hour_12:02d}:{self.minute:02d} {am_pm}"
    
    def get_time_of_day(self):
        """Get the current time of day (morning, afternoon, evening, night)."""
        if 5 <= self.hour < 12:
            return "morning"
        elif 12 <= self.hour < 17:
            return "afternoon"
        elif 17 <= self.hour < 21:
            return "evening"
        else:
            return "night"
    
    def set_time(self, hour, minute=0, day=None):
        """Set the game time to a specific hour and minute."""
        if 0 <= hour < 24 and 0 <= minute < 60:
            self.hour = hour
            self.minute = minute
            if day is not None and day > 0:
                self.day = day
        else:
            print("Invalid time values.")
    
    def set_time_scale(self, scale):
        """Set the time scale (how fast time passes)."""
        if scale > 0:
            self.time_scale = scale
        else:
            print("Time scale must be positive.")
    
    def pause(self):
        """Pause the time system."""
        self.paused = True
        print("Time paused.")
    
    def resume(self):
        """Resume the time system."""
        self.paused = False
        print("Time resumed.")
    
    def is_between(self, start_hour, end_hour):
        """Check if the current time is between the specified hours."""
        if start_hour <= end_hour:
            return start_hour <= self.hour < end_hour
        else:
            # Handle overnight periods (e.g., 22:00 to 06:00)
            return self.hour >= start_hour or self.hour < end_hour
    
    def get_time_key(self):
        """Get the current time as minutes since midnight."""
        return self.hour * 60 + self.minute
    
    def to_dict(self):
        """Convert time system to dictionary for serialization."""
        return {
            "hour": self.hour,
            "minute": self.minute,
            "day": self.day,
            "time_scale": self.time_scale,
            "paused": self.paused
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create time system from dictionary."""
        time_system = cls(
            data["hour"],
            data["minute"],
            data["day"]
        )
        time_system.time_scale = data["time_scale"]
        time_system.paused = data["paused"]
        return time_system