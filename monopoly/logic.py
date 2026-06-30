# d:/gamezone/games-backend/monopoly/logic.py

import random
from typing import List, Tuple
from monopoly.rules import SPACES, COLOR_GROUPS, CHANCE_CARDS, COMMUNITY_CHEST_CARDS

def initialize_board(player_colors: List[str]) -> dict:
    players = {}
    for col in player_colors:
        players[col] = {
            "position": 0,
            "money": 1500,
            "in_jail": False,
            "jail_turns": 0,
            "bankrupt": False,
            "color": col
        }
    buyable_indices = [
        1, 3, 5, 6, 8, 9, 11, 12, 13, 14, 15, 16, 18, 19, 21, 23, 24, 25, 26, 27, 28, 29, 31, 32, 34, 35, 37, 39
    ]
    properties = {}
    for idx in buyable_indices:
        properties[str(idx)] = {
            "owner": None,
            "houses": 0,
            "mortgaged": False
        }
    return {
        "players": players,
        "properties": properties,
        "logs": ["Game started!"],
        "phase": "roll", # "roll", "action"
        "double_roll_count": 0
    }

def calculate_rent(board_state: dict, pos: int, roll_total: int) -> int:
    space = SPACES[pos]
    prop_state = board_state["properties"].get(str(pos))
    if not prop_state:
        return 0
    owner = prop_state["owner"]
    if not owner:
        return 0
        
    space_type = space["type"]
    if space_type == "property":
        houses = prop_state["houses"]
        if houses > 0:
            return space["rent"][houses]
        else:
            color_group = space["color"]
            group_indices = COLOR_GROUPS[color_group]
            owns_all = True
            for g_pos in group_indices:
                if board_state["properties"][str(g_pos)]["owner"] != owner:
                    owns_all = False
                    break
            base_rent = space["rent"][0]
            return base_rent * 2 if owns_all else base_rent
            
    elif space_type == "railroad":
        railroad_indices = COLOR_GROUPS["railroad"]
        count = 0
        for r_pos in railroad_indices:
            if board_state["properties"][str(r_pos)]["owner"] == owner:
                count += 1
        if count == 1:
            return 25
        elif count == 2:
            return 50
        elif count == 3:
            return 100
        elif count == 4:
            return 200
        return 0
        
    elif space_type == "utility":
        utility_indices = COLOR_GROUPS["utility"]
        count = 0
        for u_pos in utility_indices:
            if board_state["properties"][str(u_pos)]["owner"] == owner:
                count += 1
        if count == 1:
            return 4 * roll_total
        elif count == 2:
            return 10 * roll_total
        return 0
        
    return 0

def apply_card(board_state: dict, color: str, card: dict, roll_total: int) -> dict:
    player = board_state["players"][color]
    logs = board_state["logs"]
    
    card_type = card["type"]
    if card_type == "money":
        amount = card["amount"]
        player["money"] += amount
        if amount > 0:
            logs.append(f"{color} received ${amount} from card.")
        else:
            logs.append(f"{color} paid ${abs(amount)} from card.")
    elif card_type == "move":
        target = card["target"]
        old_pos = player["position"]
        player["position"] = target
        logs.append(f"{color} moved to {SPACES[target]['name']} via card.")
        if target < old_pos:
            player["money"] += 200
            logs.append(f"{color} passed GO and collected $200.")
        board_state["players"][color] = player
        board_state = land_on_space(board_state, color, target, roll_total)
    elif card_type == "jail":
        player["in_jail"] = True
        player["position"] = 10
        player["jail_turns"] = 0
        logs.append(f"{color} was sent directly to Jail via card.")
        
    board_state["players"][color] = player
    return board_state

def land_on_space(board_state: dict, color: str, pos: int, roll_total: int) -> dict:
    player = board_state["players"][color]
    space = SPACES[pos]
    space_name = space["name"]
    space_type = space["type"]
    logs = board_state["logs"]
    
    logs.append(f"{color} landed on {space_name}.")
    
    if space_type == "tax":
        tax_amount = space["price"]
        player["money"] -= tax_amount
        logs.append(f"{color} paid ${tax_amount} tax.")
    elif space_type == "gotojail":
        player["in_jail"] = True
        player["position"] = 10
        player["jail_turns"] = 0
        logs.append(f"{color} was sent to Jail!")
    elif space_type in ["property", "railroad", "utility"]:
        prop_state = board_state["properties"].get(str(pos))
        if prop_state:
            owner = prop_state["owner"]
            if owner and owner != color and not prop_state["mortgaged"]:
                if not board_state["players"][owner]["bankrupt"]:
                    rent = calculate_rent(board_state, pos, roll_total)
                    player["money"] -= rent
                    board_state["players"][owner]["money"] += rent
                    logs.append(f"{color} paid ${rent} rent to {owner}.")
    elif space_type == "chance":
        card = random.choice(CHANCE_CARDS)
        logs.append(f"Chance Card drawn: '{card['text']}'")
        board_state = apply_card(board_state, color, card, roll_total)
    elif space_type == "chest":
        card = random.choice(COMMUNITY_CHEST_CARDS)
        logs.append(f"Community Chest Card drawn: '{card['text']}'")
        board_state = apply_card(board_state, color, card, roll_total)
        
    board_state["players"][color] = player
    return board_state

