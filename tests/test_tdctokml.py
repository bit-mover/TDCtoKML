"""Test TDCtoKML functions."""
import pytest

from tdctokml.tdctokml import CoordinatesError, utm32ed50_to_wgs84


def test_utm32ed50_to_wgs84_boa() -> None:
    """Test BOA coordinates is matching if input is integers."""
    # pylint: disable=unpacking-non-sequence
    latitude, longitude = utm32ed50_to_wgs84(722432, 6177673)
    assert latitude == 55.69193
    assert longitude == 12.53787


def test_utm32ed50_to_wgs84_boa_float() -> None:
    """Test BOA coordinates is matching if input is floats."""
    # pylint: disable=unpacking-non-sequence
    latitude, longitude = utm32ed50_to_wgs84(722432.0, 6177673.0)
    assert latitude == 55.69193
    assert longitude == 12.53787


def test_utm32ed50_to_wgs84_zero_zero() -> None:
    """Test that both coordinates are not zero with integers."""
    with pytest.raises(CoordinatesError, match=r"Coordinates must not both be zero .*"):
        utm32ed50_to_wgs84(0, 0)


def test_utm32ed50_to_wgs84_float_zero_zero() -> None:
    """Test that both coordinates are not zero with floats."""
    with pytest.raises(CoordinatesError, match=r"Coordinates must not both be zero .*"):
        utm32ed50_to_wgs84(0.0, 0.0)


def test_utm32ed50_to_wgs84_nan() -> None:
    """Test that coordinates Not a Number."""
    with pytest.raises(CoordinatesError, match=r"Coordinates must not be an NaN .*"):
        utm32ed50_to_wgs84(float("nan"), float("nan"))
