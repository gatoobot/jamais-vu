from config import *
from mango import *

load_dotenv()

@bot.command(name='avatar', aliases=['av'])
async def avatar(ctx, user: discord.Member = None):
    
    user = user or ctx.author  # Si aucun utilisateur n'est mentionné, prendre l'auteur du message.

    # Vérifier si l'utilisateur a un avatar
    if user.avatar:
        embed = discord.Embed(
            description=f"Avatar from {user.mention}",
            color=discord.Color(0x808080)  # Couleur par défaut
        )
        
        # Récupérer l'URL de l'avatar
        avatar_url = user.avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs
                        

                        # Assurez-vous que la liste de couleurs n'est pas vide
                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (0, 0, 0)  # Valeur par défaut si aucune couleur trouvée


                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                        embed.color = dominant_color  # Mettre à jour la couleur de l'embed
                    else:
                        embed.color = discord.Color(0x808080)  # Couleur par défaut si erreur

        embed.set_image(url=avatar_url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {user.mention} has no avatar configured.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command(name='sav', aliases=['serveravatar','savatar'])
async def sav(ctx, user: discord.Member = None):
    
    user = user or ctx.author  # Si aucun utilisateur n'est mentionné, prendre l'auteur du message.

    # Vérifier si l'utilisateur a un profil de serveur
    if user.guild_avatar:  # Vérifie si l'utilisateur a une image de profil de serveur
        embed = discord.Embed(
            description=f"Server avatar profile from {user.mention}",
            color=discord.Color(0x808080)  # Couleur par défaut
        )
        
        # Récupérer l'avatar et le traiter pour trouver la couleur dominante
        avatar_url = user.guild_avatar.url
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs
                        

                        # Assurez-vous que la liste de couleurs n'est pas vide
                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (0, 0, 0)  # Valeur par défaut si aucune couleur trouvée


                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                        embed.color = dominant_color  # Mettre à jour la couleur de l'embed
                    else:
                        embed.color = discord.Color(0x808080)  # Couleur par défaut si erreur

        embed.set_image(url=user.guild_avatar.url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {user.mention} has no server profile configured.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command(name='banner')
async def banner(ctx, user: discord.Member = None):
    
    user = user or ctx.author  # Si aucun utilisateur n'est mentionné, prendre l'auteur du message.

    # Récupérer les informations du profil de l'utilisateur
    user_info = await ctx.bot.fetch_user(user.id)

    # Vérifier si l'utilisateur a une bannière
    if user_info.banner:
        embed = discord.Embed(
            description=f"Banner from {user.mention}",
            color=discord.Color(0x808080)  # Couleur par défaut
        )
        
        # Récupérer l'URL de la bannière
        banner_url = user_info.banner.url
        async with aiohttp.ClientSession() as session:
            async with session.get(banner_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs
                                               

                        # Assurez-vous que la liste de couleurs n'est pas vide
                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (0, 0, 0)  # Valeur par défaut si aucune couleur trouvée

                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                        embed.color = dominant_color  # Mettre à jour la couleur de l'embed
                    else:
                        embed.color = discord.Color(0x808080)  # Couleur par défaut si erreur

        embed.set_image(url=user_info.banner.url)
        await ctx.send(embed=embed)
    else:
        
        await ctx.send(embed=discord.Embed(
        description=f"<:warn:1297301606362251406> : {user.mention} has no defined banner.",
        color=discord.Color.red()
))


@bot.command(name='sbanner', aliases=['serverbanner'])
async def sbanner(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # Utiliser l'utilisateur qui exécute la commande si aucun membre n'est mentionné

    # Vérifier si l'utilisateur a une bannière de serveur
    if member.guild_banner:  # Cette méthode est supportée dans la version dev
        banner_url = member.guild_banner.url
        
        # Télécharger et analyser l'image de la bannière pour extraire la couleur dominante
        async with aiohttp.ClientSession() as session:
            async with session.get(banner_url) as response:
                if response.status == 200:
                    img_data = await response.read()
                    with Image.open(io.BytesIO(img_data)) as img:
                        img = img.convert('RGB')  # Convertir l'image en RGB
                        img = img.resize((100, 100))  # Redimensionner l'image pour optimiser le traitement
                        colors = img.getcolors(maxcolors=1000000)  # Récupérer les couleurs dominantes

                        if colors:
                            most_common_color = max(colors, key=lambda x: x[0])[1]  # Obtenir la couleur la plus fréquente
                        else:
                            most_common_color = (128, 128, 128)  # Couleur par défaut (gris)

                    # Vérifier si most_common_color est bien un tuple de trois éléments
                    if isinstance(most_common_color, tuple) and len(most_common_color) == 3:
                        dominant_color = discord.Color.from_rgb(most_common_color[0], most_common_color[1], most_common_color[2])
                    else:
                        dominant_color = discord.Color(0x808080)  # Couleur par défaut si erreur

        # Créer l'embed avec la couleur dominante
        embed = discord.Embed(title=f"{member.display_name}'s Server Banner", color=dominant_color)
        embed.set_image(url=banner_url)  # Ajouter l'URL de la bannière de serveur
        await ctx.send(embed=embed)

    else:
        # Ici, assurez-vous que ce bloc est bien indenté pour qu'il ne s'exécute que si l'utilisateur n'a pas de bannière
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : {member.display_name} doesn't have a server banner.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


#IMG & LENS 

# Expression régulière pour détecter les mots NSFW
NSFW_REGEX = re.compile(r"\b(porn|nsfw|18\+|adult|xxx|nude|sex|explicit)\b", re.IGNORECASE)


# Fonction pour vérifier si une chaîne contient un mot NSFW
def contains_nsfw(content):
    return NSFW_REGEX.search(content) is not None

@bot.command(name='img', aliases=['search', 'image'])
async def img(ctx, *, query=None):  # query=None permet de détecter l'absence d'argument
    """Search for images based on the query, with NSFW filtering."""

    # Si aucun argument n'est fourni, afficher un embed d'aide
    if not query:
        embed = discord.Embed(
            title="Command name: img",
            description='Search for images on Google based on a query.',
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )

        embed.add_field(
            name="Aliases", 
            value="search, image", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="query", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        # Bloc combiné pour Syntax et Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}img <query>\n"
                  f"Example: {ctx.prefix}img cats```",
            inline=False
        )

        # Footer avec l'heure et la date de l'appel de commande
        embed.set_footer(
            text=f"Page 1/1 | Module: miscellous.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return  # Terminer ici si aucun argument n'est fourni

    # Si l'utilisateur fournit une requête, passer au processus de recherche d'image.
    if contains_nsfw(query):
        if not ctx.channel.is_nsfw():
            embed_nsfw = discord.Embed(
                description=f"<:warn:1297301606362251406> : Blocked search. No NSFW allowed in this channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed_nsfw)

    # Appel à l'API SerpAPI avec Safe Search activé
    response = requests.get(
        "https://serpapi.com/search",
        params={
            "engine": "google_images",
            "q": query,
            "safe": "active",  # Active Safe Search pour éviter les images NSFW
            "api_key": "db9cec5c7920d0e52aaff65e753e8ea3c714feaf826906ff52d0e8b4b10a9070",  # Remplace par ta clé API
        },
    )

    if response.status_code != 200:
        return await ctx.send(f"Error: {response.status_code} - {response.text}")

    data = response.json().get('images_results', [])
    if not data:
        return await ctx.send(f"No results were found for **{query}**")

    total_images = len(data)
    index = 0

    # Fonction pour créer l'embed avec la bonne image et l'utilisateur
    def get_embed_for_image(i):
        item = data[i]
        embed = discord.Embed(
            title=f"{ctx.author.display_name} | {item.get('title', 'No Title')}",
            url=item.get('link'),
            description=item.get('snippet', 'No description available.'),
            color=discord.Color(0x808080)
        ).set_image(url=item.get('thumbnail', ''))  # Utilise l'image miniature
        embed.set_footer(text=f"Image {i + 1}/{total_images}")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        return embed

    # Créer la vue pour les boutons
    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=True)
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(total_images == 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_embed(interaction):
        nonlocal index
        embed = get_embed_for_image(index)
        previous_button.disabled = (index == 0)
        next_button.disabled = (index == total_images - 1)
        await interaction.response.edit_message(embed=embed, view=buttons)

    async def previous_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:  # Vérifie que l'interaction vient de l'auteur
            if index > 0:
                index -= 1
                await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def next_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:  # Vérifie que l'interaction vient de l'auteur
            if index < total_images - 1:
                index += 1
                await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def close_callback(interaction):
        if interaction.user == ctx.author:  # Vérifie si l'utilisateur qui interagit est celui qui a exécuté la commande
            await interaction.message.delete()
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    # Envoi initial de l'embed
    embed = get_embed_for_image(index)
    await ctx.send(embed=embed, view=buttons)



#lens


@bot.command(name='lens')
async def lens(ctx):
    current_prefix = load_prefix(ctx.guild.id)
    """Analyze an image from a quoted message or embed and search it on Google with interactive buttons."""
    
    # Si la commande est appelée sans citer un message
    if not ctx.message.reference:
        embed_help = discord.Embed(
            title="Command name: Lens",
            description='Analyze an image using Google Lens. Please quote a message with an image or embed containing an image.',
            color=discord.Color(0x808080)
        )

        embed_help.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed_help.add_field(
            name="Aliases", 
            value="N/A",  # Pas d'alias pour cette commande
            inline=False
        )

        embed_help.add_field(
            name="Parameters", 
            value="N/A",  # Pas de paramètres à part le message cité
            inline=False
        )

        embed_help.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        embed_help.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}lens <image>\n"
                  f"Example:{current_prefix}lens image ```",
            inline=False
        )

        # Ajout du footer avec l'heure et le module
        embed_help.set_footer(
            text=f"Page 1/1 | Module: miscellous.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed_help)
        return

    # Récupère le message cité
    quoted_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)

    # Vérifie si le message cité contient une image directe dans les attachments
    image_url = None
    if quoted_message.attachments and quoted_message.attachments[0].url:
        image_url = quoted_message.attachments[0].url

    # Si aucune image n'a été trouvée dans les attachments, vérifie s'il s'agit d'un lien Discord
    if not image_url and quoted_message.content and "https://cdn.discordapp.com/" in quoted_message.content:
        image_url = quoted_message.content.strip()

    # Vérifie s'il y a un embed dans le message cité contenant une image
    if not image_url and quoted_message.embeds:
        for embed in quoted_message.embeds:
            if embed.image and embed.image.url:
                image_url = embed.image.url
                break

    # Si aucune image n'a été trouvée
    if not image_url:
        embed_no_image = discord.Embed(
            description=f"<:warn:1297301606362251406> : The quoted message does not contain any valid images.",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed_no_image)

    # Appel à l'API SerpAPI pour analyser l'image
    response = requests.get(
        "https://serpapi.com/search",
        params={
            "engine": "google_lens",
            "url": image_url,
            "api_key": "db9cec5c7920d0e52aaff65e753e8ea3c714feaf826906ff52d0e8b4b10a9070",  # Remplace par ta clé API
        },
    )

    if response.status_code != 200:
        embed_error = discord.Embed(
            description=f"<:warn:1297301606362251406> Error: {response.status_code} - {response.text}",
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed_error)

    data = response.json().get('visual_matches', [])
    if not data:
        embed_no_matches = discord.Embed(
            description=f"<:warn:1297301606362251406> : No visual matches were found for the image.",
            color=discord.Color.orange()
        )
        return await ctx.send(embed=embed_no_matches)

    total_images = len(data)
    index = 0

    # Fonction pour créer l'embed avec la bonne image et l'utilisateur
    def get_embed_for_image(i):
        item = data[i]
        embed = discord.Embed(
            title=f"Google Lens Result {i + 1}/{total_images}",
            url=item.get('link'),
            description=item.get('title', 'No Title'),
            color=discord.Color(0x808080)
        ).set_image(url=item.get('thumbnail'))  # Utilise l'image du résultat ici
        embed.set_footer(text=f"Result {i + 1}/{total_images}")
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        return embed

    # Créer la vue pour les boutons
    buttons = discord.ui.View(timeout=60)

    previous_button = discord.ui.Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=True)
    next_button = discord.ui.Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(total_images == 1))
    close_button = discord.ui.Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def update_embed(interaction):
        nonlocal index
        embed = get_embed_for_image(index)
        previous_button.disabled = (index == 0)
        next_button.disabled = (index == total_images - 1)
        await interaction.response.edit_message(embed=embed, view=buttons)

    async def previous_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:  # Vérifie que l'interaction vient de l'auteur
            if index > 0:
                index -= 1
                await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def next_callback(interaction):
        nonlocal index
        if interaction.user == ctx.author:  # Vérifie que l'interaction vient de l'auteur
            if index < total_images - 1:
                index += 1
                await update_embed(interaction)
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    async def close_callback(interaction):
        if interaction.user == ctx.author:  # Vérifie si l'utilisateur qui interagit est celui qui a exécuté la commande
            await interaction.message.delete()
        else:
            embed_error = discord.Embed(
                description=f"<:warn:1297301606362251406> : You are not the author of this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed_error, ephemeral=True)

    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    # Envoi initial de l'embed
    embed = get_embed_for_image(index)
    await ctx.send(embed=embed, view=buttons)

#Translator 

DEEPL_API_KEY = "5e9ea0e0-0714-4550-8a27-f9c09895f128:fx"  # Remplace par ta clé API

@bot.command(name='translate', aliases=['tr'])
async def translate(ctx, lang: str = None, *, text: str = None):
    current_prefix = load_prefix(ctx.guild.id)

    # Afficher un message d'aide si aucun argument n'est fourni
    if lang is None and text is None:
        embed = discord.Embed(
            title="Command name: Translate",
            description='Translate a message from a language to another.',
            color=discord.Color(0x808080)  # Couleur gris foncé
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Nom du bot
            icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
        )

        embed.add_field(
            name="Aliases", 
            value="tr",  # Alias de la commande
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="lang, text", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        # Bloc combiné pour Syntax et Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}translate <language> <text>\n"
                  f"Example: {current_prefix}tr fr I love cats```",
            inline=False
        )

        # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
            text=f"Page 1/1 | Module: miscellous.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return  # On arrête l'exécution ici si aucun argument n'est fourni

    # Vérifier si l'utilisateur a cité un message
    if ctx.message.reference:
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        text = referenced_message.content  # Utiliser le contenu du message cité si aucun texte n'est fourni

    if text is None:
        embed = discord.Embed(
            title="",
            description=f"<:warn:1297301606362251406> : Please provide a text to be translated. Use the format: `{current_prefix}translate <language> <text>` or reply to a message.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    # Appel à l'API DeepL pour traduire le texte
    try:
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": lang.upper()  # Langue de destination (en majuscule, ex: 'FR' pour français)
        }
        
        response = requests.post(url, data=params)
        result = response.json()

        if "translations" in result:
            translation = result['translations'][0]['text']
            embed = discord.Embed(
                description=f"<:approve:1297301591698706483> : **Translated to {lang.upper()}** - {translation}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            raise Exception("Translation error")

    except Exception as e:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> An error has occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


#TIMEZONE 

# Configuration de MongoDB
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')  # Remplace avec ta clé API Opencage

# Connexion à MongoDB
guild_collection = db['guild_timezones']

# Fonction pour charger le fuseau horaire de l'utilisateur depuis MongoDB
async def load_timezone(guild_id, user_id):
    guild_data = guild_collection.find_one({"guild_id": guild_id})
    if guild_data:
        user_timezone = guild_data.get('timezones', {}).get(str(user_id))
        return user_timezone
    return None

# Fonction pour sauvegarder le fuseau horaire de l'utilisateur dans MongoDB
async def save_timezone(guild_id, user_id, timezone_str):
    # On cherche si la guild existe déjà dans la base
    guild_data = guild_collection.find_one({"guild_id": guild_id})
    
    # Si la guild n'existe pas encore, on la crée avec un dictionnaire vide pour les fuseaux horaires
    if not guild_data:
        guild_data = {"guild_id": guild_id, "timezones": {}}
    
    # On met à jour ou on ajoute le fuseau horaire de l'utilisateur
    guild_data['timezones'][str(user_id)] = timezone_str
    
    # Mise à jour ou insertion dans MongoDB
    guild_collection.update_one({"guild_id": guild_id}, {"$set": guild_data}, upsert=True)

@bot.command(name='tz', aliases=['set_timezone', 'set_tz', 'timezone'])
async def timezone(ctx, *, city: str = None):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)
    
    current_prefix = load_prefix(ctx.guild.id)

    # Si aucune ville n'est spécifiée, on affiche le fuseau horaire actuel
    if city is None:
        timezone_str = await load_timezone(guild_id, user_id)
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)

            # Format de l'heure en anglais (AM/PM)
            time_str = now.strftime('%I:%M %p')
            # Format de la date en dd/mm/yyyy
            date_str = now.strftime('%d/%m/%Y')

            embed = discord.Embed(
                description=f"🕒 Your current date is **{date_str}**, **{time_str}**",
                color=discord.Color(0x808080)
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"<:warn:1297301606362251406> : Please define your timezone using `{current_prefix}tz [city]`. Example: `{current_prefix}tz Paris`. ",
                color=discord.Color.red())
            await ctx.send(embed=embed, reference=ctx.message)
    else:
        # Utilisation de l'API Opencage pour obtenir les informations de fuseau horaire
        url = f'https://api.opencagedata.com/geocode/v1/json?q={city}&key={OPENCAGE_API_KEY}'
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = await response.json()

        # Vérification de la réponse de l'API
        if response_data['results']:
            location = response_data['results'][0]['geometry']
            latitude = location['lat']
            longitude = location['lng']

            # Utilisation de TimezoneFinder pour récupérer le fuseau horaire en fonction de la latitude et longitude
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)

            if timezone_str:
                await save_timezone(guild_id, user_id, timezone_str)
                
                tz = pytz.timezone(timezone_str)
                now = datetime.now(tz)

                # Format de l'heure en anglais (AM/PM)
                time_str = now.strftime('%I:%M %p')
                # Format de la date en dd/mm/yyyy
                date_str = now.strftime('%d/%m/%Y')

                embed = discord.Embed(
                    title="",
                    description=f"🗺️ : Your timezone is now set to **{timezone_str}**.\n"
                                f"🕒 Current time : **{time_str}**\n"
                                f"📆 Current date : **{date_str}**",
                    color=discord.Color.green())
                await ctx.send(embed=embed)
            else:
                error_embed = discord.Embed(
                    title="",
                    description=f"<:warn:1297301606362251406> : Could not determine timezone for {city}.",
                    color=discord.Color.red())
                await ctx.send(embed=error_embed)
        else:
            error_embed = discord.Embed(
                title="",
                description=f"<:warn:1297301606362251406> : City not found. Please enter a valid city.",
                color=discord.Color.red())
            await ctx.send(embed=error_embed)

#steal 
@bot.group(name="steal")
@commands.has_permissions(administrator=True)
async def steal(ctx, emoji: discord.PartialEmoji = None):
    current_prefix = load_prefix(ctx.guild.id)
    
    # Si l'emoji n'est pas fourni, afficher l'aide de la commande steal
    if not emoji:
        embed = discord.Embed(
                    title="Command name: steal",
                    description='Steal emoji from others servers and add them to yours.',
                    color=discord.Color(0x808080)  # Couleur gris foncé
                )

        embed.set_author(
                    name=f"{bot.user.name}",  # Nom du bot
                    icon_url=bot.user.avatar.url  # Photo de profil du bot en rond
                )

        embed.add_field(
                    name="Aliases", 
                    value="N/A",  # Alias de la commande
                    inline=False
                )

        embed.add_field(
                    name="Parameters", 
                    value="emoji", 
                    inline=False
                )

        embed.add_field(
                    name="Permissions", 
                    value="N/A", 
                    inline=False
                )

                # Bloc combiné pour Syntax et Example
        embed.add_field(
                    name="Usage", 
                    value=f"```Syntax: {current_prefix}steal <emoji>\n"
                        f"Example: {current_prefix}steal emoji```",
                    inline=False
                )

                # Modification du footer avec la pagination, le module et l'heure
        embed.set_footer(
                    text=f"Page 1/1 | Module: miscellous.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)            
        return

    # Essayez de voler et d'ajouter l'emoji personnalisé
    try:
        guild = ctx.guild  # Le serveur actuel
        emoji_url = emoji.url  # URL de l'emoji (basée sur son identifiant)
        emoji_name = emoji.name  # Nom de l'emoji

        # Récupération de l'image de l'emoji avec aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(str(emoji_url)) as response:
                if response.status == 200:
                    image_data = await response.read()
                    # Ajout de l'emoji au serveur avec le même nom
                    new_emoji = await guild.create_custom_emoji(name=emoji_name, image=image_data)

                    embed = discord.Embed(
                        description=f"<:approve:1297301591698706483> : The {new_emoji} emoji has been successfully added to the server!",
                        color=discord.Color.green()
                    )
                    await ctx.send(embed=embed)
                else:
                    raise Exception(f"<:warn:1297301606362251406> : Error retrieving emoji.")
    except discord.HTTPException:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Failed to add emoji. The server may have reached its emoji limit.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    except Exception as e:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> An error has occurred: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)


@bot.command(name='enlarge', aliases=['e'])
async def enlarge(ctx, emoji: str = None):
    if not emoji:
        # Create the help embed
        embed = discord.Embed(
            title="Command name: enlarge",
            description='Enlarge an emoji',
            color=discord.Color(0x808080)  # Dark gray color
        )

        embed.set_author(
            name=bot.user.name,  # Bot's name
            icon_url=bot.user.avatar.url  # Bot's avatar
        )

        embed.add_field(
            name="Aliases", 
            value="e",  # Alias for the command
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="emoji", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="N/A", 
            inline=False
        )

        # Combined block for Syntax and Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {ctx.prefix}enlarge <emoji>\n"
                  f"Example: {ctx.prefix}enlarge :smiley:```",
            inline=False
        )

        # Footer with pagination, module, and time
        embed.set_footer(
            text=f"Page 1/1 | Module: misc.py · {ctx.message.created_at.strftime('%H:%M')}"
        )

        await ctx.send(embed=embed)
        return

    # Extract the emoji ID from the input
    emoji_id = emoji.split(':')[-1][:-1]  # Extract ID
    guild_emoji = discord.utils.get(ctx.guild.emojis, id=int(emoji_id))

    if guild_emoji:
        # Determine if the emoji is animated
        if guild_emoji.animated:
            # Construct the URL for the enlarged animated emoji
            enlarged_emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif?size=1024"
        else:
            # Construct the URL for the enlarged static emoji
            enlarged_emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png?size=1024"

        # Send the enlarged emoji
        await ctx.send(enlarged_emoji_url)
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : This emoji does not exist on this server.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