def make_move(board_state: dict, color: str, roll1: int, roll2: int) -> Tuple[dict, str]:
    player = board_state["players"][color]
    double_roll = (roll1 == roll2)
    roll_total = roll1 + roll2
    logs = board_state["logs"]
    
    logs.append(f"{color} rolled a {roll1} and {roll2} (total {roll_total}).")
    
    if player["in_jail"]:
        if double_roll:
            player["in_jail"] = False
            player["jail_turns"] = 0
            logs.append(f"{color} rolled doubles and got out of Jail!")
            old_pos = player["position"]
            new_pos = (old_pos + roll_total) % 40
            player["position"] = new_pos
            board_state["players"][color] = player
            board_state = land_on_space(board_state, color, new_pos, roll_total)
            board_state["phase"] = "action"
        else:
            player["jail_turns"] += 1
            if player["jail_turns"] >= 3:
                player["money"] -= 50
                player["in_jail"] = False
                player["jail_turns"] = 0
                logs.append(f"{color} spent 3 turns in Jail. Paid $50 fine and moved {roll_total}.")
                old_pos = player["position"]
                new_pos = (old_pos + roll_total) % 40
                player["position"] = new_pos
                board_state["players"][color] = player
                board_state = land_on_space(board_state, color, new_pos, roll_total)
                board_state["phase"] = "action"
            else:
                logs.append(f"{color} remains in Jail.")
                board_state["phase"] = "action" # Can only end turn
        board_state["players"][color] = player
        return board_state, f"{color} rolled {roll_total}."
        
    # Standard turn
    if double_roll:
        board_state["double_roll_count"] += 1
        if board_state["double_roll_count"] == 3:
            player["in_jail"] = True
            player["position"] = 10
            board_state["double_roll_count"] = 0
            board_state["phase"] = "action"
            logs.append(f"{color} rolled doubles 3 times in a row! Sent to Jail!")
            board_state["players"][color] = player
            return board_state, f"{color} sent to Jail for speed limit violation."
    else:
        board_state["double_roll_count"] = 0
        
    old_pos = player["position"]
    new_pos = (old_pos + roll_total) % 40
    player["position"] = new_pos
    
    if new_pos < old_pos:
        player["money"] += 200
        logs.append(f"{color} passed GO and collected $200.")
        
    board_state["players"][color] = player
    board_state = land_on_space(board_state, color, new_pos, roll_total)
    
    board_state["phase"] = "action"
    return board_state, f"{color} moved to {SPACES[new_pos]['name']}."

def buy_property(board_state: dict, color: str, property_idx: int) -> Tuple[dict, bool, str]:
    player = board_state["players"][color]
    prop_state = board_state["properties"].get(str(property_idx))
    space = SPACES[property_idx]
    
    if not prop_state:
        return board_state, False, "Invalid property."
    if prop_state["owner"] is not None:
        return board_state, False, "Property already owned."
    if player["position"] != property_idx:
        return board_state, False, "You must stand on the property to buy it."
    if player["money"] < space["price"]:
        return board_state, False, "Insufficient funds."
        
    player["money"] -= space["price"]
    prop_state["owner"] = color
    board_state["properties"][str(property_idx)] = prop_state
    board_state["players"][color] = player
    board_state["logs"].append(f"{color} bought {space['name']} for ${space['price']}.")
    return board_state, True, f"Bought {space['name']}."

def build_house(board_state: dict, color: str, property_idx: int) -> Tuple[dict, bool, str]:
    player = board_state["players"][color]
    prop_state = board_state["properties"].get(str(property_idx))
    space = SPACES[property_idx]
    
    if not prop_state:
        return board_state, False, "Invalid property."
    if prop_state["owner"] != color:
        return board_state, False, "You do not own this property."
    if space["type"] != "property":
        return board_state, False, "Houses can only be built on street properties."
    if prop_state["mortgaged"]:
        return board_state, False, "Property is mortgaged."
    if prop_state["houses"] >= 5:
        return board_state, False, "Maximum houses/hotel already built."
        
    color_group = space["color"]
    group_indices = COLOR_GROUPS[color_group]
    for idx in group_indices:
        g_prop = board_state["properties"][str(idx)]
        if g_prop["owner"] != color:
            return board_state, False, f"You must own all {color_group} properties to build."
        if g_prop["mortgaged"]:
            return board_state, False, "Cannot build houses while a property in the group is mortgaged."
            
    # Check even building
    curr_houses = prop_state["houses"]
    for idx in group_indices:
        if idx == property_idx:
            continue
        other_houses = board_state["properties"][str(idx)]["houses"]
        if curr_houses > other_houses:
            return board_state, False, "You must build evenly! Add houses to other properties first."
            
    if player["money"] < space["house_cost"]:
        return board_state, False, "Insufficient funds to build house."
        
    player["money"] -= space["house_cost"]
    prop_state["houses"] += 1
    board_state["properties"][str(property_idx)] = prop_state
    board_state["players"][color] = player
    
    desc = f"built a house on {space['name']}" if prop_state["houses"] < 5 else f"built a hotel on {space['name']}"
    board_state["logs"].append(f"{color} {desc} for ${space['house_cost']}.")
    return board_state, True, f"Built house on {space['name']}."

