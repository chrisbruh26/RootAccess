documenting which parts of the game version /home/reginapinkdog/projects/Game_files/RootAccessStuff/simplified_scalable_improvements/Root_Access_v2/Root_Access_v2/main.py are good so far and which ones need to be improved 


GAME CLASS:

create_world - easy and readable system for creating areas, connecting them geographically, and adding objects, items, and npcs to them. I could make it more scalable though, using json. I like the template idea so that I can define objects, areas, etc and create multiple that are similar and then change them slightly as needed. 

process_command: 
command from input is passed through, it splits the command into words and locates the key in the dictionary, then calls the right command handler. 

might wanna remove the interact command or do something else with it because it's too vague and has no gameplay impact, because if it's an unrecognized item or the item's functionality is not set up, it simply says "you interact with the item" which doesn't add anything to the game experience.

random events - don't like, doesn't have much gameplay effect. I like the concept of gang members randomly appearing, but it would only be logical if they came to start a fight with another gang, so that should only occur in gang territories. 


AREA FILE:

make changes if necessary to fit the template system, but not sure what needs to change if anything

ITEMS FILE:
may need several changes to fit the template system 


says "from object import VendingMachine" which is not going to be scalable because the vending machine is just one object and if anything there should be a vending machine template. I will implement templates, with the json file that I already have but possibly with adjustments, as soon as I can. 


class SmokeBomb(Item) - not scalable because it's just one item and not that significant, will change when I do the template implementation

Decoy(item) - good example of a starter for a template because decoy is vague and seems easily scalable

class Consumable(Item) - great class, scalable, for items like foods and drinks and how much health they give

TechItem - scalable class, for tech like the drone, which already works and does wonders for gameplay

class USBStick(TechItem) good setup, not sure if it should be its own class, but a great starting concept for templates as I'm sure there will be several types. This may work better as an intel class, and intel may be a subclass of TechItem. I could create a class and/or template for insertable tech, which would include USB sticks but be expandable for others. 

PLAYER FILE:

Player class: 

if item does not have a method for player to use it, then it will say "you cannot use the [item name] right now." This is fine, but I should make sure all existing items that have a purpose are functional

OBJECTS FILE:

computer class, not sure if keeping, probably a good template but it could be its own class too. must keep base class attributes and methods vague so that it's easy to customize with templates. 

hidingspot class - no changes necessary except player must become unhidden when they travel to another area.

storage - great class, seems set up to create templates easily

breakableglassobject - love it, may want to adjust so that it can be expanded to other objects that are not glass but still breakable, and create templates with this.

vendingmachine class is here, which is not necessary and will be changed into a template of another object later. it is both breakable and contains items, which are only retrievable by breaking it so far, not sure if I'll make it possible to get items by interacting like a normal vending machine. For now it's a breakable object and should be a template of a breakable object. The vending machine should only be an instance of a breakable object, not its own class.

GARDENING FILE:

seed class - great, ready to make templates from

plant - also template-ready

soilplot - should make it list the names of plant that are growing, but other than that, great

wateringcan - great, ready to make templates from, especially since better watering cans could hold more water and different types of water (like hacked milk)