import discord
from discord.ext import commands
import uuid
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
import schedule
import time
from datetime import date
import uuid

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)
buttons = ButtonsClient(bot)
token = "MTA2NDEyODQ3NzUwODQwNzQyNg.G0qqrx.G-YAYl4QtEZf4kS6P65UBX7lcqlTuTDk_GFLG4"


@bot.event
async def on_ready():
    print(bot.user.name, "has connected to Discord.")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('도움말 명령어는 ~도움말'))
    print('[알림]학 봇 "ON"')


@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    await bot.process_commands(msg)


@bot.command()
async def 등록(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    subnick = ctx.message.author.mention
    if not nick:
        nick = ctx.message.author.name

    file_path = "data.json"
    file_path3 = "three_month_data.json"

    with open(file_path) as f:
        df = json.load(f)

    with open(file_path3) as f:
        df2 = json.load(f)

    if not df:
        df['{0}'.format(id)] = {
            'nickname': nick,
            'subnickname': subnick,
            'cnt': 0,
        }
        df2['{0}'.format(id)] = {
            'nickname': nick,
            'subnickname': subnick,
            'cnt': 0,
            'our': 0,
        }
        # print(df)
        await ctx.message.delete()
        await ctx.channel.send(f"정보 저장 완료! {ctx.message.author.mention}님 반갑습니다!")

    else:
        # print(df)
        if df.get('{0}'.format(id)) == None:

            df['{0}'.format(id)] = {
                'nickname': nick,
                'subnickname': subnick,
                'cnt': 0,
            }
            df2['{0}'.format(id)] = {
                'nickname': nick,
                'subnickname': subnick,
                'cnt': 0,
                'our': 0,
            }
            # print(df)
            await ctx.message.delete()
            await ctx.channel.send(f"정보 저장 완료! {ctx.message.author.mention}님 반갑습니다!")

        else:
            # df['{0}'.format(id)]['tier'] = i
            # print(df)
            # if df.get('{0}'.format(id))['nickname'] != nick:
            #     df.get('{0}'.format(id))['nickname'] = nick
            #     await ctx.message.delete()
            #     await ctx.channel.send("닉네임이 수정되었습니다.")
            # else:
            df.get('{0}'.format(id))['subnickname'] = subnick
            df2.get('{0}'.format(id))['subnickname'] = subnick

            await ctx.message.delete()
            await ctx.channel.send(f"{ctx.message.author.mention}님, 이미 저장되어 있는 사용자 입니다!")

    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)

    with open(file_path3, 'w') as f:
        json.dump(df2, f, indent=2, ensure_ascii=False)


