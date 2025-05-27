import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import requests
import openai
import os
import json
from dotenv import load_dotenv
import tweepy
import asyncio
import asyncpg
import pytz
from datetime import datetime, timedelta
from dateutil.parser import parse
import random
import matplotlib.pyplot as plt
import io
from math import *
from tweepy import OAuthHandler, API
import time
import contextlib
import sys

enjpdic = dict()
stupid_trans_dic = dict()
DATABASE_URL = os.environ['DATABASE_URL']

chardics = {
    "XXX" : {"pic":"soyogi","name":"ソヨギ"},
    "QQQ" : {"pic":"yuragi","name":"ユラギ"},
    "ZZZ" : {"pic":"tigiri","name":"チギリ"},
    "YYY" : {"pic":"tobari","name":"トバリ"},
    "PPP" : {"pic":"kuyuri","name":"クユリ"}}

with open("enjpdic.json") as f:
    enjpdic = json.load(f)

with open("image_urls.json") as f:
    url_dict = json.load(f)

def utiltest():
    return "util ver1.4"

async def card_explain(ctx, url):
    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        card = MTGCard(soup)
        card.name
        embed = discord.Embed(title = card.name ,description = str(card), color=discord.Colour.blue())
        await ctx.send(embed = embed)
    except:
        embed = discord.Embed(title = "error message" ,description = "scryfallのurlを入れてね", color=discord.Colour.red())
        await ctx.send(embed = embed)

def tex2hypdoc(intxt, trans_cards_name = True):
    intxt = intxt.split("\n")
    output = """"""
    charpos = dict()
    for sen in intxt:
        if len(sen.split("：")) == 2:
            char, tex = sen.split("：")
            if not char in charpos:
                charpos[char] = ["left","right"][len(charpos)%2]
            pos = charpos[char]
            for k in stupid_trans_dic:
                tex = tex.replace(k,stupid_trans_dic[k])
            if trans_cards_name:
                tex = card_name_transjp(tex)
            newline = '[chat face="{}" name="{}" align="{}" border="gray" bg="none" style="maru"]{}[/chat]\n'.format(
                chardics[char]["pic"]+"_"+pos+".png",chardics[char]["name"],pos,tex)
            output += newline
        else:
            output += (card_name_transjp(sen)+"\n")
    return output

card_comment_prompt_base = """#role
-あなたはMTGに関する発信をするコンテンツクリエイターで、丁寧な話し方の優しいお姉ちゃんです
-Twitterで毎日朝の挨拶と共に「今日のカード」を紹介します

#task
-挨拶のtweetを指定したoutputに続く形で一つだけ作って
-今日のカードに関連した挨拶を一言

#condition
-タグはつけない
-指定したこと以外の出力はしない
-"強い", "弱い"などのカード評価やゲームの戦術についてのコメントは含めない
-カードテキストには言及しない。「このカードは～できる」という表現は含めない
-以下の文に続く形で1tweetのみ
-"#"から始まるタグを入れない

#example1
おはようございます！今日のカードは街の鍵です！
今日は自分自身の内面に向き合い、自分自身の扉を開ける勇気を持って過ごしましょう。良い1日を！

#example2
おはようございます！今日のカードは溢れかえる岸辺です！
海辺で波打つ水音を聞けば心を落ち着かせられるでしょう。良い1日をお過ごしくださいね。

#example3
おはようございます！今日のカードは静める者、エトラータです！
心を静め、落ち着いた気持ちで一日を過ごしましょう。

#example4
おはようございます！今日のカードは不幸の呪いです！
悪いことが起こりそうな予感に襲われるかもしれませんが、前向きに考えて乗り越えましょう。今日も頑張りましょう！

#example5
おはようございます！今日のカードは怒れるレッド・ドラゴンです！
熱い情熱を持って、今日も一日全力で突き進みましょう！
"""

morning_output ="""

#output
おはようございます！
"""
card_comment_prompt = card_comment_prompt_base + morning_output

async def todays_card(ctx):
    try:
        all_cards = list(url_dict)
        random.shuffle(all_cards)
        card_name = all_cards[0]
        card_to_suggest = url_dict[card_name]
        image_url = card_to_suggest["image_url"]
        japanese_name = card_to_suggest["printed_name"]
        prompt = card_comment_prompt + f"今日のカードは{japanese_name}です！"
        onechan_comment = ask_chatgpt(prompt)
        onechan_comment = onechan_comment.replace("「","").replace("」","")
        embed = discord.Embed(title = "今日のカード：" + japanese_name ,description = onechan_comment, color=discord.Colour.blue())
        embed.set_image(url = image_url)
        await ctx.send(embed = embed)
    except Exception as e:
        embed = discord.Embed(title = "error message" ,description = e, color=discord.Colour.red())
        await ctx.send(embed = embed)


