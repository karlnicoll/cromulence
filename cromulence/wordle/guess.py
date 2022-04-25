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

from typing import List, Tuple
from .game_response import GameResponse, game_response_to_str


class Guess:
    """A representation of a guess given back to the user by the game.

    A guess response is a string-like type that holds a list of characters and
    the games responses.

    Example:

        # List of tuples containing the letters in the guess, as well as the
        # game's response to those characters.
        guess_characters = [
            ("C", GameResponse.CORRECT),
            ("I", GameResponse.ELSEWHERE),
            ("G", GameResponse.INCORRECT),
            ("A", GameResponse.ELSEWHERE),
            ("R", GameResponse.INCORRECT)
        ]

        response = Guess(guess_characters)
        print(response)
        # [C(✓)][I(⟷)][G(x)][A(⟷)][R(x)]
    """

    def __init__(self, parts: List[Tuple[str, GameResponse]]):
        """Constructor:

        Args:
            parts: Parts of the response.
        """
        self._parts = [(ch.upper(), game_response) for ch, game_response in parts]

        for ch, _ in self._parts:
            if len(ch) != 1:
                raise ValueError(
                    "Tuple first element must be a single unicode character"
                )

    def match(self, word: str) -> bool:
        """Check to see if a given word could potentially be a valid answer,
        given the game's response to this guess.

        Args:
            word: The word to check.

        Returns:
            True if the word could be a valid answer, or False otherwise.
        """
        word = word.upper()
        character_matched_list = [False] * len(word)

        # Matching is done in three steps:
        #
        # 1. Scan the "CORRECT" matches, and make sure that the word has
        #    the correct character at those locations.
        # 2. Scan the "ELSEWHERE" matches, and make sure that these characters
        #    are present in the word, but not at the specified index, and not
        #    if already matched by rule #1.
        # 3. Scan the INCORRECT matches, and make sure that the guess character
        #    is not present anywhere in the string, unless already matched by
        #    #1 amd #2.
        match_functions = [
            self._match_correct,
            self._match_elsewhere,
            self._match_incorrect,
        ]
        for match_fun in match_functions:
            match_result, character_matched_list = match_fun(
                word, character_matched_list
            )

            if not match_result:
                # Word did not meet the criteria for the match function, return
                # early.
                return False

        return True

    def __repr__(self) -> str:
        return "".join(
            [_character_to_str(ch, game_response) for ch, game_response in self._parts]
        )

    def __str__(self) -> str:
        return "".join([ch for ch, _ in self._parts])

    def _match_correct(
        self, word: str, character_matched_list: List[bool]
    ) -> Tuple[bool, List[bool]]:
        """Check a given word to see if any characters in this guess that were
        marked by the game as "CORRECT" are in the correct place in the word.

        Args:
            word:
                The word to match against the guess.
            character_matched_list:
                List of booleans. Each True indicates a letter already matched
                by a previous rule, and should be excluded from matched by this
                rule.

        Returns:
            A tuple.

            Element 1 is a single boolean, set to True if the word was a
            successful match, or False if any character was out of place or
            incorrect.

            Element 2 is a list of booleans, each True item in the list
            indicates that the letter was matched in this function and should
            not be used as a match candidate in other match functions (i.e.
            ``self._match_elsewhere()`` and ``self._match_incorrect()``).
        """

        character_matched_list = [False] * len(word)
        for i, tpl in enumerate(self._parts):
            guess_character, game_response = tpl
            if game_response == GameResponse.CORRECT:
                if word[i] != guess_character:
                    # Character doesn't match. Instant fail.
                    return (False, character_matched_list)

                # Mark this character as matched, so that the fuzzy matches
                # (ELSEWHERE) don't try to reuse these values.
                character_matched_list[i] = True

        return (True, character_matched_list)

    def _match_elsewhere(
        self, word: str, character_matched_list: List[bool]
    ) -> Tuple[bool, List[bool]]:
        """Check a given word to see if any characters in this guess that were
        marked by the game as "ELSEWHERE" are at any allowed location in the
        word.

        Args:
            word:
                The word to match against the guess.
            character_matched_list:
                List of booleans. Each True indicates a letter already matched
                by a previous rule, and should be excluded from matched by this
                rule.

        Returns:
            A tuple.

            Element 1 is a single boolean, set to True if the word was a
            successful match, or False if any character was out of place or
            incorrect.

            Element 2 is a list of booleans, each True item in the list
            indicates that the letter was matched in this function and should
            not be used as a match candidate in other match functions (i.e.
            ``self._match_incorrect()``).
        """

        for i, tpl in enumerate(self._parts):
            guess_character, game_response = tpl

            if game_response == GameResponse.ELSEWHERE:
                if word[i] == guess_character:
                    # Character is at this location, instant fail (ELSEWHERE
                    # means that the character must appear in this string, but
                    # not at index i).
                    return (False, character_matched_list)

                match_found = False
                for j, ch in enumerate(word):
                    # Note that the full word is scanned, even if we find a
                    # match. If the word contains multiple of the same letter,
                    # there may be multiple valid locations for this character.
                    if (character_matched_list[j]) or (ch != guess_character):
                        continue

                    guess_character_at_j, game_response_at_j = self._parts[j]
                    guess_character_at_j_matches = (
                        guess_character_at_j == guess_character
                    )
                    character_allowed_at_j = game_response_at_j == GameResponse.CORRECT
                    if guess_character_at_j_matches and not character_allowed_at_j:
                        # If the character matches, but the game disallows
                        # this character at this location, continue looking...
                        continue

                    # Guess doesn't care that ch is at this location, so
                    # consider it a match.
                    character_matched_list[j] = True
                    match_found = True

                if not match_found:
                    # Elsewhere means that the character must appear somewhere.
                    # If no match found in the word, word is not a potential
                    # correct answer based on this guess.
                    return (False, character_matched_list)

        return (True, character_matched_list)

    def _match_incorrect(
        self, word: str, character_matched_list: List[bool]
    ) -> Tuple[bool, List[bool]]:
        """Check a given word to see if any characters in this guess that were
        marked by the game as "ELSEWHERE" are at any allowed location in the
        word.

        Args:
            word:
                The word to match against the guess.
            character_matched_list:
                List of booleans. Each True indicates a letter already matched
                by a previous rule, and should be excluded from matched by this
                rule.

        Returns:
            A tuple.

            Element 1 is a single boolean, set to True if the word was a
            successful match, or False if any character was out of place or
            incorrect.

            Element 2 is a list of booleans, each True item in the list
            indicates that the letter was matched in this function and should
            not be used as a match candidate in other match functions (i.e.
            ``self._match_incorrect()``).
        """

        for i, tpl in enumerate(self._parts):
            guess_character, game_response = tpl

            if game_response == GameResponse.INCORRECT:
                for j, ch in enumerate(word):
                    if (ch == guess_character) and (not character_matched_list[j]):
                        return (False, character_matched_list)

                character_matched_list[i] = True

        return (True, character_matched_list)


def _character_to_str(character, game_response):
    return f"[{character}({game_response_to_str(game_response)})]"