@bot.command()
async def 친선기록(ctx, *input):
    rMonth = re.compile('(?P<month>\d+)월')
    rDate = re.compile('(?P<date>\d+)일')
    rTime = re.compile('(?P<time>\d+)시')
    rWho = re.compile('vs\s(?P<who>\w+)')

    des = ' '.join(list(input))
    reg = rWho.search(des)
    tWho = reg.group('who')

    member = []
    member_did = []

    file_path = "data.json"
    file_path3 = "three_month_data.json"

    with open(file_path) as f:
        df = json.load(f)

    with open(file_path3) as f:
        df2 = json.load(f)

    for i in input:
        id = 0
        opt = 0
        if (rMonth.search(i) or rDate.search(i) or rTime.search(i)):
            try:
                reg = rMonth.search(i)
                tMonth = reg.group('month')
                # print(tMonth)
            except:
                pass
            try:
                reg = rDate.search(i)
                tDate = reg.group('date')
                # print(tDate)
            except:
                pass
            try:
                reg = rTime.search(i)
                tTime = reg.group('time')
                # print(tTime)
            except:
                pass
        else:
            if i == 'vs' or i == tWho:
                continue
            else:
                for index, (key, elem) in enumerate(df.items()):
                    # print(elem['nickname'])
                    # print(index, key, elem)
                    # print(i)
                    if i == elem['nickname']:
                        id = key
                        opt = 1
                    elif i == elem['subnickname']:
                        id = key
                        opt = 2
                if id == 0:
                    await ctx.message.delete()
                    await ctx.channel.send("{0}은(는) 등록되어 있지 않은 사용자입니다! 다른 이름으로 등록되어있는지 확인해주세요!".format(i))
                else:
                    if opt == 1:
                        member.append(i)
                        member_did.append(id)
                    elif opt == 2:
                        member.append(df.get('{0}'.format(id))['nickname'])
                        member_did.append(id)
                    # df.get('{0}'.format(id))['cnt'] = df.get('{0}'.format(id))['cnt'] + 1
                    # await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(i, df.get('{0}'.format(id))['cnt']))

    for i in range(len(member)):
        df.get('{0}'.format(member_did[i]))['cnt'] = df.get('{0}'.format(member_did[i]))['cnt'] + 1
        df2.get('{0}'.format(member_did[i]))['cnt'] = df2.get('{0}'.format(member_did[i]))['cnt'] + 1
        # await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(member[i], df.get('{0}'.format(member_did[i]))['cnt']))

    if len(member) < 4 :
        for i in range(4-len(member)):
            member.append(" ")

    # if len(member) == 4:
    #     for i in range(len(member)):
    #         df.get('{0}'.format(member_did[i]))['cnt'] = df.get('{0}'.format(member_did[i]))['cnt'] + 1
    #         df2.get('{0}'.format(member_did[i]))['cnt'] = df2.get('{0}'.format(member_did[i]))['cnt'] + 1
    #         # await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(member[i], df.get('{0}'.format(member_did[i]))['cnt']))
    # else:
    #     # print("인원이 부족합니다")
    #     if len(member) == 8:
    #         await ctx.channel.send("혹시 내전한건가요? ~내전을 이용해주세요!")
    #     else:
    #         await ctx.channel.send("인원이 부족합니다! 4명을 입력해주세요!")

    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)

    with open(file_path3, 'w') as f:
        json.dump(df2, f, indent=2, ensure_ascii=False)

    # print(tMonth + tDate + tTime)
    # print(tWho)
    # print(member)
    time = '{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)
    record_path = "Record.json"

    with open(record_path) as f:
        df = json.load(f)
        print(df)
        # print("hello")

    if not df:
        df['{0}'.format(uuid.uuid4())] = {
            'time': time,
            'vs': tWho,
            'member': member,
        }
        # df['{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)] = {
        #     'vs': tWho,
        #     'member': member,
        # }
        # print(df)
        # await ctx.channel.send("친선기록 저장 완료!")

    else:
        df['{0}'.format(uuid.uuid4())] = {
            'time': time,
            'vs': tWho,
            'member': member,
        }
    # print(df)

    with open(record_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)

    try:
        url = ctx.message.attachments[0].url
    except IndexError:
        embed = discord.Embed(title='🫰친선 임베드 ',
                              description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
                                          "\n**VS**\n{3}\n"
                                          "\n**멤버**\n{4} {5} {6} {7}\n"
                                          "\n**기록 완료**\n".format(tMonth, tDate, tTime, tWho,
                                                                 member[0], member[1], member[2], member[3]),

                              color=0x62c1cc)
        await ctx.message.delete()
        await ctx.channel.send(embed=embed)
    else:
        if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
            embed = discord.Embed(title='🫰친선 임베드 ',
                                  description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
                                              "\n**VS**\n{3}\n"
                                              "\n**멤버**\n{4} {5} {6} {7}\n"
                                              "\n**기록 완료**\n".format(tMonth, tDate, tTime, tWho,
                                                                     member[0], member[1], member[2], member[3]),
                                  color=0x62c1cc)
            embed.set_image(url=url)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed)
    # if len(member) == 4:
    #
    #     record_path = "Record.json"
    #
    #     with open(record_path) as f:
    #         df = json.load(f)
    #         print(df)
    #         # print("hello")
    #
    #     if not df:
    #         df['{0}'.format(uuid.uuid4())] = {
    #             'time': time,
    #             'vs': tWho,
    #             'member': member,
    #         }
    #         # df['{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)] = {
    #         #     'vs': tWho,
    #         #     'member': member,
    #         # }
    #         # print(df)
    #         # await ctx.channel.send("친선기록 저장 완료!")
    #
    #     else:
    #         df['{0}'.format(uuid.uuid4())] = {
    #             'time': time,
    #             'vs': tWho,
    #             'member': member,
    #         }
    #     # print(df)
    #
    #     with open(record_path, 'w') as f:
    #         json.dump(df, f, indent=2, ensure_ascii=False)
    #
    #     try:
    #         url = ctx.message.attachments[0].url
    #     except IndexError:
    #         embed = discord.Embed(title='🫰친선 임베드 ',
    #                               description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
    #                                           "\n**VS**\n{3}\n"
    #                                           "\n**멤버**\n{4} {5} {6} {7}\n"
    #                                           "\n**기록 완료**\n".format(tMonth, tDate, tTime, tWho,
    #                                                                  member[0], member[1], member[2], member[3]),
    #
    #                               color=0x62c1cc)
    #         await ctx.message.delete()
    #         await ctx.channel.send(embed=embed)
    #     else:
    #         if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
    #             embed = discord.Embed(title='🫰친선 임베드 ',
    #                                   description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
    #                                               "\n**VS**\n{3}\n"
    #                                               "\n**멤버**\n{4} {5} {6} {7}\n"
    #                                               "\n**기록 완료**\n".format(tMonth, tDate, tTime, tWho,
    #                                                                      member[0], member[1], member[2], member[3]),
    #                                   color=0x62c1cc)
    #             embed.set_image(url=url)
    #             await ctx.message.delete()
    #             await ctx.channel.send(embed=embed)


