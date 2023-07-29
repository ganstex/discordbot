import discord
from discord.ext import commands

# Configura el prefijo para los comandos del bot
prefix = "!"  # Puedes cambiar el prefijo a lo que desees

# Crea una instancia del bot con el prefijo definido
bot = commands.Bot(command_prefix=prefix)

# Evento que se ejecuta cuando el bot está listo y conectado a Discord
@bot.event
async def on_ready():
    print(f"¡{bot.user.name} está listo para ser utilizado!")

# Comando simple
@bot.command()
async def hola(ctx):
    await ctx.send(f"Hola, {ctx.author.mention}!")

# Comando para sumar dos números
@bot.command()
async def sumar(ctx, num1: int, num2: int):
    resultado = num1 + num2
    await ctx.send(f"El resultado de {num1} + {num2} es {resultado}.")

# Comando para mostrar información sobre el bot
@bot.command()
async def informacion(ctx):
    embed = discord.Embed(title="Información del Bot",
                          description="Este es un bot de ejemplo creado con discord.py",
                          color=discord.Color.blue())
    embed.add_field(name="Autor", value="Tu Nombre Aquí")
    embed.add_field(name="Versión", value="1.0")
    await ctx.send(embed=embed)

# Ejecutar el bot con el token del bot que obtuviste desde el sitio web de desarrolladores de Discord
bot.run("MTEzNDk3MjAyNzQ4OTQ5Mjk5Mg.GEiSF9.OLp3Hrizi5zhre3YgM2ma3Qv6Afm7w2y_T6gc8")
