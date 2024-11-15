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

   mongoDB part: (change 27017 to your own mongoDB local port)
   ```bash
   docker run -d --name mongodb -p 27017:27017 mongo:latest
   ```

3. **Start the project:**

   ```bash
   cd backend
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

## zichen part
LINEBOT/db_utils/裡面有把資料庫crud包成handler可以直接call 不過沒有很完整 只有一些新增刪除查找
資料庫原本是用mongoDB的atlas 但免費的一下子就滿了 後來改先用local 把uri = "mongodb://localhost:27017/"  改成自己的port
跑db_handler.py可以存基本的資料庫欄位做測試
還沒處理嵌入圖片的方法

LINEBOT/web/裡面的前端是我簡單測試用的 有兩個畫面 一個是條列文章title 還有按鈕可以點入各個文章 第二個就是顯示文章的頁面 
只要看templates/和views.py 其他沒改

不過目前把markdown傳到html不太會正確排版 好像還要下載markdown的css 或是用其他方法存 這邊還沒做

跑前面的make start / make restart可以顯示網頁
如果要測試mongoDB可以先跑python db_utils/db_handler.py填充資料庫

我在backend裡面放了Dockerfile和fly.toml是我做到一半的deploy to flyio, 還沒成功 但感覺可以最後在部屬 因為其實localhost也可以驅動linebot 可以先測試
