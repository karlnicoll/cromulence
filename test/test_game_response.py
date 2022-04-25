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

from cromulence.wordle.game_response import GameResponse, game_response_to_str
import unittest


class TestGameResponseToStr(unittest.TestCase):
    def test_incorrect(self):
        expected = "x"
        actual = game_response_to_str(GameResponse.INCORRECT)

        self.assertEqual(expected, actual)

    def test_elsewhere(self):
        expected = "⟷"
        actual = game_response_to_str(GameResponse.ELSEWHERE)

        self.assertEqual(expected, actual)

    def test_correct(self):
        expected = "✓"
        actual = game_response_to_str(GameResponse.CORRECT)

        self.assertEqual(expected, actual)

    def test_invalid(self):
        expected = "?"
        actual = game_response_to_str(999)

        self.assertEqual(expected, actual)
