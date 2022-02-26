import discord
from discord.ext import commands, tasks
from console import Console
import news
import json
from datetime import datetime
import sql

console = Console(True)

with open("config.json", "r") as f:
    config = json.load(f)

class get_data_class(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.get_data.start()

    @tasks.loop(minutes=1)
    async def get_data(self):
        data = await news.get_data()
        if data:
            posted_in = 0
            for guild in self.client.guilds:
                news_channel = sql.get_id(guild.id)
                if news_channel:
                    embed = discord.Embed(title=data["title"], description=data["content"],
                                            color=(0xeb144c if data["is_breaking"] else 0xffffff))
                    if data["image"]: embed.set_image(url=data["image"])
                    if data["is_breaking"]: embed.set_author(name="BREAKING")
                    embed.set_footer(text="🔴 Live News")

                    locator = data["locator"]
                    embed.url = f"https://www.bbc.com/news/live/world-europe-60517447?pinned_post_locator={locator}"
                    embed.timestamp = datetime.now()
                    
                    try:
                        await self.client.get_channel(news_channel).send(embed=embed)
                        posted_in += 1
                    
                    except:
                        discord.error(f"Could not post news in {guild.name}({guild.id}).")
                        try: guild.owner.send(f"Could not post news in your server {guild.name}. Make sure the bot can send messages and embeds in that channel. If the issue persists please contact `Flonc#0001`")
                        except: pass

            console.log(f"Posted data in {posted_in}/{len(self.client.guilds)} servers.")

    @get_data.before_loop
    async def before_data(self):
        await self.client.wait_until_ready()

def setup(client):
    client.add_cog(get_data_class(client))