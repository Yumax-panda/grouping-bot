from typing import TypeVar

T = TypeVar("T")


def _get_group_members(members: int) -> list[int]:
    if members <= 4:
        return [members]
    rest = members % 4

    if rest == 0 or rest == 3:
        return [4] * (members // 4) + [3] * (rest // 3)
    if rest == 1:
        if members // 4 >= 2:
            # 3人組を3つにして、残りを4人組にする
            return [3] * 3 + [4] * ((members - 9) // 4)
        else:
            return [3, 2]

    # 余りが2のとき: 3人組を2つにして、残りを4人組にする
    return [3] * 2 + [4] * ((members - 6) // 4)


def get_group_members(members: int) -> list[int]:
    """メンバー数からグループの人数を割り出す

    Parameters
    ----------
    members : int
        メンバー数

    Returns
    -------
    list[int]
        グループの人数のリスト。降順にソートされている
    """
    return sorted(_get_group_members(members), reverse=True)


def allocate(members: list[T]) -> list[list[T]]:
    """メンバーをグループに分ける

    Parameters
    ----------
    members : list[T]
        メンバーのリスト

    Returns
    -------
    list[list[T]]
        グループのリスト
    """
    group_members = get_group_members(len(members))
    groups = []
    for i in group_members:
        groups.append(members[:i])
        members = members[i:]
    return groups
