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

from enum import auto, Enum, unique


@unique
class GameResponse(Enum):
    """A response given by the game to the user to inform them how accurate
    their guess was.

    **Values:**

    INCORRECT
        Guessed character is not in the answer.
    ELSEWHERE
        Guessed character is in the answer, but not where the user put it
        ("yellow response").
    CORRECT
        Guessed character is in the answer at the correct location ("green
        response").
    """

    INCORRECT = auto()
    ELSEWHERE = auto()
    CORRECT = auto()


def game_response_to_str(response: GameResponse):
    """Convert a Response enum value to a unicode string character.

    Returns:
        A single unicode character, one of "x", "⟷", or "✓". If an unsupported
        enum value is passed as an argument, "?" is returned.
    """

    if response == GameResponse.INCORRECT:
        return "x"
    if response == GameResponse.ELSEWHERE:
        return "⟷"
    if response == GameResponse.CORRECT:
        return "✓"

    return "?"
