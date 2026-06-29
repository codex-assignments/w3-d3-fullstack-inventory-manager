from flask import Flask, request
from flask_cors import CORS
# module to randomize things, random.choice(items) picks a random item out of a list, can add weights
# specify weights with a int per item and how many items to pick (k): ex: drop = random.choices(rarities, weights=[95, 5], k=1)
import random

app = Flask(__name__)
CORS(app)

MAX_WEIGHT = 100.0

# procedural loot generation
ITEM_TYPES = ["Weapon", "Magic Item", "Tome", "Armor", "Valuable", "Tool"]
RARITIES = ["Common", "Uncommon", "Rare", "Legendary"]
ADJECTIVES = ["Rusty", "Glowing", "Ancient", "Cursed", "Blessed", "Heavy", "Ethereal", "Broken", "Polished", "Mythic", "Slime", "Twisted", "Demonic", "Chilled"]
NOUNS = {
    "Weapon": ["Sword", "Dagger", "Axe", "Bow", "Mace", "Staff", "Brass Knuckles"],
    "Magic Item": ["Ring", "Amulet", "Orb", "Cloak", "Boots", "Gloves"],
    "Tome": ["Grimoire", "Scroll", "Spellbook", "Journal", "Tablet"],
    "Armor": ["Shield", "Chestplate", "Helmet", "Gauntlets", "Greaves"],
    "Valuable": ["Gemstone", "Goblet", "Gold Coin", "Crown", "Ingot", "Jade Frog Carving"],
    "Tool": ["Pickaxe", "Hammer", "Compass", "Lockpick", "Lantern", "Rope"],
}

MASTER_LOOT_POOL = [] #initialize variable as a list
# generate pool of items to 100, randomize items to pull from -- just name, weight, and item type, rarity can be added on finding the item and adding to inventory
for i in range(1, 101): 
    item_type = random.choice(ITEM_TYPES)
    name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS[item_type])}"
    
    # item weight tied to item type
    if item_type in ["Armor", "Weapon"]:
        weight = round(random.uniform(5, 20), 1) # randomize weight between 5 and 20, round to 1 decimal place
    elif item_type in ["Valuable", "Tool"]:
        weight = round(random.uniform(0.5, 4), 1)
    else:
        weight = round(random.uniform(1, 8), 1)

    MASTER_LOOT_POOL.append({
        "pool_id": i,
        "name": name,
        "type": item_type,
        "weight": weight
    })

player_inventory = []

def get_total_weight():
    return sum(item["weight"] for item in player_inventory)

#  Routes
@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    return {
        "items": player_inventory,
        "current_weight": get_total_weight(),
        "max_weight": MAX_WEIGHT
    }, 200

# find random item based on drop rates
@app.route("/api/loot/roll", methods=["POST"])
def roll_loot():
    current_weight = get_total_weight()
    # common: 70%, ucommon: 20%, rare: 8%, legendary: 2%
    rolled_rarity = random.choices(
        population=RARITIES,
        weights=[70, 20, 8, 2], 
        k=1 
    )[0] #pulls from the [] returned by random, even if you only ask for 1

    base_item = random.choice(MASTER_LOOT_POOL)

    # encumbrance check
    if current_weight + base_item["weight"] > MAX_WEIGHT:
        return {
            "error": f"You are overencumbered! You found a [{rolled_rarity}] {base_item['name']} ({base_item['weight']} lbs), but your pack is too heavy to add it to your inventory."
        }, 400

    # unique instance of the found item
    unique_id = max([item["id"] for item in player_inventory], default=0) + 1
    new_loot = {
        "id": unique_id,
        "name": base_item["name"],
        "type": base_item["type"],
        "weight": base_item["weight"],
        "rarity": rolled_rarity
    }

    player_inventory.append(new_loot)
    return {
        "message": f"You found loot!",
        "new_item": new_loot,
        "current_weight": get_total_weight()
    }, 201

# Empty player's inventory
@app.route("/api/inventory/clear", methods=["POST"])
def clear_inventory():
    global player_inventory #change global variable with global keyword
    player_inventory = [] # clear's inventory
    return {"message": "Inventory cleared."}, 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)