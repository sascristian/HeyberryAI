# -*- coding: iso-8859-15 -*-
import unittest
from mycroft.util.format import solve_expression, extract_expression

__author__ = "jarbas"


class TestMathExtractFormat(unittest.TestCase):
    def test_extract_exps(self):
        self.assertEqual(
            extract_expression("do you think one plus two plus one are "
                               "relevant"),
            ([['1.0', '+', '2.0'], ['prev', '+', '1.0']], "do you think ___ "
                                                          "relevant"))

        self.assertEqual(
            extract_expression("how much is one dog plus one dog plus two "
                               "frogs"),
            ([['1.0dog', '+', '1.0dog'], ['prev', '+', '2.0frogs']],
             "how much ___"))

        self.assertEqual(
            extract_expression("ten factorial"),
            ([['10.0', '!', 'next']], "___"))

        self.assertEqual(
            extract_expression("square root of 4"),
            ([['4.0', 'sqrt', 'next']], "___"))

        self.assertEqual(
            extract_expression("one plus pi plus x"),
            ([['1.0', '+', 'pi'], ['prev', '+', 'x']], "___"))

        self.assertEqual(
            extract_expression("y divided by x"),
            ([['y', '/', 'x']], "___"))

        self.assertEqual(
            extract_expression("one times seven plus two multiply by two"),
            ([['1.0', '*', '7.0'], ['prev', '+', '2.0'], ['prev', '*',
                                                          '2.0']], "___"))

        self.assertEqual(
            extract_expression("six"),
            ([['0.0', '+', '6.0']], "___"))

    def test_solve_exps(self):
        self.assertEqual(
            solve_expression("one dog plus one dog plus two frogs"),
            "2dog + 2frogs")

        self.assertEqual(
            solve_expression("one dog plus one dog plus one plus two "
                             "frogs"),
            "2dog + 1 + 2frogs")

        self.assertEqual(
            solve_expression("one dog divided by one dog plus two frogs"),
            "1 + 2frogs")

        self.assertEqual(
            solve_expression("evil divided by evil plus two frogs"),
            "1 + 2frogs")

        self.assertEqual(
            solve_expression("one dog minus one dog plus 1"),
            "1")

        self.assertEqual(
            solve_expression("one dog minus one dog"),
            "0")

        self.assertEqual(
            solve_expression(
                "one dog plus one dog plus one dog plus two frogs"),
            "3dog + 2frogs")

        # TODO
        # self.assertEqual(
        #    solve_expression("one dog minus one dog plus one cat"),
        #    "1cat")

        # self.assertEqual(
        #   solve_expression("one dog multiplied by one dog plus two frogs"),
        #   "1dog squared + 2frogs")

        # self.assertEqual(
        #    solve_expression("one dog minus + one dog plus two frogs"),
        #    "2frogs")

        #      self.assertEqual(
        #           solve_expression("one dog minus one dog plus two frogs"),
        #            "2frogs")


        # TODO 3dog + 1 cat
        self.assertEqual(
            solve_expression("one dog plus one cat plus two dog"),
            "1dog + 1cat + 2dog")

        self.assertEqual(
            solve_expression("one plus two plus one"),
            '4')

        self.assertEqual(
            solve_expression("two squared"),
            '4')

        self.assertEqual(
            solve_expression("3 cubed"),
            '27')

        self.assertEqual(
            solve_expression("square root of four"),
            '2')

        self.assertEqual(
            solve_expression("x equals one plus two"),
            '3')  # TODO handle equals x = 3

        self.assertEqual(
            solve_expression("ten factorial"),
            '3628800')

        self.assertEqual(
            solve_expression("one plus pi plus x", nice=False),
            "4.14159265359 + x")

        self.assertEqual(
            solve_expression("one plus pi plus x", nice=True),
            "4 and a seventh + x")

        self.assertEqual(
            solve_expression("dog divided by frog"),
            "dog / frog")

        self.assertEqual(
            solve_expression("one times seven plus two multiply by two"),
            '11')

        self.assertEqual(
            solve_expression("six"),
            '6')


if __name__ == "__main__":
    unittest.main()
