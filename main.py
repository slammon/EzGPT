import discord
from discord.ext import commands, tasks
import os
import random
import command
import json
import openai
import alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='~', intents=intents, case_insensitive=True)

openai.api_key = os.getenv("OPENAIKEY")

bot.remove_command('help')

@bot.event
async def on_ready():
  await bot.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name="~help"))
  print(f'connected as {bot.user}')

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /

@bot.command()
async def help(ctx, args=None):
  await ctx.message.delete()
  embed=discord.Embed(title=f"{ctx.message.author} >> Help", description="Command list for EzGPT", color=0x2bffb8)
  embed.add_field(name="~askdalle", value="ask Dall-E 2 by OpenAI a question", inline=False)
  embed.add_field(name="~askgpt", value="ask GPT3 by OpenAI a question", inline=False)
  embed.add_field(name="~faq", value="Frequently asked questions", inline=False)
  embed.add_field(name="~donate", value="donate to help keep EzGPT free", inline=False)
  embed.add_field(name="~info", value="random bot info", inline=False)
  await ctx.send(embed=embed)

@bot.command()
async def faq(ctx, args=None):
  await ctx.message.delete()
  embed=discord.Embed(title=f"{ctx.message.author} >> FAQ", description="Frequently asked questions", color=0x2bffb8)
  embed.add_field(name="What makes EzGPT better than somthing like MEE6?", value="The point of EzGPT is so that people can use the bot unlimited times per day unlike MEE6 where you can only ask it 8 times per day.", inline=False)
  embed.add_field(name="Will you ever require a subscription to use the bot?", value="No. We will never require a subscription to use this bot.", inline=False)
  embed.add_field(name="What do my donations go towards.", value="They go towards hosting the bot, hosting the database, and OpenAI credits.", inline=False)
  embed.add_field(name="What do I get by donating?", value="You get early access to new features early, access to vote on new features, and the ability to help keep EzGPT free to use ", inline=False)
  embed.add_field(name="Why is the bot so slow?", value="OpenAI has made their models closed source meaning we have to aks their servers for an answer to your question, the speed is mostly the time it takes for our servers to talk to theirs.", inline=False)
  embed.add_field(name="What do I do if i get an error code?", value="It depends on the code and if its a problem with us or a problem with OpenAI, thought the problem will most likely be resolved soon.", inline=False)
  await ctx.send(embed=embed)

@bot.command()
async def info(ctx, args=None):
  await ctx.message.delete()
  embed=discord.Embed(title=f"{ctx.message.author} >> Info", description="Info on the current installation of the bot", color=0x2bffb8)
  embed.add_field(name="version", value="4.0", inline=False)
  embed.add_field(name="developer", value="slammon#0032", inline=False)
  embed.add_field(name="support server", value="None", inline=False)
  embed.add_field(name="ways to add", value="In app auth only", inline=False)
  embed.add_field(name="License", value="Not done yet", inline=False)
  embed.add_field(name="eula", value="By using this bot you agree to abide by OpenAI's usage policies. https://platform.openai.com/docs/usage-policies/", inline=False)
  await ctx.send(embed=embed)

@bot.command()
async def donate(ctx, args=None):
  await ctx.message.delete()
  embed=discord.Embed(title=f"{ctx.message.author} >> donate", description="not done yet", color=0x2bffb8)
  await ctx.send(embed=embed)
  
# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /

def moderate(prompt):
  try :
    response = openai.Moderation.create(input = prompt)
  except openai.error.Timeout as e:
    return f"OpenAI API request timed out: {e}"
  except openai.error.APIError as e:
    return f"OpenAI API returned an API Error: {e}"
  except openai.error.APIConnectionError as e:
    return f"OpenAI API request failed to connect: {e}"
  except openai.error.InvalidRequestError as e:
    return f"OpenAI API request was invalid: {e}"
  except openai.error.AuthenticationError as e:
    return f"OpenAI API request was not authorized: {e}"
  except openai.error.PermissionError as e:
    return f"OpenAI API request was not permitted: {e}"
  except openai.error.RateLimitError as e:
    return f"OpenAI API request exceeded rate limit: {e}"
  else :
    return str(response["results"][0])

def censored(commanduser, question):
  tx = f"{commanduser} >> {question}"
  ans = f"```This input violates OpenAI's usage policy```"
  embed = discord.Embed(title=tx, description=ans, color=0x2bffb8)
  return embed
  
# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /
  
