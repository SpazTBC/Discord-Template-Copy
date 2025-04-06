# Discord Server Template Bot

A Python-based Discord bot that allows you to copy and apply server templates (channels, categories, permissions, roles, etc.) from one server to another.

## Features

- Copy roles with their permissions, colors, and other properties
- Copy categories with their permissions
- Copy text channels with their topics, slowmode settings, and permissions
- Copy voice channels with their bitrates, user limits, and permissions
- Maintain the hierarchy of roles and channels
- Delete existing channels, categories, and roles in the target server
- Proper permission handling for all elements

## Requirements

- Python 3.8 or higher
- discord.py 2.0.0 or higher
- python-dotenv 0.20.0 or higher

## Installation

### 1. Install Python

#### Windows
1. Download the latest Python version from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. Make sure to check "Add Python to PATH" during installation
4. Verify installation by opening Command Prompt and typing `python --version`

#### macOS
1. Install Homebrew if not already installed:
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Python:
   ```
   brew install python
   ```
3. Verify installation: `python3 --version`

#### Linux (Ubuntu/Debian)
```
sudo apt update
sudo apt install python3 python3-pip
```

### 2. Clone or Download the Repository

Download the bot files to your local machine.

### 3. Install Dependencies

Navigate to the bot directory in your terminal/command prompt and run:

```
pip install -r requirements.txt
```

Or install dependencies manually:

```
pip install discord.py python-dotenv
```

## Configuration

1. Create a `.env` file in the bot directory with the following content:

```
# Bot Configuration
TOKEN=your_bot_token_here
PREFIX=$

# Roles (comma-separated role IDs)
ADMIN_ROLES=role_id1,role_id2
MOD_ROLES=role_id1,role_id2
VIP_ROLES=role_id1,role_id2,role_id3
```

2. Replace `your_bot_token_here` with your Discord bot token
3. Replace the role IDs with the appropriate role IDs from your server

### Getting a Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" tab and click "Add Bot"
4. Under the "TOKEN" section, click "Copy" to copy your bot token
5. Paste this token in your `.env` file

### Inviting the Bot to Your Server

1. In the Discord Developer Portal, go to the "OAuth2" tab
2. In the "URL Generator" section, select the "bot" scope
3. Select the "Administrator" permission
4. Copy the generated URL and open it in your browser
5. Select the server you want to add the bot to and authorize it

## Usage

### Commands

- `$list_guilds` - List all servers the bot is in with their IDs
- `$create_backup` - Get information about the current server for backup purposes
- `$copy_template <source_guild_id> [target_guild_id]` - Copy a template from a source server to a target server
- `$help_template` - Show help information for template commands

### Copying a Server Template

1. Make sure the bot is in both the source server (the one you want to copy from) and the target server (the one you want to copy to)
2. Use `$list_guilds` to get the IDs of both servers
3. Use `$copy_template <source_guild_id> <target_guild_id>` to start the copying process
4. Confirm the operation by reacting with ✅
5. The bot will send status updates to your DMs (make sure your DMs are open)

### Important Notes

- The bot requires Administrator permissions in both servers
- The copying process will delete all existing channels, categories, and non-managed roles in the target server
- The bot can only modify roles that are lower than its highest role
- Managed roles (like bot integration roles) will not be copied or deleted

## Troubleshooting

### Bot Not Responding to Commands
- Make sure the bot is online
- Check if the bot has the necessary permissions
- Verify that you're using the correct prefix

### Permission Errors
- Ensure the bot has Administrator permissions
- Make sure the bot's role is high enough in the role hierarchy

### DM Status Updates Not Working
- Check if your DMs are open for the server
- The bot will still continue the process even if it can't send DM updates

## Customization

You can modify the bot.py file to customize the bot's behavior:

- Change the command prefix by modifying the PREFIX variable in the .env file
- Add more commands or functionality by extending the bot.py file
- Modify the role copying behavior to include or exclude specific roles

## License

This project is open-source and available for anyone to use and modify.

## Credits

Shawn Blackwood

Created using discord.py library.

## Security Considerations

- Keep your bot token private and never share it publicly
- Regularly rotate your bot token if you suspect it has been compromised
- Be careful when giving the bot Administrator permissions, as it grants extensive control over your server
- Only allow trusted users to use the template copying commands

## Advanced Configuration

### Customizing Role Permissions

If you want to customize which roles can use admin commands, modify the ADMIN_ROLES, MOD_ROLES, and VIP_ROLES in your .env file:

```
ADMIN_ROLES=937497921744678932
MOD_ROLES=937497921744678932
VIP_ROLES=1009638963763482724,1009640951762927696,1009641026861932585
```

### Changing the Command Prefix

To change the command prefix from $ to something else, modify the PREFIX variable in your .env file:

```
PREFIX=!
```

### Adding More Commands

You can extend the bot's functionality by adding more commands to the bot.py file. Follow the existing command structure:

```python
@bot.command(name="command_name")
@is_admin()  # If you want to restrict the command to admins
async def command_function(ctx, arg1, arg2):
    # Command logic here
    await ctx.send("Response")
```

## Deployment Options

### Running the Bot Locally

For personal or testing use, running the bot on your local machine is sufficient:

```
python bot.py
```

Keep the terminal/command prompt open to keep the bot running.

### Running the Bot 24/7

For continuous operation, consider these options:

#### Using a VPS (Virtual Private Server)
1. Rent a VPS from providers like DigitalOcean, AWS, or Linode
2. Install Python and dependencies
3. Use a process manager like PM2 to keep the bot running:
   ```
   npm install -g pm2
   pm2 start bot.py --name "discord-template-bot" --interpreter python3
   ```

## Contributing

Contributions to improve the bot are welcome! Here's how you can contribute:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request

## Future Enhancements

Potential features for future versions:

- Selective copying (only specific channels or roles)
- Template saving and loading from files
- Web interface for managing templates
- Support for copying emojis and stickers
- Support for copying server settings (verification level, default notifications, etc.)
- Progress bar for the copying process
- Scheduled backups of server templates

## Support

If you encounter any issues or have questions about using the bot, you can:

1. Check the troubleshooting section in this README
2. Open an issue on the GitHub repository
3. Contact the developer directly

## Changelog

### Version 1.0.0
- Initial release
- Basic template copying functionality
- Role, channel, and category copying
- Permission handling
- Status updates via DMs

## FAQ

### Q: Can the bot copy messages?
A: No, the Discord API does not allow bots to copy messages between servers.

### Q: Will the bot copy server boosts and premium features?
A: No, server boosts and premium features are tied to the specific server and cannot be transferred.

### Q: Is there a limit to how many channels/roles the bot can copy?
A: The bot is limited by Discord's rate limits. For very large servers, the copying process might take longer or potentially hit rate limits.

### Q: Can I use this bot to backup my server?
A: Yes, you can use this bot to create a structural backup of your server. However, it won't back up messages or member data.

### Q: Will the bot copy webhooks and integrations?
A: No, webhooks and integrations are not copied as they require separate authentication.

---

Thank you for using the Discord Server Template Bot! We hope it helps you manage your Discord servers more efficiently.