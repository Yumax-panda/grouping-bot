from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord import ButtonStyle, Embed
from discord.ui import View, button
from libs.error import CustomError

if TYPE_CHECKING:
    from bot import GroupingBot
    from discord import Interaction, Member, User
    from discord.ext.commands import Context
    from discord.ui import Button, Item


class BaseView(View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    async def on_timeout(self) -> None:
        self.stop()

    async def on_error(
        self,
        interaction: Interaction[GroupingBot],
        error: Exception,
        item: Item[Any],  # noqa
    ) -> None:
        if interaction.response.is_done():
            await interaction.followup.send(str(error), ephemeral=True)
            return
        await interaction.response.send_message(str(error), ephemeral=True)


class GameJoinView(BaseView):
    def __init__(
        self, *, member_ids: list[int], owner_id: int | None = None
    ) -> None:
        super().__init__()
        self.member_ids = member_ids
        self.owner_id: int | None = owner_id
        self.lineup_embed: Embed = self.create_lineup_embed()

    def create_lineup_embed(self) -> Embed:
        embed = Embed(title="参加者一覧")
        for idx, member_id in enumerate(self.member_ids):
            embed.add_field(name=str(idx + 1), value=f"> <@{member_id}>")
        if self.owner_id is not None:
            embed.set_footer(text=f"募集ID: {self.owner_id}")
        return embed

    @staticmethod
    def from_embed(embed: Embed) -> GameJoinView:
        member_ids = []
        for field in embed.fields:
            if (value := field.value) is None:
                continue
            member_ids.append(int(value[4:-1]))
        owner_id = None
        if embed.footer.text is not None:
            owner_id = int(embed.footer.text[7:])
        return GameJoinView(member_ids=member_ids, owner_id=owner_id)

    def has(self, user: User | Member) -> bool:
        return user.id in self.member_ids

    async def start(self, ctx: Context) -> None:
        await ctx.send(embed=self.lineup_embed, view=self)

    @button(label="参加する", style=ButtonStyle.primary, custom_id="game_join")
    async def join(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        if interaction.message is None or len(interaction.message.embeds) == 0:
            raise CustomError("不正なメッセージです")
        this = self.__class__.from_embed(interaction.message.embeds[0])
        user = interaction.user

        if this.has(user):
            raise CustomError("既に参加しています")
        this.member_ids.append(user.id)

        await interaction.message.edit(embed=this.lineup_embed, view=this)
        await interaction.followup.send(f"{user.display_name}さんが参加しました")
