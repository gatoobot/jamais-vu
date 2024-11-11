from config import * 
from mango import *

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60

    if hours > 0:
        return f"{hours} hours, {minutes} minutes, {remaining_seconds} seconds"
    elif minutes > 0:
        return f"{minutes} minutes, {remaining_seconds} seconds"
    else:
        return f"{remaining_seconds} seconds"


afk_collection = db['afk']  # Collection 'afk', MongoDB la crée automatiquement si elle n'existe pas

# Charger les données AFK depuis MongoDB
def load_afk_data_from_mongo():
    afk_users = {}
    # Charger tous les documents de la collection
    docs = afk_collection.find()  # .find() renvoie tous les documents
    for doc in docs:
        guild_id = doc['_id']  # L'id du document est le guild_id
        afk_users[guild_id] = doc.get('users', {})
    return afk_users

# Sauvegarder les données AFK dans MongoDB
def save_afk_data_to_mongo(data):
    for guild_id, users in data.items():
        # Insérer ou mettre à jour un document pour chaque guilde
        afk_doc = {'_id': guild_id, 'users': users}
        afk_collection.update_one({'_id': guild_id}, {'$set': afk_doc}, upsert=True)  # 'upsert' crée un document si il n'existe pas
    print("AFK data successfully saved to MongoDB.")

# Initialisation des données AFK
afk_users = {}

@bot.event
async def on_ready():
    # Charger les données AFK depuis MongoDB
    global afk_users
    afk_users = load_afk_data_from_mongo()
    print(f"{bot.user} is ready and AFK data is loaded.")
    for guild in bot.guilds:
        if str(guild.id) not in afk_users:
            afk_users[str(guild.id)] = {}  # Si pas de données pour cette guilde, on l'ajoute
        print(f"AFK users for guild {guild.id}: {afk_users[str(guild.id)]}")

@bot.command(name='afk')
async def afk(ctx, *, reason: str = "AFK"):
    guild_id = str(ctx.guild.id)
    user_id = str(ctx.author.id)

    # Assurer que le dictionnaire a une sous-clé pour chaque serveur
    if guild_id not in afk_users:
        afk_users[guild_id] = {}

    # Vérifier si l'utilisateur est déjà AFK
    if user_id in afk_users[guild_id]:
        await ctx.send(f"{ctx.author.mention} is already AFK.")
        return

    # Stocker le statut AFK, la raison et l'heure de départ pour l'utilisateur dans ce serveur
    afk_users[guild_id][user_id] = (reason, time.time())
    save_afk_data_to_mongo(afk_users)  # Sauvegarder immédiatement les utilisateurs AFK dans le Gist

    embed = discord.Embed(
        description=f"💤 : {ctx.author.mention} is now AFK for the reason - **{reason}**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

#triggers 

triggers_collection = db['triggers']

# Fonction pour charger les données du serveur depuis MongoDB
def load_server_data(guild_id):
    try:
        # Récupérer les données du document de la guilde
        doc = triggers_collection.find_one({"guild_id": str(guild_id)})
        
        if doc:
            return doc.get('data', {})  # Retourne les données sous forme de dictionnaire
        else:
            return {}  # Retourner un dictionnaire vide si aucune donnée n'existe pour cette guilde
    except Exception as e:
        print(f"Erreur lors de la récupération des données du serveur {guild_id}: {e}")
        return {}

# Fonction pour sauvegarder les données du serveur dans MongoDB
def save_server_data(guild_id, data):
    try:
        # Mettre à jour les données pour le serveur spécifique
        result = triggers_collection.update_one(
            {"guild_id": str(guild_id)},  # Recherche du serveur
            {"$set": {"data": data}},  # Mise à jour des données
            upsert=True  # Crée le document si il n'existe pas
        )
        if result.modified_count > 0:
            print(f"Les données du serveur {guild_id} ont été mises à jour avec succès dans MongoDB.")
        else:
            print(f"Aucune modification n'a été effectuée pour le serveur {guild_id}.")
    except Exception as e:
        print(f"Erreur lors de la mise à jour des données du serveur {guild_id} dans MongoDB: {e}")

@bot.group(name='trigger', invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def set_trigger(ctx, phrase: str = None, *, role_name: str = None):
    current_prefix=load_prefix(ctx.guild.id)
    if not phrase or not role_name:
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
                    embed.add_field(name="Parameters", value="channel", inline=False)
                    embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Admin**", inline=False)
                    return embed

                # Pages d'usage
        pages = [
                    {
                        "title": "Command name : trigger ",
                        "description": "Set a status trigger for assigning roles (1 role only).",
                        "usage": f"```Syntax: {current_prefix}trigger <phrase> <role>.\n"
                                f"Example: {current_prefix}trigger i love gato role.```",
                        "footer": "Page 1/2"
                    },
                    {
                        "title": "Command name: trigger remove",
                        "description": "Remove the trigger.",
                        "usage": f"```Syntax: {current_prefix}trigger remove <phrase>\n"
                                f"Example: {current_prefix}trigger remove i love gato```",
                        "footer": "Page 2/2"
                    },
                

                ]

        async def update_embed(interaction, page_index):
                    embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
                    embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
                    embed.set_footer(text=f"{pages[page_index]['footer']} | Module: utilities.py • {current_time}")
                    await interaction.response.edit_message(embed=embed)

        buttons = await create_buttons(ctx, pages, update_embed, current_time)   

        initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
        initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
        initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: utilities.py • {current_time}")
        await ctx.send(embed=initial_embed, view=buttons)

        return

    guild_id = str(ctx.guild.id)

    # Récupérer le rôle en fonction du nom
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : Role '{role_name}' not found.",
            color=discord.Color(0x808080)
        )
        await ctx.send(embed=embed)
        return

    # Charger les données du serveur depuis Gist
    server_data = load_server_data(guild_id)

    # Sauvegarder la phrase et le rôle dans les données du serveur
    server_data['trigger'] = {
        "phrase": phrase,
        "role_id": role.id
    }
    save_server_data(guild_id, server_data)

    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Trigger set! Users with the phrase '{phrase}' in their status will receive the role '{role_name}'.",
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)


