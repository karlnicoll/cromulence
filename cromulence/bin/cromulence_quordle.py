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


import click
import logging
import re
from typing import List

from cromulence.wordle import Dictionary, GameResponse, Guess
from cromulence.wordle.dictionary import download_from_uri

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


def download_quordle_dictionary() -> List[str]:
    """Download the default dictionary from the official Wordle game.

    This will use web requests to download the game's JavaScript code files,
    and parse the dictionary.

    Args:
        uri: The URL to find the JavaScript links to download.
        download_fun: The function to execute to download the web page.

    Returns:
        A list of words, or None if the download failed.
    """
    uri_prefix = "https://www.quordle.com"
    logging.info(f"Downloading default dictionary from '{uri_prefix}'...")
    logging.debug(f"Downloading initial HTML content from '{uri_prefix}'...")
    main_html = download_from_uri(uri_prefix)
    if not main_html:
        logging.error(f"Failed to download content from '{uri_prefix}'!")
        return []

    logging.debug("Regex matching main JavaScript file...")
    script_name_match_data = re.search(r"assets/index.[0-9a-fA-F]+.js", main_html)

    if not script_name_match_data:
        logging.error("Wordle game script not found!")
        return []

    script_uri = f"{uri_prefix}/{script_name_match_data[0]}"
    js = download_from_uri(script_uri)

    if not js:
        logging.error(f"Failed to get source for script '{script_uri}'")
        return []

    logging.debug("Searching for word list...")
    match_data = re.search(r"(?<=wordBank:\")[^\"]+(?=\")", js)

    if not match_data:
        logging.error("Failed to find word list.")
        return []

    return match_data[0].split()


@click.command()
def main():
    click.echo("Downloading Quordle dictionary...")

    try:
        word_list = download_quordle_dictionary()
        dicts = [
            Dictionary(word_list),
            Dictionary(word_list),
            Dictionary(word_list),
            Dictionary(word_list),
        ]
        num_dicts = len(dicts)
    except RuntimeError:
        click.echo("Failed to get Wordle dictionary!")
        raise click.Abort()
    click.echo("Success!")
    click.echo(f"Initial dictionary size: {len(word_list)} entries")

    click.echo("(This command will ask for input until exited using CTRL+C)")
    current_guess = dicts[0].get_most_likely_word()
    word_size = len(current_guess)
    click.echo(f"Try '{current_guess}' as your initial guess.")

    click.echo("Enter the game's responses in the following format:")
    click.echo("'G'reen, 'Y'ellow, or 'B'lack.")
    click.echo("")
    click.echo("Response should have four sections, representing the responses from")
    click.echo("each of the Quordle 'quadrants'. It doesn't matter which order you")
    click.echo("enter the responses, as long as you're consistent :-)")
    click.echo("")
    click.echo("Example:")
    click.echo(">>> GBBYB BBYBB BBBBB GGYGB")
    click.echo("")
    click.echo("If a quadrant is solved, enter BBBBBB.")

    while True:
        user_input = click.prompt(
            "Enter the Game's Response (GYB)", default="", type=str
        )

        gyb_input_list = user_input.split()
        total_input_length = sum([len(gyb_value) for gyb_value in gyb_input_list])

        if len(gyb_input_list) != 4:
            click.echo(
                f"ERROR: Expected 4 responses from Quordle game, received "
                f"{len(gyb_input_list)}."
            )
        elif total_input_length != (word_size * num_dicts):
            click.echo(
                f"ERROR: inputs must be same size as guess word "
                f"({word_size} letters)"
            )
        else:
            valid_inputs = True
            for gyb_values in gyb_input_list:
                if not re.fullmatch("[gybGYB]+", gyb_values):
                    click.echo("ERROR: input must only contain 'G', 'Y', or 'B'")
                    valid_inputs = False
                    break

            if not valid_inputs:
                continue

            for i, gyb_values in enumerate(gyb_input_list):
                guess = convert_to_guess(current_guess, gyb_values.upper())
                click.echo(f"Filtering dictionary {i+1}...")
                dicts[i] = dicts[i].prune(guess)
                click.echo(f"Filtered dictionary size: {len(dicts[i])} entries")

            # Choose next word based on whichever dictionary is currently
            # smallest (should be fastest route to next answer).
            min_words = 999999
            best_dict = None
            for i, d in enumerate(dicts):
                dict_size = len(d)
                if (dict_size > 0) and (dict_size < min_words):
                    best_dict = d
                    min_words = dict_size

            current_guess = best_dict.get_most_likely_word()
            click.echo(f"Try '{current_guess}'.")


if __name__ == "__main__":
    main()
