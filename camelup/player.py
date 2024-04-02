class Player:
    def __init__(self, id) -> None:
        self.id = id
        self.points = 3
        self.winner_bet = None
        self.loser_bet = None
        # id of ally, None if none
        self.ally = None
        # List of (color, amount)
        self.bets = []
        # location of boost
        self.boost = None
        # Value of boost
        self.boost_val = None

    def reset_round(self):
        self.ally = None
        self.bets = []
        self.boost = None
        self.boost_val = None

    def __repr__(self) -> str:
        return f"Player {self.id}: (points: {self.points}, ally: {self.ally}, boost: {self.boost}, bets: {self.bets})"

    def __eq__(self, other) -> bool:
        return (
            self.id == other.id
            and self.points == other.points
            and self.winner_bet == other.winner_bet
            and self.loser_bet == other.loser_bet
            and self.ally == other.ally
            and self.boost == other.boost
            and self.bets == other.bets
        )

    def to_json(self):
        return {
            "id": self.id,
            "points": self.points,
            "winner_bet": self.winner_bet,
            "loser_bet": self.loser_bet,
            "ally": self.ally,
            "boost": self.boost,
            "bets": self.bets,
        }

    @classmethod
    def from_json(cls, data):
        player = cls(data["id"])
        player.points = data["points"]
        player.winner_bet = data["winner_bet"]
        player.loser_bet = data["loser_bet"]
        player.ally = data["ally"]
        player.boost = data["boost"]
        player.bets = data["bets"]
        return player
