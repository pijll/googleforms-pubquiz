import os
import pathlib
import textwrap
import unittest

from googleformspubquiz import Quiz, Section, Team


class TestQuiz(unittest.TestCase):
    def test_initialization_with_section(self):
        # ARRANGE
        section = Section()

        # ACT
        quiz = Quiz(sections=[section])

        # ASSERT
        self.assertEqual(quiz.sections, (section,))
        self.assertEqual(section.quiz, quiz)


class TestTeams(unittest.TestCase):
    def test_create_new_team_with_quiz(self):
        quiz = Quiz()

        # ACT
        result = quiz.get_team('12', 'test team')

        # ASSERT
        self.assertIsInstance(result, Team)
        self.assertEqual(result.team_id, '12')
        self.assertEqual(result.team_name, 'test team')

        self.assertEqual(len(quiz.teams), 1)

    def test_get_existing_team_with_quiz(self):
        quiz = Quiz()
        team = Team('12', 'test team')
        quiz.teams = [team]

        # ACT
        result = quiz.get_team('12', 'testing team')

        # ASSERT
        self.assertEqual(result, team)
        self.assertEqual(len(quiz.teams), 1)


class TestLoadFromDirectory(unittest.TestCase):
    def test_load_from_csv(self):
        # ARRANGE
        testdir = pathlib.Path(__file__).parent / 'testdata' / 'test_load_csv'
        os.makedirs(testdir, exist_ok=True)
        for file in testdir.iterdir():
            if file.suffix in ['.csv', '.zip']:
                file.unlink()

        csv_file = testdir / 'round1.csv'
        csv_file.write_text(textwrap.dedent("""\
            "Timestamp","Team","Vraag 1","Vraag 2","Vraag 3"
            "2020/10/30 3:08:44 PM GMT+1","Correct answers","Antwoord 1","Antwoord 2","Antwoord 3"
            "2020/10/30 3:08:44 PM GMT+1","test","Antwoord 5","Antwoord 2","Antwoord 1"
        """))

        # ACT
        result = Quiz.load_dir(testdir)

        # ASSERT
        self.assertIsInstance(result, Quiz)
        self.assertEqual(len(result.sections), 1)
        self.assertIsInstance(result.sections[0], Section)
        self.assertEqual(result.sections[0].name, 'round1')

        self.assertEqual(len(result.teams), 1)
        self.assertIsInstance(result.teams[0], Team)
        self.assertEqual(result.teams[0].team_id, 'test')


if __name__ == '__main__':
    unittest.main()
