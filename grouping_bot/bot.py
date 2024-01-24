import asyncio
import json
import logging

import discord
from discord.ext import commands
from ui.views import GameJoinView, LineupView

try:
    with open("config.json") as f:
        config = json.load(f)
        token: str = config["token"]
except FileNotFoundError:
    import os

    token = os.environ["TOKEN"]

initial_extensions = [
    "cogs.game",
]

log = logging.getLogger(__name__)


class GroupingBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(
            intents=intents, command_prefix="!", case_insensitive=True
        )
        self.persistent_views_add = False

    async def setup_hook(self) -> None:
        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                log.error(f"Failed to load extension {extension}.", exc_info=e)
        await self.tree.sync()
        log.info("Command tree synced.")

        if not self.persistent_views_add:
            for view_instance in (
                GameJoinView(member_ids=[]),
                LineupView(member_ids=[]),
            ):
                self.add_view(view_instance)
            self.persistent_views_add = True
            logging.info("Added views.")

    async def on_ready(self) -> None:
        log.info(f"Logged in as {self.user}")


bot = GroupingBot()


async def main() -> None:
    async with bot:
        await bot.start(token)


asyncio.run(main())
