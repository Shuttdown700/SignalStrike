import os
import pytest
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from dted import get_elevation

# Mock function to replace actual DTED file reading
def mock_get_elevation(coord):
    test_data = {
        (49.1234, 18.5678): 655,
    }
    return test_data.get(tuple(coord), None)

@pytest.mark.parametrize("coord, expected", [
    ([49.1234, 18.5678], 655)
])
def test_get_elevation(coord, expected, monkeypatch):
    monkeypatch.setattr("dted.get_elevation", mock_get_elevation)
    assert get_elevation(coord) == expected

@pytest.mark.parametrize("coord", [
    ("invalid", 18.5678),  # Invalid type
    ([91.0, 18.5678]),  # Latitude out of range
    ([49.1234, 181.0]),  # Longitude out of range
    ([49.1234]),  # Missing value
    (49.1234, 18.5678, 10.0)  # Extra value
])
def test_get_elevation_invalid_inputs(coord):
    with pytest.raises(AssertionError):
        get_elevation(coord)
