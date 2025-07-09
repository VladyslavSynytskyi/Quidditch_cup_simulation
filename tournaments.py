import csv
import random
from collections import defaultdict
from models import create_random_team
from simulation import simulate_match

TEAM_NAMES = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]

# Predefined round-robin schedule for 4 teams (indices)
SCHEDULE_INDICES = [
    (0, 1),
    (2, 3),
    (3, 1),
    (0, 2),
    (2, 1),
    (0, 3),
]

def create_default_teams():
    teams = {}
    for name in TEAM_NAMES:
        teams[name] = create_random_team(name)
    return teams

def init_results_table():
    table = {}
    for name in TEAM_NAMES:
        table[name] = {"points": 0, "scored": 0, "conceded": 0, "diff": 0}
    return table

def print_schedule(schedule, teams):
    print("\n--- Tournament Schedule ---")
    for i, (a, b) in enumerate(schedule, 1):
        print(f"{i}. {teams[a].name} vs {teams[b].name}")

def print_results_table(results):
    print("\n--- Tournament Standings ---")
    print("{:<12} {:<6} {:<8} {:<8} {:<8}".format("Team", "Points", "Scored", "Conceded", "Diff"))
    sorted_teams = sorted(results.items(), key=lambda x: (-x[1]["points"], -x[1]["diff"], -x[1]["scored"]))
    for name, stats in sorted_teams:
        print("{:<12} {:<6} {:<8} {:<8} {:<8}".format(name, stats["points"], stats["scored"], stats["conceded"], stats["diff"]))

def tournament_4_teams():
    print("Starting a 4-team Quidditch tournament!")
    teams = create_default_teams()
    results = init_results_table()
    schedule = [(TEAM_NAMES[a], TEAM_NAMES[b]) for (a, b) in SCHEDULE_INDICES]
    print_schedule(schedule, teams)
    print("\n--- Let the matches begin! ---")
    for match_num, (a, b) in enumerate(schedule, 1):
        input(f"\nPress Enter to simulate Match {match_num}: {a} vs {b}...")
        team1, team2 = teams[a], teams[b]
        print(f"\nPlayer skills for {team1.name}:")
        for p in team1.players:
            print(f"{p.name}: {p.skill}")
        print(f"\nPlayer skills for {team2.name}:")
        for p in team2.players:
            print(f"{p.name}: {p.skill}")
        # Simulate the match 
        print(f"\nSimulating: {a} vs {b}")
        # Capture scores 
        team1_score, team2_score, _, _ = simulate_match(team1, team2)
        # Decide points
        if team1_score > team2_score:
            results[a]["points"] += 1
        elif team2_score > team1_score:
            results[b]["points"] += 1
        else:
            results[a]["points"] += 0.5
            results[b]["points"] += 0.5
        # Goals for/against
        results[a]["scored"] += team1_score
        results[a]["conceded"] += team2_score
        results[b]["scored"] += team2_score
        results[b]["conceded"] += team1_score
        results[a]["diff"] = results[a]["scored"] - results[a]["conceded"]
        results[b]["diff"] = results[b]["scored"] - results[b]["conceded"]
        print_results_table(results)

    print("\n=== Final Standings ===")
    print_results_table(results)

