import random, copy
from random_factors import apply_all_factors

def get_attack_value(team, boost = 0):
    chaser_skill = sum(min(10, p.skill + boost) for p in team.players if p.role == "Chaser") * 0.75
    beater_skill = sum(min(10, p.skill + boost) for p in team.players if p.role == "Beater") * 0.5
    keeper_skill = next(min(10, p.skill + boost) for p in team.players if p.role == "Keeper") * 0.25
    return chaser_skill + beater_skill + keeper_skill

def get_defense_value(team, boost = 0):
    chaser_skill = sum(min(10, p.skill + boost) for p in team.players if p.role == "Chaser") * 0.25
    beater_skill = sum(min(10, p.skill + boost) for p in team.players if p.role == "Beater") * 0.5
    keeper_skill = next(min(10, p.skill + boost) for p in team.players if p.role == "Keeper") * 0.75
    return chaser_skill + beater_skill + keeper_skill

def get_seeker_skill(team):
    return next(p.skill for p in team.players if p.role == "Seeker")

def simulate_match(team1, team2, time_limit = None):

    # Deep copy for temp modification
    team1_sim = copy.deepcopy(team1)
    team2_sim = copy.deepcopy(team2)

    # Track original skills for normalization
    player_base_skills = {id(p): p.skill for p in team1_sim.players + team2_sim.players}

    # Apply all factors, get per-player deltas and descriptions
    player_deltas, applied_factors, ref_bias, time_step_range, timeouts = apply_all_factors(team1_sim, team2_sim)
    min_step, max_step = time_step_range

    # Normalize: sum deltas for each player, clamp to [1, 10]
    for p in team1_sim.players + team2_sim.players:
        eff_skill = player_base_skills[id(p)] + sum(player_deltas[id(p)])
        p.skill = max(1, min(10, eff_skill))

    next_penalty_attack = random.randint(1, 10)
    penalty_stats = {
        team1_sim.name: {"awarded": 0, "scored": 0},
        team2_sim.name: {"awarded": 0, "scored": 0}
    }

    time = 0
    team1_score = 0
    team2_score = 0
    highlights = []
    snitch_caught = False
    snitch_catcher = None

    # Strategic timeout mechanics
    next_strategic_timeout_attack = random.randint(10, 20)
    timeout_count = 0
    active_boosts = []  # Each item: dict(team, boost, start, end)
    attack_counter = 0  # Total number of attacks performed

    # Stats
    team1_attacks = 0
    team2_attacks = 0
    team1_goals = 0
    team2_goals = 0
    team1_saves = 0
    team2_saves = 0

    team1_seeker_skill = get_seeker_skill(team1_sim)
    team2_seeker_skill = get_seeker_skill(team2_sim)
    total_seeker_skill = team1_seeker_skill + team2_seeker_skill

    next_timeout_break = None
    timeout_break_length = None
    timeout_breaks = [t for t in timeouts if 'per_attacks' in t]
    if timeout_breaks:
        next_timeout_break = timeout_breaks[0]['per_attacks']
        timeout_break_length = timeout_breaks[0]['length']
        condition = timeout_breaks[0]['condition']

    while not snitch_caught:
        
        # Advance time randomly
        step = random.randint(min_step, max_step)
        time += step

        if time_limit:
            if time > time_limit:
                time = time_limit
                # Print factors in the result section:
                print("\n--- Random Factors Applied ---")
                for f in applied_factors:
                    print(f)

                # Output results
                print("\n--- Match Result ---")
                print(f"{team1_sim.name}: {team1_score} - {team2_sim.name}: {team2_score}")
                print("Snitch was not caught (time ran out).")
                print(f"Total match time: {time} minutes")

                print("\n--- Match Statistics ---")
                print(f"{team1_sim.name}: {team1_attacks} attacks, {team1_goals} goals, {team2_saves} misses")
                print(f"{team2_sim.name}: {team2_attacks} attacks, {team2_goals} goals, {team1_saves} misses")

                print("\n--- Penalty Statistics ---")
                print(f"{team1_sim.name}: {penalty_stats[team1_sim.name]['awarded']} awarded, {penalty_stats[team1_sim.name]['scored']} scored")
                print(f"{team2_sim.name}: {penalty_stats[team2_sim.name]['awarded']} awarded, {penalty_stats[team2_sim.name]['scored']} scored")

                print("\n--- Match Highlights ---")
                for h in highlights:
                    print(h)
                return (team1_score, team2_score, None, time)

        # Snitch logic 
        if total_seeker_skill > 0:
            snitch_threshold = total_seeker_skill * 0.001
            if random.random() < snitch_threshold:
                snitch_caught = True
                # Determine who caught it
                winner = random.randint(1, total_seeker_skill)
                if winner <= team1_seeker_skill:
                    team1_score += 150
                    snitch_catcher = team1_sim.name
                    highlights.append(f"{time}': {team1_sim.name}'s Seeker catches the Snitch! (+150 points)")
                    continue
                else:
                    team2_score += 150
                    snitch_catcher = team2_sim.name
                    highlights.append(f"{time}': {team2_sim.name}'s Seeker catches the Snitch! (+150 points)")
                    continue

        # -- Timeout break logic (only for Cloudy, Sunny, Rainy) --
        if next_timeout_break and attack_counter > 0 and attack_counter % next_timeout_break == 0 and (time_limit is None or time + timeout_break_length < time_limit):
            if condition == "Cloudy":
                if random.random() < 0.05:
                    time += timeout_break_length
                    highlights.append(f"{time}': Fan interference timeout for {timeout_break_length} min (Cloudy).")
            elif condition == "Sunny":
                if random.random() < 0.20:
                    time += timeout_break_length
                    highlights.append(f"{time}': Water break for {timeout_break_length} min (Sunny).")
            elif condition == "Rainy":
                if random.random() < 0.10:
                    time += timeout_break_length
                    highlights.append(f"{time}': Lightning risk timeout for {timeout_break_length} min (Rainy).")

        # Randomly select attacking team
        attacking, defending = (team1_sim, team2_sim) if random.choice([True, False]) else (team2_sim, team1_sim)
        if attacking == team1_sim:
            team1_attacks += 1
        else:
            team2_attacks += 1
        attack_counter += 1

        # Referee bias: attempt to steal attack if not already chosen
        if ref_bias:
            biased_team = team1_sim if team1_sim.name == ref_bias else team2_sim
            if attacking != biased_team and random.random() < 0.20:
                if biased_team == team2_sim:
                    attacking, defending = biased_team, team1_sim  
                    team1_attacks -= 1
                    team2_attacks += 1
                else:
                    attacking, defending = biased_team, team2_sim
                    team2_attacks -= 1
                    team1_attacks += 1
                highlights.append(f"{time}': Referee bias! {biased_team.name} steals the attack.")

        # Find current attack number
        current_attack = attack_counter
        boost_map = {team1_sim: 0, team2_sim: 0}
        for boost in active_boosts:
            if boost['start_attack'] <= current_attack <= boost['end_attack']:
                boost_map[boost['team']] += boost['boost']

        attacking_boost = boost_map[attacking]
        defending_boost = boost_map[defending]
        attack_val = get_attack_value(attacking, attacking_boost)
        defense_val = get_defense_value(defending, defending_boost)
        diff = attack_val - defense_val
        random_threshold = random.randint(-25, 35)

        if diff > random_threshold:
            # Goal scored
            if attacking == team1_sim:
                team1_score += 10
                team1_goals += 1
            else:
                team2_score += 10
                team2_goals += 1
            highlights.append(f"{time}': {attacking.name} scores a goal! ({team1_score}-{team2_score})")
        else:
            if defending == team1_sim:
                team1_saves += 1
            else:
                team2_saves += 1
            highlights.append(f"{time}': {defending.name} makes a big save!")

        # Check for strategic timeout
        if not time_limit and attack_counter == next_strategic_timeout_attack:
            if random.random() < 0.20:  # 20% chance
                timeout_count += 1
                # Who calls it?
                if team1_score < team2_score and random.random() < 0.75:
                    calling_team, other_team = team1_sim, team2_sim
                elif team2_score == team1_score: # tie
                    calling_team, other_team = random.choice([(team1_sim, team2_sim), (team2_sim, team1_sim)])
                else:  
                    calling_team, other_team = team2_sim, team1_sim

                # How long for each team's boost (random independently)
                call_team_duration = random.randint(5, 10)
                opp_team_duration = random.randint(5, 10)

                # Apply boost for the next N attacks (track window)
                active_boosts.append({
                    'team': calling_team,
                    'boost': 2,
                    'start_attack': attack_counter + 1,
                    'end_attack': attack_counter + call_team_duration
                })
                active_boosts.append({
                    'team': other_team,
                    'boost': 1,
                    'start_attack': attack_counter + 1,
                    'end_attack': attack_counter + opp_team_duration
                })

                # Time skipped (5 to max), max doubles each timeout
                max_skip = 15 * (2 ** (timeout_count - 1))
                if max_skip > 600:
                    max_skip = 600
                skip_minutes = random.randint(5, max_skip)
                time += skip_minutes
                highlights.append(
                    f"{time}': Strategic timeout! {calling_team.name} calls it. "
                    f"Boosts: {calling_team.name} (+2 for {call_team_duration} attacks), "
                    f"{other_team.name} (+1 for {opp_team_duration} attacks). "
                    f"Play resumed after {skip_minutes} min."
                )
            # Set next strategic timeout
            next_strategic_timeout_attack += random.randint(10, 20)

        # --- Penalty kick logic ---
        if attack_counter == next_penalty_attack:
            if random.random() < 0.20:  # 20% chance for a penalty event
                # Determine which team gets the penalty
                if ref_bias:
                    biased_team = team1_sim if team1_sim.name == ref_bias else team2_sim
                    other_team = team2_sim if biased_team == team1_sim else team1_sim
                    if random.random() < 0.75:
                        penalty_team, defending_team = biased_team, other_team
                    else:
                        penalty_team, defending_team = other_team, biased_team
                else:
                    if random.random() < 0.5:
                        penalty_team, defending_team = team1_sim, team2_sim
                    else:
                        penalty_team, defending_team = team2_sim, team1_sim

                # Apply boosts, if any, for this attack
                boost_map = {team1_sim: 0, team2_sim: 0}
                current_attack = attack_counter
                for boost in active_boosts:
                    if boost['start_attack'] <= current_attack <= boost['end_attack']:
                        boost_map[boost['team']] += boost['boost']

                # Find best chaser and opposing keeper (using current skills + boosts)
                shooting_chasers = [p for p in penalty_team.players if p.role == "Chaser"]
                if shooting_chasers:
                    chaser = max(shooting_chasers, key=lambda p: p.skill + boost_map[penalty_team])
                    keeper = next(p for p in defending_team.players if p.role == "Keeper")
                    chaser_skill = min(10, chaser.skill + boost_map[penalty_team])
                    keeper_skill = min(10, keeper.skill + boost_map[defending_team])
                    total = chaser_skill + keeper_skill
                    roll = random.randint(1, int(total))
                    # Track stats
                    penalty_stats[penalty_team.name]["awarded"] += 1
                    if roll <= chaser_skill:
                        if penalty_team == team1_sim:
                            team1_score += 10
                        else:
                            team2_score += 10
                        penalty_stats[penalty_team.name]["scored"] += 1
                        highlights.append(f"{time}': Penalty for {penalty_team.name}! {chaser.name} vs {keeper.name}: GOAL! ({team1_score}-{team2_score})")
                    else:
                        highlights.append(f"{time}': Penalty for {penalty_team.name}! {chaser.name} vs {keeper.name}: SAVED by {keeper.name}!")
                else:
                    raise ValueError("No chasers?!")

            # Schedule next penalty check
            next_penalty_attack += random.randint(1, 10)

    # Print factors in the result section:
    print("\n--- Random Factors Applied ---")
    for f in applied_factors:
        print(f)

    # Output results
    print("\n--- Match Result ---")
    print(f"{team1_sim.name}: {team1_score} - {team2_sim.name}: {team2_score}")
    print(f"Snitch caught by: {snitch_catcher}")
    print(f"Total match time: {time} minutes")

    print("\n--- Match Statistics ---")
    print(f"{team1_sim.name}: {team1_attacks} attacks, {team1_goals} goals, {team2_saves} misses")
    print(f"{team2_sim.name}: {team2_attacks} attacks, {team2_goals} goals, {team1_saves} misses")

    print("\n--- Penalty Statistics ---")
    print(f"{team1_sim.name}: {penalty_stats[team1_sim.name]['awarded']} awarded, {penalty_stats[team1_sim.name]['scored']} scored")
    print(f"{team2_sim.name}: {penalty_stats[team2_sim.name]['awarded']} awarded, {penalty_stats[team2_sim.name]['scored']} scored")

    print("\n--- Match Highlights ---")
    for h in highlights:
        print(h)

    return (team1_score, team2_score, snitch_catcher, time)