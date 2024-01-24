import pytest

from grouping_bot.libs.algorithms import allocate, get_group_members


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


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ([1, 2, 3, 4], [[1, 2, 3, 4]]),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            [[1, 2, 3, 4], [5, 6, 7], [8, 9, 10]],
        ),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9], [[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
    ],
)
def test_allocate(val: list[int], expected: list[list[int]]) -> None:
    test_case = allocate(val)
    assert test_case == expected
    assert sum(map(len, test_case)) == len(val)
