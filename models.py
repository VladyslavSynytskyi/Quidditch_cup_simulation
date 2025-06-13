import random

ROLE_LIMITS = {
    "Chaser": 3,
    "Beater": 2,
    "Keeper": 1,
    "Seeker": 1
}

class Player:
    def __init__(self, name, role, skill):
        self.name = name
        self.role = role
        self.skill = skill

    def __repr__(self):
        return f"{self.name} ({self.role}, Skill: {self.skill})"
    
    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "skill": self.skill
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["role"], data["skill"])

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []

    def count_role(self, role):
        return sum(1 for p in self.players if p.role == role)

    def can_add_role(self, role):
        return self.count_role(role) < ROLE_LIMITS.get(role, 0)

    def add_player(self, player):
        if len(self.players) >= 7:
            print("A team can only have 7 players.")
            return False
        if not self.can_add_role(player.role):
            print(f"Cannot add more {player.role}s (limit reached).")
            return False
        self.players.append(player)
        return True

    def __repr__(self):
        players_str = "\n  ".join(str(p) for p in self.players)
        return f"Team: {self.name}\n  {players_str}"

    def missing_roles(self):
        return {
            role: ROLE_LIMITS[role] - self.count_role(role)
            for role in ROLE_LIMITS
            if self.count_role(role) < ROLE_LIMITS[role]
        }
    
    def to_dict(self):
        return {
            "name": self.name,
            "players": [p.to_dict() for p in self.players]
        }

    @classmethod
    def from_dict(cls, data):
        team = cls(data["name"])
        for player_data in data["players"]:
            team.add_player(Player.from_dict(player_data))
        return team

def create_random_player(role, idx):
    name = f"{role} {idx}" 
    skill = random.randint(1, 10)
    return Player(name, role, skill)

def create_random_team(team_name):
    team = Team(team_name)
    for role, count in ROLE_LIMITS.items():
        for i in range(1, count + 1):
            player = create_random_player(role, i)
            team.add_player(player)
    return team
