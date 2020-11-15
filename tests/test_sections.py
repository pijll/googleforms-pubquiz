import io
import textwrap
import unittest

from googleformspubquiz import Section, Question, Response, Answer, Quiz, Team


class TestInit(unittest.TestCase):
    def test_initialization_with_quiz(self):
        # ARRANGE
        quiz = Quiz()

        # ACT
        section = Section(quiz=quiz)

        # ASSERT
        self.assertEqual(quiz.sections, (section,))
        self.assertEqual(section.quiz, quiz)


class TestReadLine(unittest.TestCase):
    def test_with_defaults(self):
        line = ['Date', 'Team', 'Answer1', 'Answer2', 'Answer3']

        # ACT
        result = Section._read_line(line)

        # ASSERT
        self.assertEqual(result.team_id, 'Team')
        self.assertEqual(result.team_name, 'Team')
        self.assertEqual(result.fields, ['Answer1', 'Answer2', 'Answer3'])

    def test_with_different_id_column(self):
        line = ['Date', 'Fluff', 'Team', 'Answer1', 'Answer2', 'Answer3']

        # ACT
        result = Section._read_line(line, teamid_column=2)

        # ASSERT
        self.assertEqual(result.team_id, 'Team')
        self.assertEqual(result.team_name, 'Team')
        self.assertEqual(result.fields, ['Fluff', 'Answer1', 'Answer2', 'Answer3'])

    def test_with_teamname(self):
        line = ['Date', 'Team name', 'Team id', 'Answer1', 'Answer2', 'Answer3']

        # ACT
        result = Section._read_line(line, teamid_column=2, teamname_column=1)

        # ASSERT
        self.assertEqual(result.team_id, 'Team id')
        self.assertEqual(result.team_name, 'Team name')
        self.assertEqual(result.fields, ['Answer1', 'Answer2', 'Answer3'])

    def test_with_quiz(self):
        section = Section()
        Quiz(sections=[section], teamid_column=2, teamname_column=1)
        line = ['Date', 'Team name', 'Team id', 'Answer1', 'Answer2', 'Answer3']

        # ACT
        result = section.read_line(line)

        # ASSERT
        self.assertEqual(result.team_id, 'Team id')
        self.assertEqual(result.team_name, 'Team name')
        self.assertEqual(result.fields, ['Answer1', 'Answer2', 'Answer3'])


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
        section.add_response_from_line(response)

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


class TestCsv(unittest.TestCase):
    def test_csv_from_string(self):
        # ARRANGE
        test_file = textwrap.dedent("""\
            "Timestamp","Teamnaam","Vraag 1","Vraag 2","Vraag 3"
            "2020/10/30 3:08:44 PM GMT+1","Correct answers","Antwoord 1","Antwoord 2","Antwoord 3"
            "2020/10/30 3:08:44 PM GMT+1","test","Antwoord 5","Antwoord 2","Antwoord 1"
        """)

        # ACT
        section = Section.read_csv(io.StringIO(test_file))

        # ASSERT
        self.assertIsInstance(section, Section)
        self.assertEqual(len(section.responses), 1)
        self.assertIsInstance(section.responses[0].team, Team)

    def test_csv_from_string_with_quiz(self):
        # ARRANGE
        test_file = textwrap.dedent("""\
            "Timestamp","Teamnaam","Vraag 1","Vraag 2","Vraag 3"
            "2020/10/30 3:08:44 PM GMT+1","Correct answers","Antwoord 1","Antwoord 2","Antwoord 3"
            "2020/10/30 3:08:44 PM GMT+1","test","Antwoord 5","Antwoord 2","Antwoord 1"
        """)
        quiz = Quiz()

        # ACT
        section = Section.read_csv(io.StringIO(test_file), quiz=quiz)

        # ASSERT
        self.assertEqual(len(quiz.teams), 1)


class TestTeams(unittest.TestCase):
    def test_create_team(self):
        section = Section()

        # ACT
        result = section.get_team('12', 'test team')

        # ASSERT
        self.assertIsInstance(result, Team)
        self.assertEqual(result.team_id, '12')
        self.assertEqual(result.name, 'test team')

    def test_create_new_team_with_quiz(self):
        quiz = Quiz()
        section = Section(quiz=quiz)

        # ACT
        result = section.get_team('12', 'test team')

        # ASSERT
        self.assertIsInstance(result, Team)
        self.assertEqual(result.team_id, '12')
        self.assertEqual(result.name, 'test team')

        self.assertEqual(len(quiz.teams), 1)

    def test_get_existing_team_with_quiz(self):
        quiz = Quiz()
        section = Section(quiz=quiz)
        team = Team('12', 'test team')
        quiz.teams = [team]

        # ACT
        result = section.get_team('12', 'test team')

        # ASSERT
        self.assertEqual(result, team)
        self.assertEqual(len(quiz.teams), 1)


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


class TestYaml(unittest.TestCase):
    def test_save_answers(self):
        # ARRANGE
        questions = [Question(name='Question '+ca, correct_answers=['Answer '+ca]) for ca in ('1', '2', '3')]
        section = Section(questions=questions)
        out_stream = io.StringIO()

        # ACT
        section.save_answers(out_stream)

        # ASSERT
        self.assertEqual(out_stream.getvalue(), textwrap.dedent("""\
            - - Answer 1
            - - Answer 2
            - - Answer 3
        """))

    def test_load_answers(self):
        # ARRANGE
        questions = [Question(name='Question '+ca) for ca in ('1', '2', '3')]
        section = Section(questions=questions)
        in_stream = io.StringIO(textwrap.dedent("""\
            - - Answer 1
            - - Answer 2
            - - Answer 3
        """))

        # ACT
        section.load_answers(in_stream)

        # ASSERT
        self.assertEqual(list(questions[0].correct_answers), ['Answer 1'])


if __name__ == '__main__':
    unittest.main()