@bot.command()
async def 내전(ctx, *input):
    rMonth = re.compile('(?P<month>\d+)월')
    rDate = re.compile('(?P<date>\d+)일')
    rTime = re.compile('(?P<time>\d+)시')
    rCount = re.compile('(?P<count>\d+)번')

    member = []
    member_did = []

    file_path = "data.json"
    file_path3 = "three_month_data.json"

    with open(file_path) as f:
        df = json.load(f)

    with open(file_path3) as f:
        df2 = json.load(f)

    for i in input:
        id = 0
        opt = 0
        if (rMonth.search(i) or rDate.search(i) or rTime.search(i) or rCount.search(i)):
            try:
                reg = rMonth.search(i)
                tMonth = reg.group('month')
                # print(tMonth)
            except:
                pass
            try:
                reg = rDate.search(i)
                tDate = reg.group('date')
                # print(tDate)
            except:
                pass
            try:
                reg = rTime.search(i)
                tTime = reg.group('time')
                # print(tTime)
            except:
                pass
            try:
                reg = rCount.search(i)
                tCount = reg.group('count')
                # print(tCount)
            except:
                pass
        else:
            for index, (key, elem) in enumerate(df.items()):
                # print(elem['nickname'])
                # print(index, key, elem)
                # print(i)
                if i == elem['nickname']:
                    id = key
                    opt = 1
                elif i == elem['subnickname']:
                    id = key
                    opt = 2
            if id == 0:
                await ctx.message.delete()
                await ctx.channel.send("{0}은(는) 등록되어 있지 않은 사용자입니다! 다른 이름으로 등록되어있는지 확인해주세요!".format(i))
            else:
                if opt == 1:
                    member.append(i)
                    member_did.append(id)
                elif opt == 2:
                    member.append(df.get('{0}'.format(id))['nickname'])
                    member_did.append(id)
                # df.get('{0}'.format(id))['cnt'] = df.get('{0}'.format(id))['cnt'] + 1
                # await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(i, df.get('{0}'.format(id))['cnt']))

    for i in range(len(member)):
        df.get('{0}'.format(member_did[i]))['cnt'] = df.get('{0}'.format(member_did[i]))['cnt'] + int(tCount)
        df2.get('{0}'.format(member_did[i]))['our'] = df2.get('{0}'.format(member_did[i]))['our'] + 1
        # await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(member[i], df.get('{0}'.format(member_did[i]))['cnt']))

    if len(member) < 8 :
        for i in range(8-len(member)):
            member.append(" ")

    # if len(member) == 8:
    #     for i in range(len(member)):
    #         df.get('{0}'.format(member_did[i]))['cnt'] = df.get('{0}'.format(member_did[i]))['cnt'] + int(tCount)
    #         df2.get('{0}'.format(member_did[i]))['our'] = df2.get('{0}'.format(member_did[i]))['our'] + 1
    #         # await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(member[i], df.get('{0}'.format(member_did[i]))['cnt']))
    # else:
    #     # print("인원이 부족합니다")
    #     await ctx.channel.send("인원이 부족합니다! 8명을 입력해주세요!")

    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)

    with open(file_path3, 'w') as f:
        json.dump(df2, f, indent=2, ensure_ascii=False)

    # print(tMonth + tDate + tTime)
    # print(tCount)
    # print(member)

    time = '{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)
    record_path = "Record.json"

    with open(record_path) as f:
        df = json.load(f)
        # print(df)
        # print("hello")

    if not df:
        if not df:
            df['{0}'.format(uuid.uuid4())] = {
                'time': time,
                'vs': '내전',
                'member': member,
            }
            # df['{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)] = {
            #     'vs': tWho,
            #     'member': member,
            # }
            # print(df)
            # await ctx.channel.send("친선기록 저장 완료!")

        else:
            df['{0}'.format(uuid.uuid4())] = {
                'time': time,
                'vs': '내전',
                'member': member,
            }
    # print(df)

    with open(record_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)

    try:
        url = ctx.message.attachments[0].url
    except IndexError:
        embed = discord.Embed(title='🫰내전 임베드 ',
                              description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
                                          "\n**VS**\n{3}\n"
                                          "\n**멤버**\n{4} {5} {6} {7}\n{8} {9} {10} {11}\n"
                                          "\n**친선 인정 횟수**\n{12}번\n"
                                          "\n**기록 완료**\n".format(tMonth, tDate, tTime, '내전',
                                                                 member[0], member[1], member[2], member[3],
                                                                 member[4], member[5], member[6], member[7],
                                                                 tCount),

                              color=0x62c1cc)
        await ctx.message.delete()
        await ctx.channel.send(embed=embed)
    else:
        if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
            embed = discord.Embed(title='🫰내전 임베드 ',
                                  description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
                                              "\n**VS**\n{3}\n"
                                              "\n**멤버**\n{4} {5} {6} {7}\n{8} {9} {10} {11}\n"
                                              "\n**친선 인정 횟수**\n{12}번\n"
                                              "\n**기록 완료**\n".format(tMonth, tDate, tTime, '내전',
                                                                     member[0], member[1], member[2], member[3],
                                                                     member[4], member[5], member[6], member[7],
                                                                     tCount),
                                  color=0x62c1cc)
            embed.set_image(url=url)
            await ctx.message.delete()
            await ctx.channel.send(embed=embed)
    # if len(member) == 8:
    #
    #     record_path = "Record.json"
    #
    #     with open(record_path) as f:
    #         df = json.load(f)
    #         # print(df)
    #         # print("hello")
    #
    #     if not df:
    #         if not df:
    #             df['{0}'.format(uuid.uuid4())] = {
    #                 'time': time,
    #                 'vs': '내전',
    #                 'member': member,
    #             }
    #             # df['{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)] = {
    #             #     'vs': tWho,
    #             #     'member': member,
    #             # }
    #             # print(df)
    #             # await ctx.channel.send("친선기록 저장 완료!")
    #
    #         else:
    #             df['{0}'.format(uuid.uuid4())] = {
    #                 'time': time,
    #                 'vs': '내전',
    #                 'member': member,
    #             }
    #     # print(df)
    #
    #     with open(record_path, 'w') as f:
    #         json.dump(df, f, indent=2, ensure_ascii=False)
    #
    #     try:
    #         url = ctx.message.attachments[0].url
    #     except IndexError:
    #         embed = discord.Embed(title='🫰내전 임베드 ',
    #                               description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
    #                                           "\n**VS**\n{3}\n"
    #                                           "\n**멤버**\n{4} {5} {6} {7}\n{8} {9} {10} {11}\n"
    #                                           "\n**친선 인정 횟수**\n{12}번\n"
    #                                           "\n**기록 완료**\n".format(tMonth, tDate, tTime, '내전',
    #                                                                  member[0], member[1], member[2], member[3],
    #                                                                  member[4], member[5], member[6], member[7],
    #                                                                  tCount),
    #
    #                               color=0x62c1cc)
    #         await ctx.message.delete()
    #         await ctx.channel.send(embed=embed)
    #     else:
    #         if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
    #             embed = discord.Embed(title='🫰내전 임베드 ',
    #                                   description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
    #                                               "\n**VS**\n{3}\n"
    #                                               "\n**멤버**\n{4} {5} {6} {7}\n{8} {9} {10} {11}\n"
    #                                               "\n**친선 인정 횟수**\n{12}번\n"
    #                                               "\n**기록 완료**\n".format(tMonth, tDate, tTime, '내전',
    #                                                                      member[0], member[1], member[2], member[3],
    #                                                                      member[4], member[5], member[6], member[7],
    #                                                                      tCount),
    #                                   color=0x62c1cc)
    #             embed.set_image(url=url)
    #             await ctx.message.delete()
    #             await ctx.channel.send(embed=embed)


