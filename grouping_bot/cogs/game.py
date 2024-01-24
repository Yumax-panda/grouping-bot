from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Member, app_commands
from discord.ext import commands
from libs.error import CustomError
from ui.views import GameJoinView

if TYPE_CHECKING:
    from bot import GroupingBot


class GameCog(commands.Cog):
    def __init__(self, bot: GroupingBot) -> None:
        self.bot = bot

    @commands.hybrid_command(  # type: ignore
        name="start",
        description="メンバーを募集します",
        aliases=["募集", "s", "スタート", "開始", "じゃんたま"],
    )
    async def start(self, ctx: commands.Context[GroupingBot]) -> None:
        view = GameJoinView(member_ids=[ctx.author.id])
        await ctx.send(
            f"{ctx.author.display_name}さんが募集を開始しました",
            view=view,
            embed=view.embed,
        )

    @commands.command(
        name="join",
        description="メンバーに参加します",
        aliases=["参加", "can", "c", "の", "ノ"],
    )
    @commands.guild_only()
    @app_commands.describe(members="参加するメンバー")
    async def join(
        self,
        ctx: commands.Context[GroupingBot],
        members: commands.Greedy[Member],
    ) -> None:
        members = members or [ctx.author]  # type: ignore
        view = await GameJoinView.fetch(ctx.channel)
        added: list[Member] = []
        for member in members:
            if not member.bot:
                added.append(member)
                view.add(member.id)
        if not added:
            raise CustomError("参加者できるメンバーがいません")
        await view.resend(
            f"{', '.join(m.display_name for m in set(added))}さんが参加しました"
        )

    @commands.command(
        name="cancel",
        description="メンバーから取り消します",
        aliases=["取り消し", "d", "drop"],
    )
    @commands.guild_only()
    @app_commands.describe(members="取り消すメンバー")
    async def cancel(
        self,
        ctx: commands.Context[GroupingBot],
        members: commands.Greedy[Member],
    ) -> None:
        members = members or [ctx.author]  # type: ignore
        view = await GameJoinView.fetch(ctx.channel)
        removed: list[Member] = []
        for member in members:
            if not member.bot:
                removed.append(member)
                view.remove(member.id)
        if not removed:
            raise CustomError("取り消せるメンバーがいません")
        await view.resend(
            f"{', '.join(m.display_name for m in set(removed))}さんが参加を取り消しました",
        )


async def setup(bot: GroupingBot) -> None:
    await bot.add_cog(GameCog(bot))
