from textwrap import TextWrapper
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import qrcode
import os

course_name = "Python Programming"
training_partner_name = "Naan Mudhalvan Program"
certificate_no = "NMG1003873"
date = "12/12/2020"
name = "Sathish Kumar"
reg_no = "8276352AS726"
partner_logo_url = "https://naanmudhalvan.tn.gov.in/images/patners/aws.png"

# Open the image
image = Image.open('certificate.png')

# Create an ImageDraw object
draw = ImageDraw.Draw(image)

# Choose a font and a font size
font = ImageFont.truetype('Cardo/Cardo-Regular.ttf', 60)
font_bold = ImageFont.truetype('Cardo/Cardo-Bold.ttf', 80)
font_bold_60 = ImageFont.truetype('Cardo/Cardo-Bold.ttf', 60)

# Certificate Content
# Set the margins
left_margin = 50
right_margin = 50
top_margin = 50
bottom_margin = 50

text = f"For the successful completion of {course_name} sponsored by Naan Mudhalvan Program,\nTamilnadu Skill Development Corporation and conducted by {training_partner_name}.\nDuring the course, the learner demonstrated initiative and commitment to advance in their career."
text_width, text_height = draw.textsize(text, font=font)


# # Calculate the position of the text
x = (image.width - text_width) / 2
y = (image.height - text_height) / 2
# # Draw the text on the image
draw.multiline_text((x, 1400), text, font=font, fill=(0, 0, 0), align="center", spacing=40)

draw.text((700, 1080), name, font=font_bold, fill=(0, 0, 0))

draw.text((2040, 1080), reg_no, font=font_bold, fill=(0, 0, 0))

draw.text((640, 500), certificate_no, font=font_bold_60, fill=(0, 0, 0))

draw.text((1540, image.height - 150), date, font=font_bold_60, fill=(0, 0, 0))

# draw Image from url partner_logo_url
response = requests.get(partner_logo_url)
partner_logo = Image.open(BytesIO(response.content))
# resize partner logo aspect ratio with 300px
maxsize = (300, 300)
partner_logo.thumbnail(maxsize, Image.Resampling.LANCZOS)


qr = qrcode.QRCode(box_size=5)
qr.add_data('portal.naanmudhalvan.tn.gov.in/validate/certificate/4379t7bt8c487vbs87tr63rtvr')
qr.make()
img_qr = qr.make_image()

image.paste(img_qr, (150, 600))

image.paste(partner_logo, (image.width - 400, 200), partner_logo)
# Save the image
rgb_image = image.convert('RGB')
rgb_image.thumbnail((2000,2000), Image.Resampling.LANCZOS)
rgb_image.save(f'{certificate_no}.jpg', "JPEG", optimize=True, quality=80)