@bot.command()
async def 횟수(ctx):
    id = ctx.message.author.id

    file_path = "data.json"

    with open(file_path) as f:
        df = json.load(f)

    if df.get('{0}'.format(id)) == None:
        await ctx.channel.send("등록되어 있지 않은 사용자입니다!")
    else:
        await ctx.channel.send(
            "{0}님의 이번달 친선 횟수 : {1}".format(ctx.message.author.mention, df.get('{0}'.format(id))['cnt']))


@bot.command()
async def 이번달(ctx):
    id = ctx.message.author.id
    guild = ctx.message.guild
    member = guild.get_member(id)
    # nick = ctx.message.author.nick
    # if not nick:
    # nick = ctx.message.author.name

    permission = 0
    # print(member.roles)
    try:
        for role in member.roles:
            if permission < role.position:
                permission = role.position

    except:
        pass

    # print(permission)
    file_path = "data.json"

    if permission >= 9 or guild.owner_id == id:
        with open(file_path) as f:
            df = json.load(f)
            for index, (key, elem) in enumerate(df.items()):
                # print(elem['nickname'])
                # print(elem['cnt'])
                await ctx.channel.send("{0} :  {1}".format(elem['nickname'], (elem['cnt'])))
    else:
        await ctx.channel.send(f"{ctx.message.author.mention}님은 권한이 없습니다!")


