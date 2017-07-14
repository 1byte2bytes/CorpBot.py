import asyncio
import discord
import random
from   datetime import datetime
from   discord.ext import commands
from   operator import itemgetter
from   Cogs import DisplayName
from   Cogs import Nullify
from   Cogs import CheckRoles
from   Cogs import Message

# This is the xp module.  It's likely to be retarded.

class XpStack:

	# Init with the bot reference, and a reference to the settings var
	def __init__(self, bot, settings):
		self.bot = bot
		self.settings = settings
		self.xp_save_count = 10

	@commands.command(pass_context=True)
	async def setxpcount(self, ctx, count = None):
		"""Sets the number of xp transactions to keep (default is 10)."""
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		# Only allow admins to change server stats
		if not isAdmin:
			await ctx.message.channel.send('You do not have sufficient privileges to access this command.')
			return

		if count == None:
			# Reset to default
			self.settings.setServerStat(ctx.guild, "XP Count", self.xp_save_count)
			await ctx.send("Reset the xp count to the default of {}.".format(self.xp_save_count))
			return

		try:
			count = int(count)
		except Exception:
			await ctx.send("Count must be an integer.")
			return

		if count < 0:
			await ctx.send("Count must be at least 0.")
			return

		self.settings.setServerStat(ctx.guild, "XP Count", count)
		await ctx.send("Set the xp count to {}.".format(count))

	@commands.command(pass_context=True)
	async def xpcount(self, ctx, count = None):
		"""Returns the number of xp transactions to keep (default is 10)."""
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		# Only allow admins to change server stats
		if not isAdmin:
			await ctx.message.channel.send('You do not have sufficient privileges to access this command.')
			return

		num = self.settings.getServerStat(ctx.guild, "XP Count")
		if num == None:
			num = self.xp_save_count
		
		await ctx.send("The current number of xp transactions to save is {}.".format(num))
		

	@commands.command(pass_context=True)
	async def clearxp(self, ctx):
		"""Clears the xp transaction list (bot-admin only)."""
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		if not isAdmin:
			checkAdmin = self.settings.getServerStat(ctx.message.guild, "AdminArray")
			for role in ctx.message.author.roles:
				for aRole in checkAdmin:
					# Get the role that corresponds to the id
					if str(aRole['ID']) == str(role.id):
						isAdmin = True
		if not isAdmin:
			await ctx.message.channel.send('You do not have sufficient privileges to access this command.')
			return
		
		xp_array = self.settings.getServerStat(ctx.guild, "XP Array")
		if xp_array == None:
			xp_array = []
		
		self.settings.setServerStat(ctx.guild, "XP Array", [])
		if len(xp_array) == 1:
			await ctx.send("Cleared 1 entry from the xp transactions list.")
		else:
			await ctx.send("Cleared {} entries from the xp transactions list.".format(len(xp_array)))

		
	@commands.command(pass_context=True)
	async def checkxp(self, ctx):
		"""Displays the last xp transactions (bot-admin only)."""
		isAdmin = ctx.message.author.permissions_in(ctx.message.channel).administrator
		if not isAdmin:
			checkAdmin = self.settings.getServerStat(ctx.message.guild, "AdminArray")
			for role in ctx.message.author.roles:
				for aRole in checkAdmin:
					# Get the role that corresponds to the id
					if str(aRole['ID']) == str(role.id):
						isAdmin = True
		if not isAdmin:
			await ctx.message.channel.send('You do not have sufficient privileges to access this command.')
			return
		
		# Check if we're suppressing @here and @everyone mentions
		if self.settings.getServerStat(ctx.message.guild, "SuppressMentions").lower() == "yes":
			suppress = True
		else:
			suppress = False

		xp_array = self.settings.getServerStat(ctx.guild, "XP Array")
		if xp_array == None:
			xp_array = []

		if not len(xp_array):
			await ctx.send("No recent XP transactions in *{}*.".format(ctx.guild.name))
			return

		count = 0
		maxToCount = 0 # Longest username length in to column
		maxFromCount = 0 # Longest username length in from column
		msg = "```Recent XP Transactions in {}:\n\n".format(ctx.guild.name)
		for i in range(len(xp_array)):
			i = xp_array[len(xp_array)-1-i]
			count += 1
			to_user = i["To"][:-5]
			if len(to_user) > maxToCount:
				maxToCount = len(to_user)
			from_user = i["From"][:-5]
			if len(from_user) > maxFromCount:
				maxFromCount = len(from_user)
			time = i["Time"]
			amount = i["Amount"]
			msg += "{:>3}. {} --[{:5} xp]--> {} at {}\n".format(count, from_user.ljust(maxFromCount), amount, to_user.ljust(maxToCount), time)
		msg += "```"
		# Check for suppress
		if suppress:
			msg = Nullify.clean(msg)
		await Message.say(self.bot, msg, ctx.channel, ctx.author, 1)

	# Catch custom xp event
	@asyncio.coroutine
	async def on_xp(self, to_user, from_user, amount):
		server = from_user.guild
		num = self.settings.getServerStat(server, "XP Count")
		if num == None:
			num = self.xp_save_count
		if type(to_user) is discord.Role:
			to_name = to_user.name + " role"
		else:
			to_name = "{}#{}".format(to_user.name, to_user.discriminator)
		f_name = "{}#{}".format(from_user.name, from_user.discriminator)
		# Add new xp transaction
		xp_transaction = { "To": to_name, "From": f_name, "Time": datetime.today().strftime("%Y-%m-%d %H.%M"), "Amount": amount }
		xp_array = self.settings.getServerStat(server, "XP Array")
		if xp_array == None:
			xp_array = []
		xp_array.append(xp_transaction)
		while len(xp_array) > num:
			xp_array.pop(0)
		self.settings.setServerStat(server, "XP Array", xp_array)
