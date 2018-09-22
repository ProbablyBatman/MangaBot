#!/usr/bin/env python3
import praw
import time
import asyncio
import discord
from discord.ext import commands
import pprint

#Custom value file
import values

reddit = praw.Reddit(client_id=values.CLIENT_ID,
                     client_secret=values.CLIENT_SECRET,
                     user_agent='manga grabber',
                     username=values.USERNAME,
                     password=values.PASSWORD)

MANGA_LIST_PATH = '/home/batman/manga_bot/manga_list'
mangaList = []

client = discord.Client()

bot = commands.Bot(command_prefix='$')

@bot.event
async def on_ready():
  print('Logged in as')
  print(bot.user.name)
  print(bot.user.id)
  print('-----')
  read_in_manga_list()
  bot.loop.create_task(grabber())

@bot.command(pass_context=True)
async def add(ctx, name):
  print("Added " + name)
  if (name.lower() in mangaList):
    await ctx.send(name + " exists in manga list already")
  elif (name.isspace() or "\n" in name):
  #elif (is_stupid(name)):
    await ctx.send("STOP SENDING GARBAGE. BAKA.")
  else:
    await ctx.send("Added " + name + " to manga list")
    add_to_manga_list(name)

@bot.command(pass_context=True)
async def remove(ctx, name):
  print("Removed " + name)
  if (name in mangaList):
    await ctx.send("Removed " + name + " from manga list")
    remove_from_manga_list(name)
  else:
    await ctx.send(name + " does not exist in the manga list")

@bot.command(pass_context=True)
async def exists(ctx, name):
  print("Checking if manga is in list " + name)
  for manga in mangaList:
    if (name.lower() == manga):
      await ctx.send(name + " already exists in the manga list")
      print(name + " exists in the manga list")
      return
  await ctx.send(name + " does not exist in the manga list")
  print(name + " does not exist in the manga list")

@bot.command(pass_context=True)
async def listmanga(ctx):
  message = ""
  for item in mangaList:
    if (len(message) >= 1953):
      await ctx.send(message)
      message = ""
    message += item
    message += "\n"
  await ctx.send(message)

#remove help by default
bot.remove_command('help')

@bot.command(pass_context=True)
async def help(ctx):
  embed = discord.Embed(title='Chips Ahoy Chunky', description='I\'m a fucking cookie', color=0x00114f)
  embed.add_field(name="Author", value="bananamanq")
  embed.add_field(name="$add \"name\"", value="Adds a manga to the list. Be sure to place in quotes with proper punctuation. Strip anything from the end that isn\'t necessary.")
  embed.add_field(name="$exists \"name\"", value="Checks if manga exists in list or not and lets you know.")
  embed.add_field(name="$help", value="Sends this message.")
  embed.add_field(name="$listmanga", value="Sends the current list of manga.")
  embed.add_field(name="$remove \"name\"", value="Removes a manga from the list.  Doesn't remove anything not in the list obviously.")
  await ctx.send(embed=embed)

def read_in_manga_list():
  file = open(MANGA_LIST_PATH,'r')
  global mangaList
  mangaList  = file.readlines()
  mangaList = [item.lower().rstrip('\n') for item in mangaList]
  mangaList = [check_valid_manga_name(item) for item in mangaList]
  mangaList.sort()
  file.close()
  print(mangaList)

def add_to_manga_list(item):
  file = open(MANGA_LIST_PATH, 'a')
  newItem = check_valid_manga_name(item)
  file.write(newItem + '\n')
  file.close()
  read_in_manga_list()

def remove_from_manga_list(item):
  file = open(MANGA_LIST_PATH, 'w')
  newItem = check_valid_manga_name(item)
  for manga in mangaList:
    if (newItem.lower() != manga):
      file.write(manga + '\n')
  file.close()
  read_in_manga_list()

async def grabber():
  subreddit = reddit.subreddit('manga')
  while True:
    for submission in subreddit.new(limit=25):
      #Uncomment to debug objects
      #pprint.pprint(vars(submission))
      print(submission.title.lower())
      print(submission.url)
      #check_valid_manga_name(submission.title.lower())
      for item in mangaList:
        if (item in check_valid_manga_name(submission.title.lower()) and has_numbers(submission.title.lower()) and
               'disc' in submission.title.lower() and not submission.hidden):
        #if (item in submission.title.lower() and not submission.hidden and '[disc]' in submission.title.lower()):
          #print(submission.title + " is valid")
          await bot.get_channel(477970394368704515).send('{}: {}'.format(submission.title, submission.url))
          submission.hide()
    await asyncio.sleep(60)

def check_valid_manga_name(post):
  newName = ""
  for c in post:
    #check if alphanumeric or space
    if (c.isalnum() or ord(c) == 32):
      newName += c
  return newName

def is_valid_manga_name(post):
  for c in post:
    if (not (c.isalnum() or ord(c) == 32)):
      return False
  return True

def has_numbers(post):
  return any(c.isdigit() for c in post)

def is_stupid(post):
  if (post.isspace()):
    return True
  elif ("\n" in post):
    return True
  elif (not is_valid_manga_name(post)):
    return True
  else:
    return False

def main():
  print(reddit.user.me())
  bot.run(values.BOT_TOKEN)

if __name__ == "__main__":
    main()
