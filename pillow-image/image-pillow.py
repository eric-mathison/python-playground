from PIL import Image, ImageFont, ImageDraw

def image_pillow(image, city, state):
    img = Image.open(image)
    font = ImageFont.truetype('./pillow-image/Workbar.ttf', 200)
    city_text = city
    state_text = state
    x = 100
    y = img.height - 400
    image_editable = ImageDraw.Draw(img)
    image_editable.text((x,y), city_text, (255, 255, 255), font=font)
    image_editable.text((x + 150,y + 180), state_text, (255, 255, 255), font=font)

    img.save("./pillow-image/result.jpg")

image = './pillow-image/chicago.jpg'
image_pillow(image, 'Chicago', 'Illinois')