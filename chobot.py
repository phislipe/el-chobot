import os
import re
import random
import logging
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

OPTION_EMOJIS = [
    "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯",
    "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹"
]

ROLL_TIMEOUT = 15
GIVEAWAY_MIN_TIME = 5
GIVEAWAY_MAX_TIME = 300

load_dotenv(dotenv_path="ini.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

GUILD_ID = 737751372790890508
guild = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="", intents=intents)


@bot.event
async def on_ready():
    logging.info(f"Bot connected as {bot.user}")
    await bot.change_presence(status=discord.Status.dnd)
    try:
        await bot.tree.sync(guild=guild)
        logging.info("Commands synced successfully")
    except Exception as e:
        logging.error(f"Error while syncing commands: {e}")


@bot.tree.command(name="comandos", description="Exibe lista de comandos do bot", guild=guild)
async def show_commands(interaction: discord.Interaction):
    embed = discord.Embed(title="📋 Comandos disponíveis", color=discord.Color.yellow())
    embed.add_field(name="/comandos", value="Exibe esta lista de comandos", inline=False)
    embed.add_field(name="/convite", value="Envia um link com convite para o servidor", inline=False)
    embed.add_field(name="/rolar", value="Rola dados no formato XdY (ex: 4d6)", inline=False)
    embed.add_field(name="/enquete", value="Cria uma enquete com múltiplas opções", inline=False)
    embed.add_field(name="/sorteio", value="Inicia um sorteio por reação com tempo e emoji customizáveis", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="convite", description="Envia um link com convite para o servidor", guild=guild)
async def invite(interaction: discord.Interaction):
    embed = discord.Embed(color=discord.Color.dark_gray())
    embed.set_image(url="https://i.ibb.co/fn7VvQZ/welcome.gif")
    await interaction.response.send_message(
        content="https://discord.gg/D48QWY6MhK",
        embed=embed
    )


