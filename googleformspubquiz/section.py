import csv
import pathlib
from types import SimpleNamespace
from typing import List

import yaml

from answer import Answer
from response import Response
from question import Question
from team import Team


class Section(object):
    def __init__(self, questions: List[Question] = None, name=None, quiz=None):
        self.name = name
        self.responses = []
        self.questions = questions or []
        self.quiz=None

        if quiz is not None:
            quiz.add_section(self)

    def set_header(self, header: List[str]):
        timestamp, team, *questions = header
        for question in questions:
            self.questions.append(Question(question))

    def add_response_from_line(self, response: List[str]):
        parsed_line = self.read_line(response)
        answers = [Answer(question=self.questions[i], answer=a) for i, a in enumerate(parsed_line.fields)]
        team = self.get_team(parsed_line.team_id, parsed_line.team_name)
        response = Response(timestamp=parsed_line.timestamp, team=team, answers=answers)
        self.add_response(response)

    def add_response(self, response: Response):
        self.responses.append(response)

    def set_correct_answers(self, correct_answers):
        for question, correct_answer in zip(self.questions, correct_answers):
            question.add_correct_answer(correct_answer)

    @classmethod
    def read_csv(cls, infile, name=None, quiz=None, teamid_column=None, teamname_column=None):
        section = Section(name=name, quiz=quiz)
        csv_reader = csv.reader(infile)
        header = next(csv_reader)
        section.set_header(header)

        for row in csv_reader:
            if row[1] == 'Correct answers':
                section.set_correct_answers(row[2:])
            else:
                section.add_response_from_line(row)

        return section

    def scores(self):
        return {team: self.response_for_team(team).score() for team in self.teams()}

    def fraction_of_correct_answers(self):
        correct_answers = sum(self.scores().values())
        max_possible_score = len(self.questions) * len(self.responses)

        return correct_answers / max_possible_score

    def response_for_team(self, team):
        responses = sorted(self.responses_for_team(team), key=lambda x: x.timestamp)
        if responses:
            return responses[0]
        else:
            return None

    def responses_for_team(self, team):
        return {response for response in self.responses if response.team == team}

    def teams(self):
        return {response.team for response in self.responses}

    def replace_team(self, team_to_replace, new_team):
        for response in self.responses:
            if response.team == team_to_replace:
                response.team = new_team

    def save_answers(self, out_file):
        if isinstance(out_file, str):
            path = pathlib.Path(out_file)
            self.save_answers(path)
            return
        elif isinstance(out_file, pathlib.Path):
            if out_file.is_dir():
                out_file = out_file / (self.name + '.yaml')
            with out_file.open('w') as stream:
                self.save_answers(stream)
            return

        data = [list(question.correct_answers) for question in self.questions]
        yaml.dump(data, out_file, default_flow_style=False, allow_unicode=True)

    def load_answers(self, in_file):
        if isinstance(in_file, str):
            path = pathlib.Path(in_file)
            self.load_answers(path)
            return
        elif isinstance(in_file, pathlib.Path):
            if in_file.is_dir():
                in_file = in_file / (self.name + '.yaml')
            with in_file.open() as stream:
                self.load_answers(stream)
            return

        data_loaded = yaml.safe_load(in_file)

        for question, correct_answers in zip(self.questions, data_loaded):
            question.correct_answers = correct_answers

    def get_team(self, team_id, team_name):
        if self.quiz:
            return self.quiz.get_team(team_id, team_name)
        else:
            return Team(team_id, team_name)

    def read_line(self, csv_line):
        if self.quiz:
            return self._read_line(csv_line, self.quiz.teamid_column, self.quiz.teamname_column)
        else:
            return self._read_line(csv_line)

    @staticmethod
    def _read_line(csv_line, teamid_column=None, teamname_column=None):
        timestamp = csv_line[0]
        if teamid_column is None:
            teamid_column = 1
        team_id = csv_line[teamid_column]

        team_name = csv_line[teamname_column] if teamname_column is not None else team_id

        fields = [elt for i, elt in enumerate(csv_line) if i not in [0, teamid_column, teamname_column]]

        return SimpleNamespace(timestamp=timestamp, team_id=team_id, team_name=team_name, fields=fields)
