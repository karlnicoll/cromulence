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

import html.parser
import json
import logging
import re
import requests
from typing import Callable, Generator, List, Optional, Protocol

from .guess import Guess


class _DownloadOfficialDictionaryFunc(Protocol):
    def __call__(
        self, download_fun: Callable[[str], requests.Response] = ...
    ) -> List[str]:  # pragma: no cover
        ...


def _download_official_dictionary(
    download_fun: Callable[[str], requests.Response] = requests.get
) -> List[str]:
    """Download the default dictionary from the official Wordle game.

    This will use web requests to download the game's JavaScript code files,
    and parse the dictionary.

    Args:
        uri: The URL to find the JavaScript links to download.
        download_fun: The function to execute to download the web page.

    Returns:
        A list of words, or None if the download failed.
    """
    uri_prefix = "https://www.nytimes.com/games/wordle"
    initial_page_uri = f"{uri_prefix}/index.html"
    logging.info(f"Downloading default dictionary from '{initial_page_uri}'...")
    logging.debug(f"Downloading initial HTML content from '{initial_page_uri}'...")
    main_html = download_from_uri(initial_page_uri, download_fun)
    if not main_html:
        logging.error(f"Failed to download content from '{initial_page_uri}'!")
        return []

    logging.debug("Regex matching main JavaScript file...")
    script_name = _get_script_name_from_html(main_html)

    if not script_name:
        logging.error("Wordle game script not found!")
        return []

    script_uri = f"{uri_prefix}/{script_name}"
    js = download_from_uri(script_uri, download_fun)

    if not js:
        logging.error(f"Failed to get source for script '{script_uri}'")
        return []

    logging.debug("Searching for word list...")
    match_data = re.search(r"(?<=mo=)\[[^]]*\]", js)

    if not match_data:
        logging.error("Failed to find word list.")
        return []

    return json.loads(match_data[0])


class Dictionary:
    """Dictionary object that represents the wordle word universe.

    The dictionary can be pruned by passing a GuessResponse object to it. The
    GuessResponse object

    Example:

        To query the guesses list::

            guess = Guess([
                ("C", GameResponse.CORRECT),
                ("I", GameResponse.ELSEWHERE),
                ("G", GameResponse.INCORRECT),
                ("A", GameResponse.ELSEWHERE),
                ("R", GameResponse.INCORRECT)
            ])

            d = Dictionary(words=[...])
            d = d.prune(guess)
    """

    def __init__(self, words: List[str], already_ranked=False):
        """Constructor.

        Args:
            words:
                word list.
            already_ranked:
                True when word list is already ranked, or False if the list
                needs ranking in the constructor. If in doubt, use the default
                value (False).
        """

        if already_ranked:
            self._word_list = [word.upper() for word in words]
        else:
            self._word_list = _rank_wordlist(words)

    def __iter__(self) -> Generator[str, None, None]:
        """Iterate the words in the dictionary."""
        for word in self._word_list:
            yield word

    def __len__(self) -> int:
        """Get the number of words in the dictionary"""
        return len(self._word_list)

    @property
    def word_size(self) -> int:
        """Get the size of the words in this dictionary.

        Since this dictionary is for wordle-style guessing games, the
        dictionary assumes that all words are the same length.
        """
        if self._word_list:
            return len(self._word_list[0])
        else:
            return 0

    def get_most_likely_word(self):
        """Get the top ranked word in the dictionary.

        Words are ranked using Scrabble-style point scores per-letter. Word
        with the lowest score is considered the most likely word.

        Returns:
            A string containing the best next guess, or ``None`` if the
            dictionary is empty.
        """
        if self._word_list:
            return self._word_list[0]
        else:
            return None

    def prune(self, guess: Guess) -> "Dictionary":
        """Create a copy of this dictionary containing only the words that
        could match the provided guess.
        """
        return Dictionary(
            words=[word for word in filter(guess.match, self._word_list)],
            already_ranked=True,
        )

    @staticmethod
    def official(
        download_fun: _DownloadOfficialDictionaryFunc = _download_official_dictionary,
    ) -> "Dictionary":
        """Download the official Wordle dictionary from the New York Times.

        Returns:
            A dictionary object.

        Raises:
            RuntimeError: Download of word list failed.
        """
        word_list = download_fun()
        if not word_list:
            raise RuntimeError("Unable to download word list.")

        return Dictionary(word_list)


class _JSFileExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.script_names = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            logging.debug(f"Ignoring HTML tag '{tag}'.")
            return

        for tpl in attrs:
            if tpl[0] == "src":
                logging.debug(f"Adding script source '{tpl[1]}'.")
                self.script_names.append(str(tpl[1]))


def download_from_uri(
    uri: str = "https://www.nytimes.com/games/wordle/index.html",
    download_fun: Callable[[str], requests.Response] = requests.get,
) -> Optional[str]:
    """Download an object as a string from a given URI.

    Args:
        uri: The URI to find the content.
        download_fun: The function to execute to download the web page.

    Returns:
        A string. None is returned if the request failed.
    """
    logging.debug(f"Downloading content from uri '{uri}'...")

    response = download_fun(uri)

    if response.ok:
        logging.debug(f"Download of '{uri}' successful!")
        return response.text
    else:
        logging.error(
            f"Download of '{uri}' failed! Response code: {response.status_code}"
        )
        return None


def _get_script_name_from_html(main_html: str):
    html_parser = _JSFileExtractor()
    html_parser.feed(main_html)
    script_names = html_parser.script_names

    logging.debug(f"Found scripts: {script_names}")

    for name in script_names:
        if re.match(r"main.[0-9a-fA-F]+.js", name):
            logging.debug(f"Found expected script: '{name}'.")
            return name
        logging.debug(f"Script not matching regex: '{name}'.")

    return ""


def _rank_wordlist(words: List[str]) -> List[str]:
    """Rank a given wordlist using scrabble-style scorings.

    Lower values are better.
    """
    upper_words = [word.upper() for word in words]
    sorted_order = sorted(
        [(i, _score_word(word)) for i, word in enumerate(upper_words)],
        key=lambda pair: pair[1],
    )

    return [upper_words[i] for i, _ in sorted_order]


def _score_word(word: str) -> int:
    """Score a word based on the commonality of it's letters.

    Repeated occurrences of letters are penalized."""
    scores = [
        1,
        3,
        3,
        2,
        1,
        4,
        2,
        4,
        1,
        8,
        5,
        1,
        3,  # A-M
        1,
        1,
        3,
        10,
        1,
        1,
        1,
        1,
        4,
        4,
        8,
        4,
        10,  # N-Z
    ]

    final_score = 0
    for ch in word:
        array_index = ord(ch) - ord("A")
        final_score += scores[array_index]

        # Increase the score of any future occurrences of the same character.
        scores[array_index] += 1

    return final_score
