from action import Build, NoneAction, Action
from structure import Structure
from game import Game
from card import Card
from constants import *

class GameManager:
    def __init__(self, game: Game):
        self.game = game
        self.roll_result = None
        self.game_over = False
        self.winner = None

        self.intersection_coords = {}
        self.edge_coords = {}

        self.awaiting_settlement = True
        self.awaiting_road = False

    def end_turn(self):
        """
        Called whenever the user ends their turn.
        """
        self.game.end_turn()

        if self.game.phase is Game.Phase.NORMAL:
            self.roll_dice()

        self.game.turn_counter += 1

    def roll_dice(self):
        """
        Handles rolling the die, and distributing cards.
        """
        roll_value = Game.roll()
        self.roll_result = roll_value
        self.game.handle_roll(roll_value)

    def place_initial_settlement(self, location):
        """
        Helps the user place a settlement before the main game starts.
        :param location: The place on board to build at.
        """
        intersection = self.game.board.get_at_location(location)

        if not intersection or intersection.structure is not None:
            return False

        for adj_intersection in intersection.adjacent_intersections:
            if adj_intersection.structure is not None:
                return False

        self.game.build(Structure.Type.SETTLEMENT, location)

        if self.game.turn_counter < 3:
            self.game.first_round_settlements[self.game.current_player.id].append(intersection)

        self.game.last_settlement_placed = intersection
        self.awaiting_settlement = False
        self.awaiting_road = True
        self.game.phase = Game.Phase.ROAD
        return True

    def place_initial_road(self, location):
        """
        Helps a user place a road before the main game starts and after a settlement.
        :param location: The location to build on.
        """
        edge = self.game.board.get_at_location(location)

        if not edge or edge.road is not None:
            return False

        is_connected = False
        if self.game.last_settlement_placed:
            if edge.start == self.game.last_settlement_placed or edge.end == self.game.last_settlement_placed:
                is_connected = True

        if not is_connected:
            return False

        self.game.build(Structure.Type.ROAD, location)

        if self.game.turn_counter > 2:
            self.distribute_initial_resources()

        self.awaiting_road = False
        self.awaiting_settlement = True

        if self.game.turn_counter <= len(self.game.players):
            # If we've gone through all players, switch to second round.
            if self.game.turn_counter != len(self.game.players):
                self.game.current_player_index = (self.game.current_player_index + 1) % len(self.game.players)
                self.game.current_player = self.game.players[self.game.current_player_index]

            self.game.phase = Game.Phase.SETTLEMENT
        else:
            # Move to previous player in reverse order.
            self.game.current_player_index = (self.game.current_player_index - 1) % len(self.game.players)
            self.game.current_player = self.game.players[self.game.current_player_index]

            # If we've gone through all players, switch to main game.
            if self.game.turn_counter == 4:
                self.game.phase = Game.Phase.NORMAL
                self.game.current_player_index = 0
                self.game.current_player = self.game.players[0]
                self.roll_dice()
            else:
                self.game.phase = Game.Phase.SETTLEMENT

        self.game.turn_counter += 1
        return True

    def distribute_initial_resources(self):
        """
        After the user places their second settlement, give them the resources.
        """
        if self.game.last_settlement_placed:
            for tile in self.game.last_settlement_placed.adjacent_tiles:
                if tile.type != Tile.Type.DESERT:
                    self.game.current_player.add_card(Card(tile.type))

    def build(self, structure_type, location):
        """
        Handles building a structure during the main game.
        :param structure_type: The type of structure to build.
        :param location: The location to build at.
        """
        structure = self.game.build(structure_type, location)

        winner = self.game.game_winner()
        if winner and not self.game_over:
            self.game_over = True
            self.winner = winner
        
        return structure

    def handle_agent(self, action: Action):
        """
        Handles actions taken by the agent.
        :param action: The action the agent wants to take.
        """
        match action:
            case Build(type=t, location=loc):
                match self.game.phase:
                    case Game.Phase.NORMAL:
                        self.build(t, loc)
                        self.end_turn()
                    case Game.Phase.SETTLEMENT:
                        self.place_initial_settlement(loc)
                    case Game.Phase.ROAD:
                        self.place_initial_road(loc)
            case NoneAction():
                self.end_turn()

    def run(self):
        """
        The main game loop. To be implemented by subclasses.
        """
        raise NotImplementedError