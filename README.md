# Quidditch Cup Simulation

This project provides a simple command-line simulation of Quidditch matches and tournaments written in Python. You can create teams, manage players, run individual matches, or stage full tournaments with randomly generated countries.

## Features

- **Player and Team management** – Create teams manually or generate random ones.
- **Random match factors** – Weather, injuries, crowd support, referee bias, and more influence the outcome of matches.
- **Match simulation** – Play out a single match with detailed highlights and statistics.
- **Tournament formats** – Run a quick 4-team round robin for Hogwarts houses or a World Cup style event with 16/32/64 teams picked from `world_population.csv`.

## Getting Started

1. Install Python 3 (no external packages are required).
2. Clone this repository and open a terminal inside the project directory.
3. Run the CLI with:

```bash
python3 main.py
```

Follow the menu prompts to create teams, save/load them, simulate matches, or start tournaments.

### Example

To simulate a Hogwarts House Cup:

1. Choose **Play a tournament** from the menu.
2. Enter `4` when asked for the number of teams.
3. Watch the simulated matches and view the standings.

## Project Structure

- `models.py` – Definitions of `Player` and `Team` with helper functions for random creation.
- `simulation.py` – Core logic for simulating a match including weather effects and special events.
- `random_factors.py` – Implements the random factors that modify player skills and match flow.
- `tournaments.py` – Functions for four-team and World Cup style tournaments.
- `world_population.csv` – Country data used to randomly select teams for large tournaments.
- `DenSKo.json` – Example JSON file containing two premade teams.
- `main.py` – Command-line interface that ties everything together.

## Saving and Loading Teams

Teams can be saved to a JSON file for reuse:

1. Choose **Save teams to file** and provide a filename (e.g., `teams.json`).
2. Later, choose **Load teams from file** to restore them.

## License

This project is provided for educational purposes. No official affiliation with the Harry Potter franchise is intended.