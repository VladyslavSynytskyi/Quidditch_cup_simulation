import random

# --- Weather ---
WEATHER_OPTIONS = [
    {"type": "Cloudy", "prob": 0.4, "delta": 1},
    {"type": "Sunny",  "prob": 0.3, "delta": 0},
    {"type": "Windy",  "prob": 0.1, "delta": -1},
    {"type": "Rainy",  "prob": 0.1, "delta": -2},
    {"type": "Foggy",  "prob": 0.1, "delta": -1},
]

def apply_weather(team1, team2):
    r = random.random()
    cumulative = 0
    for w in WEATHER_OPTIONS:
        cumulative += w["prob"]
        if r < cumulative:
            weather = w
            break
    else:
        ValueError("No weather option found.")
    # Everyone gets the same delta
    result = {}
    for p in team1.players + team2.players:
        result[id(p)] = weather["delta"]
    desc = f"Weather: {weather['type']} (all players skill {'+' if weather['delta'] >= 0 else ''}{weather['delta']})"
    return result, desc, weather['type']

# --- Crowd Support ---
def apply_crowd_support(team, team_name):
    got_support = random.random() < 0.25
    result = {}
    desc = f"{team_name} did not receive extra crowd support"
    if got_support:
        for p in team.players:
            result[id(p)] = 1
        desc = f"{team_name} received massive crowd support (+1 to all players)"
    return result, desc

# --- Faulty Brooms ---
def apply_faulty_brooms(team1, team2):
    num_players = 0
    while num_players < 14 and random.random() < 0.5:
        num_players += 1
    result = {}
    desc = "No players received faulty brooms."
    if num_players:
        all_players = team1.players + team2.players
        selected_players = random.sample(all_players, num_players)
        for p in selected_players:
            result[id(p)] = -2
        desc = (
            f"{num_players} player(s) received faulty brooms (skill -2): "
            + ", ".join(f"{p.name} ({team1.name if p in team1.players else team2.name}, {p.role})" for p in selected_players)
        )
    return result, desc

def apply_referee_bias(team1, team2):
    activated = random.random() < 0.10  # 10% chance of bias
    if not activated:
        return None, "No referee bias in this match."
    favored = random.choice([team1, team2])
    desc = f"Referee bias: {favored.name} has a 20% chance to steal the attack each time step."
    return favored.name, desc

def apply_injuries(team1, team2):
    # Decide how many injuries (75% for each)
    num_injuries = 0
    while num_injuries < 14 and random.random() < 0.75:
        num_injuries += 1

    if num_injuries == 0:
        return {}, "No injuries occurred this match."

    # Weight per role
    role_weights = {"Chaser": 4, "Beater": 3, "Keeper": 2, "Seeker": 1}
    all_players = team1.players + team2.players

    # Severity settings
    severities = [-1, -2, -3]
    severity_weights = [0.5, 0.3, 0.2]

    already_injured = set()
    result = {}
    descs = []

    for _ in range(num_injuries):
        # Build weighted pool of non-injured players
        weighted_players = []
        for p in all_players:
            if id(p) not in already_injured:
                weighted_players.extend([p] * role_weights[p.role])
        if not weighted_players:
            break  # All players injured, stop early

        player = random.choice(weighted_players)
        already_injured.add(id(player))
        severity = random.choices(severities, weights=severity_weights, k=1)[0]
        result[id(player)] = severity
        descs.append(
            f"{player.name} ({team1.name if player in team1.players else team2.name}, {player.role}) injured: {severity}"
        )

    return result, "Injuries: " + "; ".join(descs)

def apply_bludger_mayhem():
    # 10% chance for Bludger Mayhem
    if random.random() < 0.10:
        desc = "Bludger Mayhem: The match is chaotic and fast! Time steps reduced to 1-3 minutes."
        return (1, 3), desc
    else:
        return (1, 5), "No bludger mayhem: Normal match pace."
    
def apply_coach_strategy(team1, team2):
    result = {}
    descs = []

    for team, other_team in [(team1, team2), (team2, team1)]:
        if random.random() < 0.25:
            own_or_opp = random.choice(['own', 'opp'])
            if own_or_opp == 'own':
                boost = random.choices([1, 2], weights=[0.7, 0.3], k=1)[0]
                for p in team.players:
                    if p.role != "Seeker":
                        result.setdefault(id(p), 0)
                        result[id(p)] += boost
                descs.append(
                    f"{team.name} coach's offensive strategy: All non-Seeker players gain +{boost}"
                )
            else:
                penalty = random.choices([-1, -2], weights=[0.7, 0.3], k=1)[0]
                for p in other_team.players:
                    if p.role != "Seeker":
                        result.setdefault(id(p), 0)
                        result[id(p)] += penalty
                descs.append(
                    f"{team.name} coach's defensive strategy: Opponent's non-Seeker players suffer {penalty}"
                )
        else:
            descs.append(f"{team.name} coach's strategy: No special effect")
    return result, "; ".join(descs)

