from __future__ import annotations

from typing import TYPE_CHECKING, Any

from discord import ButtonStyle, Colour, Embed
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
        self, *, member_ids: list[int], is_archived: bool = False
    ) -> None:
        super().__init__()
        self.member_ids = member_ids
        self.is_archived = is_archived
        self.lineup_embed: Embed = self.create_lineup_embed()

    def create_lineup_embed(self) -> Embed:
        if self.is_archived:
            color = Colour.dark_grey()
        else:
            color = Colour.green()
        embed = Embed(title="参加者一覧", color=color)
        for idx, member_id in enumerate(self.member_ids):
            embed.add_field(name=str(idx + 1), value=f"> <@{member_id}>")
        return embed

    @staticmethod
    def from_embed(embed: Embed) -> GameJoinView:
        member_ids = []
        for field in embed.fields:
            if (value := field.value) is None:
                continue
            member_ids.append(int(value[4:-1]))
        is_archived = embed.color == Colour.dark_grey()
        return GameJoinView(member_ids=member_ids, is_archived=is_archived)

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

    @button(label="取り消し", style=ButtonStyle.danger, custom_id="game_cancel")
    async def cancel(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        if interaction.message is None or len(interaction.message.embeds) == 0:
            raise CustomError("不正なメッセージです")
        this = self.__class__.from_embed(interaction.message.embeds[0])
        user = interaction.user

        if not this.has(user):
            raise CustomError("参加していません")
        this.member_ids.remove(user.id)

        await interaction.message.edit(embed=this.lineup_embed, view=this)
        await interaction.followup.send(f"{user.display_name}さんが参加を取り消しました")
