import collections
import io
import pathlib
import zipfile

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
        quiz.update_from_dir(directory)
        return quiz

    def update_from_dir(self, directory):
        for p in pathlib.Path(directory).iterdir():
            if p.is_file() and p.suffix == '.csv':
                section_name = p.stem
                if not self.get_section(section_name):
                    with p.open() as infile:
                        section = Section.read_csv(infile, name=section_name)
                    self.sections.append(section)

                    yaml_name = p.with_suffix('.yaml')
                    if yaml_name.exists():
                        section.load_answers(yaml_name)
            elif p.is_file() and p.suffixes == ['.csv', '.zip']:
                csv_name = p.stem
                section_name = p.stem.split('.')[0]
                if not self.get_section(section_name):
                    with zipfile.ZipFile(p, 'r') as zipped_file:
                        with io.TextIOWrapper(zipped_file.open(csv_name, 'r')) as infile:
                            section = Section.read_csv(infile, name=section_name)
                        self.sections.append(section)
                    yaml_name = p.parent / (section_name + '.yaml')
                    print(yaml_name)
                    if yaml_name.exists():
                        print('loading')
                        section.load_answers(yaml_name)

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
