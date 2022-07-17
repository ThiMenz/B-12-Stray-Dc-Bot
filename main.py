#=========================================================================================================
#Copyright (c) 2022 - Möhrchen [Thilo] --> Meister Möhre #1623 (#7979)
#
#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and 
#associated documentation files (the "Software"), to deal in the Software without restriction, including
#without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
#copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the 
#following conditions:
#
#The above copyright notice and this permission notice shall be included in all copies or substantial 
#portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
#LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO 
#EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
#IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
#THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#=========================================================================================================

import discord
from discord.ext import tasks, commands
from webserver import keep_alive
import os
    
#=========Important Variables=========

prefix = "m!"
client = commands.Bot(command_prefix="m!")

activeGuildId = 993385631982026763 

theGuild = None
categoryOfVoiceChannels = None
memberRole = None

nicePeopleArray = ["Meister Möhre#1623", "SurprisedPika#7953", "OrangeChef#4553"]
godDamnNicePeopleArray = ["Meister Möhre#1623", "SurprisedPika#7953", "OrangeChef#4553"]

listOfBotStatus = ['Stray']
activeBotStatus = 0


#=========Discord Client=========



class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        global theGuild 
        try:
          theGuild = await client.fetch_guild(activeGuildId)
        except: 
          theGuild = client.guilds[0]
        print(theGuild)
        self.Change_Status.start()
        
    @tasks.loop(seconds=305.0)
    async def Change_Status(self):
        global activeBotStatus
        await self.change_presence(activity=discord.Game(name=listOfBotStatus[activeBotStatus]))
        if activeBotStatus < len(listOfBotStatus) - 1: activeBotStatus += 1
        else: activeBotStatus = 0
        
        
    async def on_message(self, message):
        if message.channel.type == discord.ChannelType.private: return
        
        messageStr = message.content
        prefix = "m!"
        
        if len(messageStr) < 2: return
       
        if messageStr[0] != 'm' or messageStr[1] != '!' :
            if messageStr[0] == 'M' and messageStr[1] == '!':
                prefix = 'M!'
            else:
                return 
        
        
        if str(message.author) not in nicePeopleArray and not "bot-commands" in str(message.channel.name): return


        if str(prefix + 'reactiontype') in messageStr.lower():
            roleFile = open("Roles.txt", "r", encoding='utf-8')
            roleFileRL = roleFile.readlines()
            roleFile.close()
            
            messageArgs = messageStr[15:].split(" ")
            messageID = messageArgs[0].replace("https://discord.com/channels/", "").split('/')[2]
            
            if messageArgs[1] != "True" and messageArgs[1] != "False": return await message.channel.send("You have to enter a valid bool value: True or False")
            
            roleFileW = open("Roles.txt", "w", encoding='utf-8')
            
            for ln in roleFileRL: 
                if str(messageID) in ln:
                    currentContentParts = ln.split("~")
                    roleFileW.write(currentContentParts[0] + "~" + messageArgs[1] + "~" + currentContentParts[2] + "~" + currentContentParts[3])
                else: roleFileW.write(ln)
            
            return await message.channel.send("Successfully changed the reactiontype from: " + messageArgs[0])
            
        if str(prefix + 'reaction') in messageStr.lower():
            roleFile = open("Roles.txt", "r", encoding='utf-8')
            roleFileRL = roleFile.readlines()
            roleFile.close()
            
            messageArgs = messageStr[11:].split(" ")
            
            splittedFirstArgLink = messageArgs[0].replace("https://discord.com/channels/", "").split('/')
            
            tchannel = client.get_channel(int(splittedFirstArgLink[1]))
            msg = await tchannel.fetch_message(int(splittedFirstArgLink[2]))
            await msg.add_reaction(messageArgs[1])
            onlyonerole = False
            if len(messageArgs) > 3: 
                if messageArgs[3] == "True": onlyonerole = True
            roleFileW = open("Roles.txt", "w", encoding='utf-8')
            for ln in roleFileRL: roleFileW.write(ln)
            msgId = str(msg.id)
            strBool = str(onlyonerole)
            emoji = str(messageArgs[1])
            theRole = discord.utils.get(message.author.guild.roles, name=str(messageArgs[2]))
            roleFileW.write(msgId + "~" + strBool + "~" + emoji + "~" + str(theRole.id) + " \n")
            await message.channel.send("Successfully added the reaction to: " + str(msg.jump_url))

    
    #===Reaction Add===


          
    async def on_raw_reaction_add(self, payload):
        channel = client.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = payload.member
        roleTxt = open("Roles.txt", "r", encoding='utf-8')
        roleTxtRl = roleTxt.readlines()
        roleTxt.close()
        for ln in roleTxtRl:
            if "~" in ln:
                if int(ln.split('~')[0]) == int(payload.message_id):  
                    if payload.emoji.name == ln.split('~')[2]: 
                        tempRole = discord.utils.get(user.guild.roles, id=int(ln.split('~')[3])) 
                        if user.bot: return
                        if ln.split('~')[1] == "True":
                            for ln2 in roleTxtRl:
                                if "~" in ln2:
                                    if int(ln2.split('~')[0]) == int(payload.message_id):
                                        t2Role = discord.utils.get(user.guild.roles, id=int(ln2.split('~')[3])) 
                                        _emoji_ = ln2.split('~')[2]
                                        if str(_emoji_) != str(payload.emoji): await message.remove_reaction(_emoji_, user)
                                        #await user.remove_roles(t2Role)
                        await user.add_roles(tempRole)
                        


      
    #===Reaction Remove===  
      
    async def on_raw_reaction_remove(self, payload): 
        guild = client.get_guild(payload.guild_id)
        user = await(guild.fetch_member(payload.user_id))
        if user.bot: return
        roleTxt = open("Roles.txt", "r", encoding='utf-8')
        roleTxtRl = roleTxt.readlines()
        roleTxt.close()
        for ln in roleTxtRl:
            if "~" in ln:
                if int(ln.split('~')[0]) == int(payload.message_id):  
                    if str(payload.emoji) == ln.split('~')[2]:
                        tempRole = discord.utils.get(user.guild.roles, id=int(ln.split('~')[3])) 
                        if user.bot: return
                        await user.remove_roles(tempRole)
        

#Start the Discord Bot -->

client = MyClient()
keep_alive()
TOKEN = os.environ.get("DISCORD_BOT_SECRET")
client.run(TOKEN)

