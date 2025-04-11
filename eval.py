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

def main(epochs: int = 100):
    """
    Eval script I use to count how many times a different agent wins.
    :return: A breakdown of the number of times the minimax vs expectimax agent wins.
    """
    win_count = {}
    turn_counts = {}
    stats = {
        "Player 1": {
            "win": {
                "settlements": [],
                "cities": [],
                "roads": [],
                "points": []
            },
            "loss": {
                "settlements": [],
                "cities": [],
                "roads": [],
                "points": []
            }
        },
        "Player 2": {
            "win": {
                "settlements": [],
                "cities": [],
                "roads": [],
                "points": []
            },
            "loss": {
                "settlements": [],
                "cities": [],
                "roads": [],
                "points": []
            }
        }
    }

    for epoch in range(epochs):
        print(f"-- Epoch {epoch} --")
        winner, turns, game = run_game()

        # Track stats based on whether the player won or lost.
        for player in game.players:
            result = "win" if winner and player.id == winner.id else "loss"
            stats[player.id][result]["settlements"].append(player.settlements)
            stats[player.id][result]["cities"].append(player.cities)
            stats[player.id][result]["roads"].append(len(player.roads))
            stats[player.id][result]["points"].append(player.points)

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

    print("\n\n-- WIN COUNTS --")
    print(win_count)

    print("\n\n-- AVERAGE TURNS TO WIN --")
    for player_id, turns in turn_counts.items():
        avg_turns = sum(turns) / len(turns)
        print(f"{player_id}: {avg_turns:.2f} turns")

    print("\n\n-- AVERAGE STATS --")
    for player_id in stats:
        print(f"\n{player_id} Stats:")

        win_stats = stats[player_id]["win"]
        if win_stats["points"]:
            win_count = len(win_stats["points"])
            print(f"  When Winning ({win_count} games):")
            print(f"    Settlements: {sum(win_stats['settlements'])/win_count:.2f}")
            print(f"    Cities: {sum(win_stats['cities'])/win_count:.2f}")
            print(f"    Roads: {sum(win_stats['roads'])/win_count:.2f}")
            print(f"    Points: {sum(win_stats['points'])/win_count:.2f}")
        else:
            print("  When Winning: No wins")

        loss_stats = stats[player_id]["loss"]
        if loss_stats["points"]:
            loss_count = len(loss_stats["points"])
            print(f"  When Losing ({loss_count} games):")
            print(f"    Settlements: {sum(loss_stats['settlements'])/loss_count:.2f}")
            print(f"    Cities: {sum(loss_stats['cities'])/loss_count:.2f}")
            print(f"    Roads: {sum(loss_stats['roads'])/loss_count:.2f}")
            print(f"    Points: {sum(loss_stats['points'])/loss_count:.2f}")
        else:
            print("  When Losing: No losses")

if __name__ == '__main__':
    main()