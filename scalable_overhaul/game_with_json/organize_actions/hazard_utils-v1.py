class Hazard:
    def __init__(self, name, description, effect, damage, duration=None):
        self.name = name
        self.description = description
        self.effect = effect
        self.damage = damage
        self.active = True
        self.duration = duration  # None means permanent, number is turns remaining
        self.remaining_turns = duration

    def update(self):
        """Decrement duration and deactivate if expired"""
        if self.duration is not None:
            self.remaining_turns -= 1
            if self.remaining_turns <= 0:
                self.active = False
        return self.active

    def group_results(self, results):
        """Group hazard results by effect status with proper grammar and interesting details"""
        # Placeholder for grouping logic
        return results
