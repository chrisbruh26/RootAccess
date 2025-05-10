"""
Entity Factory for Root Access game.
This module provides factory methods for creating common entity types.
"""

from components import (
    Entity, Component, 
    InventoryComponent, HealthComponent, UsableComponent, WeaponComponent,
    BreakableComponent, EffectComponent, GardeningComponent, HidingComponent,
    TechComponent, BehaviorComponent, SeedComponent, PlantComponent, SoilComponent,
    WateringCanComponent,
    create_weapon, create_consumable, create_effect_item, create_tech_item,
    create_hiding_spot, create_vending_machine, create_seed, create_watering_can,
    create_soil_plot, create_plant
)

class EntityFactory:
    """Factory class for creating game entities."""
    
    @staticmethod
    def create_player():
        """Create a player entity."""
        player = Entity("Player", "The player character.")
        player.is_player = True
        player.current_area = None
        player.is_hidden = False
        player.hiding_spot = None
        player.detected_by = set()  # Set of gangs that have detected the player
        player.active_effects = []  # List of active effects on the player
        
        # Add components
        player.add_component("inventory", InventoryComponent(capacity=20))
        player.add_component("health", HealthComponent(max_health=100))
        
        return player
    
    @staticmethod
    def create_npc(name, description, behavior_type="neutral"):
        """Create an NPC entity."""
        npc = Entity(name, description)
        npc.is_player = False
        npc.current_area = None
        npc.is_hidden = False
        npc.hiding_spot = None
        npc.active_effects = []  # List of active effects on the NPC
        
        # Add components
        npc.add_component("inventory", InventoryComponent(capacity=10))
        npc.add_component("health", HealthComponent(max_health=50))
        npc.add_component("behavior", BehaviorComponent(behavior_type=behavior_type))
        
        return npc
    
    @staticmethod
    def create_gang_member(name, description, gang):
        """Create a gang member NPC."""
        npc = EntityFactory.create_npc(name, description, "aggressive")
        npc.gang = gang
        gang.add_member(npc)
        
        # Add a weapon to the gang member
        weapon = create_weapon("Knife", "A sharp knife.", 10, 5)
        inventory = npc.get_component("inventory")
        if inventory:
            inventory.add_item(weapon)
        
        return npc
    
    @staticmethod
    def create_area(name, description):
        """Create an area entity."""
        area = Entity(name, description)
        area.connections = {}  # Dictionary of direction -> area
        area.entities = []  # List of entities in this area
        area.objects = []  # List of objects in this area
        area.items = []  # List of items in this area
        area.npcs = []  # List of NPCs in this area
        
        def add_connection(direction, target_area):
            """Add a connection to another area."""
            area.connections[direction] = target_area
        
        def add_entity(entity):
            """Add an entity to this area."""
            area.entities.append(entity)
            entity.current_area = area
        
        def remove_entity(entity):
            """Remove an entity from this area."""
            if entity in area.entities:
                area.entities.remove(entity)
                if entity.current_area == area:
                    entity.current_area = None
        
        def add_object(obj):
            """Add an object to this area."""
            area.objects.append(obj)
            area.entities.append(obj)
            obj.current_area = area
        
        def remove_object(obj):
            """Remove an object from this area."""
            if obj in area.objects:
                area.objects.remove(obj)
                if obj in area.entities:
                    area.entities.remove(obj)
                if obj.current_area == area:
                    obj.current_area = None
        
        def add_item(item):
            """Add an item to this area."""
            area.items.append(item)
            area.entities.append(item)
            item.current_area = area
        
        def remove_item(item):
            """Remove an item from this area."""
            if item in area.items:
                area.items.remove(item)
                if item in area.entities:
                    area.entities.remove(item)
                if item.current_area == area:
                    item.current_area = None
        
        def add_npc(npc):
            """Add an NPC to this area."""
            area.npcs.append(npc)
            area.entities.append(npc)
            npc.current_area = area
        
        def remove_npc(npc):
            """Remove an NPC from this area."""
            if npc in area.npcs:
                area.npcs.remove(npc)
                if npc in area.entities:
                    area.entities.remove(npc)
                if npc.current_area == area:
                    npc.current_area = None
        
        # Add methods to the area
        area.add_connection = add_connection
        area.add_entity = add_entity
        area.remove_entity = remove_entity
        area.add_object = add_object
        area.remove_object = remove_object
        area.add_item = add_item
        area.remove_item = remove_item
        area.add_npc = add_npc
        area.remove_npc = remove_npc
        
        return area
    
    @staticmethod
    def create_computer(name, description):
        """Create a computer entity."""
        computer = Entity(name, description)
        computer.add_tag("object")
        computer.add_tag("tech")
        computer.add_tag("hackable")
        
        # Add tech component
        tech_component = TechComponent(tech_level=2, energy=100, max_energy=100)
        computer.add_component("tech", tech_component)
        
        # Add programs
        tech_component.programs = ["data_miner", "security_override"]
        
        # Add usable component
        def use_computer(item, user, game):
            # Show available programs
            programs = tech_component.programs
            if not programs:
                return False, f"The {item.name} has no programs installed."
            
            program_list = "\n".join([f"- {program}" for program in programs])
            return True, f"Available programs on {item.name}:\n{program_list}\n\nUse 'run [program] on [target]' to run a program."
        
        computer.add_component("usable", UsableComponent(use_function=use_computer))
        
        return computer
    
    @staticmethod
    def create_drone(name="Drone", description="A small drone that can be controlled remotely."):
        """Create a drone entity."""
        drone = Entity(name, description)
        drone.add_tag("item")
        drone.add_tag("tech")
        drone.add_tag("drone")
        drone.value = 100
        
        # Add tech component
        tech_component = TechComponent(tech_level=3, energy=50, max_energy=50)
        drone.add_component("tech", tech_component)
        
        # Add usable component
        def use_drone(item, user, game):
            # Check if the drone has enough energy
            if tech_component.energy < 10:
                return False, f"The {item.name} doesn't have enough energy."
            
            # Use energy
            tech_component.use_energy(10)
            
            # Scan the area
            if user.current_area:
                # List all entities in the area
                entities = []
                for entity in user.current_area.entities:
                    if entity != user and entity != item:
                        entities.append(f"- {entity}")
                
                if entities:
                    return True, f"You send the {item.name} to scan the area. It detects:\n" + "\n".join(entities)
                else:
                    return True, f"You send the {item.name} to scan the area, but it doesn't detect anything."
            
            return False, f"There's nowhere to send the {item.name}."
        
        drone.add_component("usable", UsableComponent(use_function=use_drone))
        
        return drone
    
    @staticmethod
    def create_soil_plot():
        """Create a soil plot."""
        return create_soil_plot()
    
    @staticmethod
    def create_plant(name, description, plant_type, growth_stage=0):
        """Create a plant entity."""
        return create_plant(name, description, plant_type, growth_stage)
    
    @staticmethod
    def convert_existing_entities(entities):
        """Convert existing entities to use the component system."""
        converted = []
        
        for entity in entities:
            # Create a new entity
            new_entity = Entity(entity.name, entity.description)
            
            # Copy attributes
            for attr_name, attr_value in vars(entity).items():
                if attr_name not in ['name', 'description', 'components', 'tags']:
                    setattr(new_entity, attr_name, attr_value)
            
            # Add to converted list
            converted.append(new_entity)
        
        return converted