class RollAgainView(View):
    def __init__(self, dice: str):
        super().__init__(timeout=ROLL_TIMEOUT)
        self.dice = dice
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(view=None)
            except discord.NotFound:
                pass

    @discord.ui.button(label="🎲 Rolar novamente", style=discord.ButtonStyle.primary)
    async def reroll_button(self, interaction: discord.Interaction, button: Button):
        match = re.match(r"^(\d+)d(\d+)$", self.dice.lower())
        if not match:
            await interaction.response.send_message("Formato inválido. Use XdY, ex: 4d6", ephemeral=True)
            return

        quantity, faces = int(match.group(1)), int(match.group(2))

        if quantity < 1 or faces < 2 or quantity > 100 or faces > 1000:
            await interaction.response.send_message("Use até 100 dados com até 1000 lados.", ephemeral=True)
            return

        rolls = [random.randint(1, faces) for _ in range(quantity)]
        total = sum(rolls)

        embed = discord.Embed(
            title=f"Rolagem {quantity}d{faces}",
            description=f"Rolagens: {', '.join(str(r) for r in rolls)}\nTotal: **{total}**",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Rolado por {interaction.user.display_name}")

        await interaction.response.edit_message(embed=embed, view=self)


@bot.tree.command(name="rolar", description="Rola dados no formato XdY (ex: 4d6)", guild=guild)
@app_commands.describe(dado="Formato XdY, por exemplo: 4d6")
async def roll(interaction: discord.Interaction, dado: str):
    match = re.match(r"^(\d+)d(\d+)$", dado.lower())
    if not match:
        await interaction.response.send_message("Formato inválido. Use XdY, ex: 4d6", ephemeral=True)
        return

    quantity, faces = int(match.group(1)), int(match.group(2))
    if quantity < 1 or faces < 2 or quantity > 100 or faces > 1000:
        await interaction.response.send_message("Use até 100 dados com até 1000 lados.", ephemeral=True)
        return

    rolls = [random.randint(1, faces) for _ in range(quantity)]
    total = sum(rolls)

    embed = discord.Embed(
        title=f"Rolagem {quantity}d{faces}",
        description=f"Rolagens: {', '.join(str(r) for r in rolls)}\nTotal: **{total}**",
        color=discord.Color.orange()
    )
    embed.set_footer(text=f"Rolado por {interaction.user.display_name}")

    view = RollAgainView(dado)
    await interaction.response.send_message(embed=embed, view=view)
    view.message = await interaction.original_response()


@bot.tree.command(name="enquete", description="Cria uma enquete com múltiplas opções", guild=guild)
@app_commands.describe(
    pergunta="Pergunta da enquete",
    opcoes="Opções separadas por vírgula. Ex: Sim, Não, Talvez"
)
async def poll(interaction: discord.Interaction, pergunta: str, opcoes: str):
    options_list = [opt.strip() for opt in opcoes.split(",") if opt.strip()]

    if not 2 <= len(options_list) <= 20:
        await interaction.response.send_message(
            "Você deve fornecer entre 2 e 20 opções, separadas por vírgula.", ephemeral=True
        )
        return

    description = "\n".join(f"{OPTION_EMOJIS[i]} {opt}" for i, opt in enumerate(options_list))

    embed = discord.Embed(
        title=f"📊 {pergunta}",
        description=description,
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Iniciada por {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    for i in range(len(options_list)):
        await msg.add_reaction(OPTION_EMOJIS[i])


class GiveawayView(View):
    def __init__(self, interaction: discord.Interaction, emoji: str, timeout: int = 300):
        super().__init__(timeout=timeout)
        self.starter = interaction.user
        self.emoji = emoji
        self.message = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.starter:
            await interaction.response.send_message(
                f"Apenas {self.starter.mention} pode sortear ou cancelar.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="🎲 Sortear", style=discord.ButtonStyle.success)
    async def draw(self, interaction: discord.Interaction, button: Button):
        msg = await interaction.channel.fetch_message(self.message.id)
        reaction = next((r for r in msg.reactions if str(r.emoji) == str(self.emoji)), None)

        if reaction is None or reaction.count <= 1:
            await interaction.response.edit_message(content="Ninguém reagiu para participar do sorteio.", view=None)
            self.stop()
            return

        users = [user async for user in reaction.users()]
        participants = [u for u in users if not u.bot]

        winner = random.choice(participants)
        await interaction.response.edit_message(content=f"🎉 O vencedor do sorteio é {winner.mention}!", view=None)
        self.stop()

    @discord.ui.button(label="🚫 Cancelar", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="Sorteio cancelado.", view=None)
        self.stop()


@bot.tree.command(name="sorteio", description="Sorteio entre quem reagir à mensagem", guild=guild)
@app_commands.describe(name="Nome do sorteio", tempo="Tempo para reagir", emoji="Emoji para reagir")
async def giveaway_reaction(interaction: discord.Interaction, name: str, tempo: int = 30, emoji: str = "🎉"):
    if tempo < GIVEAWAY_MIN_TIME or tempo > GIVEAWAY_MAX_TIME:
        await interaction.response.send_message(
            f"Tempo deve ser entre {GIVEAWAY_MIN_TIME} e {GIVEAWAY_MAX_TIME} segundos.", ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"**{name}**\nReaja com {emoji} para participar!\nVocê tem {tempo} segundos para reagir."
    )
    msg = await interaction.original_response()
    try:
        await msg.add_reaction(emoji)
    except discord.HTTPException:
        await interaction.followup.send("Emoji inválido ou sem permissão para usá-lo.", ephemeral=True)
        return

    view = GiveawayView(interaction, emoji, timeout=tempo)
    view.message = msg
    await msg.edit(view=view)

    await view.wait()

    if view.is_finished():
        return

    reaction = next((r for r in msg.reactions if str(r.emoji) == str(emoji)), None)
    if reaction is None or reaction.count <= 1:
        await interaction.followup.send("Ninguém reagiu para participar do sorteio.", ephemeral=True)
        return

    users = [user async for user in reaction.users()]
    participants = [u for u in users if not u.bot]
    winner = random.choice(participants)

    await msg.edit(content=f"🎉 O vencedor do sorteio **{name}** é {winner.mention}!", view=None)


bot.run(TOKEN)