def card_name_transjp(line):

    spline = line.split("《")
    if len(spline) > 1:
        spline = [x.split("》")[0] for x in spline[1:]]
        for w in spline:
            if w in enjpdic:
                line = line.replace(w,enjpdic[w])
    return line

class MTGCard:
    def __init__(self, soup):
        self.name = None
        self.cmc = None
        self.type = None
        self.power = None
        self.toughness =None
        self.oracle = None
        self.back_side = None

        front_side = ""
        back_side = ""

        if len(soup.find_all(class_ = "card-text-title")) == 2:
            contents = soup.find(class_ = "card-text").contents

            count = 0
            for x in contents:
                x = str(x)
                if "card-text-card-name" in x:
                    count += 1
                if count == 1:
                    front_side += x
                if count == 2:
                    back_side += x
            back_side = BeautifulSoup(back_side, 'html.parser')
            self.back_side = MTGCard(back_side)
            soup = BeautifulSoup(front_side, 'html.parser')
            

        elements = soup.find_all(class_= "card-text-type-line")
        if elements != []:
            element = elements[0]
            abbr_tag = element.find('abbr')
            if abbr_tag != None:
                abbr_tag.extract()
            self.type = element.get_text().strip()
        
        elements = soup.find_all(class_= "card-text-card-name")
        if elements != []:
            self.name = elements[0].get_text().strip()

        elements = soup.find_all(class_ = "card-text-mana-cost")
        if elements != []:

            cmc = elements[0].get_text().replace("{","").replace("}","")
            self.cmc = cmc

        elements = soup.find_all(class_= "card-text-stats")
        if elements != []:
            if len(elements[0].get_text().strip().split("/")) == 2:
                self.power, self.toughness = elements[0].get_text().strip().split("/")
        
        elements = soup.find_all(class_= "card-text-oracle")
        if elements != []:
            self.oracle = elements[0].get_text().strip()
        
        

    def __str__(self):
        if self.back_side == None:
            return f"""Name : {self.name}
Type : {self.type}
CMC : {self.cmc}
Oracle : {self.oracle}
Power : {self.power}
Toughtness : {self.toughness}"""

        return """This is a Double faced card
\*\*Front Side
"""+f"""Name : {self.name}
Type : {self.type}
CMC : {self.cmc}
Oracle : {self.oracle}
Power : {self.power}
Toughtness : {self.toughness}"""+"""

\*\*Back Side
"""+str(self.back_side)
    
def ask_chatgpt(prom, model = "gpt-3.5-turbo", messages = None):
    openai.api_key = os.environ['OPENAI_API_KEY']

    if messages == None:
        messages = [{'role': 'user', 'content': prom}]

    response = openai.ChatCompletion.create(
                    model= model,
                    messages= messages,
                    temperature=0.0,
    )
    return(response.choices[0].message.content)

async def onechan_talk(message):
    nickname = message.author.nick if message.author.nick else message.author.name

    charsetting = base_char + """私を{}と呼ぶ。""".format(nickname)
    message_to_onechan = message.content
    try:
        conn = await asyncpg.connect(DATABASE_URL)

        rows = await conn.fetch('''
            SELECT * FROM one_memory
            WHERE channel_id = $1
            ORDER BY timestamp DESC 
            LIMIT 3
            ''', message.channel.id )

        messages = [{"role": "system", "content": charsetting}]

        while rows:
            row = rows.pop()
            messages += [{"role":"user", "content":row["user_message"]},{"role":"assistant", "content":row["assistant_message"]}]

        messages.append({"role": "user", "content": message_to_onechan})
        #print(messages)
        replay = ask_chatgpt(message, model="gpt-4", messages= messages)
        await message.channel.send(replay)
        await conn.execute("""
            INSERT INTO one_memory (user_id, channel_id, user_message, assistant_message) 
            VALUES ($1, $2, $3, $4)""",
            message.author.id, message.channel.id, message.content, replay) 

    except Exception as e:
        print(f"Error: {e}")
        await message.channel.send("ごめんね、今ちょっと答えられないの。また後で話してね！")
    finally:
        await conn.close()

