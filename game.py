import random
import copy
from enum import Enum
from typing import List, Optional

from action import Action, NoneAction, Build
from board import Board
from player import Player
from structure import Structure
from card import Card
from tile import Tile
from location import Location
from intersection import Intersection

VICTORY_POINTS_TO_WIN = 10

class Game:
    class Phase(Enum):
        # First round placements.
        SETTLEMENT = "Settlement"
        ROAD = "Road"
        # Regular gameplay.
        NORMAL = "Normal"

    def __init__(self, board: Board, players: List[Player]):
        assert len(players) > 1

        self.board = board
        self.players = players

        random.shuffle(self.players)

        self.last_settlement_placed: Optional[Intersection] = None
        self.phase = Game.Phase.SETTLEMENT
        self.turn_counter = 1
        self.current_player_index = 0
        self.current_player = players[0]
        self.first_round_settlements = { player.id: [] for player in players }

    # -- Roll Methods --
    @staticmethod
    def roll() -> int:
        """
        Rolls the die
        :return: The roll.
        """
        return random.randint(1, 6) + random.randint(1, 6)

    def handle_roll(self, roll: int):
        """
        Distributes cards to players.
        :param roll: The die number rolled.
        :return: Nothing.
        """
        if roll == 7:
            # In the real game this is the robber.
            # At least for now, not implementing to keep it simple.
            pass
        else:
            # Keep track of resources gained to print a summary
            resources_gained = {player.id: [] for player in self.players}
            
            for coord, tile in self.board.grid.items():
                if tile.roll == roll and tile.type != Tile.Type.DESERT:
                    for location, intersection in self.board.intersections.items():
                        # Check if the tile is a part of this intersection.
                        if tile in intersection.adjacent_tiles and intersection.structure is not None:
                            # Give resources to the player who owns a structure on this intersection.
                            # Settlement, 1 card.
                            # City, 2 cards.
                            player = intersection.structure.owner

                            if intersection.structure.type == Structure.Type.SETTLEMENT:
                                player.add_card(Card(tile.type))
                                resources_gained[player.id].append(tile.type)

                            elif intersection.structure.type == Structure.Type.CITY:
                                player.add_card(Card(tile.type))
                                player.add_card(Card(tile.type))
                                resources_gained[player.id].append(tile.type)
                                resources_gained[player.id].append(tile.type)

    # -- Building --
    def build(self, structure_type: Structure.Type, location: Location) -> bool:
        """
        Enables a player to build a structure.
        :param structure_type: The type of structure to build.
        :param location: The location where to build.
        :return: True if built, false if the structure cannot be built.
        """
        player = self.current_player
        require_resources = self.phase == Game.Phase.NORMAL

        # Check if player has the required resources.
        if require_resources and not player.can_make_structure(Structure(structure_type, player)):
            return False

        game_element = self.board.get_at_location(location)
        if game_element is None:
            return False

        if structure_type == Structure.Type.ROAD:
            if location.is_edge():
                edge = game_element
                if self.board.can_build_road(player, edge):
                    edge.build(player)
                    player.made_structure(structure_type, require_resources, None, edge)
                    return True

        elif structure_type == Structure.Type.SETTLEMENT:
            if location.is_intersection():
                intersection = game_element
                if self.board.can_build_structure(player, intersection, self.phase == Game.Phase.SETTLEMENT):
                    intersection.build_structure(structure_type, player)
                    player.made_structure(structure_type, require_resources, intersection)
                    return True

        elif structure_type == Structure.Type.CITY:
            if location.is_intersection():
                intersection = game_element
                if intersection.can_upgrade_to_city(player):
                    intersection.build_structure(structure_type, player)
                    player.made_structure(structure_type, require_resources, intersection)
                    return True
        
        return False

    # TODO: Add DP here.
    def get_legal_actions(self, player: Player) -> List[Action]:
        actions = []

        # Check all the roads a player can build.
        if (self.phase == Game.Phase.ROAD or
            (player.can_make_structure_of_type(Structure.Type.ROAD) and self.phase == Game.Phase.NORMAL)):
            if self.phase == Game.Phase.ROAD and self.last_settlement_placed is not None:
                # In the initial placement phase, only suggest edges connected to the last settlement.
                for edge_loc, edge in self.board.edges.items():
                    if (edge.start == self.last_settlement_placed or 
                        edge.end == self.last_settlement_placed) and edge.road is None:
                        actions.append(Build(Structure.Type.ROAD, edge_loc))
            else:
                for edge_loc, edge in self.board.edges.items():
                    if self.board.can_build_road(player, edge):
                        actions.append(Build(Structure.Type.ROAD, edge_loc))

        # Check all the settlements the player can build.
        if (self.phase == Game.Phase.SETTLEMENT or
            (player.can_make_structure_of_type(Structure.Type.SETTLEMENT) and self.phase == Game.Phase.NORMAL)):
            for location, intersection in self.board.intersections.items():
                if self.board.can_build_structure(player, intersection, self.phase == Game.Phase.SETTLEMENT):
                    actions.append(Build(Structure.Type.SETTLEMENT, location))

        # Check all the cities a player can build.
        if player.can_make_structure_of_type(Structure.Type.CITY) and self.phase == Game.Phase.NORMAL:
            for location, intersection in self.board.intersections.items():
                if intersection.can_upgrade_to_city(player):
                    actions.append(Build(Structure.Type.CITY, location))

        if self.phase == Game.Phase.NORMAL:
            actions.append(NoneAction())

        return actions

    # -- Turn --
    def end_turn(self):
        """
        Ends the current player's turn and move to the next player.
        :return:
        """
        self.next_player(True)

    def next_player(self, set_value: bool = False) -> Player:
        next_index = (self.current_player_index + 1) % len(self.players)

        if set_value:
            self.current_player_index = next_index
            self.current_player = self.players[next_index]

        return self.players[next_index]

    # -- End State --
    def game_winner(self) -> Optional[Player]:
        """
        Checks if any of the players won the game.
        :return: The winning player or None.
        """
        for player in self.players:
            if player.points >= VICTORY_POINTS_TO_WIN:
                return player
        
        return None

    # -- Generating Successors --
    def generate_successor(self, player: Player, action: Action):
        deep_copy = copy.deepcopy(self)
        deep_copy.handle_roll(Game.roll())
        match action:
            case Build(type=t, location=loc):
                deep_copy.build(t, loc)
            case NoneAction():
                pass

        deep_copy.end_turn()

        return deep_copy