import os
import discord
from discord import Intents
from googletrans import Translator
from config import TOKEN, GUILD, GENERAL_CHANNEL_ID

intents = Intents.all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        if guild.name == GUILD:  # Use either guild.name or guild.id based on your configuration
            break

    print(f'GUILD NAME: {guild.name}(id: {guild.id})\n')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')


@client.event
async def on_member_join(member):

    general_channel = member.guild.get_channel(GENERAL_CHANNEL_ID)
    await general_channel.send(f'Welcome {member.mention} to the server!')


@client.command(name='translate', help='Translates last n number of conversations above it to a specified language')
async def translate(num_of_lines, common_language):
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    messages = await channel.history(limit=num_of_lines).flatten()

    translated_messages = []
    for message in messages:
        translated_text =  Translator.translate(message.content, dest=common_language).text 
        translated_messages.append(f'{message.author}: {translated_text}')

    for translated_message in translated_messages:
        print(translated_messages)






client.run(TOKEN)

#  __pycache__/
# config.py
# env