def GPTanswer(prompt):
  try:
    completions = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=1024, n=1, stop=None, temperature=0.5)
  except openai.error.Timeout as e:
    return f"OpenAI API request timed out: {e}"
  except openai.error.APIError as e:
    return f"OpenAI API returned an API Error: {e}"
  except openai.error.APIConnectionError as e:
    return f"OpenAI API request failed to connect: {e}"
  except openai.error.InvalidRequestError as e:
    return f"OpenAI API request was invalid: {e}"
  except openai.error.AuthenticationError as e:
    return f"OpenAI API request was not authorized: {e}"
  except openai.error.PermissionError as e:
    return f"OpenAI API request was not permitted: {e}"
  except openai.error.RateLimitError as e:
    return f"OpenAI API request exceeded rate limit: {e}"
  else :
    return completions.choices[0].text.strip()

def send_gpt_response(commanduser, question, answer):
  tx = f"{commanduser} >> {question}"
  ans = f"```{answer}```"
  embed = discord.Embed(title=tx, description=ans, color=0x2bffb8)
  return embed

def gpt_wait(commanduser, question):
  tx = f"{commanduser} >> {question}"
  ans = f"```ChatGPT is thinking ...```"
  embed = discord.Embed(title=tx, description=ans, color=0x2bffb8)
  return embed

@bot.command()
async def askgpt(ctx,*,GPTquery):
  await ctx.message.delete()
  gpt_think_msg = await ctx.send(embed=gpt_wait(ctx.message.author, GPTquery))
  data = json.loads(moderate(GPTquery))
  if data["flagged"] == True:
    await gpt_think_msg.edit(embed=censored(ctx.message.author, GPTquery))
  elif data["flagged"] == False:
    GPTresponse = GPTanswer(GPTquery)
    print("GPT : ", GPTquery, GPTresponse)
    await gpt_think_msg.edit(embed=send_gpt_response(ctx.message.author, GPTquery, GPTresponse))

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /

def egg_eval(prompt, author):
  if prompt == 95:
    return 'tacocat sus'
  elif prompt == 3799:
    return 'slammon unfunni'
  elif prompt == 1001:
    return f"imagine being named {author}"
  elif prompt == 6:
    return "mee6 moment"
  else:
    return 'Cuh?'

@bot.command()
async def eggster(ctx, eggnumb: int):
  egg = egg_eval(eggnumb, ctx.message.author)
  await ctx.send(egg)

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /

def DALLEanswer(prompt, resolution):
  try :
    response = openai.Image.create(prompt=prompt, n=1, size=resolution)
  except openai.error.Timeout as e:
    return f"OpenAI API request timed out: {e}"
  except openai.error.APIError as e:
    return f"OpenAI API returned an API Error: {e}"
  except openai.error.APIConnectionError as e:
    return f"OpenAI API request failed to connect: {e}"
  except openai.error.InvalidRequestError as e:
    return f"OpenAI API request was invalid: {e}"
  except openai.error.AuthenticationError as e:
    return f"OpenAI API request was not authorized: {e}"
  except openai.error.PermissionError as e:
    return f"OpenAI API request was not permitted: {e}"
  except openai.error.RateLimitError as e:
    return f"OpenAI API request exceeded rate limit: {e}"
  else :
    return response['data'][0]['url']

#def send_dalle_error(commanduser, question, error):
#  tx = f"{commanduser} >> {question}"
#  ans = f"```An error occured : {error}```"
#  embed = discord.Embed(title=tx, description=ans, color=0x2bffb8)
#  return embed

def send_dalle_response(commanduser, question, answer):
  tx = f"{commanduser} >> {question}"
  embed = discord.Embed(title=tx, color=0x2bffb8)
  embed.set_image(url=answer)
  return embed

def dalle_wait(commanduser, question):
  tx = f"{commanduser} >> {question}"
  ans = f"```Dall-E is thinking ...```"
  embed = discord.Embed(title=tx, description=ans, color=0x2bffb8)
  return embed

@bot.command()
async def askdalle(ctx,*,DALLEquery):
  await ctx.message.delete()
  dalle_think_msg = await ctx.send(embed=dalle_wait(ctx.message.author, DALLEquery))
  data = json.loads(moderate(DALLEquery))
  if data["flagged"] == True:
    await dalle_think_msg.edit(embed=censored(ctx.message.author, DALLEquery))
  elif data["flagged"] == False:
    DALLEresponse = DALLEanswer(DALLEquery, "512x512")
    print("DALLE : ", DALLEquery)
    await dalle_think_msg.edit(embed=send_dalle_response(ctx.message.author, DALLEquery, DALLEresponse))

# / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / / /

alive.awake()
bot.run(os.getenv('DISCORDTOKEN'))
