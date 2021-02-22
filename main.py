from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import *
import discord
import asyncio
import time
import os

client = discord.Client()
prefix = '!'

@client.event
async def on_ready():

    print(client.user.name)
    print('성공적으로 봇이 시작되었습니다.')
    game = discord.Game('명령어 : !과제  ')
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):

    #맞춤법 검사기 사이트 오늘할 작업
    if message.content.startswith('!맞춤법'):
        # 타임 아웃 임베드 생성
        def Create_Timeout_Embed():
            TimeoutEmbed = discord.Embed(
                title="입력 시간이 초과되었습니다.",
                color=0xFF9900
            )
            TimeoutEmbed.set_footer(text="다시 시도하려면 !맞춤법를 입력해주세요.", )
            return TimeoutEmbed

            # 명령어를 적은 유저 + 같은 채널인지
        def check(m):
            return m.author == message.author and m.channel == message.channel

        #!맞춤법 커맨드 시작
        choose = discord.Embed(
            title="맞춤법 검사기",
            description='-----------------------------------\n1 : 맞춤법 검사기 실행 \n2 : 맞춤법 검사기 링크 출력하기\n-----------------------------------',
            color=0xFF9900
        )
        choose.set_footer(text="를 입력해주세요. \t (제한시간 : 20초)")
        choosemsg = await message.channel.send(embed=choose)

        try:
            cmsg = await client.wait_for("message", check=check, timeout=20)

            if cmsg.content == '1':
                await choosemsg.delete()

                TransEmbed = discord.Embed(
                    title="맞춤법 검사기",
                    description='-----------------------------------\n검사할 문장을 적어주세요.\n-----------------------------------',
                    color=0xFF9900
                )
                TransEmbed.set_footer(text="[글자수 제한 없음]   (제한시간 : 60초) ")
                Transmsg = await message.channel.send(embed = TransEmbed)

                try:
                    TranslateMsg = await client.wait_for("message", check=check, timeout=60)

                    timeembed = discord.Embed(
                        title="맞춤법 검사기",
                        description="-----------------------------------\n잠시만 기다려주세요!\n검사하는데 시간이 걸릴 수 있습니다.\n-----------------------------------",
                        color=0xFF9900
                    )
                    timemsg = await message.channel.send(embed=timeembed)

                    text = TranslateMsg.content
                    ready_list = []
                    while(len(text) > 500):
                        temp_str = text[:500]

                        last_space = temp_str.rfind('.')
                        if last_space == -1:
                            last_space = temp_str.rfind(',')

                            if last_space == -1:
                                last_space = temp_str.rfind(' ')

                                if last_space == -1:
                                    last_space = 500

                        temp_str = text[0:last_space]
                        ready_list.append(temp_str)

                        text = text[last_space:]

                    ready_list.append(text)

                    new_str = ''
                    #크롤링 옵션
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--no-sandbox")
                    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
                    browser.get('https://search.naver.com/search.naver?ie=UTF-8&sm=whl_hty&query=%EB%A7%9E%EC%B6%A4%EB%B2%95+%EA%B2%80%EC%82%AC%EA%B8%B0')

                    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="grammar_checker"]/div/div[2]/div[1]/div[1]/div/div[1]/textarea')))
                    time.sleep(0.4)
                    for ready in ready_list:
                        browser.find_element_by_xpath('//*[@id="grammar_checker"]/div/div[2]/div[1]/div[1]/div/div[1]/textarea').send_keys(Keys.CONTROL, "a")
                        browser.find_element_by_xpath('//*[@id="grammar_checker"]/div/div[2]/div[1]/div[1]/div/div[1]/textarea').send_keys(ready)
                        browser.find_element_by_xpath('//*[@id="grammar_checker"]/div/div[2]/div[1]/div[1]/div/div[2]/button').click()

                        time.sleep(0.4)
                        soup = BeautifulSoup(browser.page_source, 'html.parser')
                        st = soup.select("p._result_text.stand_txt")[0].text
                        new_str += st.replace('. ', '.\n')

                    # 번역한 내용 엠비드 출력
                    await timemsg.delete()

                    ResultEmbed = discord.Embed(
                        title='맞춤법 검사기 (결과)',
                        color=0xFF9900
                    )
                    ResultEmbed.add_field(name="맞춤법 검사 전", value=f"```{TranslateMsg.content}```", inline=True)
                    ResultEmbed.add_field(name="맞춤법 검사 후", value=f"```{new_str}```", inline=True)
                    ResultEmbed.set_footer(text="네이버 맞춤법 검사기에서 얻어온 번역 결과입니다.",
                                           icon_url="http://www.gnewsbiz.com/news/photo/202006/22508_23046_17.png")

                    await message.channel.send(embed=ResultEmbed)

                except asyncio.exceptions.TimeoutError:
                    await Transmsg.delete()
                    await message.channel.send(embed=Create_Timeout_Embed())

            elif cmsg.content == '2':
                await choosemsg.delete()

                embed = discord.Embed(
                    title="맞춤법 검사기",
                    description='[네이버](https://url.kr/u25xkr "제가 제일 많이 사용하는 맞춤법 검사기 사이트입니다.")',
                    colour=discord.Colour.green()
                )
                embed.set_thumbnail(url='https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAxOTA4MDJfMTMg%2FMDAxNTY0NzA2OTM5NTA3.Hjtl0rncFr84sftHtX-yZHF7mzTXFWXCYmiXIvwhWw8g.K3LfY5hsk4VEkGVSX1No0pEAXtIi56nPi6kAby8ujzog.JPEG.bynelaibhcj%2F%25B3%25D7%25C0%25CC%25B9%25F6%25B8%25C2%25C3%25E3%25B9%25FD%25B0%25CB%25BB%25E7%25B1%25E2.jpg&type=a340')

                await message.channel.send(embed=embed)

            else:
                await choosemsg.delete()

                input_Error_Embed = discord.Embed(
                    title="(입력 오류)\n범위 내 숫자만 선택 해주세요.",
                    color=0xFF9900
                )
                input_Error_Embed.set_footer(text="다시 시도하려면 !맞춤법을 입력해주세요.", )
                await message.channel.send(embed=input_Error_Embed)

        except asyncio.exceptions.TimeoutError:
            await choosemsg.delete()
            await message.channel.send(embed=Create_Timeout_Embed())

    #파파고 크롤링
    if message.content.startswith("!파파고"):
        # 타임 아웃 임베드 생성
        def Create_Timeout_Embed():
            TimeoutEmbed = discord.Embed(
                title="입력 시간이 초과되었습니다.",
                color=0xFF9900
            )
            TimeoutEmbed.set_footer(text="다시 시도하려면 !파파고를 입력해주세요.", )
            return TimeoutEmbed

        # 원하는 번역 입력
        def Create_trans_Embed(isture):
            if isture:
                TransEmbed = discord.Embed(
                    title="파파고 번역기",
                    description='-----------------------------------\n한국어 -> 영어 번역입니다.\n번역할 문장을 입력해주세요.\n-----------------------------------',
                    color=0xFF9900
                )

            else:
                TransEmbed = discord.Embed(
                    title="파파고 번역기",
                    description='-----------------------------------\n영어 -> 한국어 번역입니다.\n번역할 문장을 입력해주세요.\n-----------------------------------',
                    color=0xFF9900
                )
            TransEmbed.set_footer(text="(제한시간 : 60초)")
            return TransEmbed

        # 명령어를 적은 유저 + 같은 채널인지
        def check(m):
            return m.author == message.author and m.channel == message.channel

        KOR_EN = "https://papago.naver.com/?sk=ko&tk=en"
        EN_KOR = "https://papago.naver.com/?sk=en&tk=ko&hn=0"

        choose = discord.Embed(
            title = "파파고 번역기",
            description='-----------------------------------\n1 : 한국어 -> 영어 번역 \n2 : 영어 -> 한국어 번역 \n3 : 사이트 번역\n4 : 파파고 링크 출력하기\n-----------------------------------',
            color = 0xFF9900
        )
        choose.set_footer(text="를 입력해주세요. \t (제한시간 : 20초)")
        choosemsg = await message.channel.send(embed=choose)

        try:
            cmsg = await client.wait_for("message", check=check, timeout=20)

            if cmsg.content == '1':
                await choosemsg.delete()
                input_trans_msg = await message.channel.send(embed=Create_trans_Embed(True))

                try:
                    translateMsg = await client.wait_for("message", check=check, timeout=60)

                    message_content = translateMsg.content
                    timeembed = discord.Embed(
                        title="파파고 번역기",
                        description = "-----------------------------------\n잠시만 기다려주세요!\n번역하는데 시간이 걸릴 수 있습니다.\n-----------------------------------",
                        color=0xFF9900
                    )
                    timemsg = await message.channel.send(embed=timeembed)

                    #크롤링 옵션
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--no-sandbox")
                    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
                    browser.get(KOR_EN)

                    #텍스트 번역
                    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtSource"]')))
                    browser.find_element_by_xpath('//*[@id="txtSource"]').send_keys(message_content)
                    browser.find_element_by_xpath('//*[@id="btnTranslate"]').click()

                    #번역한 문자열 복사
                    time.sleep(1)
                    TransResult = browser.find_element_by_xpath('//*[@id="txtTarget"]').text

                    #번역한 내용 엠비드 출력
                    await timemsg.delete()

                    ResultEmbed = discord.Embed(
                        title = '파파고 번역기',
                        description = '한국어 -> 영어 번역 결과',
                        color = 0xFF9900
                    )
                    ResultEmbed.add_field(name="Korean", value=f"```{message_content}```", inline=True)
                    ResultEmbed.add_field(name="English", value=f"```{TransResult}```", inline=True)
                    ResultEmbed.set_footer(text="Papago에서 얻어온 번역 결과입니다.", icon_url="https://cdn.discordapp.com/attachments/704169918777655317/807856285545529344/papago_og.png")

                    await message.channel.send(embed=ResultEmbed)

                except asyncio.exceptions.TimeoutError:
                    await input_trans_msg.delete()
                    await message.channel.send(embed=Create_Timeout_Embed())

            elif cmsg.content == '2':
                await choosemsg.delete()
                input_trans_msg = await message.channel.send(embed=Create_trans_Embed(False))

                try:
                    translateMsg = await client.wait_for("message", check=check, timeout=60)

                    message_content = translateMsg.content
                    timeembed = discord.Embed(
                        title="파파고 번역기",
                        description = "-----------------------------------\n잠시만 기다려주세요!\n번역하는데 시간이 걸릴 수 있습니다.\n-----------------------------------",
                        color=0xFF9900
                    )
                    timemsg = await message.channel.send(embed=timeembed)

                    #크롤링 옵션
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--no-sandbox")
                    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
                    browser.get(EN_KOR)

                    #텍스트 번역
                    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtSource"]')))
                    browser.find_element_by_xpath('//*[@id="txtSource"]').send_keys(message_content)
                    browser.find_element_by_xpath('//*[@id="btnTranslate"]').click()

                    #번역한 문자열 복사
                    time.sleep(1)
                    TransResult = browser.find_element_by_xpath('//*[@id="txtTarget"]').text

                    #번역한 내용 엠비드 출력
                    await timemsg.delete()

                    ResultEmbed = discord.Embed(
                        title = '파파고 번역기',
                        description = '영어 -> 한국어 번역 결과',
                        color = 0xFF9900
                    )
                    ResultEmbed.add_field(name="English", value=f"```{message_content}```", inline=True)
                    ResultEmbed.add_field(name="Korean", value=f"```{TransResult}```", inline=True)
                    ResultEmbed.set_footer(text="Papago에서 얻어온 번역 결과입니다.", icon_url="https://cdn.discordapp.com/attachments/704169918777655317/807856285545529344/papago_og.png")

                    await message.channel.send(embed=ResultEmbed)

                except asyncio.exceptions.TimeoutError:
                    await input_trans_msg.delete()
                    await message.channel.send(embed=Create_Timeout_Embed())

            elif cmsg.content == '3':
                await choosemsg.delete()

                site_trans_input_embed = discord.Embed(
                    title='파파고 번역기',
                    description = '----------------------------------- \n사이트 한글 변환입니다. \n번역하고 싶은 사이트를 입력해주세요. \n-----------------------------------',
                    color = 0xFF9900
                )
                site_trans_input_embed.set_footer(text="(제한시간 : 60초)")
                input_trans_msg = await message.channel.send(embed=site_trans_input_embed)

                try:
                    site_trans_input = await client.wait_for("message", check=check, timeout=60)
                    await input_trans_msg.delete()

                    timeembed = discord.Embed(
                        title="파파고 번역기",
                        description="-----------------------------------\n잠시만 기다려주세요!\n번역하는데 시간이 걸릴 수 있습니다.\n-----------------------------------",
                        color=0xFF9900
                    )
                    timemsg = await message.channel.send(embed=timeembed)

                    #크롤링 옵션
                    chrome_options = webdriver.ChromeOptions()
                    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
                    chrome_options.add_argument("--headless")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    chrome_options.add_argument("--no-sandbox")
                    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
                    driver.get('https://papago.naver.com/')

                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="inp_url"]')))
                    driver.find_element_by_xpath('//*[@id="inp_url"]').send_keys(site_trans_input.content)

                    time.sleep(1)
                    driver.find_element_by_xpath('//*[@id="inp_url"]').send_keys(Keys.ENTER)
                    trans_site = driver.current_url

                    await timemsg.delete()
                    Papago_ling_Embed = discord.Embed(
                        title="파파고 번역기",
                        description='[제목을 누르면 한글 변환 사이트로 접속](trans_site)',
                        url = trans_site,
                        colour=discord.Colour.green()
                    )
                    Papago_ling_Embed.set_thumbnail(
                        url='https://cdn.discordapp.com/attachments/704169918777655317/807856285545529344/papago_og.png')

                    await message.channel.send(embed=Papago_ling_Embed)

                except asyncio.exceptions.TimeoutError:
                    await input_trans_msg.delete()
                    await message.channel.send(embed=Create_Timeout_Embed())

            elif cmsg.content == '4':
                Papago_ling_Embed = discord.Embed(
                    title="파파고 번역기",
                    description='[파파고 사이트 접속](https://papago.naver.com/ "이 곳을 누르면 파파고 사이트로 들어갈 수 있습니다.")',
                    colour=discord.Colour.green()
                )
                Papago_ling_Embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/704169918777655317/807856285545529344/papago_og.png')

                await message.channel.send(embed=Papago_ling_Embed)

            else:
                await choosemsg.delete()

                input_Error_Embed = discord.Embed(
                    title="(입력 오류)\n범위 내 숫자만 선택 해주세요.",
                    color=0xFF9900
                )
                input_Error_Embed.set_footer(text="다시 시도하려면 !파파고를 입력해주세요.", )
                await message.channel.send(embed=input_Error_Embed)

        except asyncio.exceptions.TimeoutError:
            await choosemsg.delete()
            await message.channel.send(embed=Create_Timeout_Embed())


    if message.content.startswith("!과제"):
        command_embed = discord.Embed(
            title = '봇 명령어 목록',
            color=discord.Colour.dark_gray()
        )
        command_embed.add_field(name='!맞춤법',
                                value='```옵션 1. 원하는 문장 입력할 시, 맞춤법 검사를 해줍니다.\n옵션 2. 맞춤법 검사기 사이트(네이버) 링크를 줍니다.```',
                                inline=False)

        command_embed.add_field(name='!파파고',
                                value='```옵션 1. 원하는 문장을 한국어에서 영어로 변역해줍니다.\n옵션 2. 원하는 문장을 영어에서 한국어로 번역해줍니다.\n옵션 3. 원하는 사이트를 한국어로 번역해줍니다.\n옵션 4. 파파고 사이트 링크를 줍니다..```',
                                inline=True)

        await message.author.send(embed = command_embed)



access_token = os.environ['BOT_TOKEN']
client.run(access_token)

