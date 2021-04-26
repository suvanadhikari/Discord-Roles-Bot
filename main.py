import discord
import math
import random
import os
from keep_alive import keep_alive

BOT_ID = os.environ.get("ROLE_BOT_ID")
client = discord.Client()

help_txt = "Commands list:\n\n!help: Displays this menu\n!roles: Used to assign roles to a group. Format: !roles @person1 @person2 / role1:[number] role2:[number]"

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
    await message.channel.send(help_txt)

cmds = [roles_cmd, help_cmd]

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