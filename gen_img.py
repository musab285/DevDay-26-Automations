# python script for generating appointment letter (png)


import imgkit 
from html_content import get_image_content
import datetime as dt

config = imgkit.config(wkhtmltoimage=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe")
options = {
        "enable-local-file-access": "",
        "encoding": "UTF-8"
}

def generate(name, position, team):
    # date = dt.datetime.now().strftime("%B %d, %Y")
    img = "C:/Users/ABC/Documents/DevDay-26-Automations/images/letterhead.jpeg"
    html = get_image_content("./extended-emails/pictemp.html", name, position, team, img)
    imgkit.from_string(html, "./images/final.png", config=config, options=options)

generate("Musab Ali", "Co-Head", "Automations")