@bot.command()
async def 닉변(ctx, input):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "data.json"
    file_path3 = "three_month_data.json"

    with open(file_path) as f:
        df = json.load(f)

    with open(file_path3) as f:
        df2 = json.load(f)

    if df.get('{0}'.format(id)) == None:
        await ctx.channel.send("등록되어 있지 않은 사용자입니다!")
    else:
        # print(df.get('{0}'.format(id))['nickname'])
        df.get('{0}'.format(id))['nickname'] = input
        df2.get('{0}'.format(id))['nickname'] = input
        # print(nick)
        # print(input)

        await ctx.message.delete()
        await ctx.channel.send("{0}의 닉네임이 {1}(으)로 변경되었습니다.".format(ctx.message.author.mention, input))

    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)

    with open(file_path3, 'w') as f:
        json.dump(df2, f, indent=2, ensure_ascii=False)


@bot.command()
async def 초기화(ctx):
    id = ctx.message.author.id
    guild = ctx.message.guild

    file_path = "data.json"
    destination = "last_month_data.json"

    record_path = "Record.json"
    destination2 = "last_month_record.json"

    if guild.owner_id == id:
        with open(file_path) as f:
            df = json.load(f)

        with open(record_path) as f:
            df2 = json.load(f)

        shutil.copy2(file_path, destination)

        for index, (key, elem) in enumerate(df.items()):
            elem['cnt'] = 0

        with open(file_path, 'w') as f:
            json.dump(df, f, indent=2, ensure_ascii=False)

        await ctx.channel.send("유저 친선 횟수 초기화")

        with open(destination2, 'w') as f:
            json.dump(df2, f, indent=2, ensure_ascii=False)

        with open(record_path, 'w') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)

        await ctx.channel.send("한달 기록 초기화")


    else:
        await ctx.channel.send(f"{ctx.message.author.mention}님은 권한이 없습니다!")


