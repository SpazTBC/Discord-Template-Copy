import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Bot configuration
TOKEN = os.getenv('TOKEN')
PREFIX = os.getenv('PREFIX')

# Parse role IDs
ADMIN_ROLES = [int(role_id) for role_id in os.getenv('ADMIN_ROLES', '').split(',') if role_id]
MOD_ROLES = [int(role_id) for role_id in os.getenv('MOD_ROLES', '').split(',') if role_id]
VIP_ROLES = [int(role_id) for role_id in os.getenv('VIP_ROLES', '').split(',') if role_id]

# Set up intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready! Logged in as {bot.user.name} ({bot.user.id})')
    print(f'Admin roles: {ADMIN_ROLES}')
    print(f'Mod roles: {MOD_ROLES}')
    print(f'VIP roles: {VIP_ROLES}')

# Check if user has admin permissions
def is_admin():
    async def predicate(ctx):
        if ctx.author.guild_permissions.administrator:
            return True
        for role in ctx.author.roles:
            if role.id in ADMIN_ROLES:
                return True
        return False
    return commands.check(predicate)

# Main template copying functionality
@bot.command(name="copy_template")
@is_admin()
async def copy_template(ctx, source_guild_id: int, target_guild_id: int = None):
    """
    Copy a template from a source guild to a target guild.
    If target_guild_id is not provided, the current guild will be used.
    """
    # Get source guild
    source_guild = bot.get_guild(source_guild_id)
    if not source_guild:
        await ctx.send(f"❌ Source guild with ID {source_guild_id} not found.")
        return

    # Get target guild
    if target_guild_id:
        target_guild = bot.get_guild(target_guild_id)
        if not target_guild:
            await ctx.send(f"❌ Target guild with ID {target_guild_id} not found.")
            return
    else:
        target_guild = ctx.guild

    # Confirm operation
    confirmation_message = await ctx.send(
        f"⚠️ This will copy all channels, categories, roles, and permissions from {source_guild.name} "
        f"to {target_guild.name} and **DELETE** any channels, categories, and roles that don't exist in the source guild. "
        f"This operation cannot be undone. React with ✅ to continue."
    )
    await confirmation_message.add_reaction("✅")
    await confirmation_message.add_reaction("❌")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == confirmation_message.id

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
        if str(reaction.emoji) == "❌":
            await ctx.send("Operation cancelled.")
            return
    except asyncio.TimeoutError:
        await ctx.send("Operation timed out.")
        return

    # Create a DM channel with the user for status updates
    try:
        dm_channel = await ctx.author.create_dm()
        await dm_channel.send("🔄 Starting template copy process... I'll send you updates here since the server channels will be deleted.")
    except Exception as e:
        print(f"Could not create DM channel: {e}")
        await ctx.send("⚠️ I couldn't create a DM channel with you. Please make sure your DMs are open. Continuing with the process...")
        dm_channel = None
    
    # Final confirmation before starting
    await ctx.send("Starting the template copying process. This may take a while...")
    
    try:
        # Delete existing channels and categories
        if dm_channel:
            await dm_channel.send("🔄 Deleting existing channels and categories...")
        print("Deleting existing channels and categories...")
        await delete_existing_channels(target_guild)
        
        # Copy roles first (needed for permissions)
        if dm_channel:
            await dm_channel.send("🔄 Copying roles...")
        print("Copying roles...")
        role_map = await copy_roles(source_guild, target_guild)
        
        # Copy categories and channels
        if dm_channel:
            await dm_channel.send("🔄 Copying categories and channels...")
        print("Copying categories and channels...")
        await copy_channels(source_guild, target_guild, role_map)
        
        # Fix role positions
        if dm_channel:
            await dm_channel.send("🔄 Adjusting role positions...")
        print("Adjusting role positions...")
        await fix_role_positions(source_guild, target_guild, role_map)
        
        if dm_channel:
            await dm_channel.send("✅ Template copying completed successfully!")
        print("Template copying completed successfully!")
        
        # Try to send a completion message to the guild
        try:
            # Find a channel to send the completion message to
            for channel in target_guild.text_channels:
                try:
                    await channel.send(f"✅ Template from {source_guild.name} has been successfully applied to this server!")
                    break
                except:
                    continue
        except:
            pass
            
    except Exception as e:
        error_message = f"❌ An error occurred during the copying process: {str(e)}"
        if dm_channel:
            await dm_channel.send(error_message)
        print(error_message)
        raise

