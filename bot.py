import os
import discord
import io
import tempfile
from discord.ext import commands
from discord import Intents
from googletrans import Translator
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from config import TOKEN, GUILD, GENERAL_CHANNEL_ID
from config import ACCESS_KEY, SECRET_KEY, REGION

intents = Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)

# Configure AWS Polly
aws_access_key_id = ACCESS_KEY
aws_secret_access_key = SECRET_KEY
aws_region = REGION
polly = boto3.client('polly', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

@client.event
async def on_ready():
    """Runs when bot first joins server."""
    print(f'{client.user} has connected to Discord!')

    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'GUILD NAME: {guild.name}(id: {guild.id})\n')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_member_join(member):
    """Runs when a member joins the server."""
    general_channel = member.guild.get_channel(GENERAL_CHANNEL_ID)
    await general_channel.send(f'Welcome {member.mention} to the server!')

@client.command(name='translate', help='Translates last n number of conversations above it to a specified language')
async def translate(ctx, num_of_lines: int, common_language):
    """Translates last n number of conversations above it to a specified language."""
    lines_above = num_of_lines + 1
    channel = ctx.channel
    messages = []
    index = 0
    async for message in channel.history(limit=lines_above):
        index += 1
        if '!translate' in message.content or message.author.display_name.lower() == 'lingolink':
            continue
        messages.append(message)

    translated_messages = []
    for message in messages:
        translated_text = Translator().translate(message.content, dest=common_language).text
        display = message.author.display_name
        translated_messages.append(f'**{display}**: {translated_text}')

    translated_messages.reverse()
    await ctx.send('\n'.join(translated_messages))

@client.command(name='speech', help='Does TTS for n number of conversations above it to a specified language')
async def speech(ctx, spoken_lang):
    """Translates above text into the translated tts."""
    channel = ctx.channel
    messages = []
    async for message in channel.history(limit=2):
        if '!speech' in message.content or message.author.display_name.lower() == 'lingolink':
            continue
        messages.append(message)

    translated_messages = []
    for message in messages:
        translated_text = Translator().translate(message.content, dest=spoken_lang).text
        translated_messages.append(f'{translated_text}')

    tts_file_path = await tts(translated_messages[0], spoken_lang, ctx.author.display_name)

    # Send the audio file to the text channel
    await ctx.send(file=discord.File(tts_file_path))

    # Clean up the temporary file
    os.remove(tts_file_path)

async def tts(message, spoken_lang, author):
    """Connects to AWS Polly."""
    try:
        # Use the spoken_lang parameter to select the appropriate voice
        response = polly.synthesize_speech(Text=message, OutputFormat="mp3", VoiceId=get_voice_id(spoken_lang))
        audio_data = response['AudioStream'].read()
        with tempfile.NamedTemporaryFile(delete=False, prefix=f'{author}-{spoken_lang}', suffix=".mp3") as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name

        return temp_file_path
    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error synthesizing speech: {e}")
        return None

def get_voice_id(spoken_lang):
    """Maps the language to the voice."""
    voice_mapping = {
        'en': 'Joanna',    # English
        'es': 'Conchita',  # Spanish
        'ja': 'Mizuki',    # Japanese
        'zh': 'Zhiyu',     # Mandarin
        'ko': 'Seoyeon',   # Korean
        'ar': 'Zeina',     # Arabic
    }

    return voice_mapping.get(spoken_lang, 'Joanna')


@client.command(name='join', help='Makes LingoLink join the voice channel of the person who invoked it')
async def join_vc(ctx):
    """Joins current voice channel."""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        voice_client = await channel.connect()
        await ctx.send(f'Joined {channel.name}.')
    else:
        await ctx.send(f'{ctx.author.display_name}, you need to be in a voice channel to use this command.')

@client.command(name='leave', help='Makes LingoLink leave the voice channel')
async def leave_vc(ctx):
    """Leaves the current voice channel."""
    voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice_client:
        await voice_client.disconnect()
        await ctx.send('Left the voice channel.')
    else:
        await ctx.send('I am not currently in a voice channel.')

client.run(TOKEN)
