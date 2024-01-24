from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands
from ui.views import GameJoinView

if TYPE_CHECKING:
    from bot import GroupingBot


class GameCog(commands.Cog):
    def __init__(self, bot: GroupingBot) -> None:
        self.bot = bot

    @commands.hybrid_command(  # type: ignore
        name="start", description="メンバーを募集します"
    )
    async def start(self, ctx: commands.Context[GroupingBot]) -> None:
        view = GameJoinView(member_ids=[ctx.author.id], owner_id=ctx.author.id)
        await view.start(ctx)
        await ctx.send(f"{ctx.author.display_name}さんが募集を開始しました")


async def setup(bot: GroupingBot) -> None:
    await bot.add_cog(GameCog(bot))
