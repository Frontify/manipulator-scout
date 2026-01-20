import pytest

import manipulator_scout.units


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (1000.0, 1.0),
        (123.4, 0.1234),
        (-4.0, -0.004),
    ),
)
def test___ms2m___various_numbers___matches_expectation(value: float, expected: float):
    result = manipulator_scout.units.ms2s(value)

    assert result == pytest.approx(expected, rel=0.001)


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (1.0, 1000.0),
        (0.1234, 123.4),
        (-0.004, -4.0),
    ),
)
def test___s2ms___various_numbers___matches_expectation(value: float, expected: float):
    result = manipulator_scout.units.s2ms(value)

    assert result == pytest.approx(expected, rel=0.001)
