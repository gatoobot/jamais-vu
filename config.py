# config.py
import os
import io
import json
import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import Embed, ButtonStyle
from datetime import datetime, timedelta
import random
import asyncio
import time
from discord import Embed, ButtonStyle
import re 
import aiohttp
import requests
from PIL import Image
import pytz
from timezonefinder import TimezoneFinder
import instaloader
from urllib.parse import quote
from discord import File
from collections import defaultdict
from discord import Sticker


from dotenv import load_dotenv
from prefix import get_prefix, register_prefix_commands,load_prefix


#send perms 
async def send_permission_error(ctx):
    embed = discord.Embed(
        description=f"<:warn:1297301606362251406> : You do not have permission to use this command.",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)

def has_manage_messages():
    async def predicate(ctx):
        if ctx.author.guild_permissions.manage_messages:
            return True
        else:
            embed = discord.Embed(
                title="",
                description=f"<:warn:1297301606362251406> : You do not have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return False
    return commands.check(predicate)

#-----------------------------------------

current_time = datetime.now().strftime('%H:%M')



# Charger les variables d'environnement
load_dotenv()

# Charger le token depuis les variables d'environnement
TOKEN = os.getenv('TOKEN')

# Configurer les intents
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True
intents.guilds = True
intents.emojis = True
intents.voice_states = True
intents.presences = True 

# Créer l'instance du bot
bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=None)

# Fonction pour charger les extensions
def load_extensions():
    # Charger les extensions
    register_prefix_commands(bot)

#buttons 

async def create_buttons(ctx, pages, update_embed, current_time):
    buttons = View(timeout=60)
    index = 0

    previous_button = Button(emoji="<:previous:1297292075221389347>", style=discord.ButtonStyle.primary, disabled=True)
    next_button = Button(emoji="<:next:1297292115688292392>", style=discord.ButtonStyle.primary)
    close_button = Button(emoji="<:cancel:1297292129755861053>", style=discord.ButtonStyle.danger)

    # Callback pour le bouton précédent
    async def previous_callback(interaction):
        nonlocal index
        if interaction.user.id == ctx.author.id and index > 0:
            index -= 1
            await update_embed(interaction, index)
            previous_button.disabled = index == 0
            next_button.disabled = index == len(pages) - 1
            await interaction.message.edit(view=buttons)
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
        nonlocal index
        if interaction.user.id == ctx.author.id and index < len(pages) - 1:
            index += 1
            await update_embed(interaction, index)
            previous_button.disabled = index == 0
            next_button.disabled = index == len(pages) - 1
            await interaction.message.edit(view=buttons)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description="<:warn:1297301606362251406> : You are not the author of this message.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    # Callback pour fermer l'embed
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

    # Attacher les callbacks aux boutons
    previous_button.callback = previous_callback
    next_button.callback = next_callback
    close_button.callback = close_callback

    buttons.add_item(previous_button)
    buttons.add_item(next_button)
    buttons.add_item(close_button)

    return buttons