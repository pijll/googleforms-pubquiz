class Answer:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        if question:
            question.answers.append(self)

    def is_correct(self):
        return self.answer in self.question.correct_answers
