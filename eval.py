from agent import MinimaxAgent, ExpectimaxAgent
from board import Board
from game import Game
from headlessGameManager import HeadlessGameManager

def run_game():
    """
    Runs a headless game and returns the winner, turns taken, and game stats.
    :return: Tuple of (winning player, turns, game)
    """
    # If you change this, make sure to change print statements below.
    player1 = MinimaxAgent("Player 1", (51, 93, 184))
    player2 = ExpectimaxAgent("Player 2", (184, 51, 71))
    board = Board.create_default_board()
    game = Game(board, [player1, player2])

    headless = HeadlessGameManager(game)
    winner, turns = headless.run()
    
    return winner, turns, game

def main(epochs: int = 5):
    """
    Eval script I use to count how many times a different agent wins.
    :return: A breakdown of the number of times the minimax vs expectimax agent wins.
    """
    win_count = {}
    turn_counts = {}
    stats = {
        "Player 1": {
            "settlements": [],
            "cities": [],
            "roads": [],
            "points": []
        },
        "Player 2": {
            "settlements": [],
            "cities": [],
            "roads": [],
            "points": []
        }
    }

    for epoch in range(epochs):
        print(f"-- Epoch {epoch} --")
        winner, turns, game = run_game()

        for player in game.players:
            stats[player.id]["settlements"].append(player.settlements)
            stats[player.id]["cities"].append(player.cities)
            stats[player.id]["roads"].append(len(player.roads))
            stats[player.id]["points"].append(player.points)

        if not winner:
            if "None" in win_count:
                win_count["None"] += 1
            else:
                win_count["None"] = 1
        else:
            player_id = winner.id
            if player_id in win_count:
                win_count[player_id] += 1
                turn_counts[player_id].append(turns)
            else:
                win_count[player_id] = 1
                turn_counts[player_id] = [turns]

        print("\n\n")

    print("\n-- AGENT TYPE --")
    # If players ever change, should update them here.
    # Would be better to make this adapt but too lazy to program it.
    print("Player 1:", "Minimax")
    print("Player 2:", "Expectimax")

    print("-- WIN COUNTS --")
    print(win_count)

    print("\n-- AVERAGE TURNS TO WIN --")
    for player_id, turns in turn_counts.items():
        avg_turns = sum(turns) / len(turns)
        print(f"{player_id}: {avg_turns:.2f} turns")

    print("\n-- AVERAGE STATS --")
    for player_id in stats:
        print(f"\n{player_id} Stats:")
        print(f"  Settlements: {sum(stats[player_id]['settlements'])/epochs:.2f}")
        print(f"  Cities: {sum(stats[player_id]['cities'])/epochs:.2f}")
        print(f"  Roads: {sum(stats[player_id]['roads'])/epochs:.2f}")
        print(f"  Points: {sum(stats[player_id]['points'])/epochs:.2f}")

if __name__ == '__main__':
    main()