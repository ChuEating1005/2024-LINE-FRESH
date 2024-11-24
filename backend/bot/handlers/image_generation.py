import requests
from openai import OpenAI
from PIL import Image as PILImage
import os
import io
import firebase_admin
from firebase_admin import credentials, storage
from ..models import Article, Image
from django.conf import settings

api_key = "sk-rH5ykGCX5PY9x2gJ4o94vVSIcDwBlaL9dTNtNReuOeNC0boi"
project_id = settings.FIREBASE_PROJECT_ID
private_key = settings.FIREBASE_PRIVATE_KEY.replace("\\n", "\n")
client_email = settings.FIREBASE_CLIENT_EMAIL
storage_bucket = settings.FIREBASE_STORAGE_BUCKET
# Initialize Firebase
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": project_id,
    "private_key": private_key,
    "client_email": client_email,
    "token_uri": "https://oauth2.googleapis.com/token",
})

firebase_admin.initialize_app(cred, {
    'storageBucket': storage_bucket
})

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_image(prompt, article_id, image_number):
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    article = Article.objects.get(id=article_id)
    response = requests.get(url)

    image_name = f"{article_id}/{image_number}.jpg"
    if response.status_code == 200:
        img = PILImage.open(io.BytesIO(response.content))
        cropped_img = crop_image_bottom(img)
        image_url = upload_image(cropped_img, image_name)
        print(f"Image downloaded successfully as '{image_name}'")
        
        Image.objects.create(article=article, number=image_number, image_url=image_url)
        # # Crop image bottom
        # crop_image_bottom(image_name)
    else:
        print(f"Failed to get image for prompt '{prompt}'. Status code: {response.status_code}")

def crop_image_bottom(img):
    width, height = img.size
    cropped_height = height - 50  # Adjust this value based on your need
    if cropped_height > 0:
        img_cropped = img.crop((0, 0, width, cropped_height))
        return img_cropped
    else:
        print("Image is too small to crop")
        return img

def generate_images_from_text(article_id, article_content):
    create_directory("./result")

    messages = [
        {"role": "system", "content": "你是一位專業的圖像描述專家，擅長將文字轉換成宮崎駿風格的場景描述。請注意描述要具體且富有畫面感，但避免過多文字。"},
        {"role": "user", "content": f"""請將以下文章內容轉換成三個場景描述，每個場景都要能夠作為生成圖片的提示。
描述風格要求：
- 場景要具體且富有畫面感
- 使用宮崎駿動畫風格 (Studio Ghibli style)
- 每個場景描述控制在30字以內
- 避免描述人物的具體動作，著重於場景氛圍

請依序生成以下三個場景：
###引言
###發展
###結局

原始文章內容：
{article_content}

請用以下格式回覆：
```
第一行：[引言：場景描述]
第二行：[發展：場景描述]
第三行：[結局：場景描述]
```
每行用換行符號隔開
"""}
    ]
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.chatanywhere.tech/v1"
    )
    completion = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    text = completion.choices[0].message.content
    text = text.split('\n')[1:]  # Remove the first element if necessary
    print(text)

    image_number = 1
    for paragraph in text:
        get_image(paragraph, article_id, image_number)
        image_number += 1

def upload_image(cropped_img, image_name):
    img_byte_arr = io.BytesIO()
    cropped_img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr = img_byte_arr.getvalue()

    bucket = storage.bucket()
    blob = bucket.blob(f'images/{image_name}')
    blob.upload_from_string(img_byte_arr, content_type='image/jpeg')
    blob.make_public()
    return blob.public_url
