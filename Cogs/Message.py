import asyncio
import discord
import textwrap
from   discord.ext import commands

async def say(bot, msg, target, requestor, maxMessage : int = 5, characters : int = 2000):
    """A helper function to get the bot to cut his text into chunks."""
    if not bot or not msg or not target:
        return False

    textList = textwrap.wrap(msg, characters, break_long_words=True, replace_whitespace=False)

    if not len(textList):
        return False
    
    if not requestor.dm_channel:
        # No dm channel - create it
        await requestor.create_dm()
        
    dmChannel = requestor.dm_channel

    if len(textList) > maxMessage and dmChannel.id != target.id :
        # PM the contents to the requestor
        await target.send("Since this message is *{} pages* - I'm just going to DM it to you.".format(len(textList)))
        target = requestor
        
    for message in textList:
        await target.send(message)
    
    return True
