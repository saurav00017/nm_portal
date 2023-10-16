from textwrap import TextWrapper
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import qrcode
import os

"""
{ 
    "Branch": "B.E Civil Engineering", 
    "RollNo": "812720103331", 
    "FullName": "MANIKANDAPRABHU R", 
    "CourseName": "Building Information Modelling in Architecture, Engineering and Construction", 
    "CollegeName": "MEENAKSHI RAMASWAMY ENGINEERING COLLEGE", 
    "PartnerName": "L&T EduTech", 
    "StudentName": "MANIKANDAPRABHU R", 
    "dateOfIssue": "10/01/2023", "CertificateNo": "NM23AU00009811"}
"""
course_name = "High Rise Buildings"
training_partner_name = "L&T EduTech"
certificate_no = "NM23AU00009811"
date = "10/01/2023"
name = "MANIKANDAPRABHU R"
college_name = "MEENAKSHI RAMASWAMY ENGINEERING COLLEGE"
branch_name = "B.E Civil Engineering"
reg_no = "812720103331"
partner_logo_url = "https://api.naanmudhalvan.tn.gov.in/media/images/edutech_logo_lwcndrm.png"

# Open the image
image = Image.open('certificate2.png')

# Create an ImageDraw object
draw = ImageDraw.Draw(image)

# Choose a font and a font size
font = ImageFont.truetype('Cardo/Cardo-Regular.ttf', 60)
font_bold = ImageFont.truetype('Cardo/Cardo-Bold.ttf', 70)
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
draw.multiline_text((x, 1500), text, font=font, fill=(0, 0, 0), align="center", spacing=40)

draw.text((720, 1050), name, font=font_bold, fill=(0, 0, 0))
draw.text((2180, 1050), reg_no, font=font_bold, fill=(0, 0, 0))

draw.text((720, 1200), branch_name, font=font_bold, fill=(0, 0, 0))
draw.text((900, 1340), college_name, font=font_bold, fill=(0, 0, 0))

draw.text((120, 450), certificate_no, font=font_bold_60, fill=(0, 0, 0))

draw.text((480, image.height - 205), date, font=font_bold_60, fill=(0, 0, 0))

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

image.paste(img_qr, (image.width - 350, 550))
image.paste(partner_logo, (image.width - 400, 150), partner_logo)

# Partner Signature
partner_signature = Image.open('partner_sign.png')
image.paste(partner_signature, (1200, image.height - 300), partner_signature)
# MD Mam Signature
partner_signature = Image.open('md_mam.png')
partner_signature.thumbnail((250, 250), Image.Resampling.LANCZOS)
image.paste(partner_signature, (image.width-550, image.height - 350), partner_signature)


# Save the image
rgb_image = image.convert('RGB')
rgb_image.thumbnail((2000,2000), Image.Resampling.LANCZOS)


rgb_image.save(f'{certificate_no}.jpg', "JPEG", optimize=True, quality=80)