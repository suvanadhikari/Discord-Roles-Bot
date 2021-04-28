import discord
import math
import random
import os
from keep_alive import keep_alive

BOT_ID = os.environ.get("ROLE_BOT_ID")
client = discord.Client()

desc_file = open("commandDescriptions.txt", "r")
format_file = open("commandFormats.txt", "r")

lines = desc_file.readlines()
cmd_dicts = [{"name":line.split(":")[0], "desc":line.split(":")[1].strip()} for line in lines]
cmd_formats = [line.strip() for line in format_file.readlines()]

def get_cmd_info(cmd):
    if not cmd.startswith("!"):
        cmd = "!" + cmd
    for index, cmd_dict in enumerate(cmd_dicts):
        if cmd_dict["name"] == cmd:
            return {"name":cmd_dict["name"], "desc":cmd_dict["desc"], "format":cmd_formats[index]}
    return None

async def cmdhelp_cmd(msg):
    message = msg.content
    if (not message.startswith("!cmdhelp ")):
        return
    cmd = message[9:].strip()
    cmd_info = get_cmd_info(cmd)
    if (cmd_info == None):
        await msg.channel.send("Given command does not exist.")
    else:
        embed = discord.Embed()
        embed.add_field(name=f"**Command Help for {cmd_info['name']}**", value=f"{cmd_info['desc']}\nFormat: {cmd_info['format']}")
        await msg.channel.send(embed=embed)

def get_roles(msg):
    message = msg.content
    segments = message[7:].split("/")[1].split(" ")
    # Message format: !roles @person @person2 @person3 / Jester:1 3rdImpostor:1
    segments = [i for i in segments if len(i) > 0]
    index_dict = {}

    # Each segment should be: <role>:<number>
    open_list = [i for i in range(len(msg.mentions))]
    if len(open_list) > len(segments):
        return None
    for role in segments:
        role_parts = role.split(":")
        index_dict[role_parts[0]] = []
        for _ in range(int(role_parts[1])):
            open_index = math.floor(random.random() * len(open_list)) # The index to remove from open_list
            list_index = open_list.pop(open_index) # Getting the mentions index and popping from open_list
            index_dict[role_parts[0]].append(list_index)
    return index_dict

async def roles_cmd(message):
    if not message.content.startswith("!roles"):
        return
    roles_dict = get_roles(message)
    if roles_dict is None:
        await message.channel.send("Cannot have more roles than people.")
        return
    for index, mention in enumerate(message.mentions):
        channel = mention.dm_channel
        if channel is None:
            channel = await mention.create_dm()
        assigned = False
        for role in roles_dict:
            for role_index in roles_dict[role]:
                if (role_index == index):
                    assigned = True
                    await channel.send("Your role is: " + role)
        if not assigned:
            await channel.send("You have not received a special role.")
    await message.channel.send("DMs sent successfully.")

async def help_cmd(message):
    if not message.content.startswith("!help"):
        return
    embed = discord.Embed()
    field_value = ""
    for cmd_dict in cmd_dicts:
        field_value += f"**{cmd_dict['name']}:** {cmd_dict['desc']}\n"
    embed.add_field(name="**Command List**", value=field_value[:-1])
    await message.channel.send(embed=embed)

cmds = [roles_cmd, help_cmd, cmdhelp_cmd]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    try:
        if message.author == client.user:
            return
        for cmd in cmds:
            await cmd(message)
        
    except Exception as e:
        print(e)
        await message.channel.send("An error occurred. Check to make sure your formatting is correct.")

keep_alive()
client.run(BOT_ID)