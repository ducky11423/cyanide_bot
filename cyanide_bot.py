import http.client
import discord
import asyncio
import json
import os
import urllib.request
import random
import datetime
import time
import threading

data = {}
data["channels"] = []
data["comics"] = {}
data["apikey"] = ""
print("Creating discord client")
h = http.client.HTTPConnection('explosm.net')
client = discord.Client()
savefile = "candh.json"

def saveData():
    dataString = json.dumps(data, indent = 2)
    f = open(savefile, 'w')
    f.write(dataString)
    f.close()

async def checkTimer():
    lastChecked = 0
    time.sleep(1) #Make sure we dont check before client has joined?
    
    if lastChecked != datetime.datetime.now().hour:
        lastChecked = datetime.datetime.now().hour
        await checkNew()
    
    t = threading.Timer(60, checkTimer)
    t.start()
        

async def checkNew():
    h.request("GET", "/comics/latest")
    r = h.getresponse()
    if r.status == 200:
        d = r.read()
        previdloc = d.find(b"/comics/", d.find(b"nav-button_first")) + 8
        previd = int(d[previdloc:d.find(b"/", previdloc)])
        currId = previd + 1
        print(str(currId) not in data["comics"])
        if str(currId) not in data["comics"]:
            imgstart = d.find(b"src=\"//", d.find(b"main-comic")) + 7
            imgend = d.find(b"\"", imgstart)
            img = str(d[imgstart:imgend], 'utf-8')
            data["comics"][currId] = "http://" + img
            saveData()
            urllib.request.urlretrieve(data["comics"][currId], "images/" + str(currId) + ".png")
            
            for a in data["channels"]:
                channel = client.get_channel(a["channel"])
                await client.send_file(channel, "images/" + str(currId) + ".png", content="New comic!")
    h.close()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

    saveData()

    await checkTimer()

@client.event
async def on_message(message):
    user = message.author
    server = str(message.server)
    if(message.content == ".subscribe"):
        if({"server": message.server.id, "channel": message.channel.id} not in data["channels"]):
            data["channels"].append({"server": message.server.id, "channel": message.channel.id})
            await client.send_message(message.channel, "Channel *" + str(message.channel) + "* is now subscribed to new comics!")
            saveData()
    if(message.content == ".unsubscribe"):
        if({"server": message.server.id, "channel": message.channel.id} in data["channels"]):
            data["channels"].remove({"server": message.server.id, "channel": message.channel.id})
            await client.send_message(message.channel, "Channel *" + str(message.channel) + "* is no longer subscribed to new comics :(")
            saveData()
    
    if(message.content == ".check"):
        await checkNew()
    
    if(message.content.startswith(".comic")):
        parts = message.content.split(' ')
        if(len(parts) < 2):
            await client.send_message(message.channel, "You need to put an id in!")
        else:
            if(parts[1] == "latest"):
                await client.send_file(message.channel, "images/" + max(data["comics"], key=int) + ".png", content="Comic ID " + max(data["comics"], key=int))
            elif(parts[1] == "random"):
                await client.send_file(message.channel, "images/" + random.choice(list(data["comics"].keys())) + ".png")
            else:
                if(os.path.isfile("images/" + parts[1] + ".png")):
                    await client.send_file(message.channel, "images/" + parts[1] + ".png")
                else:
                    await client.send_message(message.channel, "Sorry, I don't have that comic.")
    

print("Looking for data file")
if(os.path.isfile(savefile)):
    print("Loading data")
    f = open(savefile, 'r')
    readData = f.read()
    data = json.loads(readData)
    f.close()
    saveData()
    print("Loaded data")

    print("Connecting")
    client.run(data["apikey"])
else:
    print("Could not find save data (candh.json). Creating now. Please fill in the apikey and then restart.")



'''
for i in range(0, 4926):
    currId = i
    if str(currId) not in data:
        print("Attempting to get comic " + str(i))
        h.request("GET", "/comics/" + str(i))
        r = h.getresponse()
        
        d = r.read()
        if b"Could not find comic" not in d:
            
            imgstart = d.find(b"src=\"//", d.find(b"main-comic")) + 7
            imgend = d.find(b"\"", imgstart)
            img = str(d[imgstart:imgend], 'utf-8')
            data[currId] = "http://" + img

            try:
                urllib.request.urlretrieve(data[currId], "images/" + str(currId) + ".png")
            except:
                print("Failed to download comic :(")

            print("Downloading comic " + str(i))
            
        else:
            data[currId] = "not_found"
            print("Comic " + str(i) + " not found :/")

        saveData()
'''