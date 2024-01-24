import asyncio
import json

import discord
from discord.ext import commands

try:
    with open("config.json") as f:
        config = json.load(f)
        token: str = config["token"]
except FileNotFoundError:
    import os

    token = os.environ["TOKEN"]


class GroupingBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        super().__init__(
            intents=intents, command_prefix="!", case_insensitive=True
        )

    async def setup_hook(self) -> None:
        await self.tree.sync()


bot = GroupingBot()


async def main() -> None:
    async with bot:
        await bot.start(token)


asyncio.run(main())
