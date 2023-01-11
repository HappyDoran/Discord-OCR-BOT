import discord
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

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

token = "MTA2MDgyMzY1ODgzMjA3NjgzMA.GshC3S.5W_d5GJTRyEgIiEtCnA9U4HbyFHOWcM8xolFNg"


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

                #키워드 "기록"으로 인식된 문자열이 있을 경우에는
                if index :
                    index = index[0]

                #키워드 검색 결과가 없을 경우에는 "주간 최고 기록" 이라는 문자열과 일치도를 조사
                else:
                    for i in l:
                        if SequenceMatcher(None, "주간 최고 기록", i).ratio() > 0.5 :
                            index = l.index(i)

                map = l[index - 1]
                map = map.replace(" ", "")
                print("인식한 맵 이름 : " + map)
                rc = re.sub(r"[^0-9]", "", l[index + 1])
                record = re.sub(r'(.{2})', r':\1', rc)[1:]
                print("인식한 기록 : " + record)
                compare_record = int(record.replace(":",""))
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

                for i in range(2,7):
                    rec_list[i] = int(rec_list[i])

                print(rec_list)

                #노가다
                if compare_record <= rec_list[2] :
                    tier = "강주력"
                elif compare_record > rec_list[2] and compare_record <= rec_list[3] :
                    tier = "주력"
                elif compare_record > rec_list[3] and compare_record <= rec_list[4] :
                    tier = "1군"
                elif compare_record > rec_list[4] and compare_record <= rec_list[5] :
                    tier = "2군"
                elif compare_record > rec_list[5] and compare_record <= rec_list[6] :
                    tier = "3군"
                else :
                    tier = "의견 없음"

                f.close()

                real_map = real_map.replace("//", "[R]")
                print("실제 맵 이름 : " + real_map)
                if ctx.message.author.nick:
                    await ctx.channel.send(
                        # "인식한 맵 이름 : {0}\n인식한 기록 : {1}\n실제 맵 이름 : {2} \n작성한 사람 : {3}".format(l[index - 1], record, real_map, ctx.message.author)
                        "맵 이름 : {0} \n인식한 기록 : {1}\n군 산출 : {3}\n작성한 사람 : {2}".format(real_map,record,ctx.message.author.nick,tier)
                    )
                else :
                    await ctx.channel.send(
                        # "인식한 맵 이름 : {0}\n인식한 기록 : {1}\n실제 맵 이름 : {2} \n작성한 사람 : {3}".format(l[index - 1], record, real_map, ctx.message.author)
                        "맵 이름 : {0} \n인식한 기록 : {1}\n군 산출 : {3}\n작성한 사람 : {2}".format(real_map, record, ctx.message.author.name,tier)
                    )

@bot.command()
async def file(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick :
        nick = ctx.message.author.name

    file_path = "User.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
        print(data)

    data[id].append({
        "name": nick,
        "point": 0
    })

    with open(file_path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent="\t",ensure_ascii=False)

    await ctx.channel.send("정보 저장 완료!")

@bot.command()
async  def register(ctx, *input):
    teammate1 = re.compile(' ')
    teammate2 = re.compile(' ')
    teammate3 = re.compile(' ')
    # teammate4 = re.compile(' ')

    for i in input:
        print(i)


@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title='제 소개를 해볼게요!',
                          description='궁금해하실 것 같은 항목들은 미리 준비해놨어요!',
                          colour=0xff7676)
    embed.add_field(name='> !기능1', value='기능1에 대한 설명')
    embed.add_field(name='> !기능2', value='기능2에 대한 설명')
    embed.add_field(name='> !기능3', value='기능3에 대한 설명')
    # embed.set_thumbnail(file='Thumbnail/KakaoTalk_Photo_2023-01-06-16-36-02.png')
    embed.set_footer(text='footer부분입니다')
    await ctx.channel.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("명령어를 찾지 못했습니다")

bot.run(token)
