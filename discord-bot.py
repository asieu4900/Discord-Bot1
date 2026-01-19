import aiohttp
from aiohttp import web

async def health_check(request):
  return web.Response(text="OK", status=200)

async def start_web_server():
  app = web.Application()
  app.router.add_get('/health', health_check) # Health Check API 추가
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, '0.0.0.0', 8000)
  await site.start()

import discord
from datetime import datetime, timedelta
import pytz
import asyncio
import os

async def start_web_server():
  app = web.Application()
  runner = web.AppRunner(app)
  await runner.setup()
  site = web.TCPSite(runner, '0.0.0.0', 8000)
  await site.start()


d_intents = discord.Intents.all()
client = discord.Client(intents=d_intents)

KST = pytz.timezone("Asia/Seoul")

@client.event
async def on_ready():
  print("Bot Started")
  await client.change_presence(status=discord.Status.online, activity=discord.Game("지켜보고 있다.👀"))
  client.loop.create_task(report_every_day())
  client.loop.create_task(start_web_server())

@client.event
async def on_voice_state_update(member, before, after):
  ch = client.get_channel(os.environ['MONITORING_CHANNEL_ID'])
  if ch is None:
    print("❌ 채널을 찾을 수 없습니다.")
    return

  now_dt = datetime.now(KST)
  hour_12 = now_dt.strftime("%p").replace("AM", "오전").replace("PM", "오후")
  now = now_dt.strftime(f"%Y년 %m월 %d일 {hour_12} %I시 %M분 %S초")

  name = member.nick if member.nick else member.display_name
  name_bold = f"**{name}**"

  # 입장
  if not before.channel and after.channel:
    embed = discord.Embed(
        title="✅ 입장",
        description=f"{name_bold} 님이 🎧 **{after.channel.name}** 에 입장하셨습니다!",
        color=discord.Color.green()
    )
    embed.add_field(name="🕒 시간", value=now, inline=False)
    embed.add_field(name="💬 메시지", value=f"파이팅 {name}!", inline=False)
    if member.avatar:
      embed.set_thumbnail(url=member.avatar.url)
    await ch.send(embed=embed)

  # 퇴장
  elif before.channel and not after.channel:
    embed = discord.Embed(
        title="⛔ 퇴장",
        description=f"{name_bold} 님이 🎧 **{before.channel.name}** 에서 퇴장하셨습니다!",
        color=discord.Color.red()
    )
    embed.add_field(name="🕒 시간", value=now, inline=False)
    embed.add_field(name="💬 메시지", value="수고했어! ~~(근데 조금 더 하지?!)~~", inline=False)
    if member.avatar:
      embed.set_thumbnail(url=member.avatar.url)
    await ch.send(embed=embed)

  # 이동
  elif before.channel != after.channel:
    embed = discord.Embed(
        title="🔁 이동",
        description=f"{name_bold} 님이 🎧 **{before.channel.name}** → **{after.channel.name}** 로 이동하셨습니다!",
        color=discord.Color.blurple()
    )
    if member.avatar:
      embed.set_thumbnail(url=member.avatar.url)
    await ch.send(embed=embed)


client.run(os.environ['TOKEN'])