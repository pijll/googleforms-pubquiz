import collections
import pathlib

from section import Section


class Quiz:
    def __init__(self, sections=None):
        self.sections = sections or []

    def scores(self):
        scores_dict = collections.Counter()
        for section in self.sections:
            scores_dict.update(section.scores())
        return scores_dict

    @classmethod
    def load_dir(cls, directory):
        quiz = Quiz()
        for p in pathlib.Path(directory).iterdir():
            if p.is_file() and p.suffix == '.csv':
                with p.open() as infile:
                    section = Section.read_csv(infile, name=p.stem)
                quiz.sections.append(section)

        return quiz

    def leaderboard(self):
        previous_score = None
        for i, (team, score) in enumerate(sorted(self.scores().items(), key=lambda x: (x[1], x[0]), reverse=True), start=1):
            yield [str(i) if previous_score is None or previous_score != score else '', team, str(score)]
            previous_score = score

    def get_section(self, name):
        for section in self.sections:
            if section.name == name:
                return section

    def sections_per_team(self):
        return {team: {
            section: bool(section.response_for_team(team)) for section in self.sections
        } for team in self.teams()}

    def teams(self):
        return set.union(*[section.teams() for section in self.sections])
