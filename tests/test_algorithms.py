import pytest

from grouping_bot.libs.algorithms import get_group_members


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        (4, [4]),
        (5, [3, 2]),
        (6, [3, 3]),
        (7, [4, 3]),
        (8, [4, 4]),
        (9, [3, 3, 3]),
        (10, [4, 3, 3]),
        (11, [4, 4, 3]),
        (12, [4, 4, 4]),
        (13, [4, 3, 3, 3]),
        (14, [4, 4, 3, 3]),
        (15, [4, 4, 4, 3]),
        (16, [4, 4, 4, 4]),
    ],
)
def test_get_group_members(val: int, expected: list[int]) -> None:
    test_case = get_group_members(val)
    assert test_case == expected
    assert sum(test_case) == val