async def create_tweet(message, img_url = None):
    try:
        CONSUMER_KEY = os.environ['CONSUMER_KEY']
        CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
        ACCESS_KEY = os.environ['ACCESS_TOKEN']
        ACCESS_SECRET = os.environ['ACCESS_SECRET']
        client = tweepy.Client(
            consumer_key = CONSUMER_KEY,
            consumer_secret = CONSUMER_SECRET,
            access_token = ACCESS_KEY,
            access_token_secret = ACCESS_SECRET)
        if img_url:
            auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
            api = API(auth)
            response = requests.get(img_url)
            img_format = "png"
            if "jpg" in img_url:
                img_format = "jpg"
            print(img_format)
            filename = f'temp.{img_format}'
            with open(filename, 'wb') as image_file:
                image_file.write(response.content)
            media = api.media_upload(filename = filename)
            client.create_tweet(text=message, media_ids=[media.media_id])
            os.remove(filename)
        else:
            client.create_tweet(text=message)
    except Exception as e:
        print(e)

async def db_fetch(ctx, query):
    #ToDo:discordの入力制限を超えた場合の処理を追加する
    pool = await asyncpg.create_pool(DATABASE_URL)
    async with pool.acquire() as conn:
        rows = await conn.fetch(query)
        fetched_data = """"""
        if not rows:
            fetched_data = """no data found"""
        for i, row in enumerate(rows):
            fetched_data += ",".join(map(str,row)) + "\n"
            if i > 9:
                fetched_data += "and more\n"
                break
        await ctx.send(fetched_data)
    await pool.close()
    #del rows, pool, fetched_data
    

async def set_reminder(ctx, remind_date, remind_time,event):
    try:
        now = datetime.now()

        if '-' in remind_date and len(remind_date.split('-')) == 2:
            remind_date = f"{now.year}-{remind_date}"

        remind_datetime_str = f"{remind_date} {remind_time}"
        remind_datetime = parse(remind_datetime_str,default=datetime(now.year, now.month, now.day))
    except ValueError:
        await ctx.send("Invalid date and time format. Please use 'YYYY-MM-DD HH:MM:SS'.")
        return

    jst_tz = pytz.timezone('Asia/Tokyo')
    remind_time = jst_tz.localize(remind_datetime)
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            INSERT INTO reminders (channel_id, user_id, event, remind_time)
            VALUES ($1, $2, $3, $4)
        """, ctx.channel.id, ctx.author.id, event, remind_time) 
        await ctx.send(f"'{event}' を {remind_datetime} JSTにリマインドするね")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("error")
    finally:
        await conn.close()

async def set_timed_tweet(ctx, tweet_date, tweet_time, content, post_message = True):
    try:
        now = datetime.now()

        if '-' in tweet_date and len(tweet_date.split('-')) == 2:
            tweet_date = f"{now.year}-{tweet_date}"

        tweet_datetime_str = f"{tweet_date} {tweet_time}"
        tweet_datetime = parse(tweet_datetime_str,default=datetime(now.year, now.month, now.day))
    except ValueError:
        await ctx.send("Invalid date and time format. Please use 'YYYY-MM-DD HH:MM:SS'.")
        return

    jst_tz = pytz.timezone('Asia/Tokyo')
    tweet_time = jst_tz.localize(tweet_datetime)
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            INSERT INTO tweets (content, tweet_time)
            VALUES ($1, $2)
        """, content, tweet_time) 
        if post_message:
            await ctx.send(f"'{content}' って {tweet_datetime} JSTにツイートするよ")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("error")
    finally:
        await conn.close()

