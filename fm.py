from config import *
from fmconfig import *
from mango import *

lastfm_ref = db["lastfm_users"]  # Nom de la collection pour stocker les utilisateurs

# Charger les utilisateurs Last.fm depuis MongoDB
async def load_lastfm_users():
    # Chercher un document avec la clé "data", on suppose qu'il est unique dans cette collection
    doc = lastfm_ref.find_one({"_id": "data"})  # "_id" est la clé unique dans MongoDB
    if doc:
        # Retourne la liste des utilisateurs sous forme de dictionnaire
        return json.loads(doc.get('users', '{}'))
    else:
        # Si le document n'existe pas, retourner un dictionnaire vide
        return {}

# Sauvegarder les utilisateurs Last.fm dans MongoDB
async def save_lastfm_users(users):
    data = {
        "users": json.dumps(users)  # Convertir les utilisateurs en JSON
    }
    
    # Mettre à jour le document avec _id = "data", sinon créer ce document
    lastfm_ref.update_one({"_id": "data"}, {"$set": data}, upsert=True)
    return True

async def some_async_function():
    users = await load_lastfm_users()  # Correct
    print(users)

asyncio.run(some_async_function())


is_ready= False 

@bot.event
async def on_ready():
    global lastfm_users, is_ready
    if not is_ready:
        # Charger les utilisateurs Last.fm depuis le Gist
        lastfm_users = await load_lastfm_users()

        # Définir le statut du bot
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game("Listening to Last.fm"))
        
        is_ready = True


@bot.command(name="linkfm")
async def linkfm(ctx, username: str):
    user_id = str(ctx.author.id)

    # Link the user's Last.fm account
    lastfm_users[user_id] = username
    await save_lastfm_users(lastfm_users)  # Save the updated users to the Gist

    # Create an embed message for confirmation
    embed = discord.Embed(description=f"<:approve:1297301591698706483> : Your Last.fm account has been successfully linked! Username - {username}", color=0x808080)
    await ctx.send(embed=embed)

