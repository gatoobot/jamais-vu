from config import * 
import base64
import urllib.parse
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

# Clés API Last.fm et Spotify
lastfm_apikey = os.getenv('FM_API')
spotify_client_id = os.getenv('SPOTIFY_CLIENT')
spotify_client_secret = os.getenv('SPOTIFY_SECRET')

# Initialize Spotify client
credentials = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
spotify = Spotify(client_credentials_manager=credentials)

@bot.command(name='lastfm', invoke_without_command=True)
async def lastfm(ctx):
    current_prefix=load_prefix(ctx.guild.id)
    def create_embed(page_title, page_description):
        embed = discord.Embed(
            title=page_title,
            description=page_description,
            color=discord.Color(0x808080)
        )
        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )
        embed.add_field(name="Aliases", value="N/A", inline=False)
        embed.add_field(name="Parameters", value="user", inline=False)
        embed.add_field(name="Permissions", value="N/A", inline=False)
        return embed

    # Pages d'usage
    pages = [
        {
            "title": "Command name: linkfm",
            "description": "Links your Last.fm account with your Discord profile.",
            "usage": f"```Syntax: {current_prefix}lastfm linkfm <username>\n Example: {current_prefix}lastfm linkfm john_doe```",
            "footer": "Page 1/8"
        },
        {
            "title": "Command name: unlinkfm",
            "description": "Unlinks your Last.fm account from your Discord profile.",
            "usage": f"```Syntax: {current_prefix}lastfm unlinkfm\nExample: {current_prefix}lastfm unlinkfm```",
            "footer": "Page 2/8"
        },
        {
            "title": "Command name: fm cover",
            "description": "Show the cover of last track you listening to.",
            "usage": f"```Syntax: {current_prefix}fm cover \nExample: {current_prefix}fm cover ```",
            "footer": "Page 3/8"
        },
        {
            "title": "Command name: fm topartist",
            "description": "Show the top 5 of your most listened artists.",
            "usage": f"```Syntax: {current_prefix}fm topartist(s) \nExample: {current_prefix}fm topartist(s) ```",
            "footer": "Page 4/8"
        },
        {
            "title": "Command name: fm toptrack",
            "description": "Show the top 5 of your most listened tracks.",
            "usage": f"```Syntax: {current_prefix}fm toptrack(s) \nExample: {current_prefix}fm topatrack(s) ```",
            "footer": "Page 5/8"
        },
        {
            "title": "Command name: fm topalbum",
            "description": "Show the top 5 of your most listened albums.",
            "usage": f"```Syntax: {current_prefix}fm topalbum(s) \nExample: {current_prefix}fm topalbum(s) ```",
            "footer": "Page 6/8"
        },
        {
            "title": "Command name: fm taste",
            "description": "Compare your music taste between you and someone else.",
            "usage": f"```Syntax: {current_prefix}fm taste <username> \nExample: {current_prefix}fm taste @gato ```",
            "footer": "Page 7/8"
        },
        {
            "title": "Command name: fm user",
            "description": "Show the details of your last.fm account.",
            "usage": f"```Syntax: {current_prefix}fm user \nExample: {current_prefix}fm taste ```",
            "footer": "Page 8/8"
        },

    ]

    # Fonction pour changer d'embed
    async def update_embed(interaction, page_index):
        embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
        embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
        embed.set_footer(text=f"{pages[page_index]['footer']} | Module: lastfm.py • {ctx.message.created_at.strftime('%H:%M')}")
        await interaction.response.edit_message(embed=embed)

    buttons = await create_buttons(ctx, pages, update_embed, current_time)

    # Envoi de l'embed initial
    initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
    initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
    initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: lastfm.py • {ctx.message.created_at.strftime('%H:%M')}")
    await ctx.send(embed=initial_embed, view=buttons)


# Obtenir un jeton d'accès Spotify
async def get_spotify_token():
    auth = base64.b64encode(f"{spotify_client_id}:{spotify_client_secret}".encode()).decode()
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        async with session.post("https://accounts.spotify.com/api/token", headers=headers, data=data) as response:
            token_data = await response.json()
            return token_data.get("access_token")

