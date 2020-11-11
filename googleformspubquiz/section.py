import collections
import csv
import pathlib
from typing import List

import yaml

from answer import Answer
from response import Response
from question import Question


class Section(object):
    def __init__(self, questions: List[Question] = None, name=None):
        self.name = name
        self.responses = []
        self.questions = questions or []

    def set_header(self, header: List[str]):
        timestamp, team, *questions = header
        for question in questions:
            self.questions.append(Question(question))

    def add_response(self, response: List[str]):
        timestamp, team, *answers_as_strings = response
        answers = [Answer(question=self.questions[i], answer=a) for i, a in enumerate(answers_as_strings)]
        response = Response(timestamp=timestamp, team=team, answers=answers)
        self.responses.append(response)

    def set_correct_answers(self, correct_answers):
        for question, correct_answer in zip(self.questions, correct_answers):
            question.add_correct_answer(correct_answer)

    @classmethod
    def read_csv(cls, infile, name=None):
        section = Section(name=name)
        csv_reader = csv.reader(infile)
        header = next(csv_reader)
        section.set_header(header)

        for row in csv_reader:
            if row[1] == 'Correct answers':
                section.set_correct_answers(row[2:])
            else:
                section.add_response(row)

        return section

    def scores(self):
        return {response.team: response.score() for response in self.responses}

    def fraction_of_correct_answers(self):
        correct_answers = sum(self.scores().values())
        max_possible_score = len(self.questions) * len(self.responses)

        return correct_answers / max_possible_score

    def response_for_team(self, team):
        responses = [response for response in self.responses if response.team == team]
        if responses:
            return responses[0]
        else:
            return None

    def teams(self):
        return {response.team for response in self.responses}

    def change_team_name(self, from_name, to_name):
        for response in self.responses:
            if response.team == from_name:
                response.team = to_name

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
