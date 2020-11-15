import os
import pathlib
import textwrap
import unittest

from googleformspubquiz import Quiz, Section, Team, Response


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
        self.assertEqual(result.name, 'test team')

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


class TestMergeTeams(unittest.TestCase):
    def test_when_sections_of_teams_dont_overlap_expect_can_be_merged(self):
        # ARRANGE
        quiz = Quiz()
        section1 = Section(quiz=quiz)
        team1 = quiz.get_team(1, 'test_1')
        section1.add_response(Response(team=team1))

        section2 = Section(quiz=quiz)
        team2 = quiz.get_team(2, 'test_2')
        section2.add_response(Response(team=team2))

        # ACT
        result = quiz.can_merge_teams([team1, team2])

        # ASSERT
        self.assertTrue(result)

    def test_when_only_one_team_expect_cannot_be_merged(self):
        # ARRANGE
        quiz = Quiz()
        team = quiz.get_team(1, 'team 1')

        # ACT
        result = quiz.can_merge_teams([team])

        # ASSERT
        self.assertFalse(result)

    def test_when_no_team_expect_cannot_be_merged(self):
        # ARRANGE
        quiz = Quiz()

        # ACT
        result = quiz.can_merge_teams([])

        # ASSERT
        self.assertFalse(result)

    def test_when_teams_in_same_section_expect_cannot_be_merged(self):
        # ARRANGE
        quiz = Quiz()
        section = Section(quiz=quiz)
        team1 = quiz.get_team(1, 'test_1')
        section.add_response(Response(team=team1))

        team2 = quiz.get_team(2, 'test_2')
        section.add_response(Response(team=team2))

        # ACT
        result = quiz.can_merge_teams([team1, team2])

        # ASSERT
        self.assertFalse(result)

    def test_when_merging_teams_expect_only_one_team_remains(self):
        # ARRANGE
        quiz = Quiz()
        team1 = quiz.get_team(1, 'test_1')
        team2 = quiz.get_team(2, 'test_2')

        # ACT
        quiz.merge_teams([team1, team2])

        # ASSERT
        self.assertIn(team1, quiz.teams)
        self.assertNotIn(team2, quiz.teams)

    def test_when_merging_teams_expect_team_in_section_changes(self):
        # ARRANGE
        quiz = Quiz()
        section = Section(quiz=quiz)
        team1 = quiz.get_team(1, 'test_1')
        team2 = quiz.get_team(2, 'test_2')
        section.add_response(Response(team=team2))

        # ACT
        quiz.merge_teams([team1, team2])

        # ASSERT
        self.assertEqual(len(section.responses), 1)
        self.assertEqual(section.responses[0].team, team1)

    def test_when_merging_teams_expect_scores_are_added(self):
        # ARRANGE
        quiz = Quiz()
        section1 = Section(quiz=quiz)
        team1 = quiz.get_team(1, 'test_1')
        response1 = Response(team=team1)
        response1.score = lambda: 4
        section1.add_response(response1)

        section2 = Section(quiz=quiz)
        team2 = quiz.get_team(2, 'test_2')
        response2 = Response(team=team2)
        response2.score = lambda: 5
        section2.add_response(response2)

        # ACT
        quiz.merge_teams([team1, team2])

        # ASSERT
        self.assertEqual(section2.scores(), {team1: 5})
        self.assertEqual(quiz.scores(), {team1: 9})

    def test_when_merging_teams_and_both_in_section_expect_failure(self):
        # ARRANGE
        quiz = Quiz()
        section = Section(quiz=quiz)
        team1 = quiz.get_team(1, 'test_1')
        section.add_response(Response(team=team1))
        team2 = quiz.get_team(2, 'test_2')
        section.add_response(Response(team=team2))

        # ACT
        with self.assertRaises(Exception):
            quiz.merge_teams([team1, team2])

        # ASSERT
        pass


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


def make_teams(teamscores):
    quiz = Quiz()
    for i, teamscore in enumerate(teamscores, start=1):
        quiz.get_team(i, 'team {}'.format(i))

    for section_nr in range(len(teamscores[0])):
        section = Section(name='section {}'.format(section_nr), quiz=quiz)
        section.scores = lambda i=section_nr: {quiz.teams[j]: t[i] for j, t in enumerate(teamscores)}

    return quiz


class TestScoring(unittest.TestCase):
    def test_leaderboard_with_one_team(self):
        quiz = make_teams([[2, 3, 4]])

        # ACT
        result = list(quiz.leaderboard())

        # ASSERT
        self.assertEqual(result, [['1', 'team 1', '9']])

    def test_leaderboard_with_two_teams(self):
        # ARRANGE
        quiz = make_teams([[2, 3, 4], [1, 4, 1]])

        # ACT
        result = list(quiz.leaderboard())

        # ASSERT
        self.assertEqual(result, [['1', 'team 1', '9'], ['2', 'team 2', '6']])

    def test_leaderboard_with_two_teams_ex_aequo(self):
        # ARRANGE
        quiz = make_teams([[2, 3, 4], [1, 4, 4]])

        # ACT
        result = list(quiz.leaderboard())

        # ASSERT
        self.assertEqual(result, [['1', 'team 1', '9'], ['', 'team 2', '9']])


if __name__ == '__main__':
    unittest.main()
