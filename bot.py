import discord
import os
import asyncio
import webserver
from discord import app_commands
from discord.ext import commands

DISCORD_TOKEN = os.environ['discordkey']

intents = discord.Intents.default()
intents.message_content = True      # Ensure the bot can read message content
intents.voice_states = True         # Ensure the bot can handle voice state updates
intents.guilds = True               # Ensure the bot can access guilds (servers)
intents.members = True              # Ensure the bot can access member information

bot = commands.Bot(command_prefix = "!", intents = discord.Intents.default())

# Triggered when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

members_on_hold = []

async def rate_limiter(member):
    if member.id in members_on_hold:
        print(f'Waiting for the rate limiter for {member}')
        return False
    else:
        members_on_hold.append(member.id)
        await asyncio.sleep(1)  # Await the coroutine properly
        members_on_hold.remove(member.id)
        return True

@bot.event
async def on_voice_state_update(member, before, after):
    if not await rate_limiter(member):
        return

    mix_channel_1_id = 1279068777555689584
    mix_channel_1 = discord.utils.get(member.guild.voice_channels, id=mix_channel_1_id)
    mix_channel_2_id = 1279068803472293948
    mix_channel_2 = discord.utils.get(member.guild.voice_channels, id=mix_channel_2_id)

    if after.channel != mix_channel_1:
        if after.channel != mix_channel_2:
            return

    if after.channel == mix_channel_1:
        await member.move_to(mix_channel_2)
    if after.channel == mix_channel_2:
        await member.move_to(mix_channel_1)

@bot.tree.command(name = "mix", description = "Mix a member!")
@app_commands.describe(member='The member you want to mix')
async def slash_command(interaction: discord.Interaction, member: discord.Member):
    mix_channel_1_id = 1279068777555689584
    mix_channel_1 = discord.utils.get(member.guild.voice_channels, id=mix_channel_1_id)
    mix_channel_2_id = 1279068803472293948

    if member == interaction.user:
        await interaction.response.send_message(f"You can not mix yourself <@{interaction.user.id}>! ")
        return

    if member.voice and member.voice.channel:
        if member.voice.channel.id == mix_channel_1_id or member.voice.channel.id == mix_channel_2_id:
            await interaction.response.send_message(f"<@{member.id}> is already being mixed!")
        else:
            await interaction.response.send_message(f"<@{member.id}> is going to get mixed!")
            await member.move_to(mix_channel_1)
    else:
        await interaction.response.send_message(f"<@{member.id}> is not in a voice channel !")

webserver.keep_alive()
# Run the bot with your token
bot.run(DISCORD_TOKEN)
