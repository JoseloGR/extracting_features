import motor.motor_asyncio
import meaningcloud
import requests
import time
import asyncio
from fastapi import FastAPI, HTTPException
from bson.objectid import ObjectId
from config import (
    MONGO_CONNECTION_STRING,
    MEANING_CLOUD_KEY,
    PARALLEL_DOTS_KEY
)

app = FastAPI()

def get_mongo_client():
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_CONNECTION_STRING)
    return client.tweetsdb

def document_helper(document) -> dict:
    data = {}
    for key in document.keys():
        if isinstance(document.get(key), ObjectId):
            data[key] = str(document.get(key))
        else:
            data[key] = document.get(key)
    return data

async def get_tweets(collectionName='tweets', skip=0, limit=10) -> list:
    db = get_mongo_client()
    collection = db.get_collection(collectionName)
    tweets = []
    async for tweet in collection.find().sort("id").skip(skip).limit(limit):
        tweets.append(document_helper(tweet))
    return tweets

async def get_tweet(id: str):
    db = get_mongo_client()
    collection = db.get_collection("tweets")
    tweet = await collection.find_one(
        {
            "id": int(id)
        }
    )
    return tweet

async def add_new_sentiments_tweet_mcloud(id: int, data: dict, collectionName='sentimentsMCloud') -> str:
    if data.get('status'):
        del data['status']
    data['id'] = id
    db = get_mongo_client()
    collection = db.get_collection(collectionName)
    sentiment_tweet = await collection.find_one({"id": id})
    result = ''
    if not sentiment_tweet:
        tweet = await collection.insert_one(data)
        result = 'NUEVO' if tweet.inserted_id else 'ERROR EN NUEVO'
    else:
        del data['id']
        updated_tweet = await collection.update_one(
            {"id": id},
            {"$set": data}
        )
        result = f"ACTUALIZADO {updated_tweet.modified_count}"
    return result

async def update_tweet_with_sentiments_mcloud(id: int, data: dict, collectionName='tweets') -> bool:
    _status = False
    payload = {
        'score_tag': data.get('score_tag'),
        'agreement': data.get('agreement'),
        'subjectivity': data.get('subjectivity'),
        'confidence': data.get('confidence'),
        'irony': data.get('irony')
    }
    db = get_mongo_client()
    collection = db.get_collection(collectionName)
    updated_tweet = await collection.update_one(
        {"id": id},
        {"$set": payload}
    )
    if updated_tweet.modified_count == 1:
        _status = True
    return _status

async def update_tweet_with_emotions_pdots(id: int, data: dict, collectionName='tweets') -> bool:
    _status = False
    db = get_mongo_client()
    collection = db.get_collection(collectionName)
    updated_tweet = await collection.update_one(
        {"id": id},
        {"$set": data.get('emotion', {})}
    )
    if updated_tweet.modified_count == 1:
        _status = True
    return _status

async def extract_with_meaning_cloud(message: str) -> list:
    result = []
    try:
        topics_response = meaningcloud.TopicsResponse(meaningcloud.TopicsRequest(MEANING_CLOUD_KEY, txt=message, lang='en', topicType='e').sendReq())
    except ValueError as e:
        raise HTTPException(status_code=400, message=str(e))
    else:
        if topics_response.isSuccessful():
            entities = topics_response.getEntities()
            from pprint import pprint
            pprint(entities)
            for entity in entities:
                result.append({'type': topics_response.getTypeLastNode(topics_response.getOntoType(entity)), 'value':  topics_response.getTopicForm(entity)})
                print("\t\t" + topics_response.getTopicForm(entity) + ' --> ' + topics_response.getTypeLastNode(topics_response.getOntoType(entity)) + "\n")
    return result

async def extract_sentiments_with_meaning_cloud(message: str) -> dict:
    url = 'https://api.meaningcloud.com/sentiment-2.1'
    payload = {
        'key': MEANING_CLOUD_KEY,
        'txt': message,
        'lang': 'en'
    }
    response = requests.post(url, data=payload)
    print(response.status_code)
    if response.status_code == 200:
        return response.json()
    return {}

