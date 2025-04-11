from random import shuffle

from action import NoneAction
from game import Game
from player import Player

class Agent(Player):
    def __init__(self, name: str, color: (int, int, int)):
        super().__init__(name, color)

    def get_action(self, game: Game):
        raise NotImplementedError

    def evaluation_function(self, game: Game):
        raise NotImplementedError

class MultiAgent(Agent):
    def __init__(self, name: str, color: (int, int, int), max_depth: int):
        super().__init__(name, color)
        self.max_depth = max_depth

    def evaluation_function(self, game: Game):
        player = next((player for player in game.players if player.id == self.id), None)
        score = 0

        # Having double the roads (or more) means a settlement can be built.
        # Extra points for getting to build a settlement.
        if player.roads >= player.settlements * 2:
            score += player.roads * 0.75
        else:
            score += player.roads * 0.5

        # Value adding new resources.
        for resource, value in player.resource_connections.items():
            # Limit to 1 so it tries to get new resources.
            score += min(min([value for value in player.resource_connections.values()]) + 1, value) * 2


        # Add extra points for cities.
        score += player.cities * 4

        # Extra (but less) points for settlements.
        score += player.settlements * 2

        return score

class MinimaxAgent(MultiAgent):
    def __init__(self, name: str, color: (int, int, int)):
        super().__init__(name, color, 2)

    def minimax(self, game: Game, current_depth):
        if game.game_winner() or current_depth >= self.max_depth:
            return None, self.evaluation_function(game)

        next_depth = current_depth + 1

        if game.current_player.id == self.id:
            return self.max_val(game, game.current_player, next_depth)
        else:
            return self.min_val(game, game.current_player, next_depth)

    def max_val(self, game, current_player, next_depth):
        best_action = None
        best_score = float('-inf')
        actions = game.get_legal_actions(current_player)
        shuffle(actions)

        for action in actions:
            successor = game.generate_successor(current_player, action)
            _, score = self.minimax(successor, next_depth)

            if score > best_score:
                best_score = score
                best_action = action

        return best_action, best_score

    def min_val(self, game, current_player, next_depth):
        best_action = None
        best_score = float('inf')
        actions = game.get_legal_actions(current_player)

        for action in actions:
            successor = game.generate_successor(current_player, action)
            _, score = self.minimax(successor, next_depth)

            if score < best_score:
                best_score = score
                best_action = action

        return best_action, best_score

    def get_action(self, game: Game):
        action, _ = self.minimax(game, 0)
        return action or NoneAction()
