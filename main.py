import discord
from discord.ext import commands
import pymongo
import urllib.parse
from datetime import datetime

# Conexión a MongoDB
username = urllib.parse.quote_plus("TheRsbx")  # Reemplaza con tu nombre de usuario
password = urllib.parse.quote_plus("TheRs@MongoDB9966")  # Reemplaza con tu contraseña
client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.baqaobk.mongodb.net/")
db = client["TheRsbx"]  # Nombre de tu base de datos
collection = db["warns"]  # Nombre de la colección para almacenar los warns

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=',', intents=intents)

# Mensaje de confirmación cuando el bot está listo
@bot.event
async def on_ready():
    print(f'Conectado como {bot.user.name}')

# Comando !saludar
@bot.command()
async def saludar(ctx):
    response = 'Hola cabron'
    await ctx.send(response)

# Comando !purge
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, cantidad: int):
    if cantidad <= 0:
        await ctx.send('Por favor, especifica una cantidad válida de mensajes para eliminar')
        return

    deleted = await ctx.channel.purge(limit=cantidad)
    await ctx.send(f'Se han eliminado {len(deleted)} mensajes.', delete_after=5)

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Por favor, especifica la cantidad de mensajes que quieres eliminar. Uso: `,purge <cantidad>`')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('No tienes permisos para eliminar mensajes.')

# Comando !warn
@bot.command()
async def warn(ctx, member: discord.Member=None, *, reason: str=None):
    if member is None:
        await ctx.send('Por favor, menciona a un usuario para emitir un warn. Uso: `,warn @usuario [razón]`')
        return

    if reason is None:
        await ctx.send('Por favor, proporciona una razón para emitir un warn. Uso: `,warn @usuario [razón]`')
        return

    # Si se proporciona el ID en lugar de mencionar al usuario
    if isinstance(member, int):
        try:
            member = await bot.fetch_user(member)
        except discord.errors.NotFound:
            await ctx.send('No se encontró al usuario con el ID proporcionado.')
            return
        except discord.errors.HTTPException:
            await ctx.send('Ocurrió un error al intentar buscar al usuario.')
            return

    # Guardar el warn en MongoDB
    warn_entry = {
        "guild_id": ctx.guild.id,
        "guild_name": ctx.guild.name,
        "user_id": member.id,
        "user_name": member.display_name,
        "user_discriminator": member.discriminator,
        "user_avatar": str(member.avatar) if member.avatar else None,
        "moderator_id": ctx.author.id,
        "moderator_name": ctx.author.display_name,
        "reason": reason,
        "timestamp": datetime.utcnow()  # Agregar marca de tiempo
    }
    collection.insert_one(warn_entry)

    # Crear embed
    embed = discord.Embed(title="⚠️ Sistema de Moderación", description=f"El usuario {member.mention} ha recibido un warn.", color=discord.Color.orange())
    embed.add_field(name="Usuario", value=f"{member.mention} (`{member.id}`)", inline=False)
    embed.add_field(name="Razón", value=reason, inline=False)
    embed.set_footer(text="Warn ⚠️")

    # Agregar la foto del usuario si está disponible, o el avatar predeterminado de Discord si no lo está
    if member.avatar:
        embed.set_thumbnail(url=str(member.avatar))
    else:
        embed.set_thumbnail(url=member.default_avatar.url)

    # Enviar embed
    await ctx.send(embed=embed)

# Comando !warns
@bot.command()
async def warns(ctx, member: discord.Member = None, warn_id: int = None):
    if member is None:
        await ctx.send('Por favor, menciona a un usuario o proporciona su ID para ver sus warns. Uso: `,warns @usuario` o `,warns <ID>`')
        return

    # Si se proporciona el ID en lugar de mencionar al usuario
    if isinstance(member, int):
        try:
            member = await bot.fetch_user(member)
        except discord.errors.NotFound:
            await ctx.send('No se encontró al usuario con el ID proporcionado.')
            return
        except discord.errors.HTTPException:
            await ctx.send('Ocurrió un error al intentar buscar al usuario.')
            return

    # Consultar los warns en MongoDB
    warns = list(collection.find({"guild_id": ctx.guild.id, "user_id": member.id}))

    warn_count = len(warns)
    if warn_count == 0:
        await ctx.send(f'El usuario {member.mention} no tiene warns.')
        return

    # Determinar qué warn mostrar
    if warn_id is None:
        # Mostrar el último warn
        warn_to_show = warns[-1]
    else:
        if warn_id <= 0 or warn_id > warn_count:
            await ctx.send(f'El usuario {member.mention} solo tiene {warn_count} warns.')
            return
        # Mostrar el warn específico
        warn_to_show = warns[warn_id - 1]

    # Crear embed
    description = f"El usuario {member.mention} tiene {warn_count} warns."
    description += f"\n\n**Warn Número {warn_id if warn_id else warn_count}:**\n**Razón:** {warn_to_show['reason']}\n**Moderador:** <@{warn_to_show['moderator_id']}>"
    if 'timestamp' in warn_to_show:
        description += f"\n**Fecha:** {warn_to_show['timestamp'].strftime('%Y-%m-%d')}"

    embed = discord.Embed(title="⚠️ Sistema de Moderación", description=description, color=discord.Color.orange())
    embed.add_field(name="Usuario", value=f"{member.mention} (`{member.id}`)", inline=False)
    embed.set_footer(text="Warns ⚠️")

    # Agregar la foto del usuario si está disponible, o el avatar predeterminado de Discord si no lo está
    if member.avatar:
        embed.set_thumbnail(url=str(member.avatar))
    else:
        embed.set_thumbnail(url=member.default_avatar.url)

    # Enviar embed
    await ctx.send(embed=embed)

# Comando !clearwarns
@bot.command()
@commands.has_permissions(administrator=True)
async def clearwarns(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send('Por favor, menciona a un usuario o proporciona su ID para eliminar sus warns. Uso: `,clearwarns @usuario` o `,clearwarns <ID>`')
        return

    # Si se proporciona el ID en lugar de mencionar al usuario
    if isinstance(member, int):
        try:
            member = await bot.fetch_user(member)
        except discord.errors.NotFound:
            await ctx.send('No se encontró al usuario con el ID proporcionado.')
            return
        except discord.errors.HTTPException:
            await ctx.send('Ocurrió un error al intentar buscar al usuario.')
            return

    # Eliminar los warns en MongoDB
    result = collection.delete_many({"guild_id": ctx.guild.id, "user_id": member.id})

    # Confirmar eliminación
    await ctx.send(f'Se han eliminado {result.deleted_count} warns del usuario {member.mention}. Ahora tiene 0 warns.')

@bot.command()
async def say(ctx, *, message):
    await ctx.message.delete()  # Eliminar el mensaje del usuario
    await ctx.send(message)  # Enviar el mensaje especificado por el usuario


# Ejecutar el bot con el token del entorno
bot.run("MTI1NTI3MDE1MjA2OTcxNDA2MA.GLYeDz.7ZiY0NZnbciMyECmrRrdxFY1sCyiN1KG5MsdU8")
