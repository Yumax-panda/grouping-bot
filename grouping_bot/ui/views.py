from __future__ import annotations

from abc import abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, TypeGuard

from discord import ButtonStyle, Colour, Embed
from discord.ui import View, button
from libs.algorithms import allocate, shuffle
from libs.error import CustomError

if TYPE_CHECKING:
    from bot import GroupingBot
    from discord import Interaction, Message, TextChannel
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

    @staticmethod
    @abstractmethod
    def is_valid_message(
        message: Message | None,  # noqa
    ) -> TypeGuard[Message]:
        ...

    @property
    @abstractmethod
    def embed(self) -> Embed:
        ...

    async def refresh(self, message: Message) -> None:
        await message.edit(embed=self.embed, view=self)

    async def resend(self, message: Message, content: str) -> None:
        await message.delete()
        await message.channel.send(
            embed=self.embed, view=self, content=content
        )


class GameJoinView(BaseView):
    def __init__(
        self, *, member_ids: list[int], is_archived: bool = False
    ) -> None:
        super().__init__()
        self.member_ids = member_ids
        self.is_archived = is_archived

    @property
    def embed(self) -> Embed:
        return self.create_lineup_embed()

    def create_lineup_embed(self) -> Embed:
        if self.is_archived:
            color = Colour.dark_grey()
        else:
            color = Colour.green()
        embed = Embed(title="参加者一覧", color=color)
        for idx, member_id in enumerate(self.member_ids):
            embed.add_field(
                name=str(idx + 1), value=f"> <@{member_id}>", inline=False
            )
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

    @staticmethod
    def is_valid_message(message: Message | None) -> TypeGuard[Message]:
        return (
            message is not None
            and len(message.embeds) > 0
            and message.embeds[0].title == "参加者一覧"
        )

    @staticmethod
    async def fetch(
        channel: TextChannel, ignore_archive: bool = True
    ) -> GameJoinView:
        span = timedelta(hours=1)
        async for message in channel.history(after=datetime.utcnow() - span):
            if not GameJoinView.is_valid_message(message):
                continue
            is_archived = message.embeds[0].color == Colour.dark_grey()
            if is_archived and ignore_archive:
                continue
            return GameJoinView.from_embed(message.embeds[0])
        raise CustomError("現在参加者は募集されていません")

    def has(self, user_id: int) -> bool:
        return user_id in self.member_ids

    def add(self, user_id: int, raise_error: bool = False) -> None:
        if not self.has(user_id):
            self.member_ids.append(user_id)
            return
        if raise_error:
            raise CustomError("既に参加しています")

    def remove(self, user_id: int, raise_error: bool = False) -> None:
        if self.has(user_id):
            self.member_ids.remove(user_id)
            return
        if raise_error:
            raise CustomError("参加していません")

    async def start(self, ctx: Context) -> None:
        await ctx.send(embed=self.embed, view=self)

    @button(label="参加する", style=ButtonStyle.primary, custom_id="game_join")
    async def join(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        if not GameJoinView.is_valid_message(interaction.message):
            raise CustomError("不正なメッセージです")
        this = self.__class__.from_embed(interaction.message.embeds[0])
        user = interaction.user

        this.add(user.id, raise_error=True)

        await this.resend(
            interaction.message, content=f"{user.display_name}さんが参加しました"
        )

    @button(label="取り消し", style=ButtonStyle.danger, custom_id="game_cancel")
    async def cancel(self, interaction: Interaction, button: Button) -> None:
        await interaction.response.defer()
        if not self.is_valid_message(interaction.message):
            raise CustomError("不正なメッセージです")
        this = self.__class__.from_embed(interaction.message.embeds[0])
        user = interaction.user

        this.remove(user.id, raise_error=True)

        await this.resend(
            interaction.message, content=f"{user.display_name}さんが参加を取り消しました"
        )

    @button(label="開始", style=ButtonStyle.green, custom_id="game_start")
    async def start_game(
        self, interaction: Interaction, button: Button
    ) -> None:
        await interaction.response.defer()
        if not GameJoinView.is_valid_message(interaction.message):
            raise CustomError("不正なメッセージです")
        this = self.__class__.from_embed(interaction.message.embeds[0])
        lineup = LineupView(member_ids=this.member_ids)
        await lineup.resend(interaction.message, content="ゲームが開始されました")


class LineupView(BaseView):
    def __init__(self, *, member_ids: list[int]) -> None:
        super().__init__()
        self.member_ids = member_ids

    @property
    def embed(self) -> Embed:
        return self.create_lineup_embed()

    def create_lineup_embed(self) -> Embed:
        shuffled = shuffle(self.member_ids)
        groups = allocate(shuffled)
        embed = Embed(title="グループ分け", color=Colour.yellow())
        for idx, group in enumerate(groups):
            embed.add_field(
                name=f"{idx + 1}組. ({len(group)}人)",
                value="\n".join(f"> <@{member_id}>" for member_id in group),
                inline=False,
            )
        return embed

    @staticmethod
    def is_valid_message(message: Message | None) -> TypeGuard[Message]:
        return (
            message is not None
            and len(message.embeds) > 0
            and message.embeds[0].title == "グループ分け"
        )
