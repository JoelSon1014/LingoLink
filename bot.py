import os
import discord
from google.cloud import texttospeech
from discord.ext import commands
from discord import Intents
from googletrans import Translator
from config import TOKEN, GUILD, GENERAL_CHANNEL_ID, GOOGLE_KEY

intents = Intents.all()
# client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='!', intents=intents)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_KEY

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
    """Welcomes the member to the channel."""
    general_channel = member.guild.get_channel(GENERAL_CHANNEL_ID)
    await general_channel.send(f'Welcome {member.mention} to the server!')


@client.command(name='translate', help='Translates last n number of conversations above it to a specified language')
async def translate(ctx, num_of_lines: int, common_language):
    """Translates the last n number of conversations above the command to a specified language."""
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
        
        translated_messages.append(f'**{display}**: {translated_text}') # Change display name to markup
    translated_messages.reverse() # Need to read documentation on channel history --> Leading to bugs
    # Combine messages --> Consecutive messages by same author combine into one message, separated by punctuation

    # for translated_message in reversed(translated_messages):
    #     print(translated_message)

    # Send the translated messages back to the Discord channel
    await ctx.send('\n'.join(translated_messages))

@client.command(name='speech', help='Does TTS for n number of conversations above it to a specified language')
async def speech(ctx, num_of_lines: int, spoken_lang):
    """"Does TTS for n number of conversations above the command to a specified language."""
    if not ctx.voice_client:
        ctx.send('I am not in voice channel right now. Use !join.')
        return
    voice_channel = ctx.author.voice.channel
    members = voice_channel.members
    lines_above = num_of_lines + 1
    channel = ctx.channel
    messages = []
    index = 0
    async for message in channel.history(limit=lines_above):
        index += 1
        if '!speech' in message.content or message.author.display_name.lower() == 'lingolink':
            continue
        messages.append(message)

    translated_messages = []
    for message in messages:
        translated_text = Translator().translate(message.content, dest=spoken_lang).text
        display = message.author.display_name
        
        translated_messages.append(f'{display}: {translated_text}') # Change display name to markup
    translated_messages.reverse() # Need to read documentation on channel history --> Leading to bugs
    
    for member in members:
        for translated_message in translated_messages:
            tts_content = tts(translated_message, spoken_lang)

            await member.send(tts_content, tts=True)



async def tts(message, language): # use levenschtein distance to get the language most similar to what user typed in (same for !translate command)
    """Generates tts for the translated message."""
    tts_client = texttospeech.TextToSpeechClient()


    synthesis_input = texttospeech.SynthesisInput(text=message)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language,
        name=f"{language}-Wavenet-D",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
    )

    response = tts_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    return response.audio_content


        # print(translated_message)
        
        # transcript = subprocess.getoutput(f'espeak -v {spoken_lang} -s {110} "{translated_message}"')
    
    # Print the transcript to the console
        # print(transcript)


@client.command(name='join', help='Makes LingoLink join the voice channel of the person who invoked it')
async def join_vc(ctx):
    """"Makes LingoLink join a voice channel."""

    if ctx.author.voice:
        channel = ctx.author.voice.channel
        vc = await channel.connect()

        await ctx.send(f'Joined {channel.name}.')
    else:
        await ctx.send(f'{ctx.author.display_name}, you need to be in a voice channel to use this command.')



@client.command(name='leave', help='Makes LingoLink leave the voice channel')
async def leave_vc(ctx):
    """Makes LingoLink leave a voice channel."""

    if ctx.voice_client:

        await ctx.voice_client.disconnect()
        await ctx.send('Left the voice channel.')

    else:
         await ctx.send('I am not currently in a voice channel.')








client.run(TOKEN)

#  __pycache__/
# config.py
# env