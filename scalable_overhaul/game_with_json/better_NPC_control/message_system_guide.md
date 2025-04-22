# Root Access Message System Guide

This guide explains how the message system works in Root Access and how to customize it to your preferences.

## Understanding the Message System

The message system in Root Access is designed to control how and when different types of messages are displayed to the player. It helps prevent spam while ensuring important information is always shown.

### Key Concepts

1. **Message Categories**: Messages are organized into categories based on their content and importance.
2. **Throttle Rate**: Controls how often messages of a certain category are shown (0-100%).
3. **Cooldown**: Prevents similar messages from appearing too frequently (measured in turns).
4. **Display Settings**: Determines whether messages are shown directly in the game or added to notifications.

## Message Categories

The game uses the following message categories:

### Always Shown (Critical Information)
- **PLAYER_ACTION**: Actions performed by the player
- **COMBAT**: Combat-related messages
- **CRITICAL**: Critical game information

### NPC Categories (Configurable)
- **NPC_MINOR**: Minor NPC interactions
- **NPC_IDLE**: NPC idle behaviors (standing, waiting, etc.)
- **NPC_MOVEMENT**: NPC movement behaviors (walking, running, etc.)
- **NPC_INTERACTION**: NPC interactions with objects or other NPCs
- **NPC_TALK**: NPC talking or making sounds
- **NPC_GIFT**: NPC giving gifts or items
- **NPC_HAZARD**: NPC affected by hazards
- **NPC_SUMMARY**: Summary of NPC actions

### Environmental Categories (Configurable)
- **HAZARD_EFFECT**: Hazard effects on NPCs/environment
- **AMBIENT**: Ambient/environmental messages
- **TRIVIAL**: Very minor events
- **DEBUG**: Debug information (only shown in debug mode)

## Customizing Message Settings

You can customize message settings in-game using the `message-settings` command.

### Basic Usage

```
message-settings                       # Show current settings
message-settings [category] [setting] [value]  # Configure a setting
message-settings presets [preset_name]  # Apply a predefined preset
```

### Available Settings

For each category, you can configure:

1. **show**: Whether to show messages directly (on/off)
2. **notify**: Whether to add to notifications (on/off)
3. **rate**: How often to show messages (0-100%)
4. **cooldown**: Turns between messages (number)

### Examples

```
message-settings npc-idle show off     # Turn off idle NPC messages
message-settings npc-talk rate 70      # Show 70% of NPC talking messages
message-settings all-npc cooldown 2    # Set cooldown for all NPC messages to 2 turns
```

## Using Presets

For quick configuration, you can use predefined presets:

```
message-settings presets quiet         # Minimal NPC messages
message-settings presets chatty        # More NPC messages
message-settings presets verbose       # Show most NPC messages (good for debugging)
message-settings presets balanced      # Balanced settings (default)
```

### Preset Details

1. **quiet**: Shows only important NPC actions, minimizing distractions
2. **chatty**: Shows more NPC actions, making the world feel more alive
3. **verbose**: Shows almost all NPC actions, useful for debugging or when you want to see everything
4. **balanced**: Default settings that balance information and readability

## Understanding Throttle Rate

The throttle rate controls how often messages of a certain category are shown:

- A rate of 100% means all messages are shown
- A rate of 50% means about half of the messages are shown
- A rate of 0% means no messages of this category are shown

This is implemented as a random check each time a message is generated. For example, with a 70% rate, each message has a 70% chance of being displayed.

## Understanding Cooldown

The cooldown setting prevents similar messages from appearing too frequently:

- A cooldown of 0 means no cooldown (messages can appear every turn)
- A cooldown of 3 means at least 3 turns must pass between messages of this category
- Higher cooldowns are useful for less important messages

## Tips for Optimal Settings

1. **For more NPC visibility**: Increase rates for NPC_INTERACTION, NPC_TALK, and NPC_MOVEMENT categories
2. **For less spam**: Increase cooldowns or decrease rates for NPC_IDLE and TRIVIAL categories
3. **For important events only**: Use the "quiet" preset and only show critical information
4. **For debugging**: Use the "verbose" preset to see all game events

## Advanced: Creating Custom Presets

If you find yourself frequently using the same settings, you can create a custom preset by modifying the `presets` dictionary in the `cmd_message_settings` method in `RA_main.py`.

## Troubleshooting

If you're not seeing certain messages:
1. Check the category's show setting is "on"
2. Check the category's rate is greater than 0%
3. Check the category's cooldown isn't too high

If you're seeing too many messages:
1. Decrease the rate for less important categories
2. Increase the cooldown for repetitive categories
3. Use the "quiet" preset as a starting point

## Default Settings

The default "balanced" preset provides a good starting point with:
- Important NPC actions shown frequently
- Less important actions shown occasionally
- Trivial messages rarely shown
- Critical information always shown
