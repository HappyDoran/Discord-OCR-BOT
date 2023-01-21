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
import numpy
from discord_buttons_plugin import *
from DB import *

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="~", intents=intents)
buttons = ButtonsClient(bot)
token = "MTA2NDEyODQ3NzUwODQwNzQyNg.GzaE9j.O3nYg9GXXvtx8ua7PEEkiYNeIKWlJcvYY221_M"


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
async def 출석(ctx):
    print("flag1")
    conn, cur = util.connection.getConnection()
    print("flag2")
    sql = "SELECT * FROM dailyCheck WHERE did=%s"
    cur.execute(sql, ctx.message.author.id)
    rs = cur.fetchone()
    print(rs)
    from datetime import datetime

    today = datetime.now().strftime('%Y-%m-%d')

    if rs is not None and str(rs.get('date')) == today:
        await ctx.message.delete()
        await ctx.channel.send(f'> {ctx.message.author.display_name}님은 이미 출석체크를 했어요')
        return

    # 처음 등록을 하는 경우
    if rs is None:
        sql = "INSERT INTO dailyCheck (did,count,date) values (%s, %s, %s)"
        cur.execute(sql, (id, 1, today))
        conn.commit()
    else:
        sql = "UPDATE dailyCheck SET count = %s, date = %s WHERE did = %s"
        cur.execute(sql, (rs['count'] + 1, today, id))
        conn.commit()
    await ctx.channel.send("기입 완료")


@bot.command()
async def 등록(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "data.json"

    with open(file_path) as f:
        df = json.load(f)
        # print(df)

    if not df:
        df['{0}'.format(id)] = {
            'nickname': nick,
            'cnt': 0,
        }
        # print(df)
        await ctx.message.delete()
        await ctx.channel.send(f"정보 저장 완료! {ctx.message.author.mention}님 반갑습니다!")

    else:
        # print(df)
        if df.get('{0}'.format(id)) == None:

            df['{0}'.format(id)] = {
                'nickname': nick,
                'cnt': 0,
            }
            # print(df)
            await ctx.message.delete()
            await ctx.channel.send(f"정보 저장 완료! {ctx.message.author.mention}님 반갑습니다!")

        else:
            # df['{0}'.format(id)]['tier'] = i
            # print(df)
            if df.get('{0}'.format(id))['nickname'] != nick:
                df.get('{0}'.format(id))['nickname'] = nick
                await ctx.message.delete()
                await ctx.channel.send("닉네임이 수정되었습니다.")
            else:
                await ctx.message.delete()
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
    flag = 0

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
                    flag = flag + 1
                    await ctx.channel.send("{0}의 이번달 친선 횟수 : {1}".format(i, df.get('{0}'.format(id))['cnt']))
    if flag == 4:
        with open(file_path, 'w') as f:
            json.dump(df, f, indent=2, ensure_ascii=False)

        print(tMonth + tDate + tTime)
        print(tWho)
        print(member)
        try:
            url = ctx.message.attachments[0].url
        except IndexError:
            embed = discord.Embed(title='🫰친선 임베드 ',
                                  description="\n\n**친선 시간**\n{0}월 {1}일 {2}시\n"
                                              "\n**VS**\n{3}\n"
                                              "\n**멤버**\n{4} {5} {6} {7}\n"
                                              "\n**기록 완료**\n".format(tMonth, tDate, tTime, tWho,
                                                                     member[0],
                                                                     member[1], member[2], member[3]),

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
                                                                         member[0],
                                                                         member[1], member[2], member[3]),
                                      color=0x62c1cc)
                embed.set_image(url=url)
                await ctx.message.delete()
                await ctx.channel.send(embed=embed)

        record_path = "Record.json"

        with open(record_path) as f:
            df = json.load(f)
            print(df)
            # print("hello")

        if not df:
            df['{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)] = {
                'vs': tWho,
                'member': member,
            }
            print(df)
            await ctx.channel.send("친선기록 저장 완료!")

        else:
            df['{0}.{1}.{2}:00'.format(tMonth, tDate, tTime)] = {
                'vs': tWho,
                'member': member,
            }
        print(df)

        with open(record_path, 'w') as f:
            json.dump(df, f, indent=2, ensure_ascii=False)

    else:
        print("1")


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

                f = open('../Milky/mapp.csv', 'r', encoding='UTF-8')
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
async def 이번달(ctx):
    id = ctx.message.author.id
    nick = ctx.message.author.nick
    if not nick:
        nick = ctx.message.author.name

    file_path = "data.json"

    with open(file_path) as f:
        df = json.load(f)
        for index, (key, elem) in enumerate(df.items()):
            # print(elem['nickname'])
            # print(elem['cnt'])
            await ctx.channel.send("{0} :  {1}".format(elem['nickname'], (elem['cnt'])))


@bot.command()
async def 도움말(ctx):
    embed = discord.Embed(title='도움말',
                          description="**~등록**\n사용자 등록을 할 수 있습니다.\n`~등록`\n"
                                      "\n\n**~친선기록**\n친선 횟수를 인정 받을 수 있습니다.\n `~친선기록 <월> <일> <시> <vs 상대팀> \n <팀원1> <팀원2> <팀원3> <팀원4>`\n `친선 참여자 디스코드 닉네임 작성`",
                          color=0x62c1cc)
    # embed.set_thumbnail(file='Thumbnail/KakaoTalk_Photo_2023-01-06-16-36-02.png')
    embed.set_footer(text='- 기타 질문은 모두 서동원#5533(온라인일 때만 가능)에게 DM 바랍니다')
    await ctx.channel.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("명령어를 찾지 못했습니다")


bot.run(token)
