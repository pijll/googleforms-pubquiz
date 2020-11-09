import textwrap
import unittest

from googleformspubquiz import Section, Question, Response, Answer


class TestReadResponses(unittest.TestCase):
    def test_header(self):
        # ARRANGE
        header = ["Timestamp", "Teamnaam", "Vraag 1", "Vraag 2", "Vraag 3"]
        section = Section()

        # ACT
        section.set_header(header)

        # ASSERT
        self.assertEqual(len(section.questions), 3)
        for q in section.questions:
            self.assertIsInstance(q, Question)
        self.assertEqual(section.questions[0].name, 'Vraag 1')

    def test_add_response(self):
        # ARRANGE
        questions = [Question(x) for x in ('a', 'b', 'c')]
        section = Section(questions=questions)
        response = ["2020/10/30 3:08:44 PM GMT+1", "test", "Antwoord 1", "Antwoord 2", "Antwoord 3"]

        # ACT
        section.add_response(response)

        # ASSERT
        self.assertEqual(len(section.responses), 1)

        response = section.responses[0]
        self.assertIsInstance(response, Response)
        self.assertEqual(len(response.answers), 3)
        for i, answer in enumerate(response.answers):
            self.assertIsInstance(answer, Answer)
            self.assertEqual(answer.question, questions[i])
        for question in questions:
            self.assertEqual(len(question.answers), 1)


class TestCorrectAnswers(unittest.TestCase):
    def test_read_correct_answers(self):
        # ARRANGE
        questions = [Question(x) for x in ('a', 'b', 'c')]
        section = Section(questions=questions)
        correct_answers = ['1', '2', '3']

        # ACT
        section.set_correct_answers(correct_answers)

        # ASSERT
        self.assertEqual(section.questions[1].correct_answers, {'2'})

    def test_answer_is_correct(self):
        # ARRANGE
        question = Question('Vraag', correct_answers=[5])
        answer = Answer(question=question, answer=5)

        # ACT
        result = answer.is_correct()

        # ASSERT
        self.assertTrue(result)

    def test_score_response(self):
        # ARRANGE
        questions = [Question(correct_answers=[ca]) for ca in ('1', '2', '3')]
        answers = [Answer(question=q, answer=a) for q, a in zip(questions, ['1', '4', '3'])]
        response = Response(answers=answers)

        # ACT
        result = response.score()

        # ASSERT
        self.assertEqual(result, 2)


if __name__ == '__main__':
    unittest.main()
