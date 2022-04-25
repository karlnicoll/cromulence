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

from cromulence.wordle.dictionary import (
    Dictionary,
    download_from_uri,
    _download_official_dictionary,
)
from cromulence.wordle.guess import Guess
from cromulence.wordle.game_response import GameResponse
from unittest.mock import MagicMock
import requests
import unittest


class TestDictionary(unittest.TestCase):
    def test_default_initialize_ranks_words(self):
        d = Dictionary(["ABC", "ABA", "XYZ"])
        output_wordlist = [word for word in d]
        expected_wordlist = ["ABA", "ABC", "XYZ"]

        # Scrabble scoring should have ranked these words.
        self.assertEqual(output_wordlist, expected_wordlist)

    def test_non_default_initialize_doesnt_rank_words(self):
        expected_wordlist = ["ABC", "ABA", "XYZ"]
        d = Dictionary(words=expected_wordlist, already_ranked=True)
        output_wordlist = [word for word in d]

        self.assertEqual(output_wordlist, expected_wordlist)

    def test_dictionary_provides_length(self):
        d = Dictionary(["ABC", "ABA", "XYZ"])
        expected_length = 3
        actual_length = len(d)

        self.assertEqual(expected_length, actual_length)

    def test_dictionary_provides_zero_length_when_dictionary_is_empty(self):
        d = Dictionary([])
        expected_length = 0
        actual_length = len(d)

        self.assertEqual(expected_length, actual_length)

    def test_dictionary_provides_correct_word_size(self):
        d = Dictionary(["ABC", "ABA", "XYZ"])
        expected_word_size = 3
        actual_word_size = d.word_size

        self.assertEqual(expected_word_size, actual_word_size)

    def test_dictionary_provides_zero_word_size_when_dictionary_is_empty(self):
        d = Dictionary([])
        expected_word_size = 0
        actual_word_size = d.word_size

        self.assertEqual(expected_word_size, actual_word_size)

    def test_most_likely_word_is_lowest_ranked(self):
        d = Dictionary(
            [
                "ABC",  # Score: 7
                "ABA",  # Score: 6 (second A is penalized to be score 2 since it is
                #                   repeated)
                "XYZ",  # Score: 22
            ]
        )
        expected_word = "ABA"
        actual_word = d.get_most_likely_word()

        self.assertEqual(expected_word, actual_word)

    def test_most_likely_word_is_none_when_dictionary_is_empty(self):
        d = Dictionary([])
        actual_word = d.get_most_likely_word()

        self.assertIsNone(actual_word)

    def test_prune(self):
        d = Dictionary(["ABC", "ABA", "XYZ"])

        guess = Guess(
            [
                ("B", GameResponse.ELSEWHERE),
                ("C", GameResponse.INCORRECT),
                ("D", GameResponse.INCORRECT),
            ]
        )

        # Guess should eliminate "ABC" and "XYZ" from the dictionary since "C"
        # is not a valid character in the answer, and "XYZ" doesn't contain
        # "B".
        d2 = d.prune(guess)
        output_wordlist = [word for word in d2]
        expected_wordlist = ["ABA"]

        # Scrabble scoring should have ranked these words.
        self.assertEqual(output_wordlist, expected_wordlist)

    def test_official_word_list_returns_dictionary(self):
        def fake_download_function():
            return ["ABC", "DEF", "GHI"]

        d = Dictionary.official(fake_download_function)
        expected_length = 3
        actual_length = len(d)

        self.assertEqual(expected_length, actual_length)

    def test_official_word_list_raises_error_when_empty_wordlist_returned(self):
        def fake_download_function():
            return None

        with self.assertRaises(RuntimeError):
            Dictionary.official(fake_download_function)


class TestDownloadFromUriHelper(unittest.TestCase):
    def test_successful_download(self):
        mock_download_fun = MagicMock()
        mock_download_fun.return_value = requests.Response()
        mock_download_fun.return_value.status_code = 200
        mock_download_fun.return_value._content = b"FOO"

        self.assertEqual("FOO", download_from_uri("http://test", mock_download_fun))

    def test_failed_download(self):
        mock_download_fun = MagicMock()
        mock_download_fun.return_value = requests.Response()
        mock_download_fun.return_value.status_code = 404
        mock_download_fun.return_value._content = b"FOO"

        self.assertIsNone(download_from_uri("http://test", mock_download_fun))


class TestDownloadOfficialWordleDictionary(unittest.TestCase):
    def test_successful_download(self):
        def fake_download_fun(uri):
            return_value = requests.Response()
            return_value.status_code = 200
            if uri == "https://www.nytimes.com/games/wordle/index.html":
                # When main wordle HTML is requested, return a script tag.
                return_value._content = (
                    b"<html>"
                    b'<script src="main.abcdef.js"></script>'
                    b'<script foo="bar">alert("foo");</script>'
                    b"</html>"
                )
            elif uri == "https://www.nytimes.com/games/wordle/main.abcdef.js":
                # When script contents is requested, return a fake (but valid)
                # Javascript block.
                return_value._content = (
                    b'stuff(); mo=["abc","def","ghi"]; more_stuff();'
                )
            else:
                return_value.status_code = 404
            return return_value

        expected_word_list = ["abc", "def", "ghi"]
        actual_word_list = _download_official_dictionary(fake_download_fun)

        self.assertEqual(expected_word_list, actual_word_list)

    def test_missing_index_page_triggers_null_word_list(self):
        def fake_download_fun(uri):
            return_value = requests.Response()
            return_value.status_code = 404
            return return_value

        actual_word_list = _download_official_dictionary(fake_download_fun)

        self.assertFalse(actual_word_list)

    def test_invalid_index_page_triggers_null_word_list(self):
        def fake_download_fun(uri):
            return_value = requests.Response()
            return_value.status_code = 200
            return_value._content = b'<html><script src="foo.js"></script></html>'
            return return_value

        actual_word_list = _download_official_dictionary(fake_download_fun)

        self.assertFalse(actual_word_list)

    def test_missing_word_list_in_javascript_triggers_null_word_list(self):
        def fake_download_fun(uri):
            return_value = requests.Response()
            return_value.status_code = 200
            if uri == "https://www.nytimes.com/games/wordle/index.html":
                return_value._content = (
                    b'<html><script src="main.abcdef.js"></script></html>'
                )
            elif uri == "https://www.nytimes.com/games/wordle/main.abcdef.js":
                return_value._content = b"stuff(); more_stuff();"
            else:
                return_value.status_code = 404
            return return_value

        actual_word_list = _download_official_dictionary(fake_download_fun)

        self.assertFalse(actual_word_list)

    def test_empty_word_list_in_javascript_triggers_empty_word_list(self):
        def fake_download_fun(uri):
            return_value = requests.Response()
            return_value.status_code = 200
            if uri == "https://www.nytimes.com/games/wordle/index.html":
                return_value._content = (
                    b'<html><script src="main.abcdef.js"></script></html>'
                )
            elif uri == "https://www.nytimes.com/games/wordle/main.abcdef.js":
                return_value._content = b"stuff(); mo=[]; more_stuff();"
            else:
                return_value.status_code = 404
            return return_value

        expected_word_list = []
        actual_word_list = _download_official_dictionary(fake_download_fun)

        self.assertEqual(expected_word_list, actual_word_list)
