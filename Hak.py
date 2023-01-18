import discord
import interactions
from discord.ext import commands
import uuid
import requests
import shutil
from pathlib import Path
import pytesseract
import cv2
import os
import re
import csv
from difflib import SequenceMatcher
import json
from discord_buttons_plugin import *

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)
buttons = ButtonsClient(bot)
token = "MTA2NDEyODQ3NzUwODQwNzQyNg.GqswwK.BIMT_kBOxNQXc5UtX_OuKZa6X0EhmmVjTdQbd4"


@bot.event
async def on_ready():
    print(bot.user.name, "has connected to Discord.")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('떼햄이랑 파스타 먹기'))
    print('[알림]학 봇 "ON"')


@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    await bot.process_commands(msg)


@bot.command()
async def register(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "data.json"

    with open(file_path) as f:
        df = json.load(f)

    if not df:
        df['{0}'.format(id)] = {
            'nickname': nick,
            'cnt': 0,
        }
        print(df)
        await ctx.channel.send("정보 저장 완료!")

    else:
        if df.get('{0}'.format(id)) == None:

            df['{0}'.format(id)] = {
                'nickname': nick,
                'cnt': 0,
            }
            print(df)
            await ctx.channel.send("정보 저장 완료!")

        else:
            # df['{0}'.format(id)]['tier'] = i
            print(df)
            # if df.get('{0}'.format(id))['nickname'] != nick:
            #     df.get('{0}'.format(id))['nickname'] = nick
            #     await ctx.channel.send("닉네임이 수정되었습니다.")
            # else:
            await ctx.channel.send("이미 저장되어 있는 사용자 입니다!")

    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)


@bot.command()
async def 친선기록(ctx, *input):
    import re
    rMonth = re.compile('(?P<month>\d+)월')
    rDate = re.compile('(?P<date>\d+)일')
    rTime = re.compile('(?P<time>\d+)시')
    rWho = re.compile('vs\s(?P<who>\w+)')

    des = ' '.join(list(input))
    reg = rWho.search(des)
    tWho = reg.group('who')
    print(tWho)

    member = []

    file_path = "data.json"

    with open(file_path) as f:
        df = json.load(f)

    for i in input:
        id = 0
        if (rMonth.search(i) or rDate.search(i) or rTime.search(i)):
            try:
                reg = rMonth.search(i)
                tMonth = reg.group('month')
                print(tMonth)
            except:
                pass
            try:
                reg = rDate.search(i)
                tDate = reg.group('date')
                print(tDate)
            except:
                pass
            try:
                reg = rTime.search(i)
                tTime = reg.group('time')
                print(tTime)
            except:
                pass
        else:
            if i == 'vs' or i == tWho:
                continue
            else:
                for index, (key, elem) in enumerate(df.items()):
                    # print(elem['nickname'])
                    # print(index, key, elem)
                    if (i == elem['nickname']):
                        id = key
                if id == 0:
                    await ctx.channel.send("{0}은(는) 등록되어 있지 않은 사용자입니다! 다른 이름으로 등록되어있는지 확인해주세요!".format(i))
                else:
                    member.append(i)
                    df.get('{0}'.format(id))['cnt'] = df.get('{0}'.format(id))['cnt'] + 1
                    await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(i, df.get('{0}'.format(id))['cnt']))


    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)

    print(tMonth + tDate + tTime)
    print(tWho)
    print(member)

    record_path = "Record.json"

    with open(record_path) as f:
        df = json.load(f)
        print(df)
        #print("hello")

    if not df:
        df['{0}.{1}.{2}:00'.format(tMonth,tDate,tTime)] = {
            'vs': tWho,
            'member': member,
        }
        print(df)
        await ctx.channel.send("정보 저장 완료!")

    else:
        df['{0}.{1}.{2} : 00'.format(tMonth, tDate, tTime)] = {
            'vs': tWho,
            'member': member,
        }
    print(df)

    with open(record_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)


@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title='도움말',
                          description="**!register**\n사용자 등록을 할 수 있습니다.\n`!register`\n"
                                      "\n\n**!친선기록**\n친선 횟수를 인정 받을 수 있습니다.\n `!친선기록 <월> <일> <시> <vs 상대팀> \n <팀원1> <팀원2> <팀원3> <팀원4>`\n `친선 참여자 디스코드 닉네임 작성`",
                          color=0x62c1cc)
    # embed.set_thumbnail(file='Thumbnail/KakaoTalk_Photo_2023-01-06-16-36-02.png')
    embed.set_footer(text='- 기타 질문은 모두 서동원#5533(온라인일 때만 가능)에게 DM 바랍니다')
    await ctx.channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("명령어를 찾지 못했습니다")


bot.run(token)
