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
bot = commands.Bot(command_prefix="!", intents=intents)
buttons = ButtonsClient(bot)
token = "token"


@bot.event
async def on_ready():
    print(bot.user.name, "has connected to Discord.")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('실뭉치 가지고 놀이'))
    print('[알림]ㅈ냥이 "ON"')


@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    await bot.process_commands(msg)


@bot.command()
async def 안녕(ctx):
    await ctx.channel.send("네 주인님")


@bot.command()
async def save(ctx):
    # USAGE: use command .save in the comment box when uploading an image to save the image as a jpg
    try:
        url = ctx.message.attachments[0].url  # check for an image, call exception if none found
    except IndexError:
        print("Error: No attachments")
        await ctx.send("사진을 올림과 동시에 명령어를 써주세요")
    else:
        if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
            r = requests.get(url, stream=True)
            imageName = str(Path.home() / "PycharmProjects" / "DiscordBot" / "Photo" / Path(
                str(uuid.uuid4()) + '.jpg'))  # uuid creates random unique id to use for image names
            with open(imageName, 'wb') as out_file:
                print('Saving image : ' + imageName)
                # print(out_file)
                # print(r.raw)
                shutil.copyfileobj(r.raw, out_file)  # save image (goes to project directory)

                # time.sleep(10)

                image = cv2.imread(imageName)

                h, w, c = image.shape
                output = image[int(0.3 * h): int(0.53 * h), int(0.7 * w): int(0.92 * w)]
                # output = image

                rgb_image = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

                # use Tesseract to OCR the image
                text = pytesseract.image_to_string(rgb_image, lang='kor')
                # print(text)

                # 띄어쓰기로 문자열 분할 후 공백문자열 삭제
                l = text.split('\n')
                l = list(filter(None, l))
                print(l)

                # 키워드 "기록"으로 문자열 인덱스 추출
                find_keyword = '기록'
                index = [i for i in range(len(l)) if find_keyword in l[i]]

                # 키워드 "기록"으로 인식된 문자열이 있을 경우에는
                if index:
                    index = index[0]

                # 키워드 검색 결과가 없을 경우에는 "주간 최고 기록" 이라는 문자열과 일치도를 조사
                else:
                    for i in l:
                        if SequenceMatcher(None, "주간 최고 기록", i).ratio() > 0.5:
                            index = l.index(i)

                map = l[index - 1]
                map = map.replace(" ", "")
                print("인식한 맵 이름 : " + map)
                rc = re.sub(r"[^0-9]", "", l[index + 1])
                record = re.sub(r'(.{2})', r':\1', rc)[1:]
                print("인식한 기록 : " + record)
                compare_record = int(record.replace(":", ""))
                print(compare_record)

                if os.path.exists(imageName):
                    os.remove(imageName)

                max_match_rate = 0

                # 맵 이름 비교후 일치율 비교

                f = open('mapp.csv', 'r', encoding='UTF-8')
                rdr = csv.reader(f)
                for line in rdr:
                    # print("{0} {1}".format(line[0],SequenceMatcher(None, map, line[0]).ratio()))
                    if SequenceMatcher(None, map, line[1]).ratio() > max_match_rate:
                        max_match_rate = SequenceMatcher(None, map, line[1]).ratio()
                        real_map = line[1]
                        rec_list = line

                for i in range(2, 7):
                    rec_list[i] = int(rec_list[i])

                print(rec_list)

                # 노가다
                if compare_record <= rec_list[2]:
                    tier = "강주력"
                elif compare_record > rec_list[2] and compare_record <= rec_list[3]:
                    tier = "주력"
                elif compare_record > rec_list[3] and compare_record <= rec_list[4]:
                    tier = "1군"
                elif compare_record > rec_list[4] and compare_record <= rec_list[5]:
                    tier = "2군"
                elif compare_record > rec_list[5] and compare_record <= rec_list[6]:
                    tier = "3군"
                else:
                    tier = "의견 없음"

                f.close()

                real_map = real_map.replace("//", "[R]")
                print("실제 맵 이름 : " + real_map)
                if ctx.message.author.nick:
                    await ctx.channel.send(
                        # "인식한 맵 이름 : {0}\n인식한 기록 : {1}\n실제 맵 이름 : {2} \n작성한 사람 : {3}".format(l[index - 1], record, real_map, ctx.message.author)
                        "맵 이름 : {0} \n인식한 기록 : {1}\n군 산출 : {3}\n작성한 사람 : {2}".format(real_map, record,
                                                                                     ctx.message.author.nick, tier)
                    )
                else:
                    await ctx.channel.send(
                        # "인식한 맵 이름 : {0}\n인식한 기록 : {1}\n실제 맵 이름 : {2} \n작성한 사람 : {3}".format(l[index - 1], record, real_map, ctx.message.author)
                        "맵 이름 : {0} \n인식한 기록 : {1}\n군 산출 : {3}\n작성한 사람 : {2}".format(real_map, record,
                                                                                     ctx.message.author.name, tier)
                    )