@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title='학봇 사용 설명서',
                          description="**등록**\n사용자 등록을 할 수 있습니다.\n`~등록`\n"
                                      "\n\n**친선기록**\n친선 횟수를 인정 받을 수 있습니다.\n `~친선기록 <월> <일> <시> <vs 상대팀> \n <@팀원1> <@팀원2> <@팀원3> <@팀원4>`\n `친선 참여자 디스코드 멘션 or 닉네임 작성\n 용병 껴서 친선 진행시 닉네임 입력에 '용병' 입력`\n"
                                      "\n\n**내전**\n내전 횟수를 인정 받을 수 있습니다.\n `~내전 <월> <일> <시> \n <@팀원1> <@팀원2> <@팀원3> <@팀원4> <@팀원5> <@팀원6> <@팀원7> <@팀원8> \n<친선 인정 횟수>`\n `내전 참여자 디스코드 멘션 or 닉네임 작성`\n"
                                      "\n\n**횟수**\n사용자의 이번달 친선 횟수를 확인할 수 있습니다.\n`~횟수`\n"
                                      "\n\n**닉변**\n친선 횟수 등록에 필요한 닉네임을 수정합니다.\n`~닉변 <닉네임>`\n"
                                      "\n\n**이번달**\n크루원 전원의 이번달 친선 횟수를 확인할 수 있습니다.\n`운영진 이상만 사용 가능합니다.`\n`~이번달`\n\n",
                          color=0x62c1cc)
    # embed.set_thumbnail(url= "https://cdn.discordapp.com/attachments/1061134921034383460/1067346756003696720/KakaoTalk_Photo_2023-01-24-16-34-33.gif")
    embed.set_footer(text='\n- 기타 질문은 모두 서동원#5533(온라인일 때만 가능)에게 DM 바랍니다')
    await ctx.channel.send(embed=embed)


@bot.command()
async def qnaglfakdmfEpdh(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/1061134921034383460/1070244729926733874/IMG_2025.png")
    await ctx.channel.send(embed=embed)


@bot.command()
async def zhfhskaktmzmEpdh(ctx):
    embed = discord.Embed()
    embed.set_image(url="https://cdn.discordapp.com/attachments/1061134921034383460/1070246428720513105/IMG_2023.png")
    await ctx.channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("명령어를 찾지 못했습니다")


bot.run(token)
