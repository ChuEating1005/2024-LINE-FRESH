from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi
# from config import DB_PASSWD
import random
import string
"""
## database set (can modify)

articles:
"id" : int32,                    # not sure how to maintain
"auther" : string,               # line bot user id  
"title" : string,
"description" : string,
"content" : string

user_info:
"user_id" : int32,                # line bot user id
"young" : int32,                  # young : 1, elder : 0
#... other ?

questions:
"id" : int32,                      # not sure how to maintain
"auther" : string,                  # line bot user id 
"content" : string, 
"response counter" : int32,       # counter > 10 then write the article?

# not sure how to maintain response
responses:
"id" : int32,                      # article id
"auther" : string,                  # line bot user id 
"content" : string
"""
class DBHandler:
    def __init__(self, db_name="mydatabase", collection_name="articles"):
        # uri = f"mongodb+srv://zichen:{DB_PASSWD}@cluster0.heftb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        # self.client = MongoClient(uri, server_api=ServerApi('1'))
        uri = "mongodb://localhost:27017/"  
        self.client = MongoClient(uri)     

        self.db = self.client[db_name]
        # articles , user_id, questions, responses
        self.collection = self.db[collection_name]

    # add item(ex: {"id":id, "title" :title,"description": description, "content": content })
    def add_item(self, item):
        result = self.collection.insert_one(item)
        return result.inserted_id
    
    # get json list
    def get_all_json(self):
        return list(self.collection.find({}, {"_id": 0}))  

    def get_item_by_id(self, article_id):
        article = self.collection.find_one({"id": article_id}, {"_id": 0}) 
        return article
    
    # use any column (ex: {"title": title) to find article
    def get_items(self, query):
        articles = self.collection.find(query)
        results = [article for article in articles]
        return results

    # example: use articke id to update and delete
    # can be replaced
    def update_item(self, article_id, update_fields):
        result = self.collection.update_one(
            {"id": article_id}, 
            {"$set": update_fields} 
        )
        return result.modified_count

    def delete_item(self, article_id):
        result = self.collection.delete_one({"id": article_id})
        return result.deleted_count

    def close_connection(self):
        self.client.close()

# Initialize a basic database to test
if __name__ == "__main__":
    # Initialize handler for articles
    db_articles = DBHandler(db_name="mydatabase", collection_name="articles")
    # Add sample articles to collection
    def generate_random_line_id(length=8):
        characters = string.ascii_letters + string.digits  # 包含 a-z, A-Z, 0-9
        return ''.join(random.choice(characters) for _ in range(length))

    # Sample data for articles
    sample_articles = [
        {"id": 0, "auther": generate_random_line_id(), "title": "林悦揚 : 關於認同與自我探索的故事", "description": "同性戀", "content": "# 林悦揚：一個關於認同與自我探索的故事\n\n**摘要**\n林悦揚在面對社會壓力和自我認同的過程中，展現了驚人的勇氣和毅力。本文將探討他如何坦然接受自己的性向，並在尋求內心平衡的過程中找到屬於自己的幸福。\n\n**文章內容**\n林悦揚，一位勇敢坦然面對自我認同挑戰的年輕人。隨著社會對性別和性向的理解逐漸增加，他的成長故事更顯得意義非凡。從迷惘到堅定，林悦揚的經歷向人們展示了真實自我的力量。"},
        {"id": 1, "auther": generate_random_line_id(), "title": "楊子賝 : 反同大將軍的信仰與爭議", "description": "反同大將軍", "content": "# 楊子賝：反同大將軍的信仰與爭議\n\n**摘要**\n楊子賝以強烈的立場和信仰聞名，在許多議題上直言不諱，堅持他的價值觀。本文將探討他背後的信仰基礎，以及他在公共場合中推動反同立場的方式和反響。"},
        {"id": 2, "auther": generate_random_line_id(), "title": "陳冠智 : 與時間同行的老年生活沉思", "description": "老人", "content": "# 陳冠智：與時間同行的老年生活沉思"},
        {"id": 3, "auther": generate_random_line_id(), "title": "曾紹幃 : Poping King 的節奏人生", "description": "poping king", "content": "# 曾紹幃：Poping King 的節奏人生\n\n**摘要**\n在街舞界聞名的曾紹幃，以精湛的 Poping 技藝而成為眾人眼中的偶像。本文將深入介紹他的舞蹈旅程，以及他如何在生活中找到節奏的意義。"},
        {"id": 4, "auther": generate_random_line_id(), "title": "林鈺誠 : Loking King 的舞動人生", "description": "loking king", "content": "# 林鈺誠：Loking King 的舞動人生\n\n**摘要**\n以 Loking 舞技稱霸街頭的林鈺誠，展現了絕佳的舞蹈天賦與創造力。本文記錄了他的成長過程，以及他如何通過舞蹈傳達自我。"}
    ]

    # Add sample articles to collection
    for article in sample_articles:
        db_articles.add_item(article)
    

    # Initialize handler for user_info
    db_user_info = DBHandler(db_name="mydatabase", collection_name="user_info")
    
    # Sample data for user_info
    sample_user_info = [
        {"user_id": generate_random_line_id(), "young": random.randint(0, 1)},
        {"user_id": generate_random_line_id(), "young": random.randint(0, 1)},
        {"user_id": generate_random_line_id(), "young": random.randint(0, 1)},
        {"user_id": generate_random_line_id(), "young": random.randint(0, 1)},
        {"user_id": generate_random_line_id(), "young": random.randint(0, 1)}
    ]

    # Add sample user_info to collection
    for user in sample_user_info:
        db_user_info.add_item(user)

    # Initialize handler for questions
    db_questions = DBHandler(db_name="mydatabase", collection_name="questions")
    
    # Sample data for questions
    sample_questions = [
        {"id": 0, "auther": generate_random_line_id(), "content": "如何面對壓力？", "response counter": random.randint(0, 10)},
        {"id": 1, "auther": generate_random_line_id(), "content": "你如何看待性別平等？", "response counter": random.randint(0, 10)},
        {"id": 2, "auther": generate_random_line_id(), "content": "什麼是人生意義？", "response counter": random.randint(0, 10)},
        {"id": 3, "auther": generate_random_line_id(), "content": "如何提高自信？", "response counter": random.randint(0, 10)},
        {"id": 4, "auther": generate_random_line_id(), "content": "你如何處理失敗？", "response counter": random.randint(0, 10)}
    ]

    # Add sample questions to collection
    for question in sample_questions:
        db_questions.add_item(question)

    # Initialize handler for responses
    db_responses = DBHandler(db_name="mydatabase", collection_name="responses")
    
    # Sample data for responses
    sample_responses = [
        {"id": 0, "auther": generate_random_line_id(), "content": "保持冷靜，理性思考。"},
        {"id": 1, "auther": generate_random_line_id(), "content": "尊重和包容他人的觀點。"},
        {"id": 2, "auther": generate_random_line_id(), "content": "尋求自己的價值和目標。"},
        {"id": 3, "auther": generate_random_line_id(), "content": "每天進步一點，提升自信心。"},
        {"id": 4, "auther": generate_random_line_id(), "content": "從失敗中學習，繼續前進。"}
    ]

    # Add sample responses to collection
    for response in sample_responses:
        db_responses.add_item(response)

    # Close connections
    db_articles.close_connection()
    db_user_info.close_connection()
    db_questions.close_connection()
    db_responses.close_connection()