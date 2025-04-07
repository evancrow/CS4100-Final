from board import Board
from tile import Tile

COLORS = {
    Tile.Type.FOREST: "\033[42m",  # Green background
    Tile.Type.PASTURE: "\033[102m",  # Light green background
    Tile.Type.GRAIN: "\033[43m",  # Yellow background
    Tile.Type.BRICK: "\033[41m",  # Red background
    Tile.Type.ORE: "\033[100m",  # Gray background
    Tile.Type.DESERT: "\033[47m",  # White background
}
RESET = "\033[0m"  # Reset color
BLACK_TEXT = "\033[30m"  # Black text for contrast

def print_board(board: Board):
    """
    Print the board state in the terminal as hexagons with numbers in the middle.
    
    Args:
        board: The board to print
    """
    
    # Find the grid bounds
    min_q = min(q for q, _ in board.grid.keys())
    max_q = max(q for q, _ in board.grid.keys())
    min_r = min(r for _, r in board.grid.keys())
    max_r = max(r for _, r in board.grid.keys())
    
    # Calculate the width of each hex
    hex_width = 7
    
    # Print the top half of each row of hexagons
    for r in range(min_r, max_r + 1):
        # Add indentation based on row
        indent = " " * (r - min_r + 2) * 3
        print(indent, end="")
        
        # Print the top of the hexagons
        for q in range(min_q, max_q + 1):
            if (q, r) in board.grid:
                tile = board.grid[(q, r)]
                color = COLORS[tile.type]
                print(f"{color}  ____  {RESET}", end="")
            else:
                print("       ", end="")
        print()
        
        # Print the number in the middle
        indent = " " * (r - min_r + 2) * 3
        print(indent, end="")
        
        for q in range(min_q, max_q + 1):
            if (q, r) in board.grid:
                tile = board.grid[(q, r)]
                color = COLORS[tile.type]
                if tile.type == Tile.Type.DESERT:
                    num = "  D"
                elif tile.roll < 10:
                    num = f"  {tile.roll}"
                else:
                    num = f" {tile.roll}"
                print(f"{color} /{BLACK_TEXT}{num} {RESET}{color}\\ {RESET}", end="")
            else:
                print("       ", end="")
        print()
        
        # Print the bottom of the hexagons
        indent = " " * (r - min_r + 2) * 3
        print(indent, end="")
        
        for q in range(min_q, max_q + 1):
            if (q, r) in board.grid:
                tile = board.grid[(q, r)]
                color = COLORS[tile.type]
                print(f"{color} \\____/ {RESET}", end="")
            else:
                print("       ", end="")
        print()

def print_board_with_structures(board: Board):
    """
    Print the board state including settlements, cities, and roads.
    
    Args:
        board: The board to print
    """
    print_board(board)
    
    # Print intersections with structures (settlements/cities)
    print("\nStructures:")
    for coord, intersection in board.intersections.items():
        if intersection.structure:
            structure_type = intersection.structure.type
            owner = intersection.structure.owner
            print(f"  {coord}: {structure_type.value} (Player {owner.id})")
    
    # Print edges with roads
    print("\nRoads:")
    for edge_coords, edge in board.edges.items():
        if edge.road:
            owner = edge.road.owner
            print(f"  {edge_coords}: Road (Player {owner.id})")