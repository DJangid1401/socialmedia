from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime
import uuid  # To generate unique tweet_id for each tweet

app = Flask(__name__)

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="social_media"
)
cursor = db_connection.cursor()

@app.route('/tweet', methods=["POST"])
def post_tweet():
    print(request.json)
    message = request.json.get("message")
    user_name = request.json.get("user_name")
    if not message or not user_name:
        return jsonify({"error": "message and user_name are required"}), 400
    
    tweet_id = str(uuid.uuid4())  # Generate unique tweet_id
    created_at = datetime.now()

    # Fixed the query by removing the extra closing parenthesis
    insert_query = """INSERT INTO tweets (tweet_id, user_name, tweet_text, created_at) VALUES (%s, %s, %s, %s)"""
    
    cursor.execute(insert_query, (tweet_id, user_name, message, created_at))
    db_connection.commit()

    return jsonify({"message": "Tweet posted successfully!"}), 201

@app.route('/tweet/get', methods=['GET'])
def get_all_tweets():
    cursor.execute("SELECT * FROM tweets ORDER BY created_at DESC")
    tweets = cursor.fetchall()

    result = []
    for tweet in tweets:
        result.append({
            "tweet_id": tweet[0],  # Assuming tweet_id is the first column
            "user_name": tweet[1],  # Assuming user_name is the second column
            "tweet_text": tweet[2],  # Assuming tweet_text is the third column
            "created_at": tweet[3].strftime('%Y-%m-%d %H:%M:%S')  # Assuming created_at is the fourth column
        })
    
    return jsonify(result), 200

@app.route('/tweets/get/<user_name>', methods=['GET'])
def get_tweets_by_user(user_name):
    cursor.execute("SELECT * FROM tweets WHERE user_name = %s ORDER BY created_at DESC", (user_name,))
    tweets = cursor.fetchall()

    result = []
    for tweet in tweets:
        result.append({
            "tweet_id": tweet[0],  # tweet_id is assumed to be the first column
            "user_name": tweet[1],  # user_name is the second column
            "tweet_text": tweet[2],  # tweet_text is the third column
            "created_at": tweet[3].strftime('%Y-%m-%d %H:%M:%S')  # Formatting created_at
        })
    return jsonify(result), 200

@app.route('/tweet/<tweet_id>', methods=['PUT'])
def update_tweet(tweet_id):
    new_message = request.json.get('message')
    if not new_message:
        return jsonify({"error": "New message is required"}), 400
    
    update_query = """UPDATE tweets SET tweet_text = %s, created_at = %s WHERE tweet_id = %s"""
    created_at = datetime.now()
    cursor.execute(update_query, (new_message, created_at, tweet_id))
    db_connection.commit()

    return jsonify({"message": "Tweet updated successfully"}), 200

@app.route('/tweet/<tweet_id>', methods=['DELETE'])
def delete_tweet(tweet_id):
    delete_query = "DELETE FROM tweets WHERE tweet_id = %s"
    cursor.execute(delete_query, (tweet_id,))
    db_connection.commit()

    return jsonify({"message": "Tweet deleted successfully!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
