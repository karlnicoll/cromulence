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


def filter_dict(word: str, d: Dictionary) -> Dictionary:
    """Filter the dictionary from user input."""
    valid_gyb_values = False
    while not valid_gyb_values:
        gyb_values = click.prompt(
            "Enter the Game's Response (GYB)", default="", type=str
        )

        if len(gyb_values) != len(word):
            click.echo(
                f"ERROR: input must be same size as guess word "
                f"({len(word)} letters)"
            )
        elif not re.fullmatch("[gybGYB]+", gyb_values):
            click.echo("ERROR: input must only contain 'G', 'Y', or 'B'")
        else:
            valid_gyb_values = True

    guess = convert_to_guess(word, gyb_values.upper())
    click.echo("Filtering dictionary...")
    d = d.prune(guess)
    click.echo(f"Filtered dictionary size: {len(d)} entries")

    return d


@click.command()
@click.option(
    "-s",
    "--save-me",
    is_flag=True,
    help=(
        "Set this option if you've already started guessing and need to fill in "
        "some previous guesses"
    )
)
def main(save_me: bool):
    click.echo("Downloading official Wordle dictionary...")
    try:
        d = Dictionary.official()
    except RuntimeError as ex:
        click.echo(f"Failed to get Wordle dictionary (error: {ex})!")
        raise click.Abort()
    click.echo("Success!")

    current_guesses_set = not save_me
    while not current_guesses_set:
        word = click.prompt(
            "Enter your guess word. Use blank to end guesses", default="", type=str
        )
        if word:
            d = filter_dict(word.upper(), d)
        else:
            current_guesses_set = True

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
        d = filter_dict(current_guess, d)
        current_guess = d.get_most_likely_word()
        click.echo(f"Try '{current_guess}'.")

    click.echo("ERROR: Dictionary has no more possible words. Sorry!")
