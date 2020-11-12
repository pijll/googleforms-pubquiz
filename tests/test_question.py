import unittest

from googleformspubquiz import Question, Answer


class TestCorrectAnswers(unittest.TestCase):
    def test_correct_answers_property(self):
        # ARRANGE
        question = Question(correct_answers=['1', '4'])

        # ACT
        result = question.correct_answers

        # ASSERT
        self.assertEqual(result, {'1', '4'})

    def test_setting_correct_answers(self):
        # ARRANGE
        question = Question()

        # ACT
        question.correct_answers = ['1', '5']

        # ASSERT
        self.assertEqual(question.correct_answers, {'1', '5'})

    def test_add_correct_answer(self):
        # ARRANGE
        question = Question(correct_answers=['1', '2'])

        # ACT
        question.add_correct_answer('3')

        # ASSERT
        self.assertEqual(question.correct_answers, {'1', '2', '3'})

    def test_add_correct_answer__adding_existing_answer(self):
        # ARRANGE
        question = Question(correct_answers=['1', '2'])

        # ACT
        question.add_correct_answer('2')

        # ASSERT
        self.assertEqual(question.correct_answers, {'1', '2'})

    def test_remove_correct_answer(self):
        # ARRANGE
        question = Question(correct_answers=['1', '2'])

        # ACT
        question.remove_correct_answer('1')

        # ASSERT
        self.assertEqual(question.correct_answers, {'2'})


class TestAnswers(unittest.TestCase):
    def test_number_of_correct_responses(self):
        # ARRANGE
        question = Question(correct_answers=['3', '2'])
        for answer_string in ('1', '2', '3', '4', '5'):
            Answer(question=question, answer=answer_string)

        # ACT
        result = question.fraction_of_correct_responses()

        # ASSERT
        self.assertEqual(result, 2/5)

    def test_answer_list(self):
        # ARRANGE
        question = Question(correct_answers=['3', '6'])
        for answer_string in ('1', '3'):
            Answer(question=question, answer=answer_string)

        # ACT
        result = question.answer_list()

        # ASSERT
        self.assertEqual(len(result), 3)
        self.assertEqual(result['1'], 1)
        self.assertEqual(result['3'], 1)
        self.assertEqual(result['6'], 0)


if __name__ == '__main__':
    unittest.main()
