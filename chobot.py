import os
import random
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="ini.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Constants
CHANNEL_ID = 1385795977600045217
GUILD_ID = 737751372790890508
guild = discord.Object(id=GUILD_ID)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Track last webhook message
last_webhook_message_id = None


@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    await bot.change_presence(status=discord.Status.dnd)
    try:
        await bot.tree.sync(guild=guild)
        print("Comandos sincronizados")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")


@bot.event
async def on_message(message: discord.Message):
    global last_webhook_message_id

    if message.channel.id != CHANNEL_ID or not message.webhook_id:
        return

    if last_webhook_message_id and last_webhook_message_id != message.id:
        try:
            old_msg = await message.channel.fetch_message(last_webhook_message_id)
            await old_msg.delete()
        except discord.NotFound:
            pass

    last_webhook_message_id = message.id


@bot.tree.command(name="comandos", description="Exibe lista de comandos do bot", guild=guild)
async def comandos(interaction: discord.Interaction):
    embed = discord.Embed(color=discord.Color.yellow())
    embed.add_field(name="/comandos", value="Exibe lista de comandos do bot", inline=False)
    embed.add_field(name="/convite", value="Envia um link com convite para o servidor", inline=False)
    embed.add_field(name="/rolar", value="Rola um dado com valor escolhido", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="convite", description="Envia um link com convite para o servidor", guild=guild)
async def convite(interaction: discord.Interaction):
    embed = discord.Embed(color=discord.Color.dark_gray())
    embed.set_image(url="https://i.ibb.co/fn7VvQZ/welcome.gif")
    await interaction.response.send_message(
        content="https://discord.gg/D48QWY6MhK",
        embed=embed
    )


@bot.tree.command(name="rolar", description="Rola um dado com valor escolhido", guild=guild)
@app_commands.describe(d="Valor do dado")
async def rolar(interaction: discord.Interaction, d: int):
    if d < 2:
        await interaction.response.send_message(
            "O valor do dado deve ser no mínimo 2.",
            ephemeral=True
        )
        return

    diceroll = random.randint(1, d)

    if d == 20 and diceroll == 20:
        color = discord.Color.green()
        title = "**ACERTO CRÍTICO!**"
        image = "https://i.ibb.co/wyQPZcT/success.gif"
    elif d == 20 and diceroll == 1:
        color = discord.Color.red()
        title = "**FALHA CRÍTICA!**"
        image = "https://i.ibb.co/N9wwKW8/fail.gif"
    else:
        color = discord.Color.blue()
        title = None
        image = None

    embed = discord.Embed(color=color)
    embed.set_author(name=f"D{d} 🎲")
    if title:
        embed.add_field(name=title, value=" ", inline=False)
    embed.add_field(
        name=" ",
        value=f"**<@{interaction.user.id}>** rolou um **{diceroll}**",
        inline=False
    )
    if image:
        embed.set_image(url=image)

    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)
