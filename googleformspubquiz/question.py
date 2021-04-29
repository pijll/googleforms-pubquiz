import collections


class Question:
    def __init__(self, name=None, correct_answers=None, section=None, number_in_section=None):
        self.section = None
        self.name = name
        self._correct_answers = None
        self.correct_answers = correct_answers or {}
        self.answers = []

        if section is not None:
            section.add_question(self)

    @property
    def number_in_section(self):
        if self.section is None:
            return 0
        else:
            return self.section.questions.index(self) + 1

    @property
    def correct_answers(self):
        return frozenset(self._correct_answers)

    @correct_answers.setter
    def correct_answers(self, answers):
        self._correct_answers = []
        for answer in answers:
            self.add_correct_answer(answer)

    def add_correct_answer(self, answer):
        self._correct_answers.append(answer)

    def remove_correct_answer(self, answer):
        self._correct_answers.remove(answer)

    def fraction_of_correct_responses(self):
        correct = sum(1 for answer in self.answers if answer.is_correct())
        total = len(self.answers)

        if total > 0:
            return correct/total
        else:
            return 0

    def answer_list(self):
        counter = collections.Counter()
        for correct in self.correct_answers:
            counter[correct] = 0

        for answer in self.answers:
            counter[answer.answer] += 1

        return counter
