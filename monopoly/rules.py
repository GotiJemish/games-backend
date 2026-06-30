# d:/gamezone/games-backend/monopoly/rules.py

SPACES = [
    {"name": "GO", "type": "go"},
    {"name": "Mediterranean Avenue", "type": "property", "color": "brown", "price": 60, "rent": [2, 10, 30, 90, 160, 250], "house_cost": 50},
    {"name": "Community Chest", "type": "chest"},
    {"name": "Baltic Avenue", "type": "property", "color": "brown", "price": 60, "rent": [4, 20, 60, 180, 320, 450], "house_cost": 50},
    {"name": "Income Tax", "type": "tax", "price": 200},
    {"name": "Reading Railroad", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200]},
    {"name": "Oriental Avenue", "type": "property", "color": "lightblue", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "house_cost": 50},
    {"name": "Chance", "type": "chance"},
    {"name": "Vermont Avenue", "type": "property", "color": "lightblue", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "house_cost": 50},
    {"name": "Connecticut Avenue", "type": "property", "color": "lightblue", "price": 120, "rent": [8, 40, 100, 300, 450, 600], "house_cost": 50},
    {"name": "In Jail / Just Visiting", "type": "jail"},
    {"name": "St. Charles Place", "type": "property", "color": "pink", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "house_cost": 100},
    {"name": "Electric Company", "type": "utility", "price": 150, "rent": [4, 10]},
    {"name": "States Avenue", "type": "property", "color": "pink", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "house_cost": 100},
    {"name": "Virginia Avenue", "type": "property", "color": "pink", "price": 160, "rent": [12, 60, 180, 500, 700, 900], "house_cost": 100},
    {"name": "Pennsylvania Railroad", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200]},
    {"name": "St. James Place", "type": "property", "color": "orange", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "house_cost": 100},
    {"name": "Community Chest", "type": "chest"},
    {"name": "Tennessee Avenue", "type": "property", "color": "orange", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "house_cost": 100},
    {"name": "New York Avenue", "type": "property", "color": "orange", "price": 200, "rent": [16, 80, 220, 600, 800, 1000], "house_cost": 100},
    {"name": "Free Parking", "type": "parking"},
    {"name": "Kentucky Avenue", "type": "property", "color": "red", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "house_cost": 150},
    {"name": "Chance", "type": "chance"},
    {"name": "Indiana Avenue", "type": "property", "color": "red", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "house_cost": 150},
    {"name": "Illinois Avenue", "type": "property", "color": "red", "price": 240, "rent": [20, 100, 300, 750, 925, 1100], "house_cost": 150},
    {"name": "B. & O. Railroad", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200]},
    {"name": "Atlantic Avenue", "type": "property", "color": "yellow", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "house_cost": 150},
    {"name": "Ventnor Avenue", "type": "property", "color": "yellow", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "house_cost": 150},
    {"name": "Water Works", "type": "utility", "price": 150, "rent": [4, 10]},
    {"name": "Marvin Gardens", "type": "property", "color": "yellow", "price": 280, "rent": [24, 120, 360, 850, 1025, 1200], "house_cost": 150},
    {"name": "Go To Jail", "type": "gotojail"},
    {"name": "Pacific Avenue", "type": "property", "color": "green", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "house_cost": 200},
    {"name": "North Carolina Avenue", "type": "property", "color": "green", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "house_cost": 200},
    {"name": "Community Chest", "type": "chest"},
    {"name": "Pennsylvania Avenue", "type": "property", "color": "green", "price": 320, "rent": [28, 150, 450, 1000, 1200, 1400], "house_cost": 200},
    {"name": "Short Line Railroad", "type": "railroad", "price": 200, "rent": [25, 50, 100, 200]},
    {"name": "Chance", "type": "chance"},
    {"name": "Park Place", "type": "property", "color": "darkblue", "price": 350, "rent": [35, 175, 500, 1100, 1300, 1500], "house_cost": 200},
    {"name": "Luxury Tax", "type": "tax", "price": 100},
    {"name": "Boardwalk", "type": "property", "color": "darkblue", "price": 400, "rent": [50, 200, 600, 1400, 1700, 2000], "house_cost": 200}
]

COLOR_GROUPS = {
    "brown": [1, 3],
    "lightblue": [6, 8, 9],
    "pink": [11, 13, 14],
    "orange": [16, 18, 19],
    "red": [21, 23, 24],
    "yellow": [26, 27, 29],
    "green": [31, 32, 34],
    "darkblue": [37, 39],
    "railroad": [5, 15, 25, 35],
    "utility": [12, 28]
}

CHANCE_CARDS = [
    {"text": "Advance to GO (Collect $200)", "type": "move", "target": 0},
    {"text": "Advance to Illinois Avenue", "type": "move", "target": 24},
    {"text": "Advance to St. Charles Place", "type": "move", "target": 11},
    {"text": "Bank pays you dividend of $50", "type": "money", "amount": 50},
    {"text": "Go directly to Jail", "type": "jail"},
    {"text": "Pay poor tax of $15", "type": "money", "amount": -15},
    {"text": "Advance to Boardwalk", "type": "move", "target": 39},
    {"text": "Your building loan matures. Collect $150", "type": "money", "amount": 150},
    {"text": "You have won a crossword competition. Collect $100", "type": "money", "amount": 100}
]

COMMUNITY_CHEST_CARDS = [
    {"text": "Advance to GO (Collect $200)", "type": "move", "target": 0},
    {"text": "Bank error in your favor. Collect $200", "type": "money", "amount": 200},
    {"text": "Doctor's fees. Pay $50", "type": "money", "amount": -50},
    {"text": "From sale of stock you get $50", "type": "money", "amount": 50},
    {"text": "Income tax refund. Collect $200", "type": "money", "amount": 200},
    {"text": "Life insurance matures. Collect $100", "type": "money", "amount": 100},
    {"text": "Pay hospital fees of $100", "type": "money", "amount": -100},
    {"text": "Pay school fees of $50", "type": "money", "amount": -50},
    {"text": "You inherit $100", "type": "money", "amount": 100},
    {"text": "Holiday fund matures. Receive $100", "type": "money", "amount": 100}
]
