"""
Combat and health descriptions for Root Access game.
This module provides descriptive text for combat actions and health states.
"""

import random

# Attack descriptions based on damage amount
LIGHT_ATTACK_DESCRIPTIONS = [
    "{attacker} throws a weak punch at you",
    "{attacker} swings clumsily at you",
    "{attacker} makes a half-hearted attempt to hit you",
    "{attacker} lunges at you awkwardly",
    "{attacker} tries to grab you but mostly misses",
    "{attacker} swipes at you with minimal force",
    "{attacker} makes a sloppy attack attempt",
    "{attacker} stumbles toward you with arms flailing",
]

MEDIUM_ATTACK_DESCRIPTIONS = [
    "{attacker} lands a solid hit on you",
    "{attacker} strikes you with moderate force",
    "{attacker} connects with a decent blow",
    "{attacker} catches you with a well-aimed strike",
    "{attacker} hits you with surprising accuracy",
    "{attacker} delivers a calculated strike",
    "{attacker} attacks with practiced precision",
    "{attacker} executes a trained combat move against you",
]

HEAVY_ATTACK_DESCRIPTIONS = [
    "{attacker} slams into you with brutal force",
    "{attacker} delivers a devastating blow",
    "{attacker} strikes with shocking violence",
    "{attacker} hits you with incredible power",
    "{attacker} unleashes a vicious attack",
    "{attacker} connects with a bone-jarring impact",
    "{attacker} executes a perfectly timed power attack",
    "{attacker} catches you completely off-guard with a powerful strike",
]

CRITICAL_ATTACK_DESCRIPTIONS = [
    "{attacker} hits you with a potentially lethal strike",
    "{attacker} finds a critical weakness in your defense",
    "{attacker} delivers what might be a killing blow",
    "{attacker} attacks with terrifying precision and force",
    "{attacker} executes a masterful combat technique that leaves you reeling",
    "{attacker} unleashes an attack of shocking brutality",
    "{attacker} strikes with such force that your vision momentarily blacks out",
    "{attacker} hits you with an attack that seems impossible to survive",
]

# Weapon-specific attack descriptions
WEAPON_ATTACK_DESCRIPTIONS = {
    "Knife": [
        "{attacker} slashes at you with their knife",
        "{attacker} makes a quick stabbing motion toward you",
        "{attacker} swipes their blade in a dangerous arc",
        "{attacker} thrusts their knife with deadly intent",
    ],
    "Gun": [
        "{attacker} fires a shot that grazes you",
        "{attacker} squeezes off a round in your direction",
        "{attacker} takes aim and fires at you",
        "{attacker} discharges their weapon at close range",
    ],
    # Add more weapons as needed
}

# Injury descriptions based on health percentage
INJURY_DESCRIPTIONS = {
    # 76-100% health
    "barely_injured": [
        "You're barely scratched",
        "You shrug off the minor injury",
        "It's just a flesh wound",
        "You've had worse paper cuts",
        "The injury is more annoying than painful",
        "You're still in excellent condition",
        "You barely feel the impact",
        "You're still fighting fit",
    ],
    # 51-75% health
    "lightly_injured": [
        "You're starting to feel the pain",
        "You've sustained some minor injuries",
        "You're a bit banged up but still moving well",
        "You wince from your accumulating wounds",
        "You're hurting, but it's nothing serious",
        "Your injuries are becoming noticeable",
        "You feel a dull ache from your wounds",
        "You're somewhat battered but still strong",
    ],
    # 26-50% health
    "moderately_injured": [
        "You're definitely feeling worse for wear",
        "Your injuries are becoming concerning",
        "You struggle to maintain your composure through the pain",
        "You're significantly wounded and slowing down",
        "Blood trickles from multiple injuries",
        "Your vision occasionally blurs from the pain",
        "You're having trouble focusing through your injuries",
        "You need to find a way to recover soon",
    ],
    # 11-25% health
    "severely_injured": [
        "You're badly wounded and fading fast",
        "Your injuries are potentially life-threatening",
        "You can barely stay on your feet",
        "Your vision swims as blood loss takes its toll",
        "You're fighting to remain conscious",
        "Every movement sends waves of agony through your body",
        "You need immediate medical attention",
        "You're hanging on by a thread",
    ],
    # 1-10% health
    "critically_injured": [
        "You're at death's door",
        "You can feel yourself slipping away",
        "Darkness creeps at the edges of your vision",
        "Your heartbeat pounds in your ears as you near collapse",
        "You're moments away from unconsciousness",
        "Your body is failing from catastrophic injuries",
        "You're barely clinging to life",
        "One more hit will surely finish you",
    ]
}

