from random import shuffle

from action import NoneAction
from game import Game
from tile import Tile
from player import Player
from constants import RESOURCE_VALUES
from util import estimate_roll_probability

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
        """
        Evaluates the current game state for this (the agent). Higher is better (for the agent).
        :param game: The game state to check.
        :return: The score.
        """
        player = next((player for player in game.players if player.id == self.id), None)
        score = 0

        # Value adding new resources.
        for resource, value in player.resource_connections_probability.items():
            # Encourage getting all resources.
            if value == 0:
                score -= 10

            # Discourage desert.
            if resource == Tile.Type.DESERT and value > 0:
                score -= 100

            # Limit to the min resource so it tries to get more of smallest resource.
            score += min(min([value for value in player.resource_connections_probability.values()]) + 1, value) * 2

        # Add extra points for cities.
        score += player.cities * 20

        # Extra (but less) points for settlements.
        score += player.settlements * 10

        # Reward consecutive roads towards valuable resources
        consecutive_road_bonus = self._evaluate_roads_towards_resources(player) * 0.75
        score += consecutive_road_bonus

        return score

    def _evaluate_roads_towards_resources(self, player: Player):
        """
        Evaluates how good a chain of roads is. This prevents the agent from building random roads to nowhere.
        It encourages building roads in a chain towards valuable resources.

        :param player: The player to check roads for.
        :return: The score of the roads.
        """
        player_roads = player.roads
        
        # Use a DFS search to check where the roads are going.
        visited_roads = set()
        road_chains = []
        
        for road in player_roads:
            if road in visited_roads:
                continue
                
            visited_roads.add(road)
            current_chain = [road]
            self._expand_road_chain(current_chain, player_roads, visited_roads)

            if len(current_chain) > 1:
                road_chains.append(current_chain)

        total_bonus = 0
        for chain in road_chains:
            length = len(chain)
            resources_at_ends = set()

            # Check start/end of chain.
            for end_idx in [0, -1]:
                road = chain[end_idx]

                for intersection in [road.start, road.end]:
                    for tile in intersection.adjacent_tiles:
                        resources_at_ends.add(tile.type)

            chain_resource_value = sum(RESOURCE_VALUES[res] for res in resources_at_ends)
            chain_bonus = length * chain_resource_value
            total_bonus += chain_bonus
        
        return total_bonus

    def _expand_road_chain(self, current_chain, roads, visited_roads):
        """
        Uses DFS search to find all the connected roads in a chain.
        :param current_chain: The chain to check.
        :param roads: Possible roads (graph).
        :param visited_roads: All roads already checked.
        :return:
        """
        current_road = current_chain[-1]
        endpoints = [current_road.start, current_road.end]
        
        for endpoint in endpoints:
            for road in roads:
                if road in visited_roads:
                    continue
                    
                # Check if this road is connected to the current endpoint.
                if road.start == endpoint or road.end == endpoint:
                    visited_roads.add(road)
                    current_chain.append(road)
                    
                    # Recursively expand from this new road.
                    self._expand_road_chain(current_chain, roads, visited_roads)

# -- MINIMAX -- #
class MinimaxAgent(MultiAgent):
    def __init__(self, name: str, color: (int, int, int)):
        super().__init__(name, color, 2)

    def minimax(self, game: Game, current_depth):
        if game.game_winner() or current_depth >= self.max_depth:
            return None, self.evaluation_function(game)

        next_depth = current_depth + 1
        actions = game.get_legal_actions(game.current_player)
        shuffle(actions)

        if game.current_player.id == self.id:
            return self.max_val(game, game.current_player, actions, next_depth)
        else:
            return self.min_val(game, game.current_player, actions, next_depth)

    def max_val(self, game, current_player, actions, next_depth):
        best_action = None
        best_score = float('-inf')

        for action in actions:
            successor = game.generate_successor(current_player, action)
            _, score = self.minimax(successor, next_depth)

            if score > best_score:
                best_score = score
                best_action = action

        return best_action, best_score

    def min_val(self, game, current_player, actions, next_depth):
        best_action = None
        best_score = float('inf')

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

# -- EXPECTIMAX --#
class ExpectimaxAgent(MultiAgent):
    def __init__(self, name: str, color: (int, int, int)):
        super().__init__(name, color, 1)

    def expectimax(self, game: Game, current_depth: int):
        """
        Expectimax function to calculate the expected value of a game.

        :param game: The current game state.
        :param current_depth: The current depth.
        :return: The EV.
        """
        if game.game_winner() or current_depth >= self.max_depth:
            return None, self.evaluation_function(game)

        next_depth = current_depth + 1
        actions = game.get_legal_actions(game.current_player)
        shuffle(actions)

        if game.current_player.id == self.id:
            return self.max_val(game, game.current_player, actions, next_depth)
        else:
            return self.min_val(game, game.current_player, actions, next_depth)

    def max_val(self, game, current_player, actions, next_depth):
        best_action = None
        best_score = float('-inf')

        for action in actions:
            total = 0
            for roll in range(1, 13):
                prob = estimate_roll_probability(roll)

                successor = game.generate_successor(current_player, action, roll)
                _, score = self.expectimax(successor, next_depth)
                total += prob * score

            if total > best_score:
                best_score = total
                best_action = action

        return best_action, best_score

    def min_val(self, game, current_player, actions, next_depth):
        best_action = None
        best_score = float('inf')

        for action in actions:
            total = 0
            for roll in range(2, 13):
                prob = estimate_roll_probability(roll)

                successor = game.generate_successor(current_player, action, roll)
                _, score = self.expectimax(successor, next_depth)
                total += prob * score

            if total < best_score:
                best_score = total
                best_action = action

        return best_action, best_score

    def get_action(self, game: Game):
        action, _ = self.expectimax(game, 0)
        return action or NoneAction()