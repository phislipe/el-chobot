import os
import re
import asyncio
import random
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
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


class RollAgainView(View):
    def __init__(self, dado: str):
        super().__init__(timeout=15)
        self.dado = dado
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(view=None)
            except discord.NotFound:
                pass

    @discord.ui.button(label="🎲 Rolar novamente", style=discord.ButtonStyle.primary)
    async def reroll_button(self, interaction: discord.Interaction, button: Button):
        match = re.match(r"^(\d+)d(\d+)$", self.dado.lower())
        if not match:
            await interaction.response.send_message(
                "Formato inválido. Use XdY, ex: 4d6",
                ephemeral=True
            )
            return

        qtd, faces = int(match.group(1)), int(match.group(2))
        rolls = [random.randint(1, faces) for _ in range(qtd)]
        total = sum(rolls)

        embed = discord.Embed(
            title=f"Rolagem {qtd}d{faces}",
            description=f"Rolagens: {', '.join(str(r) for r in rolls)}\nTotal: **{total}**",
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Rolado por {interaction.user.display_name}")

        await interaction.response.edit_message(embed=embed, view=self)


@bot.tree.command(name="rolar", description="Rola dados no formato XdY (ex: 4d6)", guild=guild)
@app_commands.describe(dado="Formato XdY, por exemplo: 4d6")
async def rolar(interaction: discord.Interaction, dado: str):
    match = re.match(r"^(\d+)d(\d+)$", dado.lower())
    if not match:
        await interaction.response.send_message(
            "Formato inválido. Use XdY, ex: 4d6",
            ephemeral=True
        )
        return

    qtd, faces = int(match.group(1)), int(match.group(2))
    if qtd < 1 or faces < 2:
        await interaction.response.send_message(
            "Quantidade mínima: 1 dado de 2 lados.",
            ephemeral=True
        )
        return

    rolls = [random.randint(1, faces) for _ in range(qtd)]
    total = sum(rolls)

    embed = discord.Embed(
        title=f"Rolagem {qtd}d{faces}",
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
async def enquete(interaction: discord.Interaction, pergunta: str, opcoes: str):
    opcoes_lista = [op.strip() for op in opcoes.split(",") if op.strip()]
    
    if not 2 <= len(opcoes_lista) <= 20:
        await interaction.response.send_message(
            "Você deve fornecer entre 2 e 20 opções, separadas por vírgula.",
            ephemeral=True
        )
        return

    emojis = [
        "🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯",
        "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", "🇶", "🇷", "🇸", "🇹"
    ]

    descricao = "\n".join(f"{emojis[i]} {op}" for i, op in enumerate(opcoes_lista))

    embed = discord.Embed(
        title=f"📊 {pergunta}",
        description=descricao,
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Iniciada por {interaction.user.display_name}")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    for i in range(len(opcoes_lista)):
        await msg.add_reaction(emojis[i])


class SorteioView(View):
    def __init__(self, interaction, emoji, timeout=300):
        super().__init__(timeout=timeout)
        self.iniciador = interaction.user
        self.emoji = emoji
        self.message = None

    async def interaction_check(self, interaction):
        if interaction.user != self.iniciador:
            await interaction.response.send_message("Só o iniciador pode usar esses botões.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="🎲 Sortear", style=discord.ButtonStyle.success)
    async def sortear(self, interaction: discord.Interaction, button: Button):
        msg = await interaction.channel.fetch_message(self.message.id)
        reaction = discord.utils.get(msg.reactions, emoji=self.emoji)

        if reaction is None or reaction.count <= 1:
            await interaction.response.edit_message(content="Ninguém reagiu para participar do sorteio.", view=None)
            self.stop()
            return

        users = [user async for user in reaction.users()]
        participantes = [u for u in users if not u.bot]

        vencedor = random.choice(participantes)
        await interaction.response.edit_message(content=f"🎉 O vencedor do sorteio é {vencedor.mention}!", view=None)
        self.stop()

    @discord.ui.button(label="🚫 Cancelar", style=discord.ButtonStyle.danger)
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="Sorteio cancelado.", view=None)
        self.stop()


@bot.tree.command(name="sorteio", description="Sorteio entre quem reagir à mensagem", guild=guild)
@app_commands.describe(nome="Nome do sorteio", tempo="Tempo para reagir", emoji="Emoji para reagir")
async def sorteio_reacao(interaction: discord.Interaction, nome: str, tempo: int = 30, emoji: str = "🎉"):
    if tempo < 5 or tempo > 300:
        await interaction.response.send_message("Tempo deve ser entre 5 e 300 segundos.", ephemeral=True)
        return

    await interaction.response.send_message(
        f"**{nome}**\nReaja com  {emoji}  para participar!\nVocê tem {tempo} segundos para reagir."
    )
    msg = await interaction.original_response()
    try:
        await msg.add_reaction(emoji)
    except:
        await interaction.followup.send("Emoji inválido.", ephemeral=True)
        return

    view = SorteioView(interaction, emoji, timeout=tempo)
    view.message = msg
    await msg.edit(view=view)

    await view.wait()

    if view.is_finished():  # Ou view.is_finished() == True
        # Se a view já foi parada (botão clicado)
        return  # Não faça mais nada

    # Caso timeout e view não foi parada, faça o sorteio automático
    reaction = discord.utils.get(msg.reactions, emoji=emoji)
    if reaction is None or reaction.count <= 1:
        await interaction.followup.send("Ninguém reagiu para participar do sorteio.", ephemeral=True)
        return

    users = [user async for user in reaction.users()]
    participantes = [u for u in users if not u.bot]
    vencedor = random.choice(participantes)

    await msg.edit(content=f"🎉 O vencedor do sorteio **{nome}** é {vencedor.mention}!", view=None)

bot.run(TOKEN)
