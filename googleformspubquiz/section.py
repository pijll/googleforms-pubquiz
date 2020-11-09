import collections
import csv
from typing import List

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
