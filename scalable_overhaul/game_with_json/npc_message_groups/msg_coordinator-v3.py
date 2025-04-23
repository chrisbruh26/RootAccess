"""
Message Coordinator for Root Access

This module coordinates between the main message system, the NPC message system,
and the notification system to ensure consistent, non-redundant messaging throughout the game.

Key Components:
--------------
1. Message Processing: Filters and routes messages to appropriate systems
2. Message Throttling: Prevents message spam by limiting frequency
3. Message Categorization: Determines message types and priorities
4. Notification Filtering: Controls which messages generate notifications
5. Message Summarization: Creates summaries of NPC actions and hazard effects

Message Types:
-------------
- npc_idle: NPCs standing around, waiting
- npc_talk: NPCs talking to each other
- npc_interact: NPCs interacting with objects
- npc_attack: NPCs attacking or being attacked
- npc_hallucination: Generic "NPC is hallucinating" messages
- npc_hallucination_detail: Specific hallucination descriptions
- npc_friendly: NPCs acting unusually friendly
- npc_gift: NPCs giving items to the player
- npc_falling_object: NPCs being hit by falling objects
- hazard_trigger: NPCs triggering hazards
- npc_gardening: NPCs performing gardening actions
- npc_resist_hazard: NPCs resisting hazard effects
- player_teleport: Player teleporting between areas

Notification Control:
-------------------
Only the following message types can create notifications:
- npc_gift: When NPCs give items to the player
- npc_gardening: When NPCs perform gardening actions
- hazard_trigger: When NPCs trigger hazards
- npc_hallucination_detail: Detailed hallucination descriptions

See MESSAGE_SYSTEM_README.md for more information on customizing the system.
"""

import random
import collections
from message_system import MessageCategory, MessagePriority, MessageManager

