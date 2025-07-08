from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask.json.provider import JSONProvider
import json

# import jwt

## SSR 리턴이 필요한 것 같아서 return은 미흡한 상태로 진행

app = Flask(__name__)

database = "lincard"
collection = "memos"
user = "root"
password = "pwd1234"
port = 27017
dbService = "my-db"  # "localhost"

client = MongoClient(
    f"mongodb://{user}:{password}@{dbService}:{port}/{database}?authSource=admin"
)

db = client[database]


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)
    
def createUser(email, password):
    user = {
        "email": email,
        "password": password,  # 실제로는 해시해야함
        "binaryUrl": None,
        "introduction": None,
        "data": {},
    }

    result = db.users.insert_one(user)
    if not result.acknowledged:
            return jsonify({"error": "Failed to create user"}), 500
    
    ## SSR 해야함 
    return str(result.inserted_id) 

# 유저 Profile 수정 
def updateUser(userId, userUpdateRequest):
    introduction = userUpdateRequest['introduction']
    data = userUpdateRequest['data']

    result = db.users.update_one(
        {"_id": ObjectId(userId)},
        {"$set": {"introduction": introduction, "data": data}})
    
    if result.modified_count <= 0:
        return jsonify({"error": "Failed to update user"}), 500
    
    return jsonify({"message": "User updated successfully"}), 200

def fetchRandomUser():

    return None


# UserProfile 가져오기 
def getUser(userId):
    
    user = db.users.find_one({"_id": ObjectId(userId)})
    
    
    ## SSR - profile DTO 로 
    return None;
    

def delete_user(userId):
    """사용자 삭제"""
    # 연관된 추천도 같이 삭제
    db.recommends.delete_many({"userId": ObjectId(userId)})
    
    result = db.users.delete_one({"_id": ObjectId(userId)})
    return None

################ 추천 ################
def createRecommend(userId, title, url, description):
    
    recommend = {
        "userId": ObjectId(userId),
        "title": title,
        "url": url,
        "description": description,
    }
    
    result = db.recommends.insert_one(recommend)
    if not result.acknowledged:
        return jsonify({"error": "Failed to create recommend"}), 500

    ## SSR 해야함
    return None

def getRecommend(userId):
    
    recommend = db.recommends.find_one({"userId": ObjectId(userId)})
    if recommend:
        recommend["id"] = str(recommend["_id"])
        recommend["userId"] = str(recommend["userId"])
        del recommend["_id"]
    return None

#특정 사용자의 모든 추천 조회"""
def getUserRecommends(user_id):
    
    recommends = list(db.recommends.find({"userId": ObjectId(user_id)}))
    
    for rec in recommends:
        rec["id"] = str(rec["_id"])
        rec["userId"] = str(rec["userId"])
        del rec["_id"]
    
    return None

# 해당 userId에 맞는 추천들 전부 삭제 후 다시 create
def updateRecommend(userId, recommendUpdateRequestDTO):
    
    result = deleteUserRecommends(userId)
    if not result:
        return jsonify({"error": "Failed to update recommend"}), 400
    
    userDataList = [] 
    for request in recommendUpdateRequestDTO:
        
        title = request['title']
        url = request['url']
        description = request['description']

        if not title or not url or not description:
            return jsonify({"error": "Failed to update recommend"}), 400

        updateData = {
            'userId': ObjectId(userId),
            'title': title,
            'url': url,
            'description': description
        }
        
        userDataList.append(updateData)
    
        if not result.acknowledged:
            return jsonify({"error": "Failed to update recommend"}), 400
        
        result = db.recommends.insert_many(userDataList)
        return None

def deleteUserRecommends(user_id):
    result = db.recommends.delete_many({"userId": ObjectId(user_id)})
    return result.deleted_count > 0

