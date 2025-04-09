from board import Board
from player import Player
from structure import Structure
from card import Card
from tile import Tile
from location import Location
import random
from typing import List, Optional

VICTORY_POINTS_TO_WIN = 10

class Game:
    def __init__(self, board: Board, players: List[Player]):
        assert len(players) > 1

        self.board = board
        self.players = players

        random.shuffle(self.players)
        
        self.current_player_index = 0
        self.current_player = players[0]
        self.last_settlement_placed = None
        self.first_round_settlements = { player.id: [] for player in players }

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

    def build(self, structure_type: Structure.Type, location: Location) -> bool:
        """
        Enables a player to build a structure.
        :param structure_type: The type of structure to build.
        :param location: The location where to build.
        :return: True if built, false if the structure cannot be built.
        """
        player = self.current_player

        # Check if player has the required resources.
        if not player.can_make_structure(Structure(structure_type, player)):
            print("Not enough resources")
            return False

        game_element = self.board.get_at_location(location)
        if game_element is None:
            print("Could not find game element")
            return False

        if structure_type == Structure.Type.ROAD:
            if location.is_edge():
                edge = game_element
                if self.board.can_build_road(player, edge):
                    player.made_structure(structure_type)
                    edge.build(player)
                    return True

        elif structure_type == Structure.Type.SETTLEMENT:
            if location.is_intersection():
                intersection = game_element
                if self.board.can_build_structure(player, intersection):
                    player.made_structure(structure_type)
                    intersection.build_structure(structure_type, player)
                    return True

        elif structure_type == Structure.Type.CITY:
            if location.is_intersection():
                intersection = game_element
                if intersection.can_upgrade_to_city(player):
                    player.made_structure(structure_type)
                    intersection.build_structure(structure_type, player)
                    return True
        
        return False

    def end_turn(self):
        """
        Ends the current player's turn and move to the next player.
        :return:
        """
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]

    def game_winner(self) -> Optional[Player]:
        """
        Checks if any of the players won the game.
        :return: The winning player or None.
        """
        for player in self.players:
            if player.points >= VICTORY_POINTS_TO_WIN:
                return player
        
        return None
