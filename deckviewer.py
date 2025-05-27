import shutil
import requests
from PIL import Image, ImageDraw, ImageFont
import os
import discord
from discord.ext import commands
import asyncio
import asyncpg
import io
import re
from io import BytesIO

def draw_text(draw, text, position, font, max_width):
    #与えられた最大幅を考慮してテキストを描画し、使用した高さを返す。

    char_width = max_width / 30  # この値は適切に調整する必要があります

    lines = []
    words = text.split()
    while words:
        line = ''
        while words and len(line + words[0]) * char_width <= max_width:
            line += (words.pop(0) + ' ')
        lines.append(line)

    y_text = position[1]
    for line in lines:
        height = 20  # テキストの高さの近似。'A'の高さを取得
        # テキストを描画
        draw.text(((max_width - len(line) * char_width) / 2, y_text), line, font=font, fill="black")
        y_text += height
    return y_text - position[1]


def create_image_with_text(text, image_size, font_path=None):
    # 新しい白い画像を作成
    img = Image.new('RGB', image_size, color='white')
    d = ImageDraw.Draw(img)

    # フォントを選択
    if font_path:
        font = ImageFont.truetype(font_path, 15)
    else:
        font = ImageFont.load_default()

    # テキストを描画
    draw_text(d, text, (10, 10), font, image_size[0] - 20)

    return img

def concat_images(img_list,img_side_list, grid):
    #画像リストを指定されたグリッドサイズに基づいて結合する
    bg_color = (120, 120, 120)  # 任意の背景色（この場合は白）

    # グリッドサイズを取得
    rows, cols = grid

    width = max([img[1].width for img in img_list]) * cols
    height = max([img[1].height for img in img_list]) * rows

    dst = Image.new('RGB', (int(width), int(height)), bg_color)


    # メインの画像を並べる
    for i, nimg in enumerate(img_list):
        number, img = nimg
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("Roboto-Black.ttf",30) 

        # テキストのサイズを取得
        text_width, text_height = 20,20

        # 画像のサイズを取得
        img_width, img_height = img.size


        # テキストの位置を計算
        x = img_width - text_width - 10  # 5はマージンとして追加
        y = img_height - text_height - 15

        # 白い背景の枠を描画
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+10], fill="white")  # 5は枠のマージンとして追加

        # 黒い番号を描画
        if int(number) >= 10:
            draw.text((x-8, y), str(number), fill="black", font=font)
        else:
            draw.text((x, y), str(number), fill="black", font=font)
        x_offset = (i % cols) * max([img[1].width for img in img_list])
        y_offset = (i // cols) * max([img[1].height for img in img_list])
        dst.paste(img, (x_offset, y_offset))

    
    #サイドの画像を並べる
    for i, nimg in enumerate(img_side_list):
        number, img = nimg
        draw = ImageDraw.Draw(img)

        # フォントを選択
        # ここではPillowのデフォルトフォントを使用しますが、カスタムフォントを使用することも可能です。
        ImageFont.load_default() # フォントサイズは適宜調整してください

        # テキストのサイズを取得
        text_width, text_height = 20,20

        # 画像のサイズを取得
        img_width, img_height = img.size

        # テキストの位置を計算
        x = img_width - text_width - 10  # 10はマージンとして追加
        y = img_height - text_height - 15

        # 白い背景の枠を描画
        draw.rectangle([x-5, y-5, x+text_width+5, y+text_height+10], fill="white")  # 5は枠のマージンとして追加

        # 黒い番号を描画
        if int(number) >= 10:
            draw.text((x-8, y), str(number), fill="black", font=font)
        else:
            draw.text((x, y), str(number), fill="black", font=font)
        x_offset = (i % cols) * max([img[1].width for img in img_list])
        y_offset = int(((i // cols) + (len(img_list) -1 )//cols + 1.15)  * max([img[1].height for img in img_list]))
        dst.paste(img, (x_offset, y_offset))

    return dst

def get_card_info(card_name):
    base_url = "https://api.scryfall.com/cards/named"
    response = requests.get(base_url, params={"exact": card_name})

    if response.status_code == 200:
        return response.json()
    else:
        print("Error:", response.status_code)
        return None

def download_image(image_url, output_path):
    response = requests.get(image_url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def get_imgfiles(deck, sort_by = "mv" ):
    deck_dict = dict()
    for n, x in deck:
        if not x in deck_dict:
            deck_dict[x] = n
        else:
            deck_dict[x] += n
            
    deck = [[deck_dict[k],k] for k in deck_dict]

    cmc_dict = dict()
    res = []
    for n, x in deck:
        card_info = get_card_info(x)

        sort_rate = -n/1000

        if card_info == None:
            sort_rate -= 1000
        else:
            if "type_line" in card_info:
                if "Land" in card_info["type_line"].split("//")[0]:
                    sort_rate += 1000
            if "cmc" in card_info:
                sort_rate += card_info["cmc"] 
        if sort_by == "color":
            color_con = 1000000
            if card_info == None:
                sort_rate += 10000*color_con
            elif not "colors" in card_info:
                sort_rate += 10000*color_con
            else:
                colors = card_info["colors"]
                if len(colors) == 0:
                    sort_rate += 10000 * color_con
                if len(colors) > 1:
                    sort_rate += 100 * color_con
                if "W" in colors:
                    sort_rate += 1 * color_con
                if "U" in colors:
                    sort_rate += 2 * color_con
                if "B" in colors:
                    sort_rate += 3 * color_con
                if "R" in colors:
                    sort_rate += 4 * color_con
                if "G" in colors:
                    sort_rate += 5 * color_con


        cmc_dict[x] = sort_rate

        res.append([n, x, card_info])

    deck = sorted(res, key =lambda x: cmc_dict[x[1]])

    deck_images = []
    for n, x,card_info in deck:
        if card_info:
            if "image_uris" in card_info:
                image_url = card_info['image_uris']['small']
            else:
                image_url = card_info["card_faces"][0]["image_uris"]["small"]
            response = requests.get(image_url)
            card_img = Image.open(BytesIO(response.content))
        else:
            card_img = create_image_with_text(x,[146,204])
        deck_images.append([n, card_img])

    return deck_images

async def show_deckimg(ctx, import_list):
    try:
        message = await ctx.send("in progress...")
        import_list = import_list.split("\n")

        #各行のカッコ以降削除
        pattern = r"\s+\(\w+\)\s+\d+"
        import_list = [re.sub(pattern, "", line) for line in import_list]
        main_deck, sideboard = [],[]
        list_to_add = main_deck
        for card in import_list:
            if card == "Sideboard" or (card == "" and len(main_deck) > 0):
                list_to_add = sideboard
                if len(main_deck) == 1 and "Companion" in import_list:
                    main_deck = []
                    list_to_add = main_deck
            if len(card.split(" ")) > 1:
                n_card, card_name = card.split(" ",1)
                if n_card.isdecimal():
                    list_to_add.append([int(n_card,), card_name])
        main_cardimgs = get_imgfiles(main_deck, sort_by = "mv")
        side_cardimgs = get_imgfiles(sideboard, sort_by = "color")  

        result_img = concat_images(main_cardimgs, side_cardimgs, ((len(main_cardimgs)-1) // 10  + max(0, (len(side_cardimgs)-1)//10) + 2.15, 10))
        with io.BytesIO() as output:
            result_img.save(output, format="PNG")
            output.seek(0)
            await ctx.send(file=discord.File(output, 'image.png'))
        await message.edit(content = "done")
    except Exception as e:
        print(e)