class MessageCoordinator:
    """Coordinates between different message systems to prevent redundancy and ensure consistency."""
    
    def __init__(self, game, message_manager, npc_message_manager, notification_manager=None):
        self.game = game
        self.message_manager = message_manager  # Main game message manager
        self.npc_message_manager = npc_message_manager  # NPC-specific message manager
        self.notification_manager = notification_manager  # Optional notification manager
        
        # Track which messages have been processed to avoid duplication
        self.processed_messages = set()
        
        # Track message counts by type for throttling
        self.message_counts = {
            "npc_idle": 0,
            "npc_talk": 0,
            "npc_interact": 0,
            "npc_attack": 0,
            "npc_hallucination": 0,
            "npc_hallucination_detail": 0,  # Detailed hallucination messages
            "npc_friendly": 0,
            "npc_gift": 0,
            "npc_unnoticed": 0,
            "npc_falling_object": 0,
            "hazard_trigger": 0,
            "npc_gardening": 0,
            "npc_resist_hazard": 0,
            "player_teleport": 0
        }
        
        # Maximum messages per type per turn - prioritize hazard reactions
        self.max_messages_per_type = {
            "npc_idle": 0,                  # No idle messages shown directly (only in summary)
            "npc_talk": 1,                  # Only 1 talk message per turn
            "npc_interact": 1,              # Only 1 interaction message per turn
            "npc_attack": 2,                # At most 2 attack messages per turn
            "npc_hallucination": 0,         # Show NO GENERIC hallucination messages per turn
            "npc_hallucination_detail": 5,  # Allow up to 5 detailed hallucination messages per turn
            "npc_friendly": 2,              # Allow up to 2 friendly messages per turn
            "npc_gift": 2,                  # Allow up to 2 gift messages per turn
            "npc_unnoticed": 0,             # No "unnoticed" messages shown directly (only in summary)
            "npc_falling_object": 2,        # Allow up to 2 falling object messages per turn
            "hazard_trigger": 3,            # Allow up to 3 hazard trigger messages per turn
            "npc_gardening": 2,             # Allow up to 2 gardening messages per turn
            "npc_resist_hazard": 1,         # Allow 1 resist message per turn
            "player_teleport": 1            # At most 1 teleport message per turn
        }
        
        # Track unique messages to prevent exact duplicates
        self.unique_messages = set()
        
        # Global message limit per turn (regardless of type)
        self.max_messages_per_turn = 10  # Increased from 5 to allow more hazard reactions
        self.current_turn_message_count = 0
        
        # Track hazard effects for summarization
        self.hazard_effects = collections.defaultdict(list)
        
        # Track NPC actions by type for better summarization
        self.npc_actions = collections.defaultdict(list)
        
        # Track gardening actions separately
        self.gardening_actions = []
        
        # Track direct hazard messages (like specific hallucinations) for display
        self.direct_hazard_messages = []
    
    def new_turn(self):
        """Reset tracking for a new turn."""
        self.processed_messages.clear()
        self.unique_messages.clear()
        self.message_counts = {key: 0 for key in self.message_counts}
        self.current_turn_message_count = 0
        
        # Clear hazard effects and NPC actions tracking
        self.hazard_effects.clear()
        self.npc_actions.clear()
        self.gardening_actions.clear()
        self.direct_hazard_messages.clear()
        
        # Notify all message systems of the new turn
        if hasattr(self.message_manager, 'new_turn'):
            self.message_manager.new_turn()
        
        if hasattr(self.npc_message_manager, 'new_turn'):
            self.npc_message_manager.new_turn()
            
        # We'll handle notification reminders directly in the game loop instead
        # to prevent recursive notification issues
        if self.notification_manager and hasattr(self.notification_manager, 'new_turn'):
            self.notification_manager.new_turn()
    
    def process_npc_message(self, message, npc=None):
        """Process an NPC message through both systems with deduplication."""
        # Skip if message is empty
        if not message:
            return None
            
        # Skip if we've already processed this exact message
        if message in self.processed_messages:
            return None
            
        # Skip if this exact message has been seen this turn (even after processing)
        if message in self.unique_messages:
            return None
        
        # Add to processed messages to avoid duplication
        self.processed_messages.add(message)
        self.unique_messages.add(message)
        
        # Determine message type for throttling
        message_type = self._determine_message_type(message)
        
        # Prioritize attack messages and hazard reactions - process them first
        is_priority = message_type == "npc_attack"
        if not is_priority and "attack" in message.lower():
            message_type = "npc_attack"
            is_priority = True
            
        # Also prioritize hallucination details and other hazard reactions
        if not is_priority and (message_type == "npc_hallucination_detail" or 
                               message_type == "npc_hallucination" or
                               message_type == "npc_friendly" or
                               message_type == "npc_falling_object" or
                               message_type == "hazard_trigger"):
            is_priority = True
        
        # Always track the message for summarization, regardless of whether we display it
        # This ensures all NPC actions are included in the summary
        self._track_for_summarization(message, message_type, npc)
        
        # Check if we've hit the global message limit for this turn
        if self.current_turn_message_count >= self.max_messages_per_turn:
            # Always allow priority messages (attacks and hazard reactions) even if we hit the limit
            if not is_priority:
                # We've already tracked the message for summarization
                return None
        
        # Check if we've hit the limit for this type of message
        if message_type and self.message_counts.get(message_type, 0) >= self.max_messages_per_type.get(message_type, 1):
            # We've already tracked the message for summarization
            return None
        
        # Increment count for this message type
        if message_type:
            self.message_counts[message_type] = self.message_counts.get(message_type, 0) + 1
        
        # First, process through NPC message manager for grouping and summarization
        # This adds the message to the NPC message manager's buffer for later summarization
        npc_result = self.npc_message_manager.add_message(message)
        
        # If NPC message manager returned a summary, use that instead of the original message
        if npc_result:
            message = npc_result
            # Also track the processed result to avoid duplicates
            self.unique_messages.add(npc_result)
        
        # Determine appropriate category and priority for the main message system
        category, priority = self._categorize_message(message, message_type)
        
        # Increment the global message count
        self.current_turn_message_count += 1
        
        # Add to main message system
        result = self.message_manager.add_message(
            text=message,
            category=category,
            priority=priority,
            source=npc
        )
        
        # Also add to notification system if it exists and is appropriate
        if self.notification_manager and self._should_create_notification(message_type, priority):
            notification_category = self._map_to_notification_category(category)
            notification_importance = self._map_priority_to_importance(priority)
            self.notification_manager.add_notification(
                message,
                category=notification_category,
                importance=notification_importance
            )
            
        return result
    
    def _track_for_summarization(self, message, message_type, npc=None):
        """Track messages for later summarization, even if they aren't displayed."""
        if not message_type:
            return
            
        # Extract NPC name and gang name if possible
        npc_name, gang_name = self._extract_npc_info(message)
        
        # If we have an NPC object, use its information
        if npc:
            if hasattr(npc, 'name'):
                npc_name = npc.name
            if hasattr(npc, 'gang') and hasattr(npc.gang, 'name'):
                gang_name = npc.gang.name
        
        # Skip if we couldn't determine the NPC name or gang name
        if not npc_name or not gang_name:
            # Try harder to extract NPC info from the message
            if "member" in message:
                parts = message.split("member")
                if len(parts) > 1:
                    # Try to extract gang name from the first part
                    gang_part = parts[0].strip()
                    if "The " in gang_part:
                        gang_name = gang_part.split("The ")[1].strip()
                    
                    # Try to extract NPC name from the second part
                    npc_part = parts[1].strip()
                    if npc_part and len(npc_part) > 0:
                        npc_name = npc_part.split()[0].rstrip(',.!')
        
        # If we still don't have NPC info, we can't track this message properly
        if not npc_name or not gang_name:
            return
            
        # Initialize collections if they don't exist
        if not hasattr(self, 'hazard_effects'):
            self.hazard_effects = collections.defaultdict(list)
        if not hasattr(self, 'direct_hazard_messages'):
            self.direct_hazard_messages = []
        if not hasattr(self, 'gardening_actions'):
            self.gardening_actions = []
        if not hasattr(self, 'npc_actions'):
            self.npc_actions = collections.defaultdict(list)
        
        # Store the original message for all hazard effects to preserve details
        # This allows us to show the specific hallucination/effect details rather than generic summaries
        if message_type in ["npc_hallucination", "npc_hallucination_detail", "npc_friendly", "npc_gift", "npc_falling_object", "hazard_trigger", "npc_resist_hazard"]:
            # For hallucination details, store in both hallucination and hallucination_detail categories
            if message_type == "npc_hallucination_detail":
                self.hazard_effects["npc_hallucination"].append((npc_name, gang_name, message))
                self.hazard_effects["npc_hallucination_detail"].append((npc_name, gang_name, message))
            else:
                # Store the full message to preserve details about the specific effect
                self.hazard_effects[message_type].append((npc_name, gang_name, message))
            
            # Store detailed hallucination messages for direct display
            if message_type == "npc_hallucination_detail":
                # Format the message to make it clear who is hallucinating
                self.direct_hazard_messages.append(f"{npc_name} {message}")
            # Also store other interesting messages that aren't just "affected by" notifications
            elif message_type in ["npc_hallucination", "npc_friendly"] and "affected by" not in message.lower():
                self.direct_hazard_messages.append(message)
        
        # Track gardening actions separately
        if message_type == "npc_gardening":
            self.gardening_actions.append((npc_name, gang_name, message))
        
        # Track ALL NPC actions by type for comprehensive summarization
        # This is the key change - we track every action regardless of type
        self.npc_actions[message_type].append((npc_name, gang_name, message))
        
        # Also track common actions in their specific categories for better organization
        if "plant" in message.lower() or "water" in message.lower() or "harvest" in message.lower() or "garden" in message.lower():
            # Make sure it's tracked as a gardening action even if the message_type is different
            if message_type != "npc_gardening":
                self.npc_actions["npc_gardening"].append((npc_name, gang_name, message))
                self.gardening_actions.append((npc_name, gang_name, message))
        
        # Track talking actions
        if "talk" in message.lower() or "says" in message.lower() or "speaking" in message.lower() or "conversation" in message.lower():
            if message_type != "npc_talk":
                self.npc_actions["npc_talk"].append((npc_name, gang_name, message))
        
        # Track interaction actions
        if "interact" in message.lower() or "using" in message.lower() or "picks up" in message.lower() or "examines" in message.lower():
            if message_type != "npc_interact":
                self.npc_actions["npc_interact"].append((npc_name, gang_name, message))
    
    def _extract_npc_info(self, message):
        """Extract NPC name and gang name from a message."""
        npc_name = None
        gang_name = None
        
        # Check for gang member references
        if "member" in message:
            # Extract the member name from the message
            # Most messages follow the pattern "The [gang_name] member [name] ..."
            if " member " in message:
                parts = message.split("The ")
                if len(parts) > 1:
                    gang_part = parts[1].split(" member ")
                    if len(gang_part) > 0:
                        gang_name = gang_part[0]
                    
                    if len(gang_part) > 1:
                        member_part = gang_part[1]
                        npc_name = member_part.split()[0].rstrip(',.!')
        
        return npc_name, gang_name
    
    def _determine_message_type(self, message):
        """Determine the type of NPC message for throttling purposes."""
        message_lower = message.lower()
        
        # Check for hazard trigger messages first
        if any(trigger in message_lower for trigger in ["triggers the", "sets off the", "activates the", "fumbles with", "accidentally triggers"]):
            return "hazard_trigger"
            
        # Check for gardening actions
        if any(garden_action in message_lower for garden_action in ["waters the", "plants the", "harvests the", "applies fertilizer", "garden", "planting", "watering"]):
            return "npc_gardening"
            
        # Check for teleport messages
        if "teleport" in message_lower:
            return "player_teleport"
            
        # Check for resist hazard messages
        if "resists the" in message_lower and "effect" in message_lower:
            return "npc_resist_hazard"
            
        # Check for specific hallucination descriptions (not just "is hallucinating")
        hallucination_indicators = [
            "sees ", "imagines ", "thinks ", "believes ", 
            "hallucinates ", "visualizes ", "perceives ",
            "screams about ", "yells about ", "mutters about ",
            "swats at ", "runs from ", "hides from ",
            "stares at ", "points at ", "laughs at ",
            "confused by ", "startled by ", "terrified of ",
            "dancing with ", "talking to ", "arguing with ",
            "fighting with ", "fleeing from ", "cowering from "
        ]
        if any(indicator in message_lower for indicator in hallucination_indicators):
            return "npc_hallucination_detail"
            
        # Standard message types
        if "attack" in message_lower or "damage" in message_lower or "health" in message_lower:
            return "npc_attack"
        elif "hallucinating" in message_lower or "hallucination" in message_lower or "seeing things" in message_lower:
            return "npc_hallucination_detail"  # Upgraded from npc_hallucination to ensure it's shown
        elif "affected by hallucinations" in message_lower:
            return "npc_hallucination"
        elif "friendly" in message_lower or "friendliness" in message_lower or "smiles at you" in message_lower:
            return "npc_friendly"
        elif "gives you" in message_lower or "gift" in message_lower:
            return "npc_gift"
        elif "falls" in message_lower or "falling" in message_lower or "struck by" in message_lower:
            return "npc_falling_object"
        # Treat unnoticed/distracted messages as idle behaviors
        elif ("doesn't notice" in message_lower or "unaware" in message_lower or 
              "looking away" in message_lower or "hasn't spotted" in message_lower or
              "looking the other way" in message_lower or "distracted" in message_lower or
              "fails to notice" in message_lower or "oblivious" in message_lower or
              "walks past your hiding spot" in message_lower):
            return "npc_idle"  # Categorize as idle instead of unnoticed
        elif "talk" in message_lower or "says" in message_lower or "speaking" in message_lower:
            return "npc_talk"
        elif "interact" in message_lower or "using" in message_lower or "picks up" in message_lower:
            return "npc_interact"
        elif "standing" in message_lower or "idle" in message_lower or "waiting" in message_lower:
            return "npc_idle"
        
        return None
    
    def _categorize_message(self, message, message_type):
        """Determine the appropriate category and priority for the main message system."""
        # Default values
        category = MessageCategory.NPC_MINOR
        priority = MessagePriority.MEDIUM
        
        # Adjust based on message type
        if message_type == "npc_attack":
            category = MessageCategory.COMBAT
            priority = MessagePriority.HIGH
        elif message_type == "hazard_trigger":
            category = MessageCategory.NPC_HAZARD
            priority = MessagePriority.HIGH
        elif message_type == "npc_gardening":
            category = MessageCategory.NPC_INTERACTION
            priority = MessagePriority.HIGH
        elif message_type == "npc_hallucination_detail":
            category = MessageCategory.NPC_HAZARD
            priority = MessagePriority.HIGH  # High priority for detailed hallucinations
        elif message_type == "npc_hallucination":
            category = MessageCategory.NPC_HAZARD
            priority = MessagePriority.HIGH  # Increased to HIGH to show hallucination messages
        elif message_type == "npc_friendly":
            category = MessageCategory.NPC_TALK
            priority = MessagePriority.HIGH  # Increased to HIGH to show friendly messages
        elif message_type == "npc_gift":
            category = MessageCategory.NPC_GIFT
            priority = MessagePriority.HIGH
        elif message_type == "npc_falling_object":
            category = MessageCategory.NPC_HAZARD
            priority = MessagePriority.HIGH
        elif message_type == "npc_resist_hazard":
            category = MessageCategory.NPC_HAZARD
            priority = MessagePriority.LOW  # Low priority for resist messages
        elif message_type == "player_teleport":
            category = MessageCategory.PLAYER_ACTION
            priority = MessagePriority.MEDIUM
        elif message_type == "npc_unnoticed":
            category = MessageCategory.TRIVIAL
            priority = MessagePriority.MINIMAL
        elif message_type == "npc_talk":
            category = MessageCategory.NPC_TALK
            priority = MessagePriority.LOW  # Reduced from MEDIUM
        elif message_type == "npc_interact":
            category = MessageCategory.NPC_INTERACTION
            priority = MessagePriority.MEDIUM
        elif message_type == "npc_idle":
            category = MessageCategory.NPC_IDLE
            priority = MessagePriority.MINIMAL  # Reduced from LOW
        
        return category, priority
    
    def _should_create_notification(self, message_type, priority):
        """Determine if a message should create a notification."""
        # First, check for message types that should NEVER create notifications
        if message_type in ["npc_talk", "npc_resist_hazard"]:
            # NPCs talking to each other, NPCs resisting hazards
            return False
            
        # Check for teleport messages
        if message_type and "teleport" in str(message_type).lower():
            return False
            
        # Only specific message types should create notifications
        allowed_notification_types = [
            "npc_gift",                # NPC gives player an item
            "npc_gardening",           # NPC performs gardening action
            "hazard_trigger",          # NPC triggers a hazard
            "npc_hallucination_detail", # Detailed hallucination descriptions (interesting content)
            "npc_hallucination",       # General hallucination effects
            "npc_friendly",            # Friendly behavior from NPCs
            "npc_falling_object"       # Falling object incidents
        ]
        
        if message_type in allowed_notification_types:
            return True
            
        # All other message types should not create notifications
        return False
    
    def _map_to_notification_category(self, message_category):
        """Map message category to notification category."""
        category_mapping = {
            MessageCategory.COMBAT: "combat",
            MessageCategory.NPC_HAZARD: "hazard",
            MessageCategory.NPC_GIFT: "item",
            MessageCategory.NPC_TALK: "npc",
            MessageCategory.NPC_INTERACTION: "npc",
            MessageCategory.NPC_IDLE: "npc",
            MessageCategory.NPC_MINOR: "npc",
            MessageCategory.PLAYER_ACTION: "player",
            MessageCategory.NOTIFICATION: "general",
            MessageCategory.TRIVIAL: "general"
        }
        return category_mapping.get(message_category, "general")
    
    def _map_priority_to_importance(self, priority):
        """Map message priority to notification importance (1-5 scale)."""
        priority_mapping = {
            MessagePriority.HIGH: 5,
            MessagePriority.MEDIUM: 3,
            MessagePriority.LOW: 2,
            MessagePriority.MINIMAL: 1
        }
        return priority_mapping.get(priority, 3)
    
    def get_npc_summary(self):
        """Get a summary of NPC actions from the NPC message manager."""
        # Initialize active gangs set
        self.active_gangs = set()
        
        # Process any pending actions first to ensure all actions are tracked
        if hasattr(self.npc_message_manager, 'pending_actions') and self.npc_message_manager.pending_actions:
            if hasattr(self.npc_message_manager, '_process_pending_actions'):
                self.npc_message_manager._process_pending_actions()
        
        # Generate our own enhanced summaries for hazard effects
        hazard_summary = self._generate_hazard_summary()
        
        # Generate enhanced summaries for NPC actions
        action_summary = self._generate_action_summary()
        
        # Get the standard summary from the NPC message manager as a fallback
        standard_summary = self.npc_message_manager.get_summary(clear=True)
        
        # Combine all summaries into a single output
        all_summaries = []
        
        # Add a gang-specific introduction if we have active gangs
        if hasattr(self, 'active_gangs') and self.active_gangs:
            # Create a gang-specific introduction
            if len(self.active_gangs) == 1:
                gang_name = next(iter(self.active_gangs))
                gang_intro = f"The {gang_name} gang is active in the area:"
                all_summaries.append(gang_intro)
            else:
                # Multiple gangs
                gang_names = ", ".join(self.active_gangs)
                gang_intro = f"Multiple gangs are active: {gang_names}"
                all_summaries.append(gang_intro)
        
        if hazard_summary:
            all_summaries.append(hazard_summary)
        
        if action_summary:
            all_summaries.append(action_summary)
            
        if not all_summaries and standard_summary:
            all_summaries.append(standard_summary)
            
        # Return all summaries as a single string with proper spacing
        if all_summaries:
            return "\n\n".join(all_summaries)
        
        return None
    
    def _generate_hazard_summary(self):
        """Generate an enhanced summary of hazard effects with improved readability."""
        summary_parts = []
        
        # First, include any direct hazard messages (specific hallucinations, etc.)
        # These are the most interesting and should be shown directly
        if hasattr(self, 'direct_hazard_messages') and self.direct_hazard_messages:
            # Add up to 3 direct hazard messages
            for i, message in enumerate(self.direct_hazard_messages):
                if i >= 3:  # Limit to 3 messages to avoid spam
                    break
                
                # Clean up the message to remove redundant gang references
                cleaned_message = message
                if "The Bloodhounds member" in cleaned_message:
                    cleaned_message = cleaned_message.replace("The Bloodhounds member ", "")
                elif "The Bloodhounds members" in cleaned_message:
                    cleaned_message = cleaned_message.replace("The Bloodhounds members ", "")
                
                summary_parts.append(cleaned_message)
        
        # If we don't have any direct messages or we have room for more, add summaries
        if not self.hazard_effects:
            if summary_parts:
                return "\n".join(summary_parts)
            return None
        
        # Add a hazard effects subheader if we have any
        if any(effect_type in self.hazard_effects for effect_type in 
              ["hazard_trigger", "npc_gift", "npc_falling_object", "npc_hallucination", 
               "npc_friendly", "npc_resist_hazard"]):
            summary_parts.append("Hazard effects:")
            
        # Process hazard trigger effects - these are important
        if "hazard_trigger" in self.hazard_effects and len(summary_parts) < 6:
            trigger_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["hazard_trigger"],
                "triggered hazards",
                "triggered a hazard"
            )
            if trigger_summary:
                summary_parts.append(trigger_summary)
        
        # Process gift-giving effects - these are important for gameplay
        if "npc_gift" in self.hazard_effects and len(summary_parts) < 6:
            gift_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["npc_gift"],
                "gave you items",
                "gave you an item"
            )
            if gift_summary:
                summary_parts.append(gift_summary)
        
        # Process falling object effects - these are important for gameplay
        if "npc_falling_object" in self.hazard_effects and len(summary_parts) < 6:
            falling_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["npc_falling_object"],
                "were struck by falling objects",
                "was struck by a falling object"
            )
            if falling_summary:
                summary_parts.append(falling_summary)
        
        # Only add generic summaries if we don't have enough specific messages
        if len(summary_parts) < 4:
            # Process hallucination effects - less important
            if "npc_hallucination" in self.hazard_effects and len(summary_parts) < 6:
                hallucination_summary = self._summarize_npcs_by_effect(
                    self.hazard_effects["npc_hallucination"],
                    "are hallucinating",
                    "is hallucinating"
                )
                if hallucination_summary:
                    summary_parts.append(hallucination_summary)
            
            # Process friendly effects - less important
            if "npc_friendly" in self.hazard_effects and len(summary_parts) < 6:
                friendly_summary = self._summarize_npcs_by_effect(
                    self.hazard_effects["npc_friendly"],
                    "are acting unusually friendly",
                    "is acting unusually friendly"
                )
                if friendly_summary:
                    summary_parts.append(friendly_summary)
        
        # We don't need resist messages if we have specific messages
        if len(summary_parts) < 3:
            # Process resist hazard effects - least important
            if "npc_resist_hazard" in self.hazard_effects and len(summary_parts) < 6:
                resist_summary = self._summarize_npcs_by_effect(
                    self.hazard_effects["npc_resist_hazard"],
                    "resisted hazard effects",
                    "resisted a hazard effect"
                )
                if resist_summary:
                    summary_parts.append(resist_summary)
        
        if summary_parts:
            return "\n".join(summary_parts)
        return None
    
    def _generate_action_summary(self):
        """Generate an enhanced summary of NPC actions, grouping similar actions together."""
        if not self.npc_actions and not hasattr(self, 'gardening_actions'):
            return None
            
        summary_parts = []
        
        # Group all NPC actions by type for better summarization
        action_types = {
            "npc_attack": "combat actions",
            "npc_gardening": "gardening actions",
            "npc_interact": "interaction actions",
            "npc_talk": "conversation actions",
            "npc_idle": "idle actions",
            "npc_gift": "gift-giving actions",
            "npc_falling_object": "falling object incidents",
            "hazard_trigger": "hazard triggers",
            "npc_hallucination": "hallucination effects",
            "npc_hallucination_detail": "hallucination details",
            "npc_friendly": "friendly behaviors",
            "npc_resist_hazard": "hazard resistance",
            "player_teleport": "teleportation events"
        }
        
        # Collect all NPCs by action type
        npcs_by_action = collections.defaultdict(list)
        
        # First, process all tracked NPC actions
        for action_type, actions in self.npc_actions.items():
            for npc_name, gang_name, message in actions:
                if npc_name and gang_name:
                    npcs_by_action[action_type].append((npc_name, gang_name, message))
        
        # Add gardening actions if they exist
        if hasattr(self, 'gardening_actions') and self.gardening_actions:
            for npc_name, gang_name, message in self.gardening_actions:
                if npc_name and gang_name:
                    npcs_by_action["npc_gardening"].append((npc_name, gang_name, message))
        
        # Process attack actions first - these are important enough to list individually
        if "npc_attack" in npcs_by_action and npcs_by_action["npc_attack"]:
            summary_parts.append("Combat actions:")
            for _, _, message in npcs_by_action["npc_attack"]:
                # Clean up the message to remove redundant gang references
                cleaned_message = message
                if "The Bloodhounds member" in cleaned_message:
                    cleaned_message = cleaned_message.replace("The Bloodhounds member ", "")
                elif "The Bloodhounds members" in cleaned_message:
                    cleaned_message = cleaned_message.replace("The Bloodhounds members ", "")
                
                summary_parts.append(cleaned_message)
        
        # Group action types into categories for better organization
        action_categories = {
            "Interactions": ["npc_gift", "npc_interact"],
            "Environment": ["npc_gardening", "hazard_trigger"],
            "Social": ["npc_talk", "npc_friendly"],
            "Idle": ["npc_idle"]
        }
        
        # Process actions by category
        for category, action_list in action_categories.items():
            category_actions = []
            
            for action_type in action_list:
                if action_type in npcs_by_action and len(npcs_by_action[action_type]) > 0:
                    # Create a more descriptive action phrase based on the specific actions
                    action_phrase = self._get_specific_action_phrase(action_type, npcs_by_action[action_type])
                    
                    # Generate summary for this action type
                    action_summary = self._summarize_npcs_by_effect(
                        npcs_by_action[action_type],
                        f"are {action_phrase}",
                        f"is {action_phrase}"
                    )
                    
                    if action_summary:
                        category_actions.append(action_summary)
            
            # Add category header and actions if we have any
            if category_actions:
                summary_parts.append(f"{category}:")
                summary_parts.extend(category_actions)
        
        if summary_parts:
            return "\n".join(summary_parts)
        return None
        
    def _get_specific_action_phrase(self, action_type, actions):
        """Generate a more specific action phrase based on the actual actions being performed."""
        # Default phrases
        default_phrases = {
            "npc_gift": "giving away items",
            "npc_gardening": "tending to plants",
            "hazard_trigger": "triggering hazards",
            "npc_hallucination_detail": "experiencing hallucinations",
            "npc_hallucination": "hallucinating",
            "npc_falling_object": "being hit by falling objects",
            "npc_interact": "interacting with objects",
            "npc_talk": "talking to each other",
            "npc_idle": "standing around",
            "npc_friendly": "acting unusually friendly",
            "npc_resist_hazard": "resisting hazard effects"
        }
        
        # For gardening actions, try to be more specific
        if action_type == "npc_gardening":
            # Check for specific gardening actions
            planting = 0
            watering = 0
            harvesting = 0
            
            for _, _, message in actions:
                if "plant" in message.lower():
                    planting += 1
                elif "water" in message.lower():
                    watering += 1
                elif "harvest" in message.lower():
                    harvesting += 1
            
            # Determine the most common gardening action
            if planting > watering and planting > harvesting:
                return "planting seeds"
            elif watering > planting and watering > harvesting:
                return "watering plants"
            elif harvesting > planting and harvesting > watering:
                return "harvesting plants"
            else:
                return "gardening"
                
        # For interaction actions, try to extract what they're interacting with
        if action_type == "npc_interact":
            # Look for common objects in the messages
            objects = []
            for _, _, message in actions:
                if "with" in message:
                    obj = message.split("with")[-1].strip().rstrip('.!?')
                    if obj and len(obj) < 30:  # Reasonable length for an object name
                        objects.append(obj)
            
            # If we found objects, use them in the phrase
            if objects:
                # Get the most common object
                if len(objects) == 1:
                    return f"interacting with {objects[0]}"
                else:
                    return f"interacting with various objects"
        
        # For talking actions, be more specific if possible
        if action_type == "npc_talk":
            return "having conversations"
            
        # Default to the predefined phrase
        return default_phrases.get(action_type, "doing something")
    
    def _summarize_npcs_by_effect(self, npc_effect_list, plural_action, singular_action):
        """Create a summary in the format '[name], [name], and [X] others are [action]'."""
        if not npc_effect_list:
            return None
            
        # Group NPCs by gang
        npcs_by_gang = collections.defaultdict(list)
        for npc_name, gang_name, _ in npc_effect_list:
            if npc_name and gang_name:
                npcs_by_gang[gang_name].append(npc_name)
        
        summaries = []
        # Track which gangs are mentioned for the summary header
        self.active_gangs = set()
        
        for gang_name, npc_names in npcs_by_gang.items():
            # Add this gang to the active gangs set
            self.active_gangs.add(gang_name)
            
            # Remove duplicates while preserving order
            unique_npcs = []
            for npc in npc_names:
                if npc not in unique_npcs:
                    unique_npcs.append(npc)
            
            if not unique_npcs:
                continue
                
            # Format the list of NPCs with proper grammar - without repeating gang name
            if len(unique_npcs) == 1:
                # Single NPC
                summaries.append(f"{unique_npcs[0]} {singular_action}.")
            elif len(unique_npcs) <= 3:
                # 2-3 NPCs - list all names
                npc_list = ", ".join(unique_npcs)
                summaries.append(f"{npc_list} {plural_action}.")
            else:
                # More than 3 NPCs - list some and summarize the rest
                sample_npcs = unique_npcs[:3]  # Take first 3 (increased from 2)
                npc_list = ", ".join(sample_npcs)
                others_count = len(unique_npcs) - 3
                summaries.append(f"{npc_list}, and {others_count} others {plural_action}.")
        
        if summaries:
            return "\n".join(summaries)
        return None
    
    def process_player_message(self, message, priority=MessagePriority.MEDIUM):
        """Process a player-generated message."""
        # Determine message type for filtering
        message_type = self._determine_message_type(message)
        
        # Player messages always go directly to the main message system
        result = self.message_manager.add_message(
            text=message,
            category=MessageCategory.PLAYER_ACTION,
            priority=priority
        )
        
        # Check if this is a teleport message - never create notifications for teleports
        if "teleport" in message.lower():
            return result
            
        # Also add to notification system if appropriate - use our filter
        if self.notification_manager and self._should_create_notification(message_type, priority):
            self.notification_manager.add_notification(
                message,
                category="player",
                importance=self._map_priority_to_importance(priority)
            )
            
        return result
        
    def process_system_message(self, message, category=None, priority=MessagePriority.MEDIUM):
        """Process a system-generated message."""
        # Determine message type for filtering
        message_type = self._determine_message_type(message)
        
        # System messages go directly to the main message system
        result = self.message_manager.add_message(
            text=message,
            category=category or MessageCategory.NOTIFICATION,
            priority=priority
        )
        
        # Check for specific messages that should never create notifications
        if any(keyword in message.lower() for keyword in [
            "teleport", 
            "affected by", 
            "resist", 
            "hallucinating", 
            "talking to"
        ]):
            return result
            
        # Also add to notification system if appropriate - use our filter
        if self.notification_manager and self._should_create_notification(message_type, priority):
            notification_category = self._map_to_notification_category(category) if category else "general"
            self.notification_manager.add_notification(
                message,
                category=notification_category,
                importance=self._map_priority_to_importance(priority)
            )
            
        return result