@bot.command()
async def file(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "User.json"

    with open(file_path) as f:
        df = json.load(f)

    if not df:
        df['{0}'.format(id)] = {
            'nickname': nick,
            'point': 0,
            'tier': 'input'
        }
        await ctx.channel.send("정보 저장 완료!")

    else:
        if df.get('{0}'.format(id)) == None:

            df['{0}'.format(id)] = {
                'nickname': nick,
                'point': 0,
                'tier': 'input'
            }
            await ctx.channel.send("정보 저장 완료!")

        else:
            await ctx.channel.send("이미 저장되어 있는 사용자 입니다!")

    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)


@bot.command()
async def register(ctx, *input):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "User.json"

    # await ctx.channel.send("등록 되었다")
    for i in input:
        print(i)

        if i == "강주력":
            i = 0

        elif i == "주력":
            i = 1

        elif i == "1군":
            i = 2

        elif i == "2군":
            i = 3

        elif i == "3군":
            i = 4

        elif i == "4군":
            i = 5

        else:
            i = 6

        if i == 6:
            await ctx.channel.send("유효하지 않은 군입니다. 다시 입력 부탁드립니다.")
        else:
            try:
                with open(file_path) as f:
                    df = json.load(f)

                if not df:
                    df['{0}'.format(id)] = {
                        'nickname': nick,
                        'point': 0,
                        'tier': i
                    }
                    print(df)
                    await ctx.channel.send("정보 저장 완료!")

                else:
                    if df.get('{0}'.format(id)) == None:

                        df['{0}'.format(id)] = {
                            'nickname': nick,
                            'point': 0,
                            'tier': i
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

            except:
                pass


@bot.command()
async def update(ctx, *input):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "User.json"

    # await ctx.channel.send("등록 되었다")
    for i in input:
        print(i)

        if i == "강주력":
            i = 0

        elif i == "주력":
            i = 1

        elif i == "1군":
            i = 2

        elif i == "2군":
            i = 3

        elif i == "3군":
            i = 4

        elif i == "4군":
            i = 5

        else:
            i = 6

        print(i)
        if i == 6:
            await ctx.channel.send("유효하지 않은 군입니다. 다시 입력 부탁드립니다.")
        else:
            try:
                with open(file_path) as f:
                    df = json.load(f)

                if not df:
                    df['{0}'.format(id)] = {
                        'nickname': nick,
                        'point': 0,
                        'tier': i
                    }
                    print(df)
                    await ctx.channel.send("정보 저장 완료!")

                else:
                    if df.get('{0}'.format(id)) == None:

                        print(df.get('{0}'.format(id)))

                        df['{0}'.format(id)] = {
                            'nickname': nick,
                            'point': 0,
                            'tier': i
                        }
                        print(df)
                        await ctx.channel.send("정보 저장 완료!")

                    else:
                        df['{0}'.format(id)]['tier'] = i
                        print(df)
                        await ctx.channel.send("군 수정 완료!")

                with open(file_path, 'w') as f:
                    json.dump(df, f, indent=2, ensure_ascii=False)

            except:
                pass


@bot.command()
async def 공통(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "User.json"
    week_map = "팩토리 미완성 5구역"

    with open(file_path) as f:
        df = json.load(f)

    if df.get('{0}'.format(id)) == None:
        await ctx.channel.send("등록되어 있지 않은 사용자입니다! !register로 등록을 먼저 해주세요!")

    else:
        # USAGE: use command .save in the comment box when uploading an image to save the image as a jpg
        try:
            url = ctx.message.attachments[0].url  # check for an image, call exception if none found
        except IndexError:
            print("Error: No attachments")
            await ctx.send("사진을 올림과 동시에 명령어를 써주세요")
        else:
            if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
                r = requests.get(url, stream=True)
                imageName = str(Path.home() / "PycharmProjects" / "DiscordBot" / "Photo" / Path(
                    str(uuid.uuid4()) + '.jpg'))  # uuid creates random unique id to use for image names
                with open(imageName, 'wb') as out_file:
                    print('Saving image : ' + imageName)
                    # print(out_file)
                    # print(r.raw)
                    shutil.copyfileobj(r.raw, out_file)  # save image (goes to project directory)

                    # time.sleep(10)

                    image = cv2.imread(imageName)

                    h, w, c = image.shape
                    output = image[int(0.3 * h): int(0.53 * h), int(0.7 * w): int(0.92 * w)]
                    # output = image

                    rgb_image = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

                    # use Tesseract to OCR the image
                    text = pytesseract.image_to_string(rgb_image, lang='kor')
                    # print(text)

                    # 띄어쓰기로 문자열 분할 후 공백문자열 삭제
                    l = text.split('\n')
                    l = list(filter(None, l))
                    print(l)

                    # 키워드 "기록"으로 문자열 인덱스 추출
                    find_keyword = '기록'
                    index = [i for i in range(len(l)) if find_keyword in l[i]]

                    # 키워드 "기록"으로 인식된 문자열이 있을 경우에는
                    if index:
                        index = index[0]

                    # 키워드 검색 결과가 없을 경우에는 "주간 최고 기록" 이라는 문자열과 일치도를 조사
                    else:
                        for i in l:
                            if SequenceMatcher(None, "주간 최고 기록", i).ratio() > 0.5:
                                index = l.index(i)

                    map = l[index - 1]
                    map = map.replace(" ", "")

                    rc = re.sub(r"[^0-9]", "", l[index + 1])
                    record = re.sub(r'(.{2})', r':\1', rc)[1:]

                    compare_record = int(record.replace(":", ""))

                    if os.path.exists(imageName):
                        os.remove(imageName)

                    max_match_rate = 0

                    # 맵 이름 비교후 일치율 비교

                    f = open('mapp.csv', 'r', encoding='UTF-8')
                    rdr = csv.reader(f)
                    for line in rdr:
                        if SequenceMatcher(None, map, line[1]).ratio() > max_match_rate:
                            max_match_rate = SequenceMatcher(None, map, line[1]).ratio()
                            real_map = line[1]
                            rec_list = line

                    for i in range(2, 7):
                        rec_list[i] = int(rec_list[i])

                    # 노가다
                    if compare_record <= rec_list[2]:
                        tier = 0
                    elif compare_record > rec_list[2] and compare_record <= rec_list[3]:
                        tier = 1
                    elif compare_record > rec_list[3] and compare_record <= rec_list[4]:
                        tier = 2
                    elif compare_record > rec_list[4] and compare_record <= rec_list[5]:
                        tier = 3
                    elif compare_record > rec_list[5] and compare_record <= rec_list[6]:
                        tier = 4
                    else:
                        tier = 5

                    f.close()

                    real_map = real_map.replace("//", "[R]")

                    print(df.get('{0}'.format(id))['tier'])
                    print(tier)

                    if real_map != week_map:
                        await ctx.channel.send("금주의 은하스쿨 맵이 아닙니다!")
                    else:
                        if df.get('{0}'.format(id))['tier'] >= tier:
                            df.get('{0}'.format(id))['point'] = df.get('{0}'.format(id))['point'] + 5000
                            await ctx.channel.send("금주의 은하스쿨 완료!")
                            await ctx.channel.send("작성자의 포인트 누적 : {0}P".format(df.get('{0}'.format(id))['point']))
                        else:
                            await ctx.channel.send("군에 맞지 않는 기록입니다! ")

                    with open(file_path, 'w') as f:
                        json.dump(df, f, indent=2, ensure_ascii=False)


@bot.command()
async def 내부텟(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "User.json"

    with open(file_path) as f:
        df = json.load(f)

    if df.get('{0}'.format(id)) == None:
        await ctx.channel.send("등록되어 있지 않은 사용자입니다! !register로 등록을 먼저 해주세요!")

    else:
        df.get('{0}'.format(id))['point'] = df.get('{0}'.format(id))['point'] + 50000
        df.get('{0}'.format(id))['tier'] = df.get('{0}'.format(id))['tier'] - 1
        if df.get('{0}'.format(id))['tier'] == 0:
            tier = "강주력"

        elif df.get('{0}'.format(id))['tier'] == 1:
            tier = "주력"

        elif df.get('{0}'.format(id))['tier'] == 2:
            tier = "1군"

        elif df.get('{0}'.format(id))['tier'] == 3:
            tier = "2군"

        elif df.get('{0}'.format(id))['tier'] == 4:
            tier = "3군"

        elif df.get('{0}'.format(id))['tier'] == 5:
            tier = "4군"
        await ctx.channel.send("{0} 승급 완료! 축하드립니다!".format(tier))
        await ctx.channel.send("작성자의 포인트 누적 : {0}P".format(df.get('{0}'.format(id))['point']))

    with open(file_path, 'w') as f:
        json.dump(df, f, indent=2, ensure_ascii=False)


@bot.command()
async def 친선(ctx, *input):
    for i in input:
        print(i)
        id = 0
        file_path = "User.json"

        with open(file_path) as f:
            df = json.load(f)

        for index, (key, elem) in enumerate(df.items()):
            print(elem['nickname'])
            print(index, key, elem)
            if (i == elem['nickname']):
                id = key
        if id == 0:
            await ctx.channel.send("{0}은(는) 등록되어 있지 않은 사용자입니다! 다른 이름으로 등록되어있는지 확인해주세요!".format(i))
        else:
            df.get('{0}'.format(id))['point'] = df.get('{0}'.format(id))['point'] + 2000
            await ctx.channel.send("작성자의 포인트 누적 : {0}P".format(df.get('{0}'.format(id))['point']))

        with open(file_path, 'w') as f:
            json.dump(df, f, indent=2, ensure_ascii=False)


@bot.command()
async def 개인(ctx, *input):
    # USAGE: use command .save in the comment box when uploading an image to save the image as a jpg
    des = ' '.join(list(input))

    print(des)

    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name
    try:
        url = ctx.message.attachments[0].url  # check for an image, call exception if none found
    except IndexError:
        print("Error: No attachments")
        await ctx.send("사진을 올림과 동시에 명령어를 써주세요")
    else:
        await ctx.message.delete()
        if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
            embed = discord.Embed(title='🫰{0} 개인 은하스쿨 '.format(nick),
                                  # description="{0}".format(input),
                                  color=0x62c1cc)
            embed.set_image(url=url)
            # embed.set_footer(text='- 기타 질문은 모두 서동원#5533(온라인일 때만 가능)에게 DM 바랍니다')
            view = Clear(id)

            # print(view.id)
            await ctx.channel.send(embed=embed, view=view)
            # print(menu1)
            # await ctx.send(view=view)


class Clear(discord.ui.View):
    def __init__(self, id):
        super().__init__()
        # self.value = None
        self.id = id

    @discord.ui.button(label="확인", style=discord.ButtonStyle.blurple)
    async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        print("버튼 누른 사람의 디스코드 고유 번호 : " + str(interaction.user.id))
        print("숙제를 완료한 사람의 디스코드 고유 번호 : " + str(self.id))
        await interaction.response.send_message("Button click")


@bot.command()
async def 이개인(ctx, *input):
    # USAGE: use command .save in the comment box when uploading an image to save the image as a jpg

    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name
    try:
        url = ctx.message.attachments[0].url  # check for an image, call exception if none found
    except IndexError:
        print("Error: No attachments")
        await ctx.send("사진을 올림과 동시에 명령어를 써주세요")
    else:
        if url[0:26] == "https://cdn.discordapp.com":  # look to see if url is from discord
            embed = discord.Embed(title='🫰{0} 개인 은하스쿨 '.format(nick),
                                  # description="{0}".format(input),
                                  color=0x62c1cc)
            embed.set_image(url=url)
            # embed.set_footer(text='- 기타 질문은 모두 서동원#5533(온라인일 때만 가능)에게 DM 바랍니다')
            # view = Menu()
            # print("view.menu" + view.menu1)
            await ctx.message.delete()
            msg = await ctx.channel.send(embed=embed)
            await msg.add_reaction('✅')
            try:
                def check(reaction, user):
                    print(user)
                    print(ctx.author)
                    print(reaction.message.id)
                    print(msg.id)
                    return str(reaction) == '✅' and user == ctx.author and reaction.message.id == msg.id

                reaction, user = await bot.wait_for('reaction_add', check=check)
                embed.add_field(name='> ', value='')
                embed.add_field(name='> ', value='')
                embed.add_field(name='> ', value='')
                await msg.clear_reactions()
                await msg.edit(embed=embed)

            except:
                pass


@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title='도움말',
                          description="**!register**\n사용자 등록을 할 수 있습니다.\n`!register <군>` \n`1군일 경우 '1군' 입력, 주력일 경우 '주력' 입력`"
                                      "\n\n**!update**\n군 업데이트를 할 수 있습니다.\n`!update <군>` \n`1군일 경우 '1군' 입력, 주력일 경우 '주력' 입력`"
                                      "\n\n**!공통**\n은하수쿨 공통 숙제 인증을 받을 수 있습니다.\n `사진 첨부와 동시에 !공통`"
                                      "\n\n**!개인**\n은하수쿨 개인 숙제 인증을 받을 수 있습니다.\n `사진 첨부와 동시에 !개인`"
                                      "\n\n**!내부텟**\n은하수 내부텟 포인트를 받을 수 있습니다.\n `카톡에 기록 스샷 첨부 후 확인 받으면 !내부텟`"
                                      "\n\n**!친선**\n친선 포인트를 받을 수 있습니다.\n `!친선 <팀원1> <팀원2> <팀원3> <팀원4>`\n `친선 참여자 디스코드 닉네임 작성`"
                                      "\n\n**!save**\n맵, 기록에 대한 군을 파악할 수 있습니다.\n `사진 첨부와 동시에 !공통`",
                          color=0x62c1cc)
    # embed.set_thumbnail(file='Thumbnail/KakaoTalk_Photo_2023-01-06-16-36-02.png')
    embed.set_footer(text='- 기타 질문은 모두 서동원#5533(온라인일 때만 가능)에게 DM 바랍니다')
    await ctx.channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("명령어를 찾지 못했습니다")


bot.run(token)
