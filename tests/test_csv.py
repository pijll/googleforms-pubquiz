import io
import textwrap
import unittest

from googleformspubquiz import Section, Quiz


class TestCsv(unittest.TestCase):
    def test_csv_uit_string(self):
        # ARRANGE
        testbestand = textwrap.dedent("""\
            "Timestamp","Teamnaam","Vraag 1","Vraag 2","Vraag 3"
            "2020/10/30 3:08:44 PM GMT+1","Correct answers","Antwoord 1","Antwoord 2","Antwoord 3"
            "2020/10/30 3:08:44 PM GMT+1","test","Antwoord 5","Antwoord 2","Antwoord 1"
        """)

        # ACT
        section = Section.read_csv(io.StringIO(testbestand))

        # ASSERT
        self.assertIsInstance(section, Section)
        self.assertEqual(section.scores(), {'test': 1})


class TestLoadQuiz(unittest.TestCase):
    def test_load(self):
        # ARRANGE
        testdir = r'/home/pijll/PycharmProjects/GoogleFormsPubquiz/tests/testdata'

        # ACT
        result = Quiz.load_dir(testdir)

        # ASSERT
        self.assertIsInstance(result, Quiz)
        self.assertEqual(len(result.sections), 1)
        self.assertIsInstance(result.sections[0], Section)
        self.assertEqual(result.sections[0].name, 'Pubquiz 2020')


if __name__ == '__main__':
    unittest.main()
