import random

# 🔥 Tumhare diye hue images
RANDOM_THUMBS = [
      "https://files.catbox.moe/a6hzmb.jpg",
    "https://files.catbox.moe/ohezme.jpg",
    "https://files.catbox.moe/spylio.jpg",
    "https://files.catbox.moe/5go4t6.jpg",
    "https://files.catbox.moe/ikxb96.jpg",
    
]

_last_thumb = None

async def gen_thumb(videoid=None):  # videoid ignore
    global _last_thumb

    try:
        choice = random.choice(RANDOM_THUMBS)

        # ❌ same image repeat na ho
        while choice == _last_thumb and len(RANDOM_THUMBS) > 1:
            choice = random.choice(RANDOM_THUMBS)

        _last_thumb = choice
        return choice

    except Exception as e:
        print(e)
        return RANDOM_THUMBS[0]
