# Cromulence - A Super Serious Word Games Solver

Cromulence is a library that provides various utilities for solving popular
word games.

## Wordle Solver

The Wordle solver interactive program can be called with `cromulence-wordle`:

```shell
$ cromulence-wordle
Downloading official Wordle dictionary...
INFO:root:Downloading default dictionary from 'https://www.nytimes.com/games/wordle/index.html'...
Success!
Initial dictionary size: 2309 entries
(This command will ask for input until exited using CTRL+C)
Try 'ISLET' as your initial guess.
Enter the game's response in the following format:
'G'reen, 'Y'ellow, or 'B'lack.

Example:
>>> GBBYB
Enter the Game's Response (GYB) []: YYBYT
ERROR: input must only contain 'G', 'Y', or 'B'
Enter the Game's Response (GYB) []: YYBYG
Filtering dictionary...
Filtered dictionary size: 2 entries
Try 'HEIST'.
Enter the Game's Response (GYB) []:
...
```

### Using the `cromulence.wordle` Module

`cromulence.wordle` is a module that can be used to optimize guessing
strategies for "wordle-style" games. Given a dictionary (or from a downloaded
official Wordle dictionary using `cromulence.wordle.get_default_dictionary()`)
this mini library can provide the ability to optimize future guesses.

Example code:

```python

from cromulence.wordle import Dictionary, GameResponse, Guess

# Get the Official Wordle dictionary from the Wordle web page.
dictionary = Dictionary.official()

# Create a "Guess" object that represents the coloured cells from your
# last guess.
guess = Guess([
    ("C", GameResponse.CORRECT),    # Green square.
    ("I", GameResponse.ELSEWHERE),  # Yellow square.
    ("G", GameResponse.INCORRECT),  # Letter not in answer.
    ("A", GameResponse.ELSEWHERE),
    ("R", GameResponse.INCORRECT)
])

# Prune the dictionary of any unacceptable answers.
dictionary = dictionary.prune(guess)
print(f"Try '{dictionary.get_most_likely_word()}' as the next guess...")

# Continue entering guesses and pruning dictionary until puzzle is solved...
```

## Installing

This package currently isn't distributed on PyPI, but can be easily built and
installed manually:

```shell
$ python3 -m pip install build
$ python3 -m build
$ python3 -m pip install dist/cromulence-*.whl
```

## License

All code in this project is MIT licensed. See [LICENSE](LICENSE) for license
text.
