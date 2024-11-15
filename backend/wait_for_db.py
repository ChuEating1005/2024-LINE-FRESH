import time
import MySQLdb
from decouple import config

def wait_for_db():
    while True:
        try:
            MySQLdb.connect(
                host=config('DB_HOST'),
                user=config('DB_USER'),
                passwd=config('DB_PASSWORD'),
                db=config('DB_NAME'),
                port=int(config('DB_PORT'))
            )
            print("Database is ready!")
            break
        except MySQLdb.Error:
            print("Database is not ready. Waiting...")
            time.sleep(1)

if __name__ == "__main__":
    wait_for_db()