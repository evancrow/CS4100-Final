from tile import Tile

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

HEX_SIZE = 50
INTERSECTION_SIZE = 10
EDGE_WIDTH = 6

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)

# Resource Values.
# Kinda estimates that I gave based on when I play.
# Brick very important early in game.
RESOURCE_VALUES = {
    Tile.Type.BRICK: 3,
    Tile.Type.ORE: 3,
    Tile.Type.GRAIN: 2,
    Tile.Type.FOREST: 2,
    Tile.Type.PASTURE: 1,
    Tile.Type.DESERT: 0
}

DEFAULT_TILE_RATIO = {
    Tile.Type.FOREST: 4,
    Tile.Type.PASTURE: 4,
    Tile.Type.GRAIN: 4,
    Tile.Type.ORE: 3,
    Tile.Type.BRICK: 3,
}

DEFAULT_ROLL_RATIOS = {
    2: 1,
    3: 2,
    4: 2,
    5: 2,
    6: 2,
    8: 2,
    9: 2,
    10: 2,
    11: 2,
    12: 1
}