from config import *
from cachetools import TTLCache


# Initialiser le cache avec une taille maximale de 100 et une durée de vie de 2 heures
snipe_cache = TTLCache(maxsize=100, ttl=7200)
CLEANUP_INTERVAL = 120 

# Fonction pour créer le répertoire de snipes pour chaque serveur
def create_snipe_directory(guild_id):
    base_dir = 'snipe'
    guild_dir = os.path.join(base_dir, str(guild_id))
    if not os.path.exists(guild_dir):
        os.makedirs(guild_dir)
    return guild_dir

# Fonction pour charger et nettoyer les snipes expirés dans le JSON
def load_snipes(guild_id):
    guild_dir = create_snipe_directory(guild_id)
    snipe_file = os.path.join(guild_dir, 'snipes.json')
    snipes = {}

    if os.path.exists(snipe_file):
        with open(snipe_file, 'r') as f:
            snipes = json.load(f)

        # Supprimer les snipes qui datent de plus de 2 heures
        two_hours_ago = datetime.now() - timedelta(hours=2)
        for channel_id, snipe_list in list(snipes.items()):
            snipes[channel_id] = [
                snipe for snipe in snipe_list
                if datetime.fromisoformat(snipe['timestamp']) > two_hours_ago
            ]
            # Supprime les entrées vides pour éviter un stockage inutile
            if not snipes[channel_id]:
                del snipes[channel_id]

        save_snipes(snipes, guild_id)  # Mise à jour du fichier après nettoyage

    return snipes

# Fonction pour sauvegarder les snipes
def save_snipes(snipes, guild_id):
    guild_dir = create_snipe_directory(guild_id)
    snipe_file = os.path.join(guild_dir, 'snipes.json')
    with open(snipe_file, 'w') as f:
        json.dump(snipes, f, indent=4)

# Routine pour nettoyer les snipes expirés régulièrement
@tasks.loop(minutes=CLEANUP_INTERVAL)
async def cleanup_expired_snipes():
    for guild in bot.guilds:
        guild_id = guild.id
        snipes = load_snipes(guild_id)  # Charger et nettoyer les snipes expirés
        save_snipes(snipes, guild_id)  # Sauvegarder après nettoyage

# Initialiser la routine au démarrage du bot
@bot.event
async def on_ready():
    cleanup_expired_snipes.start()

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return

    guild_id = message.guild.id  # Obtenir l'ID de la guilde
    channel_id = str(message.channel.id)  # Obtenir l'ID du canal comme chaîne

    # Charger les snipes pour la guilde depuis le cache, sinon depuis le fichier JSON
    snipes = snipe_cache.get(guild_id) or load_snipes(guild_id)

    if channel_id not in snipes:
        snipes[channel_id] = []  # Créer une liste vide pour le canal s'il n'existe pas

    # Ajouter le snipe avec le contenu, l'auteur, les attachments et le timestamp
    snipes[channel_id].append({
        'content': message.content,
        'author': str(message.author.id),  # ID de l'utilisateur
        'attachments': [att.url for att in message.attachments],  # Récupérer les liens des attachments
        'stickers': [str(sticker.url) for sticker in message.stickers],  # Récupérer les URL des autocollants
        'timestamp': datetime.now().isoformat()  # Ajout du timestamp
    })

    # Limiter le nombre de snipes à 100 par canal
    if len(snipes[channel_id]) > 100:
        snipes[channel_id].pop(0)

    snipe_cache[guild_id] = snipes  # Mettre à jour le cache
    save_snipes(snipes, guild_id)  # Sauvegarder les snipes avec le bon argument


