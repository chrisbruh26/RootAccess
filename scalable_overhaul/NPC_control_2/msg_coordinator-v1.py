"""
Message Coordinator for Root Access

This module coordinates between the main message system, the NPC message system,
and the notification system to ensure consistent, non-redundant messaging throughout the game.
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
            "npc_friendly": 0,
            "npc_gift": 0,
            "npc_unnoticed": 0,
            "npc_falling_object": 0,
            "hazard_trigger": 0,
            "npc_gardening": 0,
            "npc_resist_hazard": 0,
            "player_teleport": 0
        }
        
        # Maximum messages per type per turn - much more restrictive
        self.max_messages_per_type = {
            "npc_idle": 0,           # No idle messages shown directly (only in summary)
            "npc_talk": 1,           # Only 1 talk message per turn
            "npc_interact": 1,       # Only 1 interaction message per turn
            "npc_attack": 2,         # At most 2 attack messages per turn
            "npc_hallucination": 1,  # At most 1 hallucination message per turn
            "npc_friendly": 1,       # At most 1 friendly message per turn
            "npc_gift": 2,           # Allow up to 2 gift messages per turn (increased from 1)
            "npc_unnoticed": 0,      # No "unnoticed" messages shown directly (only in summary)
            "npc_falling_object": 1, # At most 1 falling object message per turn
            "hazard_trigger": 2,     # Allow up to 2 hazard trigger messages per turn
            "npc_gardening": 2,      # Allow up to 2 gardening messages per turn
            "npc_resist_hazard": 0,  # No resist messages shown directly (only in summary)
            "player_teleport": 1     # At most 1 teleport message per turn
        }
        
        # Track unique messages to prevent exact duplicates
        self.unique_messages = set()
        
        # Global message limit per turn (regardless of type)
        self.max_messages_per_turn = 5
        self.current_turn_message_count = 0
        
        # Track hazard effects for summarization
        self.hazard_effects = collections.defaultdict(list)
        
        # Track NPC actions by type for better summarization
        self.npc_actions = collections.defaultdict(list)
        
        # Track gardening actions separately
        self.gardening_actions = []
    
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
        
        # Notify all message systems of the new turn
        if hasattr(self.message_manager, 'new_turn'):
            self.message_manager.new_turn()
        
        if hasattr(self.npc_message_manager, 'new_turn'):
            self.npc_message_manager.new_turn()
            
        if self.notification_manager and hasattr(self.notification_manager, 'new_turn'):
            notification_reminder = self.notification_manager.new_turn()
            if notification_reminder:
                self.process_system_message(notification_reminder, category=MessageCategory.NOTIFICATION)
    
    def process_npc_message(self, message, npc=None):
        """Process an NPC message through both systems with deduplication."""
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
        
        # Prioritize attack messages - process them first
        is_attack = message_type == "npc_attack"
        if not is_attack and "attack" in message.lower():
            message_type = "npc_attack"
            is_attack = True
        
        # Check if we've hit the global message limit for this turn
        if self.current_turn_message_count >= self.max_messages_per_turn:
            # Always allow critical messages (attacks) even if we hit the limit
            if message_type != "npc_attack":
                # Track the message for summarization even if we don't display it
                self._track_for_summarization(message, message_type, npc)
                return None
        
        # Check if we've hit the limit for this type of message
        if message_type and self.message_counts.get(message_type, 0) >= self.max_messages_per_type.get(message_type, 1):
            # Track the message for summarization even if we don't display it
            self._track_for_summarization(message, message_type, npc)
            return None
        
        # Increment count for this message type
        if message_type:
            self.message_counts[message_type] = self.message_counts.get(message_type, 0) + 1
        
        # Track the message for summarization
        self._track_for_summarization(message, message_type, npc)
        
        # First, process through NPC message manager for grouping and summarization
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
        
        # Track hazard effects
        if message_type in ["npc_hallucination", "npc_friendly", "npc_gift", "npc_falling_object", "hazard_trigger", "npc_resist_hazard"]:
            if npc_name and gang_name:
                self.hazard_effects[message_type].append((npc_name, gang_name, message))
        
        # Track gardening actions separately
        if message_type == "npc_gardening" and npc_name:
            if not hasattr(self, 'gardening_actions'):
                self.gardening_actions = []
            self.gardening_actions.append((npc_name, gang_name, message))
        
        # Track NPC actions by type
        if npc_name:
            self.npc_actions[message_type].append((npc_name, gang_name, message))
    
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
            
        # Standard message types
        if "attack" in message_lower or "damage" in message_lower or "health" in message_lower:
            return "npc_attack"
        elif "hallucinating" in message_lower or "hallucination" in message_lower:
            return "npc_hallucination"
        elif "friendly" in message_lower or "friendliness" in message_lower:
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
        elif message_type == "npc_hallucination":
            category = MessageCategory.NPC_HAZARD
            priority = MessagePriority.MEDIUM  # Reduced from HIGH
        elif message_type == "npc_friendly":
            category = MessageCategory.NPC_TALK
            priority = MessagePriority.LOW  # Reduced from MEDIUM
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
        if message_type in ["npc_talk", "npc_hallucination", "npc_friendly"]:
            # NPCs talking to each other, NPCs affected by hallucinations, NPCs being friendly
            return False
            
        # Check for teleport messages
        if message_type and "teleport" in str(message_type).lower():
            return False
            
        # Only specific message types should create notifications
        allowed_notification_types = [
            "npc_gift",           # NPC gives player an item
            "npc_gardening",      # NPC performs gardening action
            "hazard_trigger"      # NPC triggers a hazard
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
        # Get the standard summary from the NPC message manager
        standard_summary = self.npc_message_manager.get_summary(clear=True)
        
        # Generate our own enhanced summaries for hazard effects
        hazard_summary = self._generate_hazard_summary()
        
        # Generate enhanced summaries for NPC actions
        action_summary = self._generate_action_summary()
        
        # Combine summaries, prioritizing our enhanced ones
        if hazard_summary and action_summary:
            return f"{hazard_summary}\n\n{action_summary}"
        elif hazard_summary:
            return hazard_summary
        elif action_summary:
            return action_summary
        else:
            return standard_summary
    
    def _generate_hazard_summary(self):
        """Generate an enhanced summary of hazard effects."""
        if not self.hazard_effects:
            return None
            
        summary_parts = []
        
        # Process hazard trigger effects - these are important
        if "hazard_trigger" in self.hazard_effects:
            trigger_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["hazard_trigger"],
                "triggered hazards",
                "triggered a hazard"
            )
            if trigger_summary:
                summary_parts.append(trigger_summary)
        
        # Process gift-giving effects - these are important for gameplay
        if "npc_gift" in self.hazard_effects:
            gift_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["npc_gift"],
                "gave you items",
                "gave you an item"
            )
            if gift_summary:
                summary_parts.append(gift_summary)
        
        # Process falling object effects - these are important for gameplay
        if "npc_falling_object" in self.hazard_effects:
            falling_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["npc_falling_object"],
                "were struck by falling objects",
                "was struck by a falling object"
            )
            if falling_summary:
                summary_parts.append(falling_summary)
        
        # Process hallucination effects - less important
        if "npc_hallucination" in self.hazard_effects and len(summary_parts) < 3:
            hallucination_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["npc_hallucination"],
                "are hallucinating",
                "is hallucinating"
            )
            if hallucination_summary:
                summary_parts.append(hallucination_summary)
        
        # Process friendly effects - less important
        if "npc_friendly" in self.hazard_effects and len(summary_parts) < 3:
            friendly_summary = self._summarize_npcs_by_effect(
                self.hazard_effects["npc_friendly"],
                "are acting unusually friendly",
                "is acting unusually friendly"
            )
            if friendly_summary:
                summary_parts.append(friendly_summary)
        
        # Process resist hazard effects - least important
        if "npc_resist_hazard" in self.hazard_effects and len(summary_parts) < 3:
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
        """Generate an enhanced summary of NPC actions."""
        if not self.npc_actions and not hasattr(self, 'gardening_actions'):
            return None
            
        summary_parts = []
        
        # Process attack actions - these are important enough to list individually
        if "npc_attack" in self.npc_actions:
            for _, _, message in self.npc_actions["npc_attack"]:
                summary_parts.append(message)
        
        # Process gardening actions - high priority
        if hasattr(self, 'gardening_actions') and self.gardening_actions:
            gardening_summary = self._summarize_npcs_by_effect(
                self.gardening_actions,
                "are tending to plants",
                "is tending to plants"
            )
            if gardening_summary:
                summary_parts.append(gardening_summary)
        
        # Process interaction actions
        if "npc_interact" in self.npc_actions:
            interact_summary = self._summarize_npcs_by_effect(
                self.npc_actions["npc_interact"],
                "are interacting with objects",
                "is interacting with objects"
            )
            if interact_summary:
                summary_parts.append(interact_summary)
        
        # Process talk actions - lower priority
        if "npc_talk" in self.npc_actions and len(summary_parts) < 3:
            talk_summary = self._summarize_npcs_by_effect(
                self.npc_actions["npc_talk"],
                "are talking to each other",
                "is talking"
            )
            if talk_summary:
                summary_parts.append(talk_summary)
        
        # Process idle actions - lowest priority
        if "npc_idle" in self.npc_actions and len(summary_parts) < 3:  # Limit to avoid too many messages
            idle_summary = self._summarize_npcs_by_effect(
                self.npc_actions["npc_idle"],
                "are standing around",
                "is standing around"
            )
            if idle_summary:
                summary_parts.append(idle_summary)
        
        if summary_parts:
            return "\n".join(summary_parts)
        return None
    
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
        
        for gang_name, npc_names in npcs_by_gang.items():
            # Remove duplicates while preserving order
            unique_npcs = []
            for npc in npc_names:
                if npc not in unique_npcs:
                    unique_npcs.append(npc)
            
            if not unique_npcs:
                continue
                
            # Format the list of NPCs with proper grammar
            if len(unique_npcs) == 1:
                # Single NPC
                summaries.append(f"The {gang_name} member {unique_npcs[0]} {singular_action}.")
            elif len(unique_npcs) <= 3:
                # 2-3 NPCs - list all names
                npc_list = ", ".join(unique_npcs)
                summaries.append(f"The {gang_name} members {npc_list} {plural_action}.")
            else:
                # More than 3 NPCs - list some and summarize the rest
                sample_npcs = unique_npcs[:2]  # Take first 2
                npc_list = ", ".join(sample_npcs)
                others_count = len(unique_npcs) - 2
                summaries.append(f"The {gang_name} members {npc_list}, and {others_count} others {plural_action}.")
        
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
