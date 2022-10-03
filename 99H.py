from datetime import datetime
import discord
from discord import FFmpegPCMAudio
import getHeader
from discord.ext import tasks
import getSkinOffers
from discord.embeds import Embed
import db
import os
from embedReplies import *
from dotenv import load_dotenv
from cryptography.fernet import Fernet
from gtts import gTTS
import langid
load_dotenv()
KEY = (os.getenv('KEY')).encode('utf-8')
TOKEN = (os.getenv('TOKEN'))
client = discord.Client()




@tasks.loop(minutes=1.0)
async def sendtoday():
	time = datetime.today()
	if time.hour == 7 and time.minute == 10:
		data = db.getallUser()
		for i in data:
			dm = await client.fetch_user(i['user_id'])
			username = i['username']
			password = (Fernet(KEY).decrypt(i["password"])).decode('utf-8')
			region = 'ap'
			try:
				headers,user_id = await getHeader.run(username,password,region)
				if headers==403:
					embed = smallEmbed("ไอดี หรือ รหัสผ่าน ผิด!")
					await dm.send(embed=embed)
					return
				elif headers==429:
					embed = smallEmbed("เกิน limited",f'{username} รออีก 10 นาที ค่อยลองใหม่นะ')
					await dm.send(embed=embed)
					return
				elif headers==405:
					embed = smallEmbed("2FA Detected!",f'{username} ไปปิด 2FA ก่อนแล้วค่อยมาลองใหม่นะ')
					await dm.send(embed=embed)
					return
				else:
					res = await getSkinOffers.getStore(headers,user_id,region)
					embed = smallEmbed("ของ !!!",f'{username}')
					await dm.send(embed=embed)
					for item in res[0]:
						embed = discord.Embed(title=item[0], description=f"ราคา : {item[1]}", color=discord.Color.red())
						embed.set_thumbnail(url=item[2])
						await dm.send(embed=embed)
					embed=smallEmbed("หมดเวลาใน",res[1])
					await dm.send(embed=embed)
			except:
				embed=exceptionEmbed()
				await dm.send(embed=embed)

@client.event
async def on_ready():
	""" automatic execute whwn you loged in to the system"""
	print("We have logged in a {0.user}".format(client))
	sendtoday.start()
@client.event
async def on_message(ctx):
	if ctx.content.lower().startswith("+say"):
		tt = discord.utils.get(client.voice_clients,guild=ctx.guild)
		print(tt)
		try:
			data = ctx.content.split()
			data = "".join(data[1:len(data)])
			lang = langid.classify(data)[0]
			myobj=gTTS(text=data,lang=lang,slow=True)
			myobj.save("tt.mp3")
			if tt is None:
				data = ctx.content.split()
				channel = ctx.author.voice.channel
				voice = await channel.connect()
				source = FFmpegPCMAudio('tt.mp3')
				player = voice.play(source)
			else:
				source = FFmpegPCMAudio('tt.mp3')
				player = tt.play(source)

		except:
			print("error")
	"""Recieve msg to Discord and send Message"""
	if ctx.author == client.user:
		"""return nothing if msg is send by itself"""
		return
	if ctx.content.lower().startswith("+valo"):
		"""Send Hello to the channel if anybody say hello"""
		try:
			data = ctx.content.split()
			if(len(data) == 3):
				username = data[1]
				password = data[2]
				region = 'ap'
				try:
					headers,user_id = await getHeader.run(username,password,region)
					if headers==403:
						embed = smallEmbed("ไอดี หรือ รหัสผ่าน ผิด!")
						await ctx.channel.send(embed=embed)
						return
					elif headers==429:
						embed = smallEmbed("เกิน limited",f'{username} รออีก 10 นาที ค่อยลองใหม่นะ')
						await ctx.channel.send(embed=embed)
						return
					elif headers==405:
						embed = smallEmbed("2FA Detected!",f'{username} ไปปิด 2FA ก่อนแล้วค่อยมาลองใหม่นะ')
						await ctx.channel.send(embed=embed)
						return
					else:
						res = await getSkinOffers.getStore(headers,user_id,region)
						embed = smallEmbed("ของ !!!",f'{username}')
						await ctx.channel.send(embed=embed)
						for item in res[0]:
							embed = discord.Embed(title=item[0], description=f"ราคา : {item[1]}", color=discord.Color.red())
							embed.set_thumbnail(url=item[2])
							await ctx.channel.send(embed=embed)
						embed=smallEmbed("หมดเวลาใน",res[1])
						await ctx.channel.send(embed=embed)
				except:
					embed=exceptionEmbed()
					await ctx.channel.send(embed=embed)
			if(len(data) == 2):
				username = data[1]
				region = 'ap'
				if(db.checkUser(username,region)):
					user=db.getUser(username,region)
					password=user['password']
					try:
						headers,user_id = await getHeader.run(username,password,region)
						if headers==403:
							embed = smallEmbed("Update Password!","+updatepass <username> <updated password>")
							await ctx.channel.send(embed=embed)
							return
						elif headers==429:
							embed = smallEmbed("เกิน limited",f'{username} รออีก 10 นาที ค่อยลองใหม่นะ')
							await ctx.channel.send(embed=embed)
							return
						elif headers==405:
							embed = smallEmbed("2FA Detected!",f'{username} ไปปิด 2FA ก่อนแล้วค่อยมาลองใหม่นะ')
							await ctx.channel.send(embed=embed)
							return
						else:
							res = await getSkinOffers.getStore(headers,user_id,region)
							res = await getSkinOffers.getStore(headers,user_id,region)
							embed = smallEmbed("ของ !!!",f'{username}')
							for item in res[0]:
								embed = discord.Embed(title=item[0], description=f"ราคา : {item[1]}", color=discord.Color.red())
								embed.set_thumbnail(url=item[2])
								await ctx.channel.send(embed=embed)
							embed=smallEmbed("หมดเวลาใน",res[1])
							await ctx.channel.send(embed=embed)
					except:
						embed=exceptionEmbed()
						await ctx.channel.send(embed=embed)
				else:
					embed=smallEmbed("Add user!","+adduser <username> <password>")
					await ctx.author.send(embed=embed)
					if not isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != client.user:
						embed=smallEmbed("Add user","Please add your user in private message!")
						await ctx.channel.send(embed=embed)
		except:
			embed = smallEmbed("เขียนแบบนี้!","+valo <username> <password>")
			await ctx.channel.send(embed=embed)
	if ctx.content.lower().startswith("+adduser"):
		try:
			data = ctx.content.split()
			username = data[1]
			password = data[2]
			user_id = ctx.author.id
			region = 'ap'
			try:
				if(db.checkUser(username,region)):
					embed=smallEmbed("User already exists","Please check +help for available commands")
					await ctx.channel.send(embed=embed)
				else:
					_,res = await getHeader.run(username,password,region)
					if(res==403):
						embed=smallEmbed("Incorrect credentials!","Your login credentials don't match an account in our system")
						await ctx.channel.send(embed=embed)
						return
					else:
						res=db.addUserDb(username,password,region,user_id)
						if res:
							embed=thumbnailEmbed("User Added!","User has been successfully added","https://emoji.gg/assets/emoji/confetti.gif")
							await ctx.channel.send(embed=embed)
			except:
				embed=exceptionEmbed()
				await ctx.channel.send(embed=embed)		
		except:
			print("error")

if __name__ == "__main__":
	# my_secret = os.environ['token']  # enter your token here
	client.run(TOKEN)
		