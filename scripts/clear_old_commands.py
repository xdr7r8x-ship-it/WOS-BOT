#!/usr/bin/env python3
import os
import asyncio
import discord


OLD_COMMANDS = [
    "setup",
    "player_list",
    "player_remove",
    "redeem",
    "status",
    "retry",
    "cleanup",
    "health",
    "system",
    "diagnostics",
    "backup_create",
    "backup_list",
    "rollback",
    "updates_check",
    "updates_plan",
    "updates_apply",
    "watchdog_status",
    "security_scan",
    "integrity_check",
    "predict_status",
    "autopilot_status",
]


async def clear_old_commands():
    confirm = os.getenv("CONFIRM_CLEAR_COMMANDS", "false").lower() == "true"
    
    if not confirm:
        print("ERROR: CONFIRM_CLEAR_COMMANDS environment variable must be set to 'true'")
        print("Usage: CONFIRM_CLEAR_COMMANDS=true python scripts/clear_old_commands.py")
        return
    
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("ERROR: DISCORD_BOT_TOKEN environment variable not set")
        return
    
    intents = discord.Intents.default()
    intents.guilds = True
    
    client = discord.Client(intents=intents)
    
    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")
        
        for guild in client.guilds:
            print(f"\nProcessing guild: {guild.name}")
            
            try:
                commands = await guild.application_commands()
                print(f"Found {len(commands)} application commands")
                
                for cmd in commands:
                    if cmd.name in OLD_COMMANDS:
                        print(f"  Deleting: /{cmd.name}")
                        await cmd.delete()
                        print(f"  Deleted: /{cmd.name}")
                    elif cmd.name != "wos":
                        print(f"  Deleting: /{cmd.name} (not in allowed list)")
                        await cmd.delete()
                        print(f"  Deleted: /{cmd.name}")
                    else:
                        print(f"  Keeping: /{cmd.name}")
            except Exception as e:
                print(f"  Error: {e}")
        
        await client.close()
    
    await client.start(token)


if __name__ == "__main__":
    asyncio.run(clear_old_commands())
