import pytest
from swecc_pypi_template.main import hello_world


def test_hello_world_default():
    """Test hello_world function with default parameter."""
    result = hello_world()
    assert result == "hello, world"
    assert isinstance(result, str)


def test_hello_world_custom_name():
    """Test hello_world function with custom name parameter."""
    result = hello_world(name="Python")
    assert result == "hello, Python"
    assert isinstance(result, str)