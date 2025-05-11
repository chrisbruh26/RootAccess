# Root Access v2

A text-based open-world game combining elements of Animal Crossing and Watch Dogs 2 in a wacky and entertaining way.

## Key Features

- **Scalable NPC Behavior System**: NPCs can perform various actions like talking, fighting, using items, and gardening.
- **Gang System**: Gang members can switch between silly villager-like behavior and aggressive combat.
- **Gardening**: Plant, water, and harvest crops with special effects.
- **Hacking**: Hack computers to run special programs and gain advantages.
- **Environmental Interaction**: NPCs react to the environment, player actions, and other NPCs.

## NPC Behavior Management

The game uses a streamlined NPC behavior system that:

1. **Limits NPC Actions**: Controls how many actions NPCs can take per turn to prevent spam.
2. **Provides Variety**: NPCs can perform different types of actions based on their environment and state.
3. **Summarizes Actions**: Condenses NPC actions into readable summaries for the player.
4. **Enables Scalability**: The system is designed to handle many NPCs without overwhelming the player.

## Commands

- **Movement**: north, south, east, west
- **Basic Actions**: look, inventory/inv, take [item], drop [item], use [item]
- **Object Interaction**: interact [object]
- **Gardening**: plant [seed], water, harvest [plant]
- **Hacking**: hack, run [program]
- **Help**: help
- **Exit**: quit

## Customizing NPC Behaviors

You can adjust NPC behavior frequencies and cooldowns by modifying the `BehaviorSettings` class in the code:

```python
# Example: Make NPCs fight less often
behavior_settings.set_frequency(BehaviorType.FIGHT, 0.5)  # 50% of normal frequency

# Example: Increase cooldown between gardening actions
behavior_settings.set_cooldown(BehaviorType.GARDENING, 4)  # 4 turns between gardening actions
```

## Adding New NPC Actions

To add new NPC actions, edit the `npc_actions.json` file with new categories and actions.

## Future Improvements

- More complex NPC decision-making based on relationships and goals
- Expanded gardening system with more plant types and effects
- Advanced hacking mechanics with puzzles and rewards
- Dynamic world events that affect NPC behavior
- Expanded combat system with more tactical options
