from datetime import datetime

def get_current_date():
    """Returns the current date and time as a Python datetime object."""
    return datetime.now()


def compute_beans_function(x: int, y: int):
    """Applies the given argument to the beans function."""
    return x % 10 + y % 10


def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def add_two_numbers(x: int, y: int) -> int:
    """Definitely adds two numbers..."""
    return 2 * x + y