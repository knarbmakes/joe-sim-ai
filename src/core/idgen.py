import time
import random

BASE36_DIGITS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ID_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
TIMESTAMP_PART_LENGTH = 5
RANDOM_PART_LENGTH = 3

def base36encode(number: int) -> str:
    """Converts an integer to a base36 string.

    Args:
        number (int): The number to convert.

    Returns:
        str: The base36 encoded string.
    """
    if not isinstance(number, int):
        raise TypeError('number must be an integer')

    if number < 0:
        return '-' + base36encode(-number)

    result = ''
    while number:
        number, remainder = divmod(number, 36)
        result = BASE36_DIGITS[remainder] + result

    return result or '0'

def generate_random_component(length: int) -> str:
    """Generates a random string component of specified length.

    Args:
        length (int): The length of the random component.

    Returns:
        str: A random string of the specified length.
    """
    return ''.join(random.choice(ID_CHARS) for _ in range(length))

def generate_id(length: int = 8) -> str:
    """Generates a unique identifier.

    Args:
        length (int): The total length of the identifier.

    Returns:
        str: The unique identifier.
    """
    if length < TIMESTAMP_PART_LENGTH:
        raise ValueError(f"Minimum length for ID is {TIMESTAMP_PART_LENGTH}")

    timestamp = int(time.time())
    timestamp_base36 = base36encode(timestamp)[-TIMESTAMP_PART_LENGTH:]

    # Adjust the length of the random component based on the total desired length
    random_part_length = length - TIMESTAMP_PART_LENGTH
    random_component = generate_random_component(random_part_length)

    return timestamp_base36 + random_component