async def delete_existing_channels(guild):
    """Delete all existing channels and categories in the guild."""
    # Delete all channels first
    for channel in guild.channels:
        if not isinstance(channel, discord.CategoryChannel):
            try:
                await channel.delete()
                print(f"Deleted channel: {channel.name}")
            except Exception as e:
                print(f"Error deleting channel {channel.name}: {e}")
    
    # Then delete categories
    for category in guild.categories:
        try:
            await category.delete()
            print(f"Deleted category: {category.name}")
        except Exception as e:
            print(f"Error deleting category {category.name}: {e}")

async def copy_roles(source_guild, target_guild):
    """Copy roles from source guild to target guild and return a mapping of old role IDs to new role IDs."""
    role_map = {}
    
    # Store the bot's highest role position
    bot_member = target_guild.get_member(bot.user.id)
    bot_top_role_position = bot_member.top_role.position if bot_member else 0
    
    # Get existing roles in target guild
    existing_roles = {role.name: role for role in target_guild.roles}
    
    # Map the @everyone role
    role_map[source_guild.default_role.id] = target_guild.default_role.id
    
    # Delete roles that don't exist in the source guild (except @everyone and managed roles)
    source_role_names = [role.name for role in source_guild.roles]
    
    for role in list(target_guild.roles):  # Create a copy of the list to avoid modification during iteration
        if role.name not in source_role_names and not role.managed and role.name != "@everyone" and role.position < bot_top_role_position:
            try:
                await role.delete()
                print(f"Deleted role: {role.name}")
            except Exception as e:
                print(f"Error deleting role {role.name}: {e}")
    
    # Create or update roles
    for role in sorted(source_guild.roles, key=lambda r: r.position):
        # Skip default @everyone role
        if role.name == "@everyone":
            continue
            
        # Skip managed roles
        if role.managed:
            continue
            
        # Check if role already exists
        if role.name in existing_roles:
            existing_role = existing_roles[role.name]
            # Update existing role
            try:
                await existing_role.edit(
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                role_map[role.id] = existing_role.id
                print(f"Updated role: {existing_role.name}")
            except Exception as e:
                print(f"Error updating role {existing_role.name}: {e}")
        else:
            # Create new role
            try:
                new_role = await target_guild.create_role(
                    name=role.name,
                    permissions=role.permissions,
                    colour=role.colour,
                    hoist=role.hoist,
                    mentionable=role.mentionable
                )
                role_map[role.id] = new_role.id
                print(f"Created role: {new_role.name}")
            except Exception as e:
                print(f"Error creating role {role.name}: {e}")
    
    return role_map

async def fix_role_positions(source_guild, target_guild, role_map):
    """Fix role positions to match the source guild."""
    # Get roles from source guild sorted by position (highest to lowest)
    source_roles = sorted(
        [role for role in source_guild.roles if not role.managed and role.name != "@everyone"],
        key=lambda r: r.position,
        reverse=True
    )
    
    # Create a list of (role_id, position) tuples for roles that exist in the target guild
    role_positions = []
    position = len(source_roles)
    
    for role in source_roles:
        if role.id in role_map:
            target_role_id = role_map[role.id]
            target_role = target_guild.get_role(target_role_id)
            if target_role and not target_role.managed and target_role.name != "@everyone":
                role_positions.append((target_role_id, position))
                position -= 1
    
    # Sort by position (highest first)
    role_positions.sort(key=lambda x: x[1], reverse=True)
    
    # Get the bot's highest role position
    bot_member = target_guild.get_member(bot.user.id)
    bot_top_role_position = bot_member.top_role.position if bot_member else 0
    
    # Filter out roles that are higher than the bot's highest role
    valid_role_positions = []
    for role_id, position in role_positions:
        role = target_guild.get_role(role_id)
        if role and role.position < bot_top_role_position:
            valid_role_positions.append((role_id, position))
    
    # Update role positions if there are any valid roles
    if valid_role_positions:
        try:
            # Convert to the format expected by edit_role_positions
            positions = {target_guild.get_role(role_id): pos for role_id, pos in valid_role_positions}
            await target_guild.edit_role_positions(positions=positions)
            print("Updated role positions")
        except Exception as e:
            print(f"Error updating role positions: {e}")

async def copy_channels(source_guild, target_guild, role_map):
    """Copy categories and channels from source guild to target guild."""
    # First, create a mapping of category IDs
    category_map = {}
    
    # Create categories first
    for category in sorted(source_guild.categories, key=lambda c: c.position):
        # Create overwrites for the new category
        overwrites = await convert_overwrites(category.overwrites, role_map, target_guild)
        
        # Create the category
        try:
            new_category = await target_guild.create_category(
                name=category.name,
                overwrites=overwrites,
                position=category.position
            )
            category_map[category.id] = new_category.id
            print(f"Created category: {new_category.name}")
        except Exception as e:
            print(f"Error creating category {category.name}: {e}")
    
    # Create text channels
    for channel in sorted(source_guild.text_channels, key=lambda c: (c.category.position if c.category else -1, c.position)):
        # Get the category for this channel
        category_id = category_map.get(channel.category_id) if channel.category_id else None
        category = discord.utils.get(target_guild.categories, id=category_id) if category_id else None
        
        # Create overwrites for the new channel
        overwrites = await convert_overwrites(channel.overwrites, role_map, target_guild)
        
        # Create the channel
        try:
            new_channel = await target_guild.create_text_channel(
                name=channel.name,
                topic=channel.topic,
                position=channel.position,
                slowmode_delay=channel.slowmode_delay,
                nsfw=channel.nsfw,
                category=category,
                overwrites=overwrites
            )
            print(f"Created text channel: {new_channel.name}")
        except Exception as e:
            print(f"Error creating text channel {channel.name}: {e}")
    
    # Create voice channels
    for channel in sorted(source_guild.voice_channels, key=lambda c: (c.category.position if c.category else -1, c.position)):
        # Get the category for this channel
        category_id = category_map.get(channel.category_id) if channel.category_id else None
        category = discord.utils.get(target_guild.categories, id=category_id) if category_id else None
        
        # Create overwrites for the new channel
        overwrites = await convert_overwrites(channel.overwrites, role_map, target_guild)
        
        # Create the channel
        try:
            new_channel = await target_guild.create_voice_channel(
                name=channel.name,
                bitrate=min(channel.bitrate, target_guild.bitrate_limit),
                user_limit=channel.user_limit,
                position=channel.position,
                category=category,
                overwrites=overwrites
            )
            print(f"Created voice channel: {new_channel.name}")
        except Exception as e:
            print(f"Error creating voice channel {channel.name}: {e}")

async def convert_overwrites(overwrites, role_map, target_guild):
    """Convert permission overwrites using the role mapping."""
    new_overwrites = {}
    
    for target, overwrite in overwrites.items():
        if isinstance(target, discord.Role):
            # If it's the @everyone role
            if target.name == "@everyone":
                new_overwrites[target_guild.default_role] = overwrite
            # If we have this role in our mapping
            elif target.id in role_map:
                new_role = target_guild.get_role(role_map[target.id])
                if new_role:
                    new_overwrites[new_role] = overwrite
        elif isinstance(target, discord.Member):
            # Try to find the member in the target guild
            member = target_guild.get_member(target.id)
            if member:
                new_overwrites[member] = overwrite
    
    return new_overwrites

@bot.command(name="list_guilds")
@is_admin()
async def list_guilds(ctx):
    """List all guilds the bot is a member of."""
    guilds = bot.guilds
    if not guilds:
        await ctx.send("I'm not in any guilds.")
        return
    
    guild_list = "\n".join([f"**{guild.name}** (ID: {guild.id})" for guild in guilds])
    await ctx.send(f"I am in the following guilds:\n{guild_list}")

@bot.command(name="create_backup")
@is_admin()
async def create_backup(ctx):
    """Create a backup of the current server structure."""
    guild = ctx.guild
    
    await ctx.send(f"To restore this server's template elsewhere, use the command: `{PREFIX}copy_template {guild.id} <target_guild_id>`")
    await ctx.send(f"Server ID: `{guild.id}`")
    
    # Count server elements
    role_count = len([r for r in guild.roles if not r.managed and r.name != "@everyone"])
    category_count = len(guild.categories)
    text_channel_count = len(guild.text_channels)
    voice_channel_count = len(guild.voice_channels)
    
    await ctx.send(f"Server structure: {role_count} roles, {category_count} categories, {text_channel_count} text channels, {voice_channel_count} voice channels")

@bot.command(name="help_template")
async def help_template(ctx):
    """Show help information for template commands."""
    embed = discord.Embed(
        title="Template Bot Commands",
        description="Commands for managing server templates",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name=f"{PREFIX}list_guilds",
        value="List all servers the bot is in with their IDs",
        inline=False
    )
    
    embed.add_field(
        name=f"{PREFIX}create_backup",
        value="Get information about the current server for backup purposes",
        inline=False
    )
    
    embed.add_field(
        name=f"{PREFIX}copy_template <source_guild_id> [target_guild_id]",
        value="Copy a template from a source server to a target server. If target_guild_id is not provided, the current server will be used.",
        inline=False
    )
    
    embed.add_field(
        name="Note",
        value="⚠️ The copy_template command will delete all existing channels, categories, and non-managed roles in the target server!",
        inline=False
    )
    
    await ctx.send(embed=embed)

# Run the bot
bot.run(TOKEN)