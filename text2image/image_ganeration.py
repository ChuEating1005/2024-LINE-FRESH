import requests
from openai import OpenAI
from PIL import Image
import os

api_key = "sk-rH5ykGCX5PY9x2gJ4o94vVSIcDwBlaL9dTNtNReuOeNC0boi"

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_image(prompt, image_number):
    url = f"https://image.pollinations.ai/prompt/{prompt}"
    response = requests.get(url)

    if response.status_code == 200:
        filename = f"./result/{image_number}.jpg"
        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully as '{filename}'")
        
        # Crop image bottom
        crop_image_bottom(filename)
    else:
        print(f"Failed to get image for prompt '{prompt}'. Status code: {response.status_code}")

def crop_image_bottom(filename):
    with Image.open(filename) as img:
        width, height = img.size
        cropped_height = height - 50  # Adjust this value based on your need
        if cropped_height > 0:
            img_cropped = img.crop((0, 0, width, cropped_height))
            img_cropped.save(filename)
            print(f"Image '{filename}' cropped successfully")
        else:
            print(f"Unable to crop image '{filename}' due to insufficient height")

def generate_images_from_text(prompt_text):
    create_directory("./result")

    messages = [
        {"role": "system", "content": "系統訊息，目前無用"},
        {"role": "user", "content": "生成文章的段落大綱，每個段落一句話，段落中不要有換行符號\n，不同段落中間用換行區分\n。這是您的原始提示文字： " + prompt_text}
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
        get_image(paragraph, image_number)
        image_number += 1

# Main function call
if __name__ == "__main__":
    prompt_text = "編譯器是一個很無聊 很孤兒 又很難的領域 建議不要去孤獨編譯器無聊難懂的世界 在一個寧靜的小鎮上，住著一位名叫小明的年輕工程師。他對編譯器這個領域充滿了好奇，但卻被人說成是無聊又孤獨的領域，讓他望而卻步。 某天，小明無意中發現了一個被遺忘的編譯器專案，他決定挑戰自己，開始著手研究這個看似無聊又孤獨的領域。日以繼夜的努力下，小明漸漸沉浸在編譯器的世界中，發現其中蘊含著無限的樂趣和挑戰。 經過一番努力，小明終於完成了那個被遺忘的編譯器專案，不僅得到了同行的認可，也找到了自己在這個領域的價值和存在感。他明白到，即使是看似無聊孤獨的事物，只要用心去探索，都會發現其中的美好和意義。从此，小明走上了一條屬於自己的獨特之路，成為了編譯器領域的傳奇人物。"
    generate_images_from_text(prompt_text)
