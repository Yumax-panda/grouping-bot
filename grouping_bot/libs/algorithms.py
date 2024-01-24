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
