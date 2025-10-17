def greet(name: str) -> str:
    """Return a friendly greeting for name.

    Args:
        name: Person's name. If empty, returns a generic greeting.

    Returns:
        Greeting string.
    """
    if not name:
        return "Hello!"
    return f"Hello, {name}!"
