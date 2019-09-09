from PIL import Image, ImageDraw, ImageFont
import random

letters = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c',
           'v', 'b', 'n', 'm']


def _create_dots(image):
    d = ImageDraw.Draw(image)
    dimension_x, dimension_y = image.size
    count = 50

    while count:
        x1 = random.randint(0, dimension_x)
        y1 = random.randint(0, dimension_y)
        d.line(
            ((x1, y1), (x1 - 1, y1 - 1)),
            fill=(0, 0, 0),
            width=6
        )
        count -= 1
    return image


def _create_line(image):
    d = ImageDraw.Draw(image)
    for x in range(5):  # Make random lines
        w, h = image.size
        x1 = random.randint(0, int(w / 5))
        x2 = random.randint(w - int(w / 5), w)
        y1 = random.randint(int(h / 5), h - int(h / 5))
        y2 = random.randint(y1, h - int(h / 5))
        points = [x1, y1, x2, y2]
        end = random.randint(100, 300)
        start = random.randint(0, 150)
        d.arc(points, start, end, fill=(50, 50, 50))
    return image


def create_image(user_id):
    img = Image.new(
        'RGB',
        (300, 300),
        color=(80, 80, 80)  # Darker colour
    )

    d = ImageDraw.Draw(img)

    random_string = '  '.join(
        random.sample(letters, random.randint(6, 10))
    )
    x_coords = 0
    for x in range(len(random_string)):
        x_coords += 10
        font = ImageFont.truetype('assets/typewriter.ttf', random.randint(20, 35))
        d.text(
            (x_coords, random.randint(0, 200)),
            random_string[x],
            font=font,
            fill=(0, 0, 0)
        )
    # d.text(textLocation, randomString, font=font, fill=(0,0,0))

    _create_line(img)
    _create_dots(img)

    img.save(f'{user_id}.png')
    correct_text = ''.join(random_string.split())

    print(correct_text)
    return f"{user_id}.png", correct_text