# Command to unlink Last.fm account
@bot.command(name="unlinkfm")
async def unlinkfm(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    user_id = str(ctx.author.id)

    # Check if the user has linked a Last.fm account
    if user_id not in lastfm_users:
        embed = discord.Embed(color=0xff0000)  # Red color for error
        embed.description = f"<:warn:1297301606362251406> : You haven't linked your Last.fm account yet! Use `{current_prefix}linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    # Unlink the user's Last.fm account
    del lastfm_users[user_id]
    await save_lastfm_users(lastfm_users)  # Save the updated users to the Gist

    # Create an embed message for confirmation
    embed = discord.Embed(description=f"<:approve:1297301591698706483> : Your Last.fm account has been successfully unlinked!", color=0x00ff00)  # Green color
    await ctx.send(embed=embed)

@bot.group(name="fm")
async def fm(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    user_id = str(ctx.author.id)

    # Check if the user has linked their Last.fm account
    if user_id not in lastfm_users:
        embed = discord.Embed(color=0xff0000)  # Red for the error
        embed.description = f"<:warn:1297301606362251406> : You haven't linked your Last.fm account yet! Use `{current_prefix}linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    # Only if it's not a sub-command
    if ctx.invoked_subcommand is None:
        username = lastfm_users[user_id]

        # Fetch the total scrobbles
        scrobbles = await get_total_scrobbles(username)
        if scrobbles is None:
            await ctx.send("Unable to fetch the total scrobbles.")
            return

        # Retry mechanism for getting the currently playing track
        try:
            url = f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={lastfm_apikey}&format=json&limit=1"
            data = await fetch_with_retry(url)

            # Check if a track is currently playing
            if 'recenttracks' not in data or not data['recenttracks']['track']:
                await ctx.send("Unable to fetch the currently playing track.")
                return

            track = data['recenttracks']['track'][0]
            artist = track['artist']['#text']
            title = track['name']

            # Use asyncio.gather to fetch the song details
            user_playcount_task = get_user_track_playcount(username, artist, title)
            album_name_task = get_album_name_from_spotify(artist, title)
            album_cover_task = get_spotify_album_cover(artist, title)

            # Fetch results in parallel
            user_playcount, album_name, album_cover = await asyncio.gather(
                user_playcount_task,
                album_name_task,
                album_cover_task
            )

            # Create the embed with song details
            embed = discord.Embed(color=0x808080)
            embed.set_author(name=username, icon_url=ctx.author.avatar.url)
            embed.add_field(name="Artist", value=f"[{artist}](https://www.last.fm/music/{urllib.parse.quote(artist)})", inline=True)
            embed.add_field(name="Title", value=f"[{title}](https://www.last.fm/music/{urllib.parse.quote(artist)}/_/{urllib.parse.quote(title)})", inline=True)

            # Add album cover if available
            if album_cover:
                embed.set_thumbnail(url=album_cover)
            else:
                embed.add_field(name="Album Cover", value="Unavailable via Spotify", inline=False)

            # Add total scrobbles to the footer
            embed.set_footer(text=f"Play Count: {user_playcount} · Scrobbles: {scrobbles} | Album: {album_name}")

            # Send the embed message
            message = await ctx.send(embed=embed)

            # Add reactions to the embed
            await message.add_reaction("🔥")
            await message.add_reaction("🗑️")

        except Exception as e:
            return


@fm.command(name="cover")
async def fmcover(ctx):
    user_id = str(ctx.author.id)

    # Check if the user has linked a Last.fm account
    if user_id not in lastfm_users:
        embed = discord.Embed(color=0xff0000)  # Red color for error
        embed.description = f"<:warn:1297301606362251406> : You haven't linked your Last.fm account yet! Use `linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    username = lastfm_users[user_id]

    # Fetch the currently playing song information
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={lastfm_apikey}&format=json&limit=1") as response:
            data = await response.json()

            # Check if there is a currently playing song
            if 'recenttracks' not in data or not data['recenttracks']['track']:
                await ctx.send("Unable to retrieve the current track.")
                return

            track = data['recenttracks']['track'][0]

            # Track details
            artist = track['artist']['#text']
            title = track['name']

            # Get album cover from Spotify
            album_cover = await get_spotify_album_cover(artist, title)

            # Create the embed for the album cover
            embed = discord.Embed(color=0x808080)

            # Set the author's profile picture and username at the top
            embed.set_author(name=username, icon_url=ctx.author.avatar.url)

            # Add the artist and title fields with clickable links
            embed.add_field(name="Artist", value=f"[{artist}](https://www.last.fm/music/{urllib.parse.quote(artist)})", inline=True)
            embed.add_field(name="Title", value=f"[{title}](https://www.last.fm/music/{urllib.parse.quote(artist)}/_/{urllib.parse.quote(title)})", inline=True)

            # Add the album cover if available
            if album_cover:
                embed.set_image(url=album_cover)
            else:
                embed.add_field(name="Album Cover", value="Album cover is unavailable via Spotify.", inline=False)

            footer_text = f"{username} | Module : fm.py"
            embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed)

@fm.command(name="topartists", aliases=['topartist'] )
async def fmtopartists(ctx):
    user_id = str(ctx.author.id)

    # Check if the user has linked a Last.fm account
    if user_id not in lastfm_users:
        embed = discord.Embed(color=0xff0000)  # Red color for error
        embed.description = f"<:warn:1297301606362251406> : You haven't linked your Last.fm account yet! Use `linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    username = lastfm_users[user_id]

    # Fetch the user's top artists
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.gettopartists&user={username}&api_key={lastfm_apikey}&format=json&limit=5") as response:
            data = await response.json()

            # Check if we received valid data
            if 'topartists' not in data or not data['topartists']['artist']:
                await ctx.send("Unable to retrieve the top artists.")
                return

            # Create the embed for the top artists
            embed = discord.Embed(title=f"Top Artists of {username}", color=0x808080)

            # Get the first artist for the thumbnail
            top_artist = data['topartists']['artist'][0]  # Get the first artist
            top_artist_name = top_artist['name']
            artist_cover_url = await get_artist_cover(top_artist_name)  # Fetch cover image from Spotify
            if artist_cover_url:
                embed.set_thumbnail(url=artist_cover_url)

            # Add top artists to the embed without clickable links
            for artist in data['topartists']['artist']:
                artist_name = artist['name']
                playcount = artist['playcount']

                # Add artist details to the embed without links
                embed.add_field(name=artist_name, value=f"Play Count: {playcount}", inline=False)

            footer_text = f"{username} | Module : fm.py"
            embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed)