def sell_house(board_state: dict, color: str, property_idx: int) -> Tuple[dict, bool, str]:
    player = board_state["players"][color]
    prop_state = board_state["properties"].get(str(property_idx))
    space = SPACES[property_idx]
    
    if not prop_state:
        return board_state, False, "Invalid property."
    if prop_state["owner"] != color:
        return board_state, False, "You do not own this property."
    if prop_state["houses"] <= 0:
        return board_state, False, "No houses to sell."
        
    # Check even selling
    curr_houses = prop_state["houses"]
    color_group = space["color"]
    group_indices = COLOR_GROUPS[color_group]
    for idx in group_indices:
        if idx == property_idx:
            continue
        other_houses = board_state["properties"][str(idx)]["houses"]
        if curr_houses < other_houses:
            return board_state, False, "You must sell evenly! Sell houses from other properties first."
            
    sell_value = space["house_cost"] // 2
    player["money"] += sell_value
    prop_state["houses"] -= 1
    board_state["properties"][str(property_idx)] = prop_state
    board_state["players"][color] = player
    board_state["logs"].append(f"{color} sold a house on {space['name']} for ${sell_value}.")
    return board_state, True, f"Sold house on {space['name']}."

def mortgage_property(board_state: dict, color: str, property_idx: int) -> Tuple[dict, bool, str]:
    player = board_state["players"][color]
    prop_state = board_state["properties"].get(str(property_idx))
    space = SPACES[property_idx]
    
    if not prop_state:
        return board_state, False, "Invalid property."
    if prop_state["owner"] != color:
        return board_state, False, "You do not own this property."
    if prop_state["houses"] > 0:
        return board_state, False, "Must sell houses before mortgaging."
        
    mortgage_value = space["price"] // 2
    
    if prop_state["mortgaged"]:
        unmortgage_cost = int(mortgage_value * 1.1)
        if player["money"] < unmortgage_cost:
            return board_state, False, f"Insufficient funds. Cost: ${unmortgage_cost}."
        player["money"] -= unmortgage_cost
        prop_state["mortgaged"] = False
        board_state["logs"].append(f"{color} unmortgaged {space['name']} for ${unmortgage_cost}.")
        msg = f"Unmortgaged {space['name']}."
    else:
        player["money"] += mortgage_value
        prop_state["mortgaged"] = True
        board_state["logs"].append(f"{color} mortgaged {space['name']} for ${mortgage_value}.")
        msg = f"Mortgaged {space['name']}."
        
    board_state["properties"][str(property_idx)] = prop_state
    board_state["players"][color] = player
    return board_state, True, msg

def pay_jail_fine(board_state: dict, color: str) -> Tuple[dict, bool, str]:
    player = board_state["players"][color]
    if not player["in_jail"]:
        return board_state, False, "You are not in Jail."
    if player["money"] < 50:
        return board_state, False, "Insufficient funds to pay Jail fine."
        
    player["money"] -= 50
    player["in_jail"] = False
    player["jail_turns"] = 0
    board_state["phase"] = "roll"
    board_state["logs"].append(f"{color} paid $50 Jail fine and is out of Jail.")
    
    board_state["players"][color] = player
    return board_state, True, "Paid $50 fine."

def declare_bankruptcy(board_state: dict, color: str) -> Tuple[dict, bool, str]:
    player = board_state["players"][color]
    if player["money"] >= 0:
        return board_state, False, "You are not in debt."
        
    player["bankrupt"] = True
    board_state["logs"].append(f"{color} declared bankruptcy and is out of the game!")
    
    for idx_str, prop in board_state["properties"].items():
        if prop["owner"] == color:
            prop["owner"] = None
            prop["houses"] = 0
            prop["mortgaged"] = False
            board_state["properties"][idx_str] = prop
            
    active_players = [col for col, p in board_state["players"].items() if not p["bankrupt"]]
    if len(active_players) == 1:
        board_state["phase"] = "finished"
        
    board_state["players"][color] = player
    return board_state, True, f"{color} is bankrupt."

def end_turn(board_state: dict, active_colors: List[str]) -> Tuple[dict, str]:
    curr_color = board_state.get("current_turn")
    if not curr_color:
        curr_color = active_colors[0]
        
    try:
        idx = active_colors.index(curr_color)
    except ValueError:
        idx = 0
        
    next_idx = (idx + 1) % len(active_colors)
    attempts = 0
    while attempts < len(active_colors):
        next_color = active_colors[next_idx]
        if not board_state["players"][next_color]["bankrupt"]:
            board_state["current_turn"] = next_color
            board_state["phase"] = "roll"
            board_state["double_roll_count"] = 0
            board_state["logs"].append(f"It is now {next_color}'s turn.")
            return board_state, f"Turn passed to {next_color}."
        next_idx = (next_idx + 1) % len(active_colors)
        attempts += 1
        
    return board_state, "No active players."
