from typing import Dict, List, Tuple, Set

def get_next_turn_go(current: str) -> str:
    """
    Alternates between BLACK and WHITE.
    """
    return "WHITE" if current == "BLACK" else "BLACK"

def get_neighbors(r: int, c: int, size: int) -> List[Tuple[int, int]]:
    """
    Returns list of adjacent (row, col) coordinates within the board.
    """
    neighbors = []
    if r > 0:
        neighbors.append((r - 1, c))
    if r < size - 1:
        neighbors.append((r + 1, c))
    if c > 0:
        neighbors.append((r, c - 1))
    if c < size - 1:
        neighbors.append((r, c + 1))
    return neighbors

def find_group(stones: Dict[str, str], r: int, c: int, size: int) -> Set[Tuple[int, int]]:
    """
    Finds all connected stones of the same color starting at (r, c).
    """
    key = f"{r}_{c}"
    color = stones.get(key)
    if not color:
        return set()

    visited = set()
    queue = [(r, c)]

    while queue:
        curr = queue.pop(0)
        if curr in visited:
            continue
        visited.add(curr)

        for nr, nc in get_neighbors(curr[0], curr[1], size):
            nkey = f"{nr}_{nc}"
            if stones.get(nkey) == color and (nr, nc) not in visited:
                queue.append((nr, nc))

    return visited

def count_liberties(stones: Dict[str, str], group: Set[Tuple[int, int]], size: int) -> Set[Tuple[int, int]]:
    """
    Finds the set of empty spaces adjacent to the group of stones.
    """
    liberties = set()
    for gr, gc in group:
        for nr, nc in get_neighbors(gr, gc, size):
            nkey = f"{nr}_{nc}"
            if nkey not in stones:
                liberties.add((nr, nc))
    return liberties
