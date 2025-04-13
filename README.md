# Catan Search Agent
## Tl;DR
This project implements a simplified version of the Settlers of Catan board game with AI agents that use Minimax and Expectimax search algorithms to make decisions. The game can be played in GUI mode for visualization or headless mode for faster evaluation and comparison of agent performance.

## How to Run

### GUI Mode
To run the game with a graphical interface where you can watch AI agents play against each other:

```bash
python main.py
```

This will launch a pygame window showing the game board, with Minimax and Expectimax agents competing against each other.

### Headless Mode
To run the game without a graphical interface (much faster):

```bash
python headlessGameManager.py
```

This will run a single game between AI agents and output the results to the console.

### Evaluations
To run multiple games and evaluate agent performance:

```bash
python eval.py
```

By default, this runs 100 games between the agents and provides statistics including:
- Win counts for each agent
- Average turns to win
- Average stats for settlements, cities, roads, and points

You can modify the number of evaluation games by changing the number of runs in the file.

## Important Files
- `agent.py`: Implementation of AI agents (Minimax and Expectimax)
- `game.py`: Core game logic and state management
- `board.py`: Board representation and setup
- `guiGameManager.py`: Graphical interface for the game
- `headlessGameManager.py`: Console-based game manager for fast simulations
- `eval.py`: Evaluation script to compare agent performance