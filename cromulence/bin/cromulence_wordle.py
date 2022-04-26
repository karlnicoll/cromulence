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


import re
import click
import logging

from cromulence.wordle import Dictionary, GameResponse, Guess

logging.basicConfig(level=logging.INFO)


def gyb_to_game_response_enum(gyb_value: str) -> GameResponse:
    """Convert a "G", "Y", or "B" response to the equivalent GameResponse value.

    Conversion Table
    ================

    +----------------+------------------------+
    | User Character | GameResponse Value     |
    +================+========================+
    |       G        | GameResponse.CORRECT   |
    +----------------+------------------------+
    |       Y        | GameResponse.ELSEWHERE |
    +----------------+------------------------+
    |       B        | GameResponse.INCORRECT |
    +----------------+------------------------+

    Args:
        gyb_value: the user entered 'G'reen, 'Y'ellow, or 'B'lack value.

    Returns:
        A GameResponse enum value.

    Raises:
        ValueError: gyb_value is not one of "G", "Y", or "B".
    """
    if gyb_value == "G":
        return GameResponse.CORRECT
    if gyb_value == "Y":
        return GameResponse.ELSEWHERE
    if gyb_value == "B":
        return GameResponse.INCORRECT

    raise ValueError(f"{gyb_value} is not a supported GYB value.")


def convert_to_guess(word: str, gyb: str) -> Guess:
    """Convert a user's command line input to a cromulence.wordle.Guess object.

    Args:
        word:
            The guess word provided by this application initially.
        gyb:
            The user's "G", "Y", and "B" entry representing the game's response.

    Returns:
        A Guess object.
    """
    if len(word) != len(gyb):
        raise ValueError("Word and GYB values must be the same size")

    return Guess(
        [(word[i], gyb_to_game_response_enum(gyb[i])) for i in range(len(word))]
    )


@click.command()
def main():
    click.echo("Downloading official Wordle dictionary...")
    try:
        d = Dictionary.official()
    except RuntimeError:
        click.echo("Failed to get Wordle dictionary!")
        raise click.Abort()
    click.echo("Success!")
    click.echo(f"Initial dictionary size: {len(d)} entries")

    click.echo("(This command will ask for input until exited using CTRL+C)")
    current_guess = d.get_most_likely_word()
    click.echo(f"Try '{current_guess}' as your initial guess.")

    click.echo("Enter the game's response in the following format:")
    click.echo("'G'reen, 'Y'ellow, or 'B'lack.")
    click.echo("")
    click.echo("Example:")
    click.echo(">>> GBBYB")

    while d:
        gyb_values = click.prompt(
            "Enter the Game's Response (GYB)", default="", type=str
        )

        if len(gyb_values) != len(current_guess):
            click.echo(
                f"ERROR: input must be same size as guess word "
                f"({len(current_guess)} letters)"
            )
        elif not re.fullmatch("[gybGYB]+", gyb_values):
            click.echo("ERROR: input must only contain 'G', 'Y', or 'B'")
        else:
            guess = convert_to_guess(current_guess, gyb_values.upper())
            click.echo("Filtering dictionary...")
            d = d.prune(guess)
            click.echo(f"Filtered dictionary size: {len(d)} entries")
            current_guess = d.get_most_likely_word()
            click.echo(f"Try '{current_guess}'.")

    click.echo("ERROR: Dictionary has no more possible words. Sorry!")