@bot.command(name='s', aliases=['snipe'])
async def snipe(ctx, index: int = 1):
    current_prefix = load_prefix(ctx.guild.id)
    channel_id = str(ctx.channel.id)

    # Charger les snipes pour le canal depuis le cache
    snipes = snipe_cache.get(ctx.guild.id) or load_snipes(ctx.guild.id)

    if channel_id not in snipes or not snipes[channel_id]:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : There are no deleted messages to display in this channel.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    index -= 1  # Ajuste l'index pour le traitement interne
    if index < 0 or index >= len(snipes[channel_id]):
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : Invalid snipe index.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Récupérer le snipe
    snipe = snipes[channel_id][-(index + 1)]
    author = await bot.fetch_user(int(snipe['author']))

    # Créer l'embed
    embed = discord.Embed(
        description=f"**Message sniped**: {snipe['content']}" if snipe['content'] else "No content.",
        color=discord.Color(0x808080)
    )
    embed.set_author(name=author.name, icon_url=author.avatar.url if author.avatar else None)

    # Réinitialiser l'image pour éviter les résidus d'anciens snipes
    embed.set_image(url=None)

    # Afficher les attachments ou stickers
    if snipe['attachments']:
        embed.set_image(url=snipe['attachments'][0])  # Affiche la première image si elle existe
    elif snipe['stickers']:
        embed.set_image(url=snipe['stickers'][0])  # Affiche le premier sticker si existe

    # Affichage de la date et de l'heure
    current_time = datetime.now().strftime('%H:%M')
    embed.set_footer(text=f"Page: {index + 1}/{len(snipes[channel_id])} • Today at {current_time}")

    # Créer une vue pour les boutons
    buttons = View(timeout=60)

    # Boutons
    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(index == 0))
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(index == len(snipes[channel_id]) - 1))
    close_button = Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    # Callback pour le bouton précédent
    async def previous_callback(interaction):
        nonlocal index  # Utilisation de nonlocal pour accéder à index
        if interaction.user.id == ctx.author.id:  # Vérification de l'auteur de la commande
            if index > 0:
                index -= 1
                await update_embed(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Callback pour le bouton suivant
    async def next_callback(interaction):
        nonlocal index  # Utilisation de nonlocal pour accéder à index
        if interaction.user.id == ctx.author.id:  # Vérification de l'auteur de la commande
            if index < len(snipes[channel_id]) - 1:
                index += 1
                await update_embed(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Callback pour le bouton de fermeture
    async def close_callback(interaction):
        if interaction.user.id == ctx.author.id:  # Vérification de l'auteur de la commande
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Fonction de mise à jour de l'embed
    async def update_embed(interaction):
        nonlocal index  # Utilisation de nonlocal pour accéder à index
        snipe = snipes[channel_id][-(index + 1)]
        author = await bot.fetch_user(int(snipe['author']))
        embed.description = f"**Message sniped**: {snipe['content']}" if snipe['content'] else "No content."
        embed.set_author(name=author.name, icon_url=author.avatar.url if author.avatar else None)

        # Réinitialiser l'image pour éviter les résidus d'anciens snipes
        embed.set_image(url=None)

        # Afficher les attachments ou stickers
        if snipe['attachments']:
            embed.set_image(url=snipe['attachments'][0])  # Affiche la première image
        elif snipe['stickers']:
            embed.set_image(url=snipe['stickers'][0])  # Affiche le premier sticker

        # Mettre à jour l'état des boutons
        previous_button.disabled = (index == 0)
        next_button.disabled = (index == len(snipes[channel_id]) - 1)
        embed.set_footer(text=f"Page: {index + 1}/{len(snipes[channel_id])} • Today at {current_time}")

        await interaction.response.edit_message(embed=embed, view=buttons)

    # Assignation des callbacks aux boutons
    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    # Ajout des boutons à la vue
    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    # Envoi du message avec l'embed et les boutons
    await ctx.send(embed=embed, view=buttons)


# Dictionnaire pour garder les editsnipes en mémoire
editsnipes_cache = {}
# Durée de vie des editsnipes en heures
EDIT_SNIPE_LIFETIME = timedelta(hours=2)

# Fonction pour charger les editsnipes
def load_editsnipes(guild_id):
    guild_dir = create_snipe_directory(guild_id)
    editsnipe_file = os.path.join(guild_dir, 'editsnipes.json')

    if os.path.exists(editsnipe_file):
        with open(editsnipe_file, 'r') as f:
            return json.load(f)
    return {}

# Fonction pour sauvegarder les editsnipes
def save_editsnipes(editsnipes, guild_id):
    guild_dir = create_snipe_directory(guild_id)
    editsnipe_file = os.path.join(guild_dir, 'editsnipes.json')

    with open(editsnipe_file, 'w') as f:
        json.dump(editsnipes, f)

# Fonction de nettoyage des editsnipes
def clean_editsnipes(editsnipes):
    current_time = datetime.now()
    for channel_id in list(editsnipes.keys()):
        editsnipes[channel_id] = [
            edit for edit in editsnipes[channel_id]
            if datetime.fromisoformat(edit['timestamp']) > (current_time - EDIT_SNIPE_LIFETIME)
        ]
        if not editsnipes[channel_id]:  # Si la liste est vide, supprimer la clé
            del editsnipes[channel_id]
    return editsnipes

# Gestion des messages édités
@bot.event
async def on_message_edit(before, after):
    if before.author.bot:
        return

    guild_id = before.guild.id
    channel_id = str(before.channel.id)
    editsnipes = load_editsnipes(guild_id)
    editsnipes = clean_editsnipes(editsnipes)  # Nettoyage des editsnipes

    if channel_id not in editsnipes:
        editsnipes[channel_id] = []

    editsnipes[channel_id].append({
        'author': str(before.author.id),
        'before': before.content,
        'after': after.content,
        'timestamp': datetime.now().isoformat()  # Ajout de la timestamp
    })

    save_editsnipes(editsnipes, guild_id)

@bot.command(name='es', aliases=['editsnipe'])
async def editsnipe(ctx, index: int = 1):
    channel_id = str(ctx.channel.id)

    # Charger les editsnipes pour le canal
    editsnipes = load_editsnipes(ctx.guild.id)
    editsnipes = clean_editsnipes(editsnipes)  # Nettoyage des editsnipes

    if channel_id not in editsnipes or not editsnipes[channel_id]:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : There are no edited messages to display in this channel.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)
        return

    index -= 1
    if index < 0 or index >= len(editsnipes[channel_id]):
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : Invalid editsnipe index.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    edit_snipe = editsnipes[channel_id][-(index + 1)]
    author = await bot.fetch_user(int(edit_snipe['author']))

    embed = discord.Embed(
        description=f"**Message Before**: {edit_snipe['before']}\n\n**Message After**: {edit_snipe['after']}",
        color=discord.Color(0x808080)
    )
    embed.set_author(name=author.name, icon_url=author.avatar.url)

    current_time = datetime.now().strftime('%H:%M')
    embed.set_footer(text=f"Page: {index + 1}/{len(editsnipes[channel_id])} • Today at {current_time}")

    buttons = View(timeout=60)

    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=(index == 0))
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary, disabled=(index == len(editsnipes[channel_id]) - 1))
    close_button = Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    async def previous_callback(interaction):
        if interaction.user.id == ctx.author.id:
            nonlocal index
            if index > 0:
                index -= 1
                await update_embed(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def next_callback(interaction):
        if interaction.user.id == ctx.author.id:
            nonlocal index
            if index < len(editsnipes[channel_id]) - 1:
                index += 1
                await update_embed(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    async def close_callback(interaction):
        if interaction.user.id == ctx.author.id:
            await interaction.message.delete()
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    await ctx.send(embed=embed, view=buttons)

    async def update_embed(interaction):
        edit_snipe = editsnipes[channel_id][-(index + 1)]
        author = await bot.fetch_user(int(edit_snipe['author']))

        embed.set_author(name=author.name, icon_url=author.avatar.url)
        embed.description = f"**Message Before**: {edit_snipe['before']}\n\n**Message After**: {edit_snipe['after']}"
        embed.set_footer(text=f"Page: {index + 1}/{len(editsnipes[channel_id])} • Today at {current_time}")

        previous_button.disabled = (index == 0)
        next_button.disabled = (index == len(editsnipes[channel_id]) - 1)
        await interaction.response.edit_message(embed=embed, view=buttons)

    await update_embed(None)

@bot.command(name='cs', aliases=['clear_snipe'])
@commands.has_permissions(manage_messages=True)  # Restreindre la commande aux modérateurs
async def clear_snipe(ctx):
    channel_id = str(ctx.channel.id)
    guild_id = ctx.guild.id

    # Charger les snipes et editsnipes depuis le cache ou les fichiers JSON
    snipes = snipe_cache.get(guild_id) or load_snipes(guild_id)
    editsnipes = editsnipes_cache.get(guild_id) or load_editsnipes(guild_id)

    # Vérifier si des snipes ou editsnipes existent pour le canal spécifique
    snipes_deleted = channel_id in snipes
    editsnipes_deleted = channel_id in editsnipes

    # Supprimer les snipes et editsnipes du canal spécifique
    if snipes_deleted:
        del snipes[channel_id]
    if editsnipes_deleted:
        del editsnipes[channel_id]

    # Mettre à jour le cache et sauvegarder dans les fichiers JSON
    snipe_cache[guild_id] = snipes
    editsnipes_cache[guild_id] = editsnipes
    save_snipes(snipes, guild_id)
    save_editsnipes(editsnipes, guild_id)

    # Vérifier si quelque chose a été supprimé et répondre en conséquence
    if snipes_deleted or editsnipes_deleted:
        await ctx.message.add_reaction("✅")  # Réaction de validation
    else:
        # Envoi d'un message en embed s'il n'y a rien à supprimer
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : Il n'y a pas de snipes ou editsnipes à supprimer dans ce canal.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, reference=ctx.message)  # Réponse avec référence




