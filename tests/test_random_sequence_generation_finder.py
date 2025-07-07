"""Smoke tests for random_sequence_generation finder."""
from pyregularexpression.random_sequence_generation_finder import RANDOM_SEQUENCE_GENERATION_FINDERS

examples = {
    "hit_block": "The allocation sequence was computer-generated using block randomization with block size = 4.",
    "hit_coin": "Participants were assigned by a coin toss sequence.",
    "miss_randomly": "Participants were randomly selected from the registry.",
    "miss_random_effects": "We fitted a random-effects model to the data."
}

for label, txt in examples.items():
    print(f"\n=== {label} ===\n{txt}")
    for name, fn in RANDOM_SEQUENCE_GENERATION_FINDERS.items():
        print(f" {name}: {fn(txt)}")