# Load countries by continent
def load_countries_by_continent(filename):
    countries_by_continent = defaultdict(list)
    populations_by_continent = defaultdict(list)
    with open(filename, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            country = row['Country/Territory']
            continent = row['Continent']
            try:
                pop = int(row['2022 Population'].replace(',', ''))
            except:
                continue
            countries_by_continent[continent].append(country)
            populations_by_continent[continent].append(pop)
    return countries_by_continent, populations_by_continent

# Calculate how many to pick from each continent
def get_team_allocation(n_teams):
    allocation = {
        "Oceania": round(n_teams * 0.05),
        "North America": round(n_teams * 0.08),
        "South America": round(n_teams * 0.10),
        "Africa": round(n_teams * 0.12),
        "Asia": round(n_teams * 0.25)
    }
    # Rest goes to Europe
    total_allocated = sum(allocation.values())
    allocation["Europe"] = n_teams - total_allocated
    return allocation

# Sample countries per continent
def pick_random_teams_by_continent(n_teams, filename="world_population.csv"):
    countries_by_continent, populations_by_continent = load_countries_by_continent(filename)
    allocation = get_team_allocation(n_teams)
    chosen_countries = []
    for continent, count in allocation.items():
        countries = countries_by_continent[continent]
        pops = populations_by_continent[continent]
        if count > len(countries):
            count = len(countries) 
        # Use random.choices for population weighting, but avoid duplicates
        selected = set()
        while len(selected) < count and len(selected) < len(countries):
            pick = random.choices(countries, weights=pops, k=1)[0]
            selected.add(pick)
        chosen_countries.extend(selected)
    return chosen_countries

# --- GROUP STAGE LOGIC ---
def round_robin_group(group_names, teams_dict):
    results = {name: {"points": 0, "scored": 0, "conceded": 0, "diff": 0} for name in group_names}
    schedule = [
        (0, 1), (2, 3), (3, 1), (0, 2), (2, 1), (0, 3)
    ]
    team_indices = {i: name for i, name in enumerate(group_names)}
    print(f"\n-- Group: {', '.join(group_names)} --")
    for a, b in schedule:
        name_a = team_indices[a]
        name_b = team_indices[b]
        print(f"\nPress Enter to simulate match: {name_a} vs {name_b}...")
        t1, t2 = teams_dict[name_a], teams_dict[name_b]
        
        print("\n--- Initial Skills ---")
        print(f"\n{t1.name}:")
        for p in t1.players:
            print(f"{p.name}: {p.skill}")
        print(f"\n{t2.name}:")
        for p in t2.players:
            print(f"{p.name}: {p.skill}")
        input()

        s1, s2, snitch_catcher, _ = simulate_match(t1, t2)
        print(f"  {name_a} {s1} - {s2} {name_b}  (Snitch: {snitch_catcher})")
        # Points
        if s1 > s2:
            results[name_a]["points"] += 1
        elif s2 > s1:
            results[name_b]["points"] += 1
        else:
            results[name_a]["points"] += 0.5
            results[name_b]["points"] += 0.5
        # Goals for/against
        results[name_a]["scored"] += s1
        results[name_a]["conceded"] += s2
        results[name_a]["diff"] = results[name_a]["scored"] - results[name_a]["conceded"]
        results[name_b]["scored"] += s2
        results[name_b]["conceded"] += s1
        results[name_b]["diff"] = results[name_b]["scored"] - results[name_b]["conceded"]
        if a == 0 and b == 3:
            print("\nFinal group standings:")
        else:
            print("\nCurrent standings:")
        for i, (name, stats) in enumerate(sorted(results.items(), key=lambda x: (-x[1]['points'], -x[1]['diff'], -x[1]['scored'])), 1):
            print(f" {i}. {name} ({stats['points']} pts, {stats['diff']} diff, {stats['scored']} for, {stats['conceded']} conceded)")
    # Sort teams: points, diff, scored
    sorted_teams = sorted(results.items(), key=lambda x: (-x[1]["points"], -x[1]["diff"], -x[1]["scored"]))
    # Return first and second place
    return [sorted_teams[0][0], sorted_teams[1][0]] #, matches, results

def cannon_group(group_names, teams_dict):
    results = {name: {"points": 0, "scored": 0, "conceded": 0, "diff": 0, "snitches caught": 0, "total snitch catching time": 0} for name in group_names}
    schedule = [
        (0, 1), (2, 3), (3, 1), (0, 2), (2, 1), (0, 3)
    ]
    team_indices = {i: name for i, name in enumerate(group_names)}
    print(f"\n-- Group: {', '.join(group_names)} --")
    for a, b in schedule:
        name_a = team_indices[a]
        name_b = team_indices[b]
        print(f"\nPress Enter to simulate match: {name_a} vs {name_b}...")
        t1, t2 = teams_dict[name_a], teams_dict[name_b]
        
        print("\n--- Initial Skills ---")
        print(f"\n{t1.name}:")
        for p in t1.players:
            print(f"{p.name}: {p.skill}")
        print(f"\n{t2.name}:")
        for p in t2.players:
            print(f"{p.name}: {p.skill}")
        input()

        s1, s2, snitch_catcher, match_time = simulate_match(t1, t2, 240)
        if snitch_catcher:
            print(f"  {name_a} {s1} - {s2} {name_b}  (Snitch: {snitch_catcher})")
            results[snitch_catcher]["snitches caught"] += 1
            results[snitch_catcher]["total snitch catching time"] += match_time
        else:
            print(f"  {name_a} {s1} - {s2} {name_b}  (Match is concluded with no snitch caught)")
        # Points
        if s1 > s2:
            results[name_a]["points"] += 2
            if s1 - s2 > 150:
                results[name_a]["points"] += 5
            elif s1 - s2 > 100:
                results[name_a]["points"] += 3
            elif s1 - s2 > 50:
                results[name_a]["points"] += 1
        elif s2 > s1:
            results[name_b]["points"] += 2
            if s2 - s1 > 150:
                results[name_b]["points"] += 5
            elif s2 - s1 > 100:
                results[name_b]["points"] += 3
            elif s2 - s1 > 50:
                results[name_b]["points"] += 1
        else:
            results[name_a]["points"] += 1
            results[name_b]["points"] += 1

        #Goals for/against
        results[name_a]["scored"] += s1
        results[name_a]["conceded"] += s2
        results[name_a]["diff"] = results[name_a]["scored"] - results[name_a]["conceded"]
        results[name_b]["scored"] += s2
        results[name_b]["conceded"] += s1
        results[name_b]["diff"] = results[name_b]["scored"] - results[name_b]["conceded"]

        if a == 0 and b == 3:
            print("\nFinal group standings:")
        else:
            print("\nCurrent standings:")
        for i, (name, stats) in enumerate(sorted(results.items(), key=lambda x: (-x[1]['points'], -x[1]['snitches caught'], x[1]['total snitch catching time'], -x[1]['diff'], -x[1]['scored'])), 1):
            print(f" {i}. {name} ({stats['points']} pts, {stats['snitches caught']} snitches caught in the total of {stats['total snitch catching time']} minutes, {stats['diff']} diff, {stats['scored']} for, {stats['conceded']} conceded)")
    # Sort teams: points, diff, scored
    sorted_teams = sorted(results.items(), key=lambda x: (-x[1]["points"], -x[1]['snitches caught'], x[1]['total snitch catching time'], -x[1]["diff"], -x[1]["scored"]))
    # Return first place and points
    return (sorted_teams[0][0], results[sorted_teams[0][0]])

# --- PLAYOFFS LOGIC ---
def playoff_bracket(group_winners, group_runners_up, teams_dict):
    """Play knockout rounds until champion. Groupmates can't meet until final."""
    N = len(group_winners)
    pairs = []
    # Pair 1st from group i with 2nd from group (i+1)%N
    for i in range(N):
        first = group_winners[i]
        second = group_runners_up[(i + 1) % N]
        pairs.append((first, second))

    round_num = 1
    while len(pairs) > 1:
        print(f"\n--- Playoff Round {round_num} ---")
        next_round = []
        for t1, t2 in pairs:
            print(f"{t1} vs {t2}")
            s1, s2, snitch_catcher, _ = simulate_match(teams_dict[t1], teams_dict[t2])
            print(f"  Result: {t1} {s1} - {s2} {t2}  (Snitch: {snitch_catcher})")
            if s1 > s2:
                winner = t1
            elif s2 > s1:
                winner = t2
            else:
                winner = snitch_catcher
                print(f"    Tie! {snitch_catcher} wins as Seeker caught the Snitch.")
            next_round.append(winner)
        pairs = [(next_round[i], next_round[i+1]) for i in range(0, len(next_round), 2)]
        round_num += 1
    print(f"\n=== CHAMPION: {pairs[0][0]} ===")

# --- TOURNAMENT DRIVER ---
def display_teams(teams_dict):
    print("\n=== PARTICIPATING TEAMS ===")
    for name, team in teams_dict.items():
        print(f"\n{name}")
        for player in team.players:
            print(f"  {player.role}: {player.name}, skill {player.skill}")
    print("\n" + "="*40)

def display_groups(groups):
    print("\n=== GROUPS ===")
    for idx, group in enumerate(groups, 1):
        print(f"Group {idx}: {', '.join(group)}")

def display_bracket(pairs, round_title):
    print(f"\n=== {round_title.upper()} ===")
    for idx, (a, b) in enumerate(pairs, 1):
        print(f"  Match {idx}: {a} vs {b}")

def build_split_bracket_pairs(group_winners, group_runners_up):
    n = len(group_winners)
    pairs = []
    for i in range(0, n, 2):
        pairs.append((group_winners[i], group_runners_up[i+1]))
    for i in range(1, n, 2):
        pairs.append((group_winners[i], group_runners_up[i-1]))
    return pairs

def get_bracket_order(n):
    if n == 2:
        return [0, 1]
    prev = get_bracket_order(n // 2)
    order = []
    for x in prev:
        order.append(x)
        order.append(n - 1 - x)
    return order

def build_ranked_pairs(group_winners_points):
    sorted_winners = sorted(group_winners_points.items(), key=lambda x: (-x[1]["points"], -x[1]['snitches caught'], x[1]['total snitch catching time'], -x[1]["diff"], -x[1]["scored"]))
    n = len(sorted_winners)
    temp_pairs = [(sorted_winners[i][0], sorted_winners[n - 1 - i][0]) for i in range(n // 2)]
    order = get_bracket_order(len(temp_pairs))
    result = [temp_pairs[i] for i in order]
    return result

def run_tournament(num_teams, fifa_style = True):
    print(f"\n=== QUIDDITCH WORLD CUP: {num_teams} TEAMS ===")
    team_names = pick_random_teams_by_continent(num_teams)
    random.shuffle(team_names)
    teams_dict = {name: create_random_team(name) for name in team_names}
    num_groups = num_teams // 4
    groups = [team_names[i*4:(i+1)*4] for i in range(num_groups)]

    # Show teams and groups
    display_teams(teams_dict)
    input("\nPress Enter to continue to group draw...")
    display_groups(groups)
    input("\nPress Enter to begin group simulations...")

    # GROUP STAGE
    group_winners = []
    group_runners_up = []
    group_winners_points = {}
    for idx, group in enumerate(groups, 1):
        input(f"\nPress Enter to simulate all matches in GROUP {idx} ({', '.join(group)}):")
        print(f"\n===== GROUP {idx} =====")

        if fifa_style:
            top2 = round_robin_group(group, teams_dict)
            group_winners.append(top2[0])
            group_runners_up.append(top2[1])
        else:
            top1, results = cannon_group(group, teams_dict)
            group_winners_points[top1] = results

    # PLAYOFFS
    print("\nAll group stages complete! Advancing to the playoffs!")
    if fifa_style:
        pairs = build_split_bracket_pairs(group_winners, group_runners_up)
    else:
        pairs = build_ranked_pairs(group_winners_points)

    round_names = []
    if len(pairs) == 16:
        round_names = ["Round of 32", "Round of 16", "Quarterfinals", "Semifinals", "Finals"]
    elif len(pairs) == 8:
        round_names = ["Round of 16", "Quarterfinals", "Semifinals", "Finals"]
    elif len(pairs) == 4:
        round_names = ["Quarterfinals", "Semifinals", "Finals"]
    elif len(pairs) == 2:
        round_names = ["Semifinals", "Finals"]
    else:
        print("Invalid number of teams in playoffs.")
        return

    round_idx = 0
    while True:
        round_title = round_names[round_idx] if round_idx < len(round_names) else f"Round {round_idx+1}"
        display_bracket(pairs, round_title)
        input(f"\nPress Enter to simulate {round_title} matches...")
        next_round = []
        for idx, (t1, t2) in enumerate(pairs, 1):
            input(f"Press Enter to simulate {round_title} Match {idx}: {t1} vs {t2}...")
            s1, s2, snitch_catcher, _ = simulate_match(teams_dict[t1], teams_dict[t2])
            print(f"  Result: {t1} {s1} - {s2} {t2}  (Snitch: {snitch_catcher})")
            if s1 > s2:
                winner = t1
            elif s2 > s1:
                winner = t2
            else:
                winner = snitch_catcher
                print(f"    Tie! {snitch_catcher} wins as Seeker caught the Snitch.")
            print(f"    Winner: {winner}\n")
            next_round.append(winner)
        if len(next_round) == 1:
            champion = next_round[0]
            break
        else:
            pairs = [(next_round[i], next_round[i+1]) for i in range(0, len(next_round), 2)]
            round_idx += 1

    print(f"\n=== CHAMPION: {champion} ===\n")
    print(f"🏆 {champion} WINS THE QUIDDITCH WORLD CUP! 🏆")