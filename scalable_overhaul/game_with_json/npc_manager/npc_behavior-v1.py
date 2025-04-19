import random

class Behavior:
    """Base class for NPC behaviors."""
    def __init__(self, npc):
        self.npc = npc

    def perform(self, game):
        """Perform the behavior action. To be overridden by subclasses."""
        pass

    def __str__(self):
        return self.__class__.__name__

class IdleBehavior(Behavior):
    """NPC does nothing or simple idle actions."""
    def perform(self, game):
        # NPC might look around or say something idle
        reactions = game.NPC_REACTIONS.get("idle_phrases", ["{} is standing around."])
        reaction = random.choice(reactions)
        return reaction.format(self.npc.name)

class TalkBehavior(Behavior):
    """NPC talks to another NPC or player."""
    def __init__(self, npc, target):
        super().__init__(npc)
        self.target = target

    def perform(self, game):
        # Use npc_reactions.json talking phrases
        reactions = game.NPC_REACTIONS.get("talking_phrases", ["{} talks to {}."])
        reaction = random.choice(reactions)
        return reaction.format(self.npc.name, self.target.name)

class FightBehavior(Behavior):
    """NPC fights another NPC or player."""
    def __init__(self, npc, target):
        super().__init__(npc)
        self.target = target

    def perform(self, game):
        # Simple fight logic: reduce health, print fight message
        damage = random.randint(5, 15)
        self.target.health -= damage
        if self.target.health <= 0:
            self.target.is_alive = False
            result = f"{self.npc.name} has defeated {self.target.name}!"
        else:
            result = f"{self.npc.name} attacks {self.target.name} for {damage} damage. {self.target.name} has {self.target.health} health left."
        return result

class UseItemBehavior(Behavior):
    """NPC uses an item in the environment."""
    def __init__(self, npc, item):
        super().__init__(npc)
        self.item = item

    def perform(self, game):
        # Example: NPC uses an item, e.g., healing or weapon
        if hasattr(self.item, 'health_restore'):
            self.npc.health += self.item.health_restore
            return f"{self.npc.name} uses {self.item.name} and restores {self.item.health_restore} health."
        elif hasattr(self.item, 'damage'):
            return f"{self.npc.name} brandishes {self.item.name} menacingly."
        else:
            return f"{self.npc.name} interacts with {self.item.name}."

class BehaviorManager:
    """Manages NPC behaviors and transitions."""
    def __init__(self, npc):
        self.npc = npc
        self.current_behavior = IdleBehavior(npc)

    def update(self, game):
        """Update NPC behavior each tick."""
        if not self.npc.is_alive:
            return f"{self.npc.name} is dead and cannot act."

        # Perform current behavior
        result = self.current_behavior.perform(game)

        # Decide next behavior (simple random for now)
        self.choose_next_behavior(game)

        return result

    def choose_next_behavior(self, game):
        """Randomly choose next behavior for demonstration."""
        behaviors = [IdleBehavior, TalkBehavior, FightBehavior, UseItemBehavior]
        choice = random.choice(behaviors)

        if choice == IdleBehavior:
            self.current_behavior = IdleBehavior(self.npc)
        elif choice == TalkBehavior:
            # Pick a random NPC or player in the same area to talk to
            targets = [npc for npc in self.npc.location.npcs if npc != self.npc and npc.is_alive]
            if hasattr(game, 'player') and game.player.current_area == self.npc.location:
                targets.append(game.player)
            if targets:
                target = random.choice(targets)
                self.current_behavior = TalkBehavior(self.npc, target)
            else:
                self.current_behavior = IdleBehavior(self.npc)
        elif choice == FightBehavior:
            # Pick a random NPC or player to fight
            targets = [npc for npc in self.npc.location.npcs if npc != self.npc and npc.is_alive]
            if hasattr(game, 'player') and game.player.current_area == self.npc.location:
                targets.append(game.player)
            if targets:
                target = random.choice(targets)
                self.current_behavior = FightBehavior(self.npc, target)
            else:
                self.current_behavior = IdleBehavior(self.npc)
        elif choice == UseItemBehavior:
            # Pick a random item in the area
            items = self.npc.location.items if hasattr(self.npc.location, 'items') else []
            if items:
                item = random.choice(items)
                self.current_behavior = UseItemBehavior(self.npc, item)
            else:
                self.current_behavior = IdleBehavior(self.npc)
