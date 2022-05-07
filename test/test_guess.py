#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2022 Karl Nicoll
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from cromulence.wordle.game_response import GameResponse
from cromulence.wordle.guess import Guess
import unittest


class TestGuess(unittest.TestCase):
    def test_initialize(self):
        g = Guess(
            [
                ("f", GameResponse.CORRECT),
                ("o", GameResponse.ELSEWHERE),
                ("o", GameResponse.INCORRECT),
            ]
        )

        expected = "[F(✓)][O(⟷)][O(x)]"
        actual = repr(g)

        self.assertEqual(expected, actual)

    def test_invalid_char_raises(self):
        with self.assertRaises(ValueError):
            Guess(
                [
                    ("this_is_not_a_single_character", GameResponse.CORRECT),
                    ("o", GameResponse.ELSEWHERE),
                    ("o", GameResponse.INCORRECT),
                ]
            )

    def test_match_correct_word(self):
        g = Guess(
            [
                ("f", GameResponse.CORRECT),
                ("o", GameResponse.CORRECT),
                ("o", GameResponse.CORRECT),
            ]
        )

        actual = g.match("fOo")

        self.assertTrue(actual)

    def test_match_reversed_string_still_matches(self):
        g = Guess(
            [
                ("f", GameResponse.ELSEWHERE),
                ("o", GameResponse.CORRECT),
                ("o", GameResponse.ELSEWHERE),
            ]
        )

        actual = g.match("oof")

        self.assertTrue(actual)

    def test_match_wrong_character_in_start_location_returns_false(self):
        g = Guess(
            [
                ("f", GameResponse.CORRECT),
                ("o", GameResponse.CORRECT),
                ("o", GameResponse.CORRECT),
            ]
        )

        actual = g.match("woo")

        self.assertFalse(actual)

    def test_match_missing_character_returns_false(self):
        g = Guess(
            [
                ("f", GameResponse.ELSEWHERE),
                ("o", GameResponse.CORRECT),
                ("o", GameResponse.CORRECT),
            ]
        )

        actual = g.match("woo")

        self.assertFalse(actual)

    def test_match_duplicated_character(self):
        g = Guess(
            [
                ("f", GameResponse.ELSEWHERE),
                ("o", GameResponse.ELSEWHERE),
                ("o", GameResponse.INCORRECT),
            ]
        )

        actual = g.match("off")

        self.assertTrue(actual)

    def test_match_duplicated_character2(self):
        g = Guess(
            [
                ("g", GameResponse.INCORRECT),
                ("r", GameResponse.ELSEWHERE),
                ("e", GameResponse.ELSEWHERE),
                ("e", GameResponse.INCORRECT),
                ("n", GameResponse.INCORRECT),
            ]
        )

        actual = g.match("acrue")

        self.assertTrue(actual)

    def test_match_duplicated_character_in_answer(self):
        g = Guess(
            [
                ("a", GameResponse.INCORRECT),
                ("c", GameResponse.INCORRECT),
                ("r", GameResponse.ELSEWHERE),
                ("u", GameResponse.INCORRECT),
                ("e", GameResponse.ELSEWHERE),
            ]
        )

        actual = g.match("green")

        self.assertTrue(actual)

    def test_match_anagram(self):
        g = Guess(
            [
                ("a", GameResponse.ELSEWHERE),
                ("b", GameResponse.ELSEWHERE),
                ("c", GameResponse.ELSEWHERE),
                ("d", GameResponse.ELSEWHERE),
                ("e", GameResponse.ELSEWHERE),
            ]
        )

        actual = g.match("ecabd")

        self.assertTrue(actual)

    def test_all_repeated_characters_in_word_with_all_elsewhere_responses_in_guess(
        self,
    ):
        g = Guess(
            [
                ("a", GameResponse.ELSEWHERE),
                ("b", GameResponse.ELSEWHERE),
                ("c", GameResponse.ELSEWHERE),
                ("d", GameResponse.ELSEWHERE),
                ("e", GameResponse.ELSEWHERE),
            ]
        )

        actual = g.match("aaaaa")

        # This should not match, no "b", "c", "d", or "e"
        self.assertFalse(actual)

    def test_elsewhere_followed_by_incorrect_fails(
        self,
    ):
        g = Guess(
            [
                ("f", GameResponse.CORRECT),
                ("o", GameResponse.ELSEWHERE),
                ("o", GameResponse.INCORRECT),
            ]
        )

        actual = g.match("fio")

        # Won't match, because the "o" in "fio" is marked as incorrect, even
        # though the first "o" is marked as ELSEWHERE.
        #
        # NOTE: No answer can exist for this example feedback; "f" is correct,
        # but "o" can't be in either index 1 or 2, so no acceptable answer
        # exists.
        self.assertFalse(actual)

    def test_guess_with_double_character_allows_answer_with_double_character(
        self,
    ):
        g = Guess(
            [
                ("w", GameResponse.INCORRECT),
                ("o", GameResponse.ELSEWHERE),
                ("r", GameResponse.ELSEWHERE),
                ("r", GameResponse.ELSEWHERE),
                ("y", GameResponse.INCORRECT),
            ]
        )

        actual = g.match("order")

        # Should match
        self.assertTrue(actual)

    def test_guess_with_double_character_disallows_answer_with_single_character(
        self,
    ):
        g = Guess(
            [
                ("w", GameResponse.INCORRECT),
                ("o", GameResponse.ELSEWHERE),
                ("r", GameResponse.ELSEWHERE),
                ("r", GameResponse.ELSEWHERE),
                ("y", GameResponse.INCORRECT),
            ]
        )

        actual = g.match("odour")

        # Should match
        self.assertFalse(actual)

    def test_str(self):
        g = Guess(
            [
                ("f", GameResponse.CORRECT),
                ("o", GameResponse.ELSEWHERE),
                ("o", GameResponse.INCORRECT),
            ]
        )

        expected = "FOO"
        actual = str(g)

        self.assertEqual(expected, actual)

    def test_repr(self):
        g = Guess(
            [
                ("f", GameResponse.CORRECT),
                ("o", GameResponse.ELSEWHERE),
                ("o", GameResponse.INCORRECT),
            ]
        )

        expected = "[F(✓)][O(⟷)][O(x)]"
        actual = repr(g)

        self.assertEqual(expected, actual)
