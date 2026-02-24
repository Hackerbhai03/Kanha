import os
import re
import aiohttp
import aiofiles
from config import YOUTUBE_IMG_URL
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from py_yt import VideosSearch


def clear(text):
    return re.sub(r"\s+", " ", text).strip()


async def gen_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    try:
        # 🔍 Search using video ID
        results = VideosSearch(videoid, limit=1)
        data = await results.next()

        if not data["result"]:
            return YOUTUBE_IMG_URL

        result = data["result"][0]

        title = result.get("title", "Unsupported Title")
        title = clear(title)

        duration = result.get("duration", "Unknown")
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")

        # 📥 Download thumbnail
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status != 200:
                    return YOUTUBE_IMG_URL

                async with aiofiles.open(f"cache/thumb{videoid}.png", "wb") as f:
                    await f.write(await resp.read())

        youtube = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")

        # 🎨 Background blur
        background = youtube.resize((1280, 720)).filter(
            ImageFilter.GaussianBlur(radius=15)
        )
        background = ImageEnhance.Brightness(background).enhance(0.5)

        draw = ImageDraw.Draw(background)

        # 🎬 Center thumbnail
        center_thumb = youtube.resize((942, 422))

        border_size = 10
        bordered = Image.new(
            "RGBA",
            (center_thumb.width + border_size * 2,
             center_thumb.height + border_size * 2),
            (255, 255, 255)
        )
        bordered.paste(center_thumb, (border_size, border_size))

        pos_x = (1280 - bordered.width) // 2
        pos_y = (720 - bordered.height) // 2 - 40

        background.paste(bordered, (pos_x, pos_y))

        # 🔤 Load Fonts (Safe Mode)
        try:
            font = ImageFont.truetype("AviaxMusic/assets/font.ttf", 32)
            small_font = ImageFont.truetype("AviaxMusic/assets/font2.ttf", 28)
            bold_font = ImageFont.truetype("AviaxMusic/assets/font.ttf", 35)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
            bold_font = ImageFont.load_default()

        # 🏷 Watermark
        draw.text((1100, 20), "", fill="yellow", font=font)

        # 📌 Channel & Views
        draw.text(
            (60, 570),
            f"{channel} | {views}",
            fill="white",
            font=small_font
        )

        # 🎵 Title (limit long titles)
        if len(title) > 60:
            title = title[:57] + "..."

        draw.text(
            (60, 610),
            title,
            fill="white",
            font=font
        )

        # ⏳ Duration Line
        draw.text((60, 650), "00:00", fill="white", font=bold_font)
        draw.line([(150, 665), (1130, 665)], fill="white", width=4)
        draw.text((1145, 650), duration, fill="white", font=bold_font)

        # 🗑 Remove temp file
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass

        background.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"

    except Exception as e:
        print("Thumbnail Error:", e)
        return YOUTUBE_IMG_URL