@set_trigger.command(name='remove')
@commands.has_permissions(administrator=True)
async def remove_trigger(ctx):
    guild_id = str(ctx.guild.id)

    # Charger les données du serveur depuis le Gist
    server_data = load_server_data(guild_id)

    # Si aucun trigger n'est défini, envoyer un message
    if 'trigger' not in server_data:
        embed = discord.Embed(
            description="<:warn:1297301606362251406> : No trigger is currently set for this server.",
            color=discord.Color(0x808080)
        )
        await ctx.send(embed=embed)
        return

    # Supprimer le trigger
    server_data.pop('trigger', None)

    # Sauvegarder les données mises à jour dans le Gist
    save_server_data(guild_id, server_data)

    embed = discord.Embed(
        description="<:approve:1297301591698706483> : Trigger removed successfully.",
        color=discord.Color(0x808080)
    )
    await ctx.send(embed=embed)



@bot.event
async def on_message(message):
    
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    # Charger les données AFK depuis le Gist pour le serveur
    if guild_id not in afk_users:
        afk_users[guild_id] = {}

    # Si l'utilisateur est AFK, on le retire et on envoie un message
    if user_id in afk_users[guild_id]:
        reason, start_time = afk_users[guild_id].pop(user_id)  # Retirer le statut AFK
        elapsed_time = round(time.time() - start_time)
        formatted_time = format_time(elapsed_time)

        # Sauvegarder immédiatement dans le Gist après suppression
        save_afk_data_to_mongo(afk_users)

        embed = discord.Embed(
            description=f"👋 : {message.author.mention}, you came back after **{formatted_time}**.",
            color=discord.Color.green()
        )
        await message.channel.send(embed=embed)

    # Vérifier si un utilisateur AFK est mentionné dans le message
    for afk_user_id, (reason, start_time) in afk_users[guild_id].items():
        user = bot.get_user(int(afk_user_id))
        if user is not None and (user in message.mentions or f'@{user.name}' in message.content):
            elapsed_time = round(time.time() - start_time)
            formatted_time = format_time(elapsed_time)

            embed = discord.Embed(
                description=f"🔔 : {user.mention} is currently AFK since **{formatted_time}** ago - **{reason}**",
                color=discord.Color.orange()
            )
            await message.channel.send(embed=embed, reference=message)
            break


    if message.content.startswith(f'<@{bot.user.id}>'):
        current_prefix = load_prefix(message.guild.id)
        embed = discord.Embed(
            description=f"👋 : It's not just a call, it's a warning to them. Prefix - `{current_prefix}`.",
            color=discord.Color(0x808080)
        )
        # Ajouter l'image GIF
        embed.set_image(url="https://c.tenor.com/QJjJ7Oy5stoAAAAd/tenor.gif")
        await message.channel.send(embed=embed)


    guild_id = str(message.guild.id)  # ID of the guild
    triggers = load_triggers(guild_id)  # Load triggers for the guild from Firestore

    # Check if there are triggers for this guild
    if guild_id in triggers:
        # Loop through the words and associated emojis
        for word, emoji in triggers[guild_id].items():
            if word in message.content:  # Check if the word exists in the message
                # Try to add the emoji reaction to the message
                try:
                    await message.add_reaction(emoji)
                except discord.HTTPException:
                    # If an error occurs (e.g., invalid emoji or permission issues)
                    embed = discord.Embed(
                        description=f"<:warn:1297301606362251406> : Unable to add reaction for `{word}`. The emoji `{emoji}` is not available on this server.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)
                    return

    await bot.process_commands(message)



#autoreact 

autoreact_collection = db['autoreact']

# Fonction pour charger les triggers depuis MongoDB
def load_triggers(guild_id):
    try:
        # Récupérer les triggers du serveur
        doc = autoreact_collection.find_one({"guild_id": str(guild_id)})
        
        if doc:
            return doc.get('triggers', {})  # Retourne les triggers sous forme de dictionnaire
        else:
            return {}  # Retourner un dictionnaire vide si aucune donnée n'existe pour cette guilde
    except Exception as e:
        print(f"Erreur lors de la récupération des triggers pour la guilde {guild_id}: {e}")
        return {}

# Fonction pour sauvegarder les triggers dans MongoDB
def save_triggers(guild_id, triggers):
    try:
        # Mettre à jour ou créer un document pour la guilde spécifique
        result = autoreact_collection.update_one(
            {"guild_id": str(guild_id)},  # Recherche du serveur
            {"$set": {"triggers": triggers}},  # Mise à jour des triggers
            upsert=True  # Crée le document si il n'existe pas
        )
        if result.modified_count > 0:
            print(f"Les triggers de la guilde {guild_id} ont été sauvegardés avec succès dans MongoDB.")
        else:
            print(f"Aucune modification n'a été effectuée pour la guilde {guild_id}.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des triggers dans MongoDB pour la guilde {guild_id}: {e}")

async def validate_emoji(ctx, emoji):
    if emoji.startswith('<:') and emoji.endswith('>'):
        emoji_id = int(emoji.split(':')[2][:-1])
        return discord.utils.get(ctx.guild.emojis, id=emoji_id) is not None
    else:
        return is_unicode_emoji(emoji)

def is_unicode_emoji(emoji):
    try:
        emoji.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


@bot.group(name='autoreact', invoke_without_command=True)
async def autoreact(ctx):
    current_prefix = load_prefix(ctx.guild.id)  # You can load the prefix for each server if necessary
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
            embed.add_field(name="Parameters", value="N/A", inline=False)
            embed.add_field(name="Permissions", value=f"<:warn:1297301606362251406> : **Admin**", inline=False)

            return embed

        # Pages d'usage
    pages = [
            {
                "title": "Command name: autoreact add",
                "description": "Add a reaction to a word, up to two emojis.",
                "usage": f"```Syntax: {current_prefix}autoreact add <word> <emoji> \n"
                          f"Example: {current_prefix}autoreact add gato :emoji:```",
                "footer": "Page 1/2"
            },
            {
                "title": "Command name: autoreact remove",
                "description": "Remove reaction to the word.",
                "usage": f"```Syntax: {current_prefix}autoreact remove <word> \n"
                          f"Example: {current_prefix}autoreact remove gato```",
                "footer": "Page 2/2"
            },
        ]

    async def update_embed(interaction, page_index):
            embed = create_embed(pages[page_index]["title"], pages[page_index]["description"])
            embed.add_field(name="Usage", value=pages[page_index]["usage"], inline=False)
            embed.set_footer(text=f"{pages[page_index]['footer']} | Module: utilities.py • {current_time}")
            await interaction.response.edit_message(embed=embed)

    buttons = await create_buttons(ctx, pages, update_embed, current_time)

    initial_embed = create_embed(pages[0]["title"], pages[0]["description"])
    initial_embed.add_field(name="Usage", value=pages[0]["usage"], inline=False)
    initial_embed.set_footer(text=f"{pages[0]['footer']} | Module: utilities.py • {current_time}")

    await ctx.send(embed=initial_embed, view=buttons)

@autoreact.command(name='add')
@commands.has_permissions(administrator=True)
async def set_trigger(ctx, word: str = None, *emojis: str):
    guild_id = str(ctx.guild.id)  # ID of the server
    triggers = load_triggers(guild_id)  # Load triggers for the guild

    # If word or emojis are not provided, show the help message
    if word is None or len(emojis) == 0:
        embed = discord.Embed(
            title="Command: add",
            description='Add a reaction to a specified word.',
            color=discord.Color(0x808080)
        )

        embed.set_author(
            name=f"{bot.user.name}",
            icon_url=bot.user.avatar.url
        )

        embed.add_field(
            name="Aliases", 
            value="N/A", 
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="word, emojis", 
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value="<:warn:1297301606362251406> : **Admin**", 
            inline=False
        )

        embed.add_field(
            name="Usage", 
            value=f"```Syntax: add <word> <emoji1> <emoji2>\nExample: add gato 👍 ❤️```",
            inline=False
        )

        embed.set_footer(
            text=f"Page 1/1 | Module: utilities.py · {current_time}"
        )

        await ctx.send(embed=embed)
        return

    if len(emojis) > 2:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : You can only add up to 2 emojis.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # Validate emojis
    invalid_emojis = []
    for emoji in emojis:
        if not await validate_emoji(ctx, emoji):
            invalid_emojis.append(emoji)

    if invalid_emojis:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : The following emoji(s) are not available on this server or are invalid: {', '.join(invalid_emojis)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    # If guild doesn't have triggers yet, initialize it
    if guild_id not in triggers:
        triggers[guild_id] = {}

    # Add the word and emojis to the triggers
    triggers[guild_id][word] = " ".join(emojis)

    # Save the updated triggers back to Firestore
    save_triggers(guild_id, triggers)

    embed = discord.Embed(
        description=f"<:approve:1297301591698706483> : Reaction added - The word `{word}` will react with the emoji(s) {', '.join(emojis)}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@autoreact.command(name='remove')
@commands.has_permissions(administrator=True)
async def remove_trigger(ctx, word: str = None):
    current_prefix = load_prefix(ctx.guild.id)  # Modify according to your needs for your prefix

    # Check if the word is provided
    if word is None:
        embed = discord.Embed(
            title="Command name: remove",
            description='Remove a reaction associated with a specified word.',
            color=discord.Color(0x808080)  # Dark gray color
        )

        embed.set_author(
            name=f"{bot.user.name}",  # Bot's name
            icon_url=bot.user.avatar.url  # Bot's avatar
        )

        embed.add_field(
            name="Aliases", 
            value="N/A",  # No aliases for this command
            inline=False
        )

        embed.add_field(
            name="Parameters", 
            value="word",  # Parameter for this command
            inline=False
        )

        embed.add_field(
            name="Permissions", 
            value=f"<:approve:1297301591698706483> : **Admin**", 
            inline=False
        )

        # Combined Syntax and Example
        embed.add_field(
            name="Usage", 
            value=f"```Syntax: {current_prefix}remove <word>\n"
                  f"Example: {current_prefix}remove gato```",
            inline=False
        )

        # Modify footer with pagination, module, and time
        embed.set_footer(
            text=f"Page 1/1 | Module: utilities.py · {current_time}"
        )

        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    triggers = load_triggers(guild_id)  # Load existing triggers from Firestore

    if guild_id in triggers and word in triggers[guild_id]:
        del triggers[guild_id][word]  # Remove the trigger for the word
        save_triggers(guild_id, triggers)  # Save updated triggers in Firestore
        embed = discord.Embed(
            description=f"<:approve:1297301591698706483> : The reaction is no longer added to the word `{word}`.",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            description=f"<:warn:1297301606362251406> : No trigger found for the word `{word}`.",
            color=discord.Color.red()
        )

    await ctx.send(embed=embed)


# Handle permission errors for commands
@set_trigger.error
async def set_trigger_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await send_permission_error(ctx)

@remove_trigger.error
async def remove_trigger_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await send_permission_error(ctx)

#---------------------------------------------

@bot.event
async def on_presence_update(before, after):
    guild = after.guild
    guild_id = str(guild.id)

    # Charger les données du serveur depuis le Gist
    server_data = load_server_data(guild_id)

    # Si aucun trigger n'est défini pour ce serveur, sortir
    if 'trigger' not in server_data:
        return

    trigger_phrase = server_data['trigger']['phrase']
    role_id = server_data['trigger']['role_id']
    role = discord.utils.get(guild.roles, id=role_id)

    if not role:
        print(f"Role with ID {role_id} not found in guild {guild.name}.")
        return

    # Vérifier si l'utilisateur est offline
    if after.status == discord.Status.offline:
        # Retirer le rôle si l'utilisateur est offline
        if role in after.roles:
            await after.remove_roles(role)
            print(f"Removed role {role.name} from {after.name} (offline)")
        return

    # Vérifier le statut personnalisé
    custom_status = next((activity for activity in after.activities if isinstance(activity, discord.CustomActivity)), None)

    if custom_status and trigger_phrase in custom_status.name:
        # Ajouter le rôle si la phrase est présente dans le statut
        if role not in after.roles:
            await after.add_roles(role)
            print(f"Added role {role.name} to {after.name} (status contains trigger)")
    else:
        # Retirer le rôle si la phrase n'est plus présente
        if role in after.roles:
            await after.remove_roles(role)
            print(f"Removed role {role.name} from {after.name} (status doesn't contain trigger)")