# Function to get the play count of a track for a specific user
async def get_user_track_playcount(username: str, artist: str, track: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={username}&api_key={lastfm_apikey}&format=json&limit=100") as response:
            data = await response.json()
            if 'toptracks' in data and 'track' in data['toptracks']:
                for item in data['toptracks']['track']:
                    if item['artist']['name'].lower() == artist.lower() and item['name'].lower() == track.lower():
                        return item['playcount']  # Return the user's play count for the track
    return '0'  # Default if not found


# Récupérer la cover d'album depuis Spotify
async def get_spotify_album_cover(artist: str, track: str):
    token = await get_spotify_token()
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {token}"
        }
        query = f"track:{track} artist:{artist}"
        async with session.get(f"https://api.spotify.com/v1/search?q={urllib.parse.quote(query)}&type=track&limit=1", headers=headers) as response:
            data = await response.json()
            items = data.get("tracks", {}).get("items", [])
            if items:
                return items[0]["album"]["images"][0]["url"]  # URL de la plus grande image d'album
    return None

# Function to get the album name from Spotify
async def get_album_name_from_spotify(artist: str, title: str):
    query = f"{artist} {title}"
    results = spotify.search(q=query, type='track', limit=1)
    if results['tracks']['items']:
        return results['tracks']['items'][0]['album']['name']
    return "Unknown Album"

async def get_artist_cover(artist_name):
    token = await get_spotify_token()
    # Replace spaces with '%20' for the URL
    artist_name = urllib.parse.quote(artist_name)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1", headers={
            "Authorization": f"Bearer {token}"  # Ensure you have the valid access token
        }) as response:
            data = await response.json()
            if 'artists' in data and 'items' in data['artists'] and data['artists']['items']:
                # Get the first artist's image
                artist_data = data['artists']['items'][0]
                if artist_data['images']:
                    return artist_data['images'][0]['url']  # Return the largest image available
    return None

async def get_user_info(username: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={username}&api_key={lastfm_apikey}&format=json") as response:
            data = await response.json()
            if 'user' in data:
                return data['user']
            else:
                return None

async def get_top_albums(username: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.gettopalbums&user={username}&api_key={lastfm_apikey}&format=json&limit=5") as response:
            data = await response.json()

            # Vérifier si la réponse contient des albums
            if 'topalbums' in data and 'album' in data['topalbums']:
                return data['topalbums']['album']
            else:
                return None
            
async def get_total_scrobbles(username: str):
    async with aiohttp.ClientSession() as session:
        # Envoie une requête GET pour récupérer les infos de l'utilisateur
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={username}&api_key={lastfm_apikey}&format=json") as response:
            data = await response.json()
            
            # Vérifie si la réponse contient les informations de l'utilisateur et le nombre de scrobbles
            if 'user' in data and 'playcount' in data['user']:
                total_scrobbles = data['user']['playcount']  # Obtient le total des scrobbles
                return total_scrobbles
            else:
                return None


async def get_taste_comparison(username1: str, username2: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&user={username1}&api_key={lastfm_apikey}&format=json") as response1, \
                   session.get(f"https://ws.audioscrobbler.com/2.0/?method=artist.gettoptags&user={username2}&api_key={lastfm_apikey}&format=json") as response2:
            data1 = await response1.json()
            data2 = await response2.json()

            # Here you should analyze the data to find common artists and other information
            common_artists = []  # List of common artists
            # Replace this logic with the one that compares artists and calculates compatibility

            # Example of adding common artists and other information
            return {
                'common_artists': common_artists,
                'top_artist_user1': data1['topartists']['artist'][0]['name'] if data1['topartists']['artist'] else 'None',
                'top_artist_user2': data2['topartists']['artist'][0]['name'] if data2['topartists']['artist'] else 'None',
                'compatibility': 75  # Replace with actual compatibility calculation
            } 

# Retry function to handle API calls with retry mechanism
async def fetch_with_retry(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Failed to fetch data. Status code: {response.status}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                await asyncio.sleep(delay)  # Wait before retrying
            else:
                raise e      

