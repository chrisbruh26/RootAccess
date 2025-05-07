from items import Item

# ----------------------------- #
# HYBRID ITEM CLASS              #
# ----------------------------- #

class HybridItem(Item):
    """
    A special item that combines the functionality of two other items.
    This class uses composition to maintain the functionality of both parent items.
    """
    def __init__(self, name, description, value, parent1, parent2):
        super().__init__(name, description, value)
        self.parent1 = parent1
        self.parent2 = parent2
        self.parent_types = []
        
        # Store the types of the parent items for functionality checks
        if hasattr(parent1, '__class__'):
            self.parent_types.append(parent1.__class__.__name__)
        if hasattr(parent2, '__class__'):
            self.parent_types.append(parent2.__class__.__name__)
        
        # Copy relevant attributes from parent items
        self._copy_attributes(parent1)
        self._copy_attributes(parent2)
        
        # Add hybrid-specific attributes
        self.is_hybrid = True
        
        # Add class type checks for better compatibility with isinstance()
        # This allows the hybrid item to be recognized as its parent types
        self._parent_classes = []
        if hasattr(parent1, '__class__'):
            self._parent_classes.append(parent1.__class__)
        if hasattr(parent2, '__class__'):
            self._parent_classes.append(parent2.__class__)
        
    def _copy_attributes(self, parent):
        """Copy relevant attributes from a parent item."""
        # List of attributes to copy if they exist
        attributes_to_copy = [
            'damage', 'health_restore', 'effect', 'is_electronic',
            'capacity', 'current_water', 'crop_type', 'growth_time',
            'is_deployed', 'battery', 'max_battery'
        ]
        
        for attr in attributes_to_copy:
            if hasattr(parent, attr) and not hasattr(self, attr):
                setattr(self, attr, getattr(parent, attr))
    
    # We can't override __instancecheck__ directly in the instance
    # Instead, we'll use a custom method that can be used to check compatibility
    def is_instance_of(self, class_type):
        """Check if this hybrid item is compatible with the given class type."""
        # Check if this is directly an instance of the class
        if isinstance(self, class_type):
            return True
        
        # Check if either parent is an instance of the class
        for parent_class in self._parent_classes:
            if issubclass(parent_class, class_type):
                return True
        
        return False
    
    def __str__(self):
        """Custom string representation that shows hybrid nature."""
        base_str = f"{self.name}"
        
        # Add damage if it's a weapon
        if hasattr(self, 'damage'):
            base_str += f" (Damage: {self.damage})"
        
        # Add health restore if it's a consumable
        if hasattr(self, 'health_restore'):
            base_str += f" (Restores: {self.health_restore} HP)"
        
        # Add effect if it has one
        if hasattr(self, 'effect'):
            base_str += f" ({self.effect.name} effect)"
        
        # Add water info if it's a watering can
        if hasattr(self, 'current_water') and hasattr(self, 'capacity'):
            base_str += f" ({self.current_water}/{self.capacity} water)"
        
        # Add seed info if it's a seed
        if hasattr(self, 'crop_type'):
            base_str += f" ({self.crop_type})"
        
        # Add battery info if it's electronic
        if hasattr(self, 'battery') and hasattr(self, 'max_battery'):
            base_str += f" (Battery: {self.battery}%)"
        
        return base_str
    
    def use(self, player, game):
        """
        Use the hybrid item, delegating to the appropriate parent item's use method.
        This method tries to call the use method of both parent items and combines the results.
        """
        # Check if we need to handle special cases based on the item type
        from gardening import Seed
        
        # If this is a seed hybrid, delegate to the seed planting functionality
        if hasattr(self, 'crop_type') and hasattr(self, 'growth_time'):
            # Check if there's soil in the current location
            from gardening import SoilPlot, Plant
            objects = player.get_current_location_objects()
            soil = next((obj for obj in objects if isinstance(obj, SoilPlot)), None)
            
            if soil:
                # Create a plant from this seed
                plant = Plant(
                    f"{self.crop_type} plant", 
                    f"A young {self.crop_type} plant.", 
                    self.crop_type, 
                    self.value * 2
                )
                
                result = soil.add_plant(plant)
                if result[0]:
                    # Don't remove the hybrid item since it has multiple uses
                    pass
                return result
        
        # For other cases, try to use both parent functionalities
        messages = []
        messages.append(f"You use the {self.name}.")
        success_count = 0
        
        # Try to use parent1's functionality
        if hasattr(self.parent1, 'use'):
            try:
                result = self.parent1.use(player, game)
                if isinstance(result, tuple) and len(result) >= 2:
                    # Handle tuple return format (success, message)
                    success, message = result[0], result[1]
                    if success:
                        success_count += 1
                    # Replace references to the parent item with the hybrid item
                    message = message.replace(self.parent1.name, self.name)
                    messages.append(message)
                elif isinstance(result, str):
                    # Handle string return format
                    result = result.replace(self.parent1.name, self.name)
                    messages.append(result)
                    success_count += 1
            except Exception as e:
                messages.append(f"Error using {self.parent1.name} functionality: {str(e)}")
        
        # Try to use parent2's functionality
        if hasattr(self.parent2, 'use'):
            try:
                result = self.parent2.use(player, game)
                if isinstance(result, tuple) and len(result) >= 2:
                    # Handle tuple return format (success, message)
                    success, message = result[0], result[1]
                    if success:
                        success_count += 1
                    # Replace references to the parent item with the hybrid item
                    message = message.replace(self.parent2.name, self.name)
                    messages.append(message)
                elif isinstance(result, str):
                    # Handle string return format
                    result = result.replace(self.parent2.name, self.name)
                    messages.append(result)
                    success_count += 1
            except Exception as e:
                messages.append(f"Error using {self.parent2.name} functionality: {str(e)}")
        
        # Return success if at least one parent functionality worked
        return (success_count > 0), "\n".join(messages)
    
    # Instead of duplicating code, we'll use delegation for these methods
    def consume(self, player, game):
        """Consume the hybrid item to restore health."""
        if hasattr(self, 'health_restore'):
            # Create a temporary copy of the health_restore value
            health_restore = self.health_restore
            
            # Delegate to parent if it has a consume method
            if hasattr(self.parent1, 'consume'):
                result = self.parent1.consume(player, game)
                if isinstance(result, tuple) and result[0]:
                    # Replace parent name with hybrid name in the message
                    message = result[1].replace(self.parent1.name, self.name)
                    return True, message
            elif hasattr(self.parent2, 'consume'):
                result = self.parent2.consume(player, game)
                if isinstance(result, tuple) and result[0]:
                    # Replace parent name with hybrid name in the message
                    message = result[1].replace(self.parent2.name, self.name)
                    return True, message
            
            # If no parent has a consume method, implement basic consumption
            player.health = min(player.max_health, player.health + health_restore)
            # Don't remove the hybrid item since it has multiple uses
            return True, f"You consume the {self.name} and restore {health_restore} health."
        return False, f"The {self.name} cannot be consumed."
    
    def apply_effect(self, player, game):
        """Apply the effect of the hybrid item."""
        if hasattr(self, 'effect'):
            # Delegate to parent if it has an apply_effect method
            if hasattr(self.parent1, 'apply_effect'):
                result = self.parent1.apply_effect(player, game)
                if isinstance(result, tuple) and result[0]:
                    # Replace parent name with hybrid name in the message
                    message = result[1].replace(self.parent1.name, self.name)
                    return True, message
            elif hasattr(self.parent2, 'apply_effect'):
                result = self.parent2.apply_effect(player, game)
                if isinstance(result, tuple) and result[0]:
                    # Replace parent name with hybrid name in the message
                    message = result[1].replace(self.parent2.name, self.name)
                    return True, message
            
            # If no parent has an apply_effect method, implement basic effect application
            messages = []
            affected_npcs = []
            
            messages.append(f"You use the {self.name} to apply its effect!")
            
            # Apply effect to NPCs in the current area
            if player.current_area and player.current_area.npcs:
                for npc in player.current_area.npcs:
                    # Skip dead NPCs
                    if hasattr(npc, 'is_alive') and not npc.is_alive:
                        continue
                        
                    # Apply the effect to the NPC
                    if hasattr(npc, 'active_effects'):
                        # Create a new instance of the effect for this NPC
                        effect_copy = type(self.effect)()
                        npc.active_effects.append(effect_copy)
                        affected_npcs.append(npc)
            
                # Add the effect messages to the NPC coordinator
                if game and game.npc_coordinator:
                    game.npc_coordinator.add_effect_messages(affected_npcs, self.effect)
                
                # Add more detailed message about affected NPCs
                if affected_npcs:
                    if len(affected_npcs) == 1:
                        messages.append(f"{affected_npcs[0].name} is affected by the {self.effect.name} effect!")
                    elif len(affected_npcs) <= 3:
                        npc_names = ", ".join(npc.name for npc in affected_npcs)
                        messages.append(f"{npc_names} are affected by the {self.effect.name} effect!")
                    else:
                        messages.append(f"Several NPCs are affected by the {self.effect.name} effect!")
            
            return True, "\n".join(messages)
        return False, f"The {self.name} does not have an effect to apply."
    
    def attack_npc(self, player, target_npc):
        """Attack a specific NPC with this hybrid item."""
        if hasattr(self, 'damage'):
            # Delegate to parent if it has an attack_npc method
            if hasattr(self.parent1, 'attack_npc'):
                result = self.parent1.attack_npc(player, target_npc)
                if isinstance(result, tuple) and result[0]:
                    # Replace parent name with hybrid name in the message
                    message = result[1].replace(self.parent1.name, self.name)
                    return True, message
            elif hasattr(self.parent2, 'attack_npc'):
                result = self.parent2.attack_npc(player, target_npc)
                if isinstance(result, tuple) and result[0]:
                    # Replace parent name with hybrid name in the message
                    message = result[1].replace(self.parent2.name, self.name)
                    return True, message
            
            # If no parent has an attack_npc method, implement basic attack
            import random
            messages = []
            
            # Calculate damage (random value between half and full damage)
            damage = random.randint(self.damage // 2, self.damage)
            
            # Apply damage to the target
            if hasattr(target_npc, 'health'):
                target_npc.health -= damage
                
                # Check if target died
                if target_npc.health <= 0:
                    target_npc.is_alive = False
                    if hasattr(target_npc, 'gang'):
                        target_npc.gang.remove_member(target_npc)
                    messages.append(f"You attack {target_npc.name} with your {self.name} for {damage} damage, defeating them!")
                else:
                    messages.append(f"You attack {target_npc.name} with your {self.name} for {damage} damage!")
                    
                    # If target is a gang member, they might become hostile
                    if hasattr(target_npc, 'gang') and hasattr(player, 'detected_by'):
                        player.detected_by.add(target_npc.gang)
                        messages.append(f"The {target_npc.gang.name} are now hostile toward you!")
            else:
                # For NPCs without health attribute
                target_npc.is_alive = False
                messages.append(f"You attack and defeat {target_npc.name} with your {self.name}!")
                
            return True, "\n".join(messages)
        return False, f"The {self.name} cannot be used as a weapon."
    
    # Delegate special methods to parent items
    def __getattr__(self, name):
        """
        This method is called when an attribute is not found in the normal way.
        It tries to find the attribute in the parent items.
        """
        # Special case for 'crop_type' and other seed attributes
        if name in ['crop_type', 'growth_time'] and hasattr(self.parent1, name):
            return getattr(self.parent1, name)
        elif name in ['crop_type', 'growth_time'] and hasattr(self.parent2, name):
            return getattr(self.parent2, name)
        
        # First check parent1
        if hasattr(self.parent1, name):
            attr = getattr(self.parent1, name)
            # If it's a method, bind it to this instance
            if callable(attr):
                def method(*args, **kwargs):
                    # Special case for methods that might remove the item
                    if name in ['use', 'consume', 'apply_effect']:
                        # Make a copy of the original method arguments
                        args_copy = list(args)
                        
                        # If this is a player method that would remove the item,
                        # we need to prevent that for hybrid items
                        if len(args) >= 1 and hasattr(args[0], 'inventory') and self in args[0].inventory:
                            # Remember that we're a hybrid and shouldn't be removed
                            is_hybrid = True
                        
                        # Call the original method
                        result = attr(*args, **kwargs)
                        
                        # Process the result
                        if isinstance(result, tuple) and len(result) >= 2:
                            # Handle tuple return format (success, message)
                            success, message = result[0], result[1]
                            # Replace references to the parent item with the hybrid item
                            message = message.replace(self.parent1.name, self.name)
                            return success, message
                        elif isinstance(result, str):
                            # Handle string return format
                            result = result.replace(self.parent1.name, self.name)
                            return result
                        return result
                    else:
                        # For other methods, just call them normally
                        result = attr(*args, **kwargs)
                        if isinstance(result, tuple) and len(result) >= 2:
                            # Handle tuple return format (success, message)
                            success, message = result[0], result[1]
                            # Replace references to the parent item with the hybrid item
                            message = message.replace(self.parent1.name, self.name)
                            return success, message
                        elif isinstance(result, str):
                            # Handle string return format
                            result = result.replace(self.parent1.name, self.name)
                            return result
                        return result
                return method
            return attr
        
        # Then check parent2
        if hasattr(self.parent2, name):
            attr = getattr(self.parent2, name)
            # If it's a method, bind it to this instance
            if callable(attr):
                def method(*args, **kwargs):
                    # Special case for methods that might remove the item
                    if name in ['use', 'consume', 'apply_effect']:
                        # Make a copy of the original method arguments
                        args_copy = list(args)
                        
                        # If this is a player method that would remove the item,
                        # we need to prevent that for hybrid items
                        if len(args) >= 1 and hasattr(args[0], 'inventory') and self in args[0].inventory:
                            # Remember that we're a hybrid and shouldn't be removed
                            is_hybrid = True
                        
                        # Call the original method
                        result = attr(*args, **kwargs)
                        
                        # Process the result
                        if isinstance(result, tuple) and len(result) >= 2:
                            # Handle tuple return format (success, message)
                            success, message = result[0], result[1]
                            # Replace references to the parent item with the hybrid item
                            message = message.replace(self.parent2.name, self.name)
                            return success, message
                        elif isinstance(result, str):
                            # Handle string return format
                            result = result.replace(self.parent2.name, self.name)
                            return result
                        return result
                    else:
                        # For other methods, just call them normally
                        result = attr(*args, **kwargs)
                        if isinstance(result, tuple) and len(result) >= 2:
                            # Handle tuple return format (success, message)
                            success, message = result[0], result[1]
                            # Replace references to the parent item with the hybrid item
                            message = message.replace(self.parent2.name, self.name)
                            return success, message
                        elif isinstance(result, str):
                            # Handle string return format
                            result = result.replace(self.parent2.name, self.name)
                            return result
                        return result
                return method
            return attr
        
        # If not found in either parent, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
