import discord
from discord.ext import commands
import asyncio


from PIL import Image
import requests
from io import BytesIO
from PIL import _imaging


def grab_colour(url):
    if url != None:
        response = requests.get(url)
        im = Image.open(BytesIO(response.content))
        im = im.convert("RGB")
        r, g, b = im.getpixel((im.width // 2, im.height // 2))
        return discord.Colour.from_rgb(r=r, g=g, b=b)
    else:
        return discord.Colour.from_rgb(r=19, g=19, b=19)