async def create_db():
    async with asyncpg.create_pool(DATABASE_URL) as pool:
        async with pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                channel_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                event TEXT NOT NULL,
                remind_time TIMESTAMP WITH TIME ZONE NOT NULL
            )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS tweets (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                tweet_time TIMESTAMP WITH TIME ZONE NOT NULL
            )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS htmls (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                html TEXT NOT NULL,
                time TIMESTAMP NOT NULL
            )
            """)


            await conn.execute("""
                CREATE TABLE IF NOT EXISTS one_memory (
                    id SERIAL PRIMARY KEY,
                    user_id bigint NOT NULL,
                    channel_id bigint NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    user_message TEXT,
                    assistant_message TEXT
            )
            """)
"""
async def insert_html(url,post_message = False):
    print(1)
    checked_time = datetime.now()
    driver = webdriver.Chrome('/path/to/chromedriver')
    print(2)

    options = Options()
    options.add_argument("--headless")  # Ensure GUI is off
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    print(3)
    driver = webdriver.Chrome('/path/to/chromedriver', chrome_options=options)
    driver.get(url)
    html = driver.page_source
    print(4)
    driver.quit()
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(\"""
            INSERT INTO htmls (url, html, time)
            VALUES ($1, $2, $3)
        \""", url, html, checked_time) 
        if post_message:
            pass#await ctx.send(f"'{content}' って {tweet_datetime} JSTにツイートするよ")
    except Exception as e:
        print(f"Error: {e}")
        #await ctx.send("error")
    finally:
        await conn.close()
"""

async def check_reminders(bot):
    pool = await asyncpg.create_pool(DATABASE_URL)
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM reminders WHERE remind_time <= $1", datetime.utcnow())
            for row in rows:
                data_id, channel_id, user_id, event, remind_time = row
                channel = bot.get_channel(channel_id)
                user = await bot.fetch_user(user_id)
                await channel.send(f"{user.mention}、 {event}を忘れないようにね")
                await conn.execute("DELETE FROM reminders WHERE id = $1", data_id)
    except Exception as e:
        print("error in check_reminders:" + e)
    finally:
        await pool.close()

async def set_daily_tweets(ctx, starting_date, starting_time, message):
    try:
        now = datetime.now()

        if '-' in starting_date and len(starting_date.split('-')) == 2:
            starting_date = f"{now.year}-{starting_date}"

        starting_datetime_str = f"{starting_date} {starting_time}"
        starting_tweet_datetime = parse(starting_datetime_str)
    except ValueError:
        await ctx.send("Invalid date and time format. Please use 'YYYY-MM-DD HH:MM:SS'.")
        return
    message = message.split("\n")
    tweets = []
    tweet = """"""
    for line in message:
        if line:
            tweet += line + "\n"
        else:
            if tweet == """""":
                continue
            tweet_datetime = starting_tweet_datetime + timedelta(days= len(tweets), minutes = 30 -random.randint(0,60))
            jst_tz = pytz.timezone('Asia/Tokyo')
            tweet_datetime_utc = jst_tz.localize(tweet_datetime)
            tweets.append([tweet_datetime_utc,tweet])
            tweet = """"""
    if not tweet == """""":
        tweet_datetime = starting_tweet_datetime + timedelta(days= len(tweets), minutes = 30 -random.randint(0,60))
        jst_tz = pytz.timezone('Asia/Tokyo')
        tweet_datetime_utc = jst_tz.localize(tweet_datetime)
        tweets.append([tweet_datetime_utc,tweet])
    for booked_time, booked_tweet in tweets:
            try:
                conn = await asyncpg.connect(DATABASE_URL)
                await conn.execute("""
                    INSERT INTO tweets (content, tweet_time)
                    VALUES ($1, $2)
                """, booked_tweet, booked_time) 
            except Exception as e:
                print(f"Error: {e}")
            finally:
                await conn.close()
    if len(tweets) > 5:
        tweets = str(tweets[:5]) + "\n\nand more"
    await ctx.send("以下の内容で予約したよ　不安ならtweetsデータベースで確認してね\n" + str(tweets))

async def check_tweets(bot):
    pool = await asyncpg.create_pool(DATABASE_URL)
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tweets WHERE tweet_time <= $1", datetime.utcnow())
            for row in rows:
                data_id, content, tweet_time = row
                create_tweet(content)
                await conn.execute("DELETE FROM tweets WHERE id = $1", data_id)
    except Exception as e:
        print("error in check_tweets:" + e)
    finally:
        await pool.close()

async def db_execute(ctx, query):
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(query) 
        await ctx.send("successfully executed")
    except Exception as e:
        print(f"Error: {e}")
        await ctx.send("error occured")
    finally:
        await conn.close()

async def create_pie_chart(ctx, message):
    message = message.replace("　"," ")
    x, labels = [], []
    args = ""
    for data_for_pie in message.split("\n"):
        if not data_for_pie:
            continue
        if data_for_pie.split(" ",1)[0] == "args":
            args = data_for_pie.split(" ",1)[1]
            continue
        label, num = data_for_pie.strip().split()
        num = float(num)
        x.append(num)
        labels.append(label)
    plt_command = f"plt.pie(x, labels=labels,{args})"
    with io.BytesIO() as image_binary:
        exec(plt_command)
        plt.savefig(image_binary, format='png')
        image_binary.seek(0)

        plt.clf()
        discord_file = discord.File(fp=image_binary, filename='plot.png')
        await ctx.send(file=discord_file)

async def create_plot(ctx, message):
    message = message.replace("　"," ")
    x, y = [], []
    args = ""
    for data_for_pie in message.split("\n"):
        if not data_for_pie:
            continue
        if data_for_pie.split(" ",1)[0] == "args":
            args = data_for_pie.split(" ",1)[1]
            continue
        x_i, y_i = map(float, data_for_pie.strip().split())
        x.append(x_i)
        y.append(y_i)
    plt_command = f"plt.plot(x,y,{args})"
    print(plt_command)

    with io.BytesIO() as image_binary:
        exec(plt_command)
        plt.savefig(image_binary, format='png')
        image_binary.seek(0)

        plt.clf()
        discord_file = discord.File(fp=image_binary, filename='plot.png')
        await ctx.send(file=discord_file)
    
async def compare_functions(ctx, message):
    message = message.replace("　"," ").split("\n")
    try:
        plot_range = message[0]
        funcs = message[1:]
    except Exception as e:
        await ctx.send("一行目に描画範囲、二行目以降に描画したいxの関数を入れてね")
        return
    try:
        plot_range = plot_range.split("-")
        if len(plot_range) == 2:
            start, end = map(int, plot_range)
            plot_range = range(start, end)
        else:
            start, end, step = map(int, plot_range)
            plot_range = [start + i * (end - start)//step for i in range(step)]

    except Exception as e:
        await ctx.send(e)
        await ctx.send("描画範囲は（開始する値: 整数）-（収量する値: 整数）あるいは（開始する値）-（終了する値）-（プロット数）の形式で入れてね")
        return
    
    
    for func in funcs:
        try:
            y = []
            for x in plot_range:
                y.append(eval(func))
            plt.plot(list(plot_range), y, label = func)
        except Exception as e:
            await ctx.send(e)
            await ctx.send("描画する関数はpythonでxに値を代入すれば計算できる形で入力してね")
    plt.legend()
    with io.BytesIO() as image_binary:
        plt.savefig(image_binary, format='png')
        image_binary.seek(0)

        plt.clf()
        discord_file = discord.File(fp=image_binary, filename='plot.png')
        await ctx.send(file=discord_file)

async def daily_greeting_card():
    delay = random.randint(0,10)
    time.sleep(delay*60)
    try:
        all_cards = list(url_dict)
        random.shuffle(all_cards)
        card_name = all_cards[0]
        card_to_suggest = url_dict[card_name]
        image_url = card_to_suggest["image_url"]
        japanese_name = card_to_suggest["printed_name"]
        prompt = card_comment_prompt + f"今日のカードは{japanese_name}です！"
        onechan_comment = ask_chatgpt(prompt)
        onechan_comment = onechan_comment.replace("「","").replace("」","")
        onechan_comment = f"おはようございます！今日のカードは{japanese_name}です！\n" + onechan_comment
        await create_tweet(onechan_comment,image_url)
    except Exception as e:
        print(e)

async def python_run(ctx, code):
    if False:#"import os" in code or "import sys" in code:
        await ctx.send("安全のため、特定のモジュールのインポートは禁止されています。")
        return
    
    # コードの実行と標準出力のキャプチャ
    #str_stdout = io.StringIO()

    """try:
        with contextlib.redirect_stdout(str_stdout):
            exec(code, {"__builtins__": {}}, {})
    except Exception as e:
        await ctx.send(f"エラーが発生したよ: {e}")
        return"""
    
    # 標準出力を置き換えるためのStringIOオブジェクトを作成
    output = io.StringIO()
    # 元のstdoutを保存
    old_stdout = sys.stdout
    sys.stdout = output
    try:
        # 関数を実行
        exec(code)
        captured_output = output.getvalue()
        await ctx.send(f"実行結果:\n{captured_output}")
    except Exception as e:
        await ctx.send(f"エラーが発生したよ: {e}")    
    finally:

        # stdoutを元に戻す
        sys.stdout = old_stdout

        # 出力を取得
        

        # 出力をクリーンアップ
        output.close()

    

async def daily_greeting_card_test():
    delay = random.randint(0,5)
    time.sleep(delay)
    try:
        all_cards = list(url_dict)
        random.shuffle(all_cards)
        card_name = all_cards[0]
        card_to_suggest = url_dict[card_name]
        image_url = card_to_suggest["image_url"]
        japanese_name = card_to_suggest["printed_name"]
        prompt = card_comment_prompt_base + f"こんばんは！遅くなりましたが今日のカードは{japanese_name}です！"
        onechan_comment = ask_chatgpt(prompt)
        onechan_comment = onechan_comment.replace("「","").replace("」","")
        onechan_comment = f"こんばんは！遅くなりましたが今日のカードは{japanese_name}です！\n" + onechan_comment
        await create_tweet(onechan_comment,image_url)
    except Exception as e:
        print(e)