def apply_weather_timeouts(weather_type, team1, team2):
    # Returns a dict: {'timeouts': [...], 'skill_debuffs': {...}, 'desc': [...]}
    desc = []
    out = {'timeouts': [], 'skill_debuffs': {}, 'desc': desc}
    per_attacks = random.randint(10, 100)

    if weather_type == "Cloudy":
        t_len = random.randint(10, 30)
        out['timeouts'].append({'per_attacks': per_attacks, 'length': t_len, 'condition': "Cloudy"})
        desc.append(f"Fan interference timeout: {t_len} minutes every {per_attacks} attacks (Cloudy)")
    elif weather_type == "Sunny":
        t_len = random.randint(5, 15)
        out['timeouts'].append({'per_attacks': per_attacks, 'length': t_len, 'condition': "Sunny"})
        desc.append(f"Water break: {t_len} minutes after every {per_attacks} attacks (Sunny)")
    elif weather_type == "Rainy":
        t_len = random.randint(5, 60)
        out['timeouts'].append({'start': per_attacks, 'length': t_len, 'condition': "Rainy"})
        desc.append(f"Lightning risk timeout: {t_len} minutes every {per_attacks} attacks (Rainy)")
    elif weather_type == "Windy":
        # All beaters get -1 skill
        beaters = [p for p in team1.players + team2.players if p.role == "Beater"]
        for p in beaters:
            out['skill_debuffs'][id(p)] = -1
        desc.append("All Beaters suffer -1 skill for the whole match (Windy)")
    elif weather_type == "Foggy":
        # Both seekers get -2 skill
        seekers = [p for p in team1.players + team2.players if p.role == "Seeker"]
        for p in seekers:
            out['skill_debuffs'][id(p)] = -2
        desc.append("Both Seekers suffer -2 skill for the whole match (Foggy)")
    return out

# --- Apply all factors and return {player_id: [deltas]} and list of descriptions ---
def apply_all_factors(team1, team2):
    player_deltas = {id(p): [] for p in team1.players + team2.players}
    descriptions = []

    # Weather
    weather_result, weather_desc, weather_type = apply_weather(team1, team2)
    descriptions.append(weather_desc)
    for pid, delta in weather_result.items():
        player_deltas[pid].append(delta)

    # Weather-linked effects (timeouts or debuffs)
    weather_effects = apply_weather_timeouts(weather_type, team1, team2)
    descriptions.extend(weather_effects['desc'])
    # Skill debuffs from weather effects:
    for pid, delta in weather_effects['skill_debuffs'].items():
        player_deltas[pid].append(delta)

    # Crowd Support (both teams independently)
    crowd1_result, crowd1_desc = apply_crowd_support(team1, team1.name)
    crowd2_result, crowd2_desc = apply_crowd_support(team2, team2.name)
    descriptions.append(crowd1_desc)
    descriptions.append(crowd2_desc)
    for pid, delta in crowd1_result.items():
        player_deltas[pid].append(delta)
    for pid, delta in crowd2_result.items():
        player_deltas[pid].append(delta)

    # Faulty Brooms
    broom_result, broom_desc = apply_faulty_brooms(team1, team2)
    descriptions.append(broom_desc)
    for pid, delta in broom_result.items():
        player_deltas[pid].append(delta)

    # Referee bias
    ref_bias, ref_bias_desc = apply_referee_bias(team1, team2)
    descriptions.append(ref_bias_desc)

    # Injuries
    injuries_result, injuries_desc = apply_injuries(team1, team2)
    descriptions.append(injuries_desc)
    for pid, delta in injuries_result.items():
        player_deltas[pid].append(delta)

    # Bludger mayhem
    time_range, bludger_desc = apply_bludger_mayhem()
    descriptions.append(bludger_desc)

    # Coach game-plan
    coach_result, coach_desc = apply_coach_strategy(team1, team2)
    descriptions.append(coach_desc)
    for pid, delta in coach_result.items():
        player_deltas[pid].append(delta)

    return player_deltas, descriptions, ref_bias, time_range, weather_effects['timeouts']
