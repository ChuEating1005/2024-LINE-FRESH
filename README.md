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

