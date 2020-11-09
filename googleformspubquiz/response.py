class Response:
    def __init__(self, timestamp=None, team=None, answers=None):
        self.team = team
        self.timestamp = timestamp
        self.answers = answers

    def score(self):
        return sum(answer.is_correct() for answer in self.answers)

