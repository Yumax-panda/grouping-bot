from discord.ext.commands import CommandError


class CustomError(CommandError):
    """Base class for other exceptions"""

    pass
