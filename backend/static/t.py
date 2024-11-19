from PIL import Image

# 開啟原始圖片
image_path = "richmenu-topic.png"  # 替換成你的圖片路徑
output_path = "richmenu-topic.png" # 輸出圖片的路徑

# 開啟圖片
img = Image.open(image_path)

# 計算新的高度，保持比例
new_width = 1040
aspect_ratio = img.height / img.width
new_height = int(new_width * aspect_ratio)

# 調整大小，使用新的 LANCZOS 方法
resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

# 儲存圖片
resized_img.save(output_path)

print(f"圖片已成功縮放並儲存為 {output_path}")