# Death and respawn descriptions
DEATH_DESCRIPTIONS = [
    "Everything goes black as you collapse to the ground...",
    "Your vision tunnels and fades as you fall...",
    "The world spins and then disappears as you lose consciousness...",
    "Your legs give out and darkness claims you...",
    "Pain overwhelms your senses before everything goes silent...",
    "You feel strangely weightless as consciousness slips away...",
    "The last thing you see is your attacker standing over you...",
    "Your body finally gives in to its injuries and shuts down...",
]

RESPAWN_DESCRIPTIONS = [
    "You wake up in your bed, somehow transported home safely.",
    "A medical drone must have carried you home after you passed out.",
    "You regain consciousness in familiar surroundings, your wounds treated.",
    "Someone or something brought you back to safety while you were unconscious.",
    "You're not sure how you got here, but you're grateful to be alive.",
    "The city's automated medical system seems to have saved your life.",
    "You remember nothing after falling, but somehow you're back home.",
    "Despite your injuries, you've survived to fight another day.",
]

def get_attack_description(attacker_name, damage, weapon_name=None):
    """Get a descriptive attack message based on damage amount and weapon."""
    # Determine attack severity based on damage
    if damage <= 5:
        descriptions = LIGHT_ATTACK_DESCRIPTIONS
    elif damage <= 15:
        descriptions = MEDIUM_ATTACK_DESCRIPTIONS
    elif damage <= 30:
        descriptions = HEAVY_ATTACK_DESCRIPTIONS
    else:
        descriptions = CRITICAL_ATTACK_DESCRIPTIONS
        
    # Check for weapon-specific descriptions
    if weapon_name and weapon_name in WEAPON_ATTACK_DESCRIPTIONS:
        # 50% chance to use weapon-specific description
        if random.random() < 0.5:
            descriptions = WEAPON_ATTACK_DESCRIPTIONS[weapon_name]
    
    # Select and format description
    description = random.choice(descriptions)
    return description.format(attacker=attacker_name)

def get_injury_description(health, max_health=100):
    """Get a descriptive injury message based on health percentage."""
    health_percent = (health / max_health) * 100
    
    if health_percent > 75:
        category = "barely_injured"
    elif health_percent > 50:
        category = "lightly_injured"
    elif health_percent > 25:
        category = "moderately_injured"
    elif health_percent > 10:
        category = "severely_injured"
    else:
        category = "critically_injured"
        
    return random.choice(INJURY_DESCRIPTIONS[category])

def get_death_description():
    """Get a descriptive death message."""
    return random.choice(DEATH_DESCRIPTIONS)

def get_respawn_description():
    """Get a descriptive respawn message."""
    return random.choice(RESPAWN_DESCRIPTIONS)

def format_combat_message(attacker_name, damage, health, max_health=100, weapon_name=None):
    """Format a complete combat message with attack and injury descriptions."""
    attack_desc = get_attack_description(attacker_name, damage, weapon_name)
    injury_desc = get_injury_description(health, max_health)
    
    # Format the complete message
    if damage <= 5:
        return f"{attack_desc}. {injury_desc}."
    elif damage <= 15:
        return f"{attack_desc}, causing you to stagger. {injury_desc}."
    elif damage <= 30:
        return f"{attack_desc}, sending a shock of pain through your body. {injury_desc}."
    else:
        return f"{attack_desc}! The world spins from the impact. {injury_desc}."
