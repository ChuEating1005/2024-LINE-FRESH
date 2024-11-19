# 2024-LINE-FRESH

## Prerequisites

- Docker
- Python 3.x
- pip

## Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ChuEating1005/2024-LINE-FRESH.git
   cd 2024-LINE-FRESH
   ```

2. **Create a `.env` file:**

   Create a `.env` file in the `backend` directory with the following content:

   ```env
   DB_NAME=
   DB_USER=
   DB_PASSWORD=
   DB_ROOT_PASSWORD=
   DB_HOST=
   DB_PORT=
   SECRET_KEY=
   LINE_ACCESS_TOKEN=
   LINE_CHANNEL_SECRET=
   ```

4. **Pull the docker images:**

   ```bash
   docker pull mysql:8.0
   ```


3. **Start the project:**

   ```bash
   cd backend
   python3 set_richmenu.py
   make start
   ```

4. **Create a superuser:**

   ```bash
   make createsuperuser
   ```

5. **Restart the project (when modifying the models):**

   ```bash
   make restart
   ```

6. **Remove all datas and start the project:**

   ```bash
   make restart-hard
   ```

## Usage

- Access the Django admin interface at `http://localhost:8000/admin/`.
- The bot's callback URL is `http://localhost:8000/bot/callback/`.

### 11/19 zichen
- 新增一個richmenu : 所有文章vs推薦文章 如果點所有文章 會導向一個有所有文章的website(要手動更新link 在settings.py) 點推薦文章的話會變成linebot中可以滑動的文章列表
- 新增openai的連接 在openai_Handlers裡面 用gpt3.5 有下基本的prompt 感覺質量還有點普通 要調整一下
- 目前還沒有加入audio 所以先用語言輸入測試生成文章 點擊發表文章就可以測
- 一個問題回答超過五次的話會送去生成然後create article 
- 網頁目前是一般的html 我測試後端用的 也還沒建liff 美編就之後交給阿原了
- 有做生成和顯示tag 看之後要不要限制tag種類 可以分類文章