@fm.command(name="toptracks", aliases=["toptrack"] )
async def fmtoptracks(ctx):
    user_id = str(ctx.author.id)

    # Check if the user has linked a Last.fm account
    if user_id not in lastfm_users:
        embed = discord.Embed(color=0xff0000)  # Red color for error
        embed.description = f"<:warn:1297301606362251406> : You haven't linked your Last.fm account yet! Use `linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    username = lastfm_users[user_id]

    # Fetch the user's top tracks
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={lastfm_apikey}&format=json&limit=5") as response:
            data = await response.json()

            # Check if we received valid data
            if 'toptracks' not in data or not data['toptracks']['track']:
                await ctx.send("Unable to retrieve the top tracks.")
                return

            # Create the embed for the top tracks
            embed = discord.Embed(title=f"Top Tracks of {username}", color=0x808080)

            # Loop through the top tracks and create a list for track info
            track_info = []
            for track in data['toptracks']['track']:
                track_name = track['name']
                artist_name = track['artist']['name']
                playcount = track['playcount']

                # Format track info with bold title and artist, and a line break before play count
                track_info.append(f"**{track_name}** by **{artist_name}**\nPlay Count: {playcount}")

            # Get the album cover for the top track
            top_track = data['toptracks']['track'][0]
            top_artist = top_track['artist']['name']
            top_track_name = top_track['name']
            album_cover = await get_spotify_album_cover(top_artist, top_track_name)

            # Add all track info as fields in the embed
            for info in track_info:
                embed.add_field(name="\u200b", value=info, inline=False)  # Empty name for a clean look

            # Set the thumbnail to the album cover of the top track if available
            if album_cover:
                embed.set_thumbnail(url=album_cover)

            footer_text = f"{username} | Module : fm.py"
            embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)
            
            await ctx.send(embed=embed)

@fm.command(name="topalbums", aliases=['topalbum'])
async def fmtopalbums(ctx):
    user_id = str(ctx.author.id)

    # Check if the user has linked their Last.fm account
    if user_id not in lastfm_users:
        embed = discord.Embed(color=0xff0000)
        embed.description = f"<:warn:1297301606362251406> : You have not linked your Last.fm account yet! Use `linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    username = lastfm_users[user_id]
    
    # Call the function to retrieve the top albums
    albums = await get_top_albums(username)

    # Check if albums were retrieved
    if albums is None:
        embed = discord.Embed(color=0xff0000)
        embed.description = "Unable to retrieve the top listened albums."
        await ctx.send(embed=embed)
        return

    # Create an embed for the albums
    embed = discord.Embed(title=f"Top Albums by {username}", color=0x808080)

    # Loop through the albums and add them to the embed
    for album in albums:
        album_name = album['name']
        artist_name = album['artist']['name']
        playcount = album['playcount']
        album_url = f"https://www.last.fm/music/{urllib.parse.quote(artist_name)}/_/{urllib.parse.quote(album_name)}"
        image_url = album['image'][3]['#text']  # Use the appropriate image size

        # Add fields for each album
        embed.add_field(
            name=f"**{album_name}** by **{artist_name}**",
            value=f"Play Count: {playcount}\n[View on Last.fm]({album_url})",
            inline=False
        )

        # Set the thumbnail for the first album
        if image_url and albums.index(album) == 0:
            embed.set_thumbnail(url=image_url)

    footer_text = f"{username} | Module : fm.py"
    embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)

@fm.command(name="user")
async def fmuser(ctx):
    user_id = str(ctx.author.id)

    # Check if the user has linked a Last.fm account
    if user_id not in lastfm_users:
        embed = discord.Embed(color=0xff0000)
        embed.description = f"<:warn:1297301606362251406> : You haven't linked your Last.fm account yet! Use `linkfm <username>` to link it."
        await ctx.send(embed=embed)
        return

    username = lastfm_users[user_id]

    # Fetch user information using the helper function
    user_info = await get_user_info(username)

    # Check if we received valid data
    if user_info is None:
        await ctx.send("Unable to retrieve user information.")
        return

    playcount = user_info.get('playcount', '0')
    profile_image = user_info.get('image', [{}])[2].get('#text')
    country = user_info.get('country', 'Unknown')
    registered = user_info.get('registered', {}).get('unixtime', 'Unknown')

    # Create the embed for user information
    embed = discord.Embed(title=f"<:lastfm_iconicons:1303143391533469786> Profile: {username}", color=0x808080)

    # Set the user's profile image
    if profile_image:
        embed.set_thumbnail(url=profile_image)

    # Add user details to the embed
    embed.add_field(name="Play Count", value=playcount, inline=True)
    embed.add_field(name="Country", value=country, inline=True)
    embed.add_field(name="Registered On", value=f"<t:{registered}:F>", inline=True)

    footer_text = f"{username} | Module : fm.py"
    embed.set_footer(text=footer_text, icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
   
