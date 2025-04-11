import sys
from agent import Agent, MinimaxAgent, ExpectimaxAgent
from game import Game
from board import Board
from gameManager import GameManager

class HeadlessGameManager(GameManager):
    def __init__(self, game: Game):
        super().__init__(game)

    def roll_dice(self):
        """
        Handles rolling the die, and distributing cards.
        """
        roll_value = Game.roll()
        self.roll_result = roll_value
        print(f"Dice roll: {roll_value}")
        self.game.handle_roll(roll_value)

    def place_initial_settlement(self, location):
        """
        Handles initial settlement placement.
        """
        player = self.game.current_player
        if super().place_initial_settlement(location):
            print(f"{player.id} built initial settlement")
            return True
        return False

    def place_initial_road(self, location):
        """
        Handles initial road placement.
        """
        player = self.game.current_player
        if super().place_initial_road(location):
            print(f"{player.id} built initial road")
            return True
        return False

    def build(self, structure_type, location):
        """
        Handles building a structure during the main game.
        """
        structure = super().build(structure_type, location)
        if structure:
            print(f"{self.game.current_player.id} built {structure_type}")

        if self.winner and self.game_over:
            print(f"GAME OVER! {self.winner.id} wins!")
            
        return structure

    def run(self):
        """
        The main game loop for headless execution.
        :returns The winner and number of turns.
        """
        # Set a maximum turn limit to prevent infinite loops.
        max_turns = 1000
        turn_count = 0
        
        while turn_count < max_turns:
            if self.winner:
                break

            # AI player.
            if hasattr(self.game.current_player, 'get_action'):
                agent: Agent = self.game.current_player
                action = agent.get_action(self.game)
                self.handle_agent(action)
                turn_count += 1
            else:
                assert False, "Must be AI player"
        
        # If we hit the turn limit without a winner.
        if turn_count >= max_turns and not self.winner:
            return None, max_turns
            
        return self.winner, turn_count

def start_headless_game():
    """
    Creates players, board, and starts a headless game.
    """
    player1 = MinimaxAgent("Player 1", (51, 93, 184))
    player2 = ExpectimaxAgent("Player 2", (184, 51, 71))
    board = Board.create_default_board()
    game = Game(board, [player1, player2])

    headless = HeadlessGameManager(game)
    headless.run()

if __name__ == "__main__":
    start_headless_game()