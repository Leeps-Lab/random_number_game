from PIL import Image, ImageDraw, ImageFont
import math

def writeText(text, fileName):
    """"
    This method generates the image version of an inputted text
    and saves it to fileName
    
    Input: text to be transcripted into the image, name of the output img file
    Output: None
    """

    image = Image.open('random_number_game/background.png')
    image = image.resize((250, 50))
    image.save('random_number_game/background.png')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('random_number_game/Roboto-Regular.ttf', size=19)
    imageChars = 100
    numLines = len(text) / imageChars
    numLines = math.ceil(numLines)
    lines = []

    for i in range(numLines):
        if(imageChars * (i + 1) < len(text)):
            lines.append(text[imageChars * i : imageChars * (i+1)])
        else:
            lines.append(text[imageChars * i : len(text)])

    for i in range(numLines):
        (x, y) = (10, 20 * i)
        message = lines[i]
        print("Message is: ", message)
        color = 'rgb(0, 0, 0)' # black color
        draw.text((x, y), message, fill=color, font=font)

    image.save(fileName) # stores the image on a specified folder
