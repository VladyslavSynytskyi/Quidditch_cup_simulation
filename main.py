import random
import json
from models import Player, Team, create_random_team
from simulation import simulate_match
from tournaments import tournament_4_teams, run_tournament

def save_teams(teams):
    filename = input("Enter filename to save teams (e.g., teams.json): ").strip()
    if not filename:
        print("Invalid filename.")
        return
    data = [team.to_dict() for team in teams.values()]
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Teams saved to {filename}")

def load_teams():
    filename = input("Enter filename to load teams from (e.g., teams.json): ").strip()
    if not filename:
        print("Invalid filename.")
        return {}
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        teams = {}
        for team_data in data:
            team = Team.from_dict(team_data)
            teams[team.name] = team
        print(f"Loaded {len(teams)} teams from {filename}")
        return teams
    except FileNotFoundError:
        print(f"No file named {filename} found.")
        return {}

def print_menu():
    print("\n=== Quidditch Simulation CLI ===")
    print("1. Create a new team")
    print("2. Add player to a team")
    print("3. View team info")
    print("4. List all teams")
    print("5. Create a random team")
    print("6. Save teams to file")
    print("7. Load teams from file")
    print("8. Simulate a match")
    print("9. Play a tournament")
    print("0. Exit")

def main():
    teams = {}

    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            team_name = input("Enter team name: ").strip()
            if team_name in teams:
                print("Team already exists!")
            else:
                teams[team_name] = Team(team_name)
                print(f"Team '{team_name}' created.")
                add_random = input("Do you want to auto-create random players for this team? (y/n): ").strip().lower()
                if add_random == "y":
                    teams[team_name] = create_random_team(team_name)
                    print(f"Random team '{team_name}' created:")
                    print(teams[team_name])

        elif choice == "2":
            if not teams:
                print("No teams created yet.")
                continue
            team_name = input("Enter team name to add player to: ").strip()
            if team_name not in teams:
                print("Team does not exist!")
                continue
            team = teams[team_name]
            missing_roles = team.missing_roles()
            if not missing_roles:
                print("Team already has all roles filled.")
                continue
            print("Roles you can add (remaining slots):")
            for role, count in missing_roles.items():
                print(f"- {role}: {count} left")
            role = input("Enter player role: ").strip().title()
            if role not in missing_roles:
                print(f"Cannot add more {role}s.")
                continue
            player_name = input("Enter player name: ").strip()
            skill_choice = input("Random skill? (y/n): ").strip().lower()
            if skill_choice == "y":
                skill = random.randint(1, 10)
            else:
                try:
                    input_skill = int(input("Enter skill level (1-10): ").strip())
                    skill = input_skill if input_skill >= 1 and input_skill <= 10 else None
                    if not skill:
                        print("Skill should be between 1 and 10.")
                        continue
                except ValueError:
                    print("Please enter a number.")
                    continue
            idx = team.count_role(role) + 1
            player = Player(player_name or f"{role} {idx}", role, skill)
            if team.add_player(player):
                print(f"Added {player} to team '{team_name}'.")

        elif choice == "3":
            team_name = input("Enter team name: ").strip()
            if team_name in teams:
                print(teams[team_name])
            else:
                print("Team not found.")

        elif choice == "4":
            if teams:
                for name in teams:
                    print(f"- {name}")
            else:
                print("No teams created yet.")

        elif choice == "5":
            team_name = input("Enter new team name: ").strip()
            if team_name in teams:
                print("Team already exists!")
            else:
                teams[team_name] = create_random_team(team_name)
                print(f"Random team '{team_name}' created:")
                print(teams[team_name])

        elif choice == "6":
            save_teams(teams)

        elif choice == "7":
            teams = load_teams()

        elif choice == "8":
            if len(teams) < 2:
                print("You need at least two teams to simulate a match.")
                continue
            print("Available teams:")
            for name in teams:
                print(f"- {name}")
            team1_name = input("Enter name of Team 1: ").strip()
            team2_name = input("Enter name of Team 2: ").strip()
            if team1_name not in teams or team2_name not in teams:
                print("One or both teams not found.")
                continue
            if team1_name == team2_name:
                print("Choose two different teams.")
                continue
            team1 = teams[team1_name]
            team2 = teams[team2_name]
            if len(team1.players) != 7 or len(team2.players) != 7:
                print("Both teams must have 7 players.")
                continue
            simulate_match(team1, team2)

        elif choice == "9":
            try:
                number_of_teams = int(input("How many teams do you want to simulate? (4/16/32/64): ").strip())
            except ValueError:
                print("Please enter a valid number (4, 16, 32, or 64).")
                continue
            if number_of_teams not in [4, 16, 32, 64]:
                print("Invalid number of teams. Please enter 4, 16, 32, or 64.")
                continue
            if number_of_teams == 4:
                tournament_4_teams()
            else:
                run_tournament(number_of_teams)

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
