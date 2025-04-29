from nanoid import generate
from typing import Callable

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def guid_gen(length: int = 16) -> Callable[[], str]:
    """
    Create a function that can generate a unique identifier, leveraging nanoid.
    returns: a lambda function that generates a unique identifier
    """
    return lambda: generate(alphabet=ALPHABET, size=length)


def guid16() -> str:
    """
    Generate a unique identifier.
    returns: a string of length 16
    """
    return guid_gen(length=16)()
