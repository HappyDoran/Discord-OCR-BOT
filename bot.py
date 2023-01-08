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

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents= intents)

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
        url = ctx.message.attachments[0].url            # check for an image, call exception if none found
    except IndexError:
        print("Error: No attachments")
        await ctx.send("사진을 올림과 동시에 명령어를 써주세요")
    else:
        if url[0:26] == "https://cdn.discordapp.com":   # look to see if url is from discord
            r = requests.get(url, stream=True)
            imageName = str(Path.home() / "PycharmProjects" / "DiscordBot" / "Photo" / Path(str(uuid.uuid4()) + '.jpg'))      # uuid creates random unique id to use for image names
            with open(imageName, 'wb') as out_file:
                print('Saving image : ' + imageName)
                # print(out_file)
                # print(r.raw)
                shutil.copyfileobj(r.raw, out_file)     # save image (goes to project directory)

                # time.sleep(10)

                path = imageName
                image = cv2.imread(path)

                h, w, c = image.shape
                output = image[int(0.3 * h): int(0.53 * h), int(0.7 * w): int(0.92 * w)]
                # output = image

                rgb_image = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)

                # use Tesseract to OCR the image
                text = pytesseract.image_to_string(rgb_image, lang='kor')
                # print(text)

                #띄어쓰기로 문자열 분할 후 공백문자열 삭제
                l = text.split('\n')
                l = list(filter(None, l))
                print(l)

                #키워드 "기록"으로 문자열 인덱스 추출
                find_berry = '기록'
                index = [i for i in range(len(l)) if find_berry in l[i]]
                # print(index[0])
                map = l[index[0] - 1]
                print("인식한 맵 이름 : " + map)
                rc  = re.sub(r"[^0-9]", "", l[index[0] + 1])
                record = re.sub(r'(.{2})', r':\1', rc)[1:]
                print("인식한 기록 : " + record)

                if os.path.exists(path):
                    os.remove(path)

                max_match_rate = 0

                f = open('map.csv', 'r', encoding='cp949')
                rdr = csv.reader(f)
                for line in rdr:
                    if SequenceMatcher(None, map, line[0]).ratio() > max_match_rate :
                        max_match_rate = SequenceMatcher(None, map, line[0]).ratio()
                        real_map = line[0]

                f.close()

                print("실제 맵 이름 : " + real_map)

                await ctx.channel.send("인식한 맵 이름 : {0}\n인식한 기록 : {1}\n실제 맵 이름 : {2}".format(l[index[0] - 1], record, real_map))
@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title='제 소개를 해볼게요!',
                          description='궁금해하실 것 같은 항목들은 미리 준비해놨어요!',
                          colour = 0xff7676)
    embed.add_field(name='> !기능1',value='기능1에 대한 설명')
    embed.add_field(name='> !기능2', value='기능2에 대한 설명')
    embed.add_field(name='> !기능3', value='기능3에 대한 설명')
    # embed.set_thumbnail(file='Thumbnail/KakaoTalk_Photo_2023-01-06-16-36-02.png')
    embed.set_footer(text='footer부분입니다')
    await ctx.channel.send(embed = embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("명령어를 찾지 못했습니다")


bot.run(token)