async def extract_emotions_with_meaning_cloud(message: str) -> dict:
    url = 'https://api.meaningcloud.com/deepcategorization-1.0'
    payload = {
        'key': MEANING_CLOUD_KEY,
        'txt': message,
        'model': 'Emotion_en'
    }
    # 'polarity': 'y'
    response = requests.post(url, data=payload)
    print(response.text)
    if response.status_code == 200:
        return response.json()
    return {}

async def extract_emotions_with_parallel_dots(message: str) -> dict:
    url = 'https://apis.paralleldots.com/v5/emotion'
    payload = {
        'api_key': PARALLEL_DOTS_KEY,
        'text': message,
        'lang_code': 'en'
    }
    response = requests.post(url, data=payload)
    print(response.text)
    if response.status_code == 200:
        return response.json()
    return {}


@app.get('/')
def home():
    return {"Hello": "World"}

@app.get('/tweets', tags=["Tweets"], response_description="Tweets Retrieved")
async def get_sample_tweets():
    tweets = await get_tweets()
    return tweets

@app.get('/tweet/entities/{id}', tags=["Tweets"], response_description="Entities Retrieved")
async def get_tweet_entities(id: str):
    tweet = await get_tweet(id)
    entities_response = await extract_with_meaning_cloud(tweet.get('text'))
    return entities_response

@app.get('/tweet/sentiment/{id}', tags=["Tweets"], response_description="Sentiments Retrieved")
async def get_tweet_sentiments(id: str):
    tweet = await get_tweet(id)
    entities_response = await extract_sentiments_with_meaning_cloud(tweet.get('text'))
    updated_tweet = await update_tweet_with_sentiments_mcloud(tweet.get('id'), entities_response)
    print(updated_tweet)
    saved = await add_new_sentiments_tweet_mcloud(tweet.get('id'), entities_response)
    print(saved)
    return entities_response

@app.get('/tweet/sentiment/{skip}/{limit}', tags=["Tweets"], response_description="Emotions Retrieved For All Tweets")
async def get_tweet_sentiments_all(skip: int, limit: int):
    collectionName = 'testing'
    collectionName2 = 'sentimentsMCloudTesting'
    tweets = await get_tweets(collectionName, skip, limit)
    start = time.time()
    for tweet in tweets:
        entities_response = await extract_sentiments_with_meaning_cloud(tweet.get('text'))
        updated_tweet = await update_tweet_with_sentiments_mcloud(tweet.get('id'), entities_response, collectionName)
        saved = await add_new_sentiments_tweet_mcloud(tweet.get('id'), entities_response, collectionName2)
        print(f"{tweet.get('id')} {updated_tweet} - {saved}")
        await asyncio.sleep(2)
    end = time.time()
    print(f"It took {round(end-start)} seconds to finish execution")
    
    return {'success': f"{len(tweets)} analized tweets"}

@app.get('/tweet/emotions/{id}', tags=["Tweets"], response_description="Emotions Retrieved")
async def get_tweet_emotions(id: str):
    tweet = await get_tweet(id)
    emotions_response = await extract_emotions_with_parallel_dots(tweet.get('text'))
    updated_tweet = await update_tweet_with_emotions_pdots(tweet.get('id'), emotions_response)
    print(f"{id} {updated_tweet}")
    return emotions_response

@app.get('/tweet/emotions/{skip}/{limit}', tags=["Tweets"], response_description="Emotions Retrieved For All Tweets")
async def get_tweet_emotions_all(skip: int, limit: int):
    collectionName = 'testing'
    tweets = await get_tweets(collectionName, skip, limit)
    start = time.time()
    for tweet in tweets:
        emotions_response = await extract_emotions_with_parallel_dots(tweet.get('text'))
        updated_tweet = await update_tweet_with_emotions_pdots(tweet.get('id'), emotions_response, collectionName)
        print(f"{tweet.get('id')} {updated_tweet}")
        await asyncio.sleep(5)
    end = time.time()
    print(f"It took {round(end-start)} seconds to finish execution")
    
    return {'success': f"{len(tweets)} analized tweets"}
