import asyncio
import discord
from discord.ext import commands, tasks
from discord.message import Message
import youtube_dl

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

#prefixes=['+','-','!','#', '.']
client = commands.Bot(command_prefix='-')
#@client.command(name='prefix', help='This command changes prefix',aliases=['cp'])
#async def prefix(ctx):
   # await ctx.send('''Choose: 

status = ['Valorant', 'Music','-help','Minecraft']

@client.event
async def on_ready():
    queue.clear()
    change_status.start()
    print('Bot is online!')

@client.event
async def on_member_join(ctx):
    await ctx.send(f'Welcome {ctx.author.mention}!  Ready to jam out? See `-help` command for details!')

@client.command(name = 'ping_user', help='Pings the user',aliases=['pu'])
async def mention_ping(ctx,member:discord.Member):
    await ctx.send(f"HI  {member.mention}")


@client.command(name='ping', help='This command returns the latency')
async def ping(ctx):
    await ctx.send(f'**Hallelujah!** Latency: {round(client.latency * 1000)}ms')

@client.command(name='hello', help='This command returns a welcome message',aliases=['hi','yo'])
async def hello(ctx):
    responses = ['Play a song,i aint a chatbot','**Wasssuup!**']
    await ctx.send('**HI!**')
    await ctx.send(choice(responses))

@client.command(name='achha_aise', help='Cant expect better from MCOE',aliases=['auwmdya'])
async def hello(ctx):
    await ctx.send(':achha_aise:')

@client.command(name='kd', help='Cant expect better from MCOE',aliases=['ki','kcd','krm','klu','kb'])
async def hello(ctx):
    await ctx.send('Karuta is a Bitch!')

@client.command(name='happybirthdayitachi', help='Cant expect better from MCOE',aliases=['HBDI'])
async def hello(ctx):
    await ctx.send('**HAPPY BIRTHDAY ITUCHI KUN!!**')   

@client.command(name='die', help='Why does this even exist')
async def die(ctx):
    responses = ['Take care bruh', 'You give auwm vibes', 'Get a job']
    await ctx.send(":(")
    await ctx.send(choice(responses))

@client.command(name='join', help='This command will connect me',aliases=['j','connect'])
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel,Dumbass")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


queue=[]

@tasks.loop(seconds=1)
async def not_playing(ctx):
    voice_client = ctx.message.guild.voice_client
    server = ctx.message.guild
    voice_channel = server.voice_client
    if voice_client and voice_client.is_playing():
        pass
    else:
        if voice_client and voice_client.is_paused():
            pass
        else:
            async with ctx.typing():
                player_queue = await YTDLSource.from_url(queue[0], loop=client.loop)
                voice_channel.play(player_queue, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('**Now playing: {}**'.format(player_queue.title)+' **Requested By: **'+format(ctx.author.mention))
            del queue[0]


@client.command(name='play', help='This command plays music',aliases=['p','sing','gaa'])
async def play(ctx,url,*args):
    voice_client = ctx.message.guild.voice_client
    server = ctx.message.guild
    voice_channel = server.voice_client

    for word in args:
        url += ' '
        url += word
    if voice_client and voice_client.is_playing():
        queue.append(url)
        print(queue)
        await ctx.send('**Added:** {}'.format(url)+' **Requested By: **'+format(ctx.author.mention))
        not_playing.start(ctx)
    else:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=client.loop)
                voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send('**Now playing:** {}'.format(player.title)+'** Requested By: **'+format(ctx.author.mention))


@client.command(name='disconnect', help='This command stops the music and makes the bot leave the voice channel',aliases=['dc'])
async def disconnect(ctx):
    voice_client = ctx.message.guild.voice_client
    await ctx.send('**Byeee!**')
    queue.clear()
    await voice_client.disconnect()
    

@client.command(name='stop', help='This command stops the music',aliases=['wait'])
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await ctx.send('**Music Stopped**')
    await voice_client.stop()

@client.command(name='queue', help='This command displays the queue',aliases=['q'])
async def queue_(ctx):
    await ctx.send('**Queue: ** {}'.format(queue))

@client.command(name='pause', help='This command pauses the music',aliases=['pau'])
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("**Music Paused**")
    else:
        await ctx.send("Music is not playing bruh you high!?")

@client.command(name='resume', help='This command resumes the music',aliases=['pla','res'])
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("**Music Resumed**")
    else:
        await ctx.send("Music is playing bruh,you need rehab")

@client.command(name='skip', help='This command skips the song',aliases=['next','n'])
async def skip(ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client
        voice_client = ctx.message.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            async with ctx.typing():
                player_queue = await YTDLSource.from_url(queue[0], loop=client.loop)
                voice_channel.play(player_queue, after=lambda e: print('Player error: %s' % e) if e else None)
            await ctx.send("**Song Skipped**")
            await ctx.send('**Now playing:** {}'.format(player_queue.title))
            del queue[0]  
  



@tasks.loop(seconds=20)
async def change_status():

    await client.change_presence(activity=discord.Game(choice(status)))

client.run('ODg4NzkzOTMxNTkxMDY1NzMw.YUX32g.bgzQAgKkBq6Mxu_ZwX6YKKMaAxA')