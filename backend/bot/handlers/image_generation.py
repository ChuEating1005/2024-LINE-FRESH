import requests
from openai import OpenAI
from PIL import Image as PILImage
import os
import io
import firebase_admin
from firebase_admin import credentials, storage
from ..models import Article, Image
from django.conf import settings
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

api_key = settings.OPENAI_API_KEY
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

def get_image_v2(prompt, article_id, image_number):
    try:
        url = "https://api.openai.com/v1/images/generations"
        article = Article.objects.get(id=article_id)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024"
        }
        
        # 添加重試機制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=data)
                
                if response.status_code == 200:
                    response_json = response.json()
                    image_url = response_json["data"][0]["url"]
                    image_response = requests.get(image_url)
                    
                    if image_response.status_code == 200:
                        image_name = f"{article_id}/{image_number}.jpg"
                        img = PILImage.open(io.BytesIO(image_response.content))
                        
                        # 使用線程鎖確保安全的文件操作
                        with threading.Lock():
                            image_url = upload_image(img, image_name)
                            Image.objects.create(article=article, number=image_number, image_url=image_url)
                        return True
                    
                break  # 如果成功就跳出重試循環
                
            except Exception as e:
                if attempt == max_retries - 1:  # 最後一次嘗試
                    raise e
                print(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(1)  # 重試前等待
                
    except Exception as e:
        print(f"Failed to generate image for prompt '{prompt}'. Error: {str(e)}")
        raise e
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
        {"role": "user", "content": f"""請將以下文章內容轉換成三個完整的場景描述，每個場景都要能夠作為生成圖片的提示。
        描述風格要求：
        - 場景要具體且富有畫面感
        - 使用宮崎駿動畫風格 (Studio Ghibli style) 等卡通畫風
        - 每個場景描述控制在30字左右
        - 避免描述人物的具體動作，著重於場景氛圍

        請依序生成以下三個場景：
        ###引言
        ###發展
        ###結局

        原始文章內容：
        {article_content}

        請用以下格式回覆：
        ```
        第一行：引言場景描述
        第二行：發展場景描述
        第三行：結局場景描述
        ```
        每行用換行符號隔開
        """}
    ]
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(model="gpt-4o", messages=messages)
    text = completion.choices[0].message.content
    paragraphs = [p for p in text.split('\n') if len(p) >= 10]  # Remove empty lines and short strings
    paragraphs = paragraphs[:3]
    print(paragraphs)

    # 使用 ThreadPoolExecutor 並行生成圖片
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 創建任務列表
        future_to_paragraph = {
            executor.submit(get_image_v2, paragraph, article_id, idx + 1): (idx + 1, paragraph)
            for idx, paragraph in enumerate(paragraphs)
        }

        # 等待所有任務完成並處理結果
        for future in as_completed(future_to_paragraph):
            image_number, paragraph = future_to_paragraph[future]
            try:
                future.result()  # 獲取執行結果
                print(f"Successfully generated image {image_number}")
            except Exception as e:
                print(f"Error generating image {image_number}: {str(e)}")

def upload_image(img, image_name):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG', quality=95)
    img_byte_arr = img_byte_arr.getvalue()

    bucket = storage.bucket()
    blob = bucket.blob(f'images/{image_name}')
    blob.upload_from_string(img_byte_arr, content_type='image/jpeg')
    blob.make_public()
    return blob.public_url
