from spafw37 import greet


def test_greet_with_name():
    assert greet("Alice") == "Hello, Alice!"


def test_greet_empty():
    assert greet("") == "Hello!"
