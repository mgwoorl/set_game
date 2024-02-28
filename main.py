from flask import Flask, render_template, request, jsonify
import secrets
import random

app = Flask(__name__)

users = [] # все пользователи
rooms = [] # комнаты (хранит id комнат и создателя)
current_user = [] # текущий пользователь, вошедший в аккаунт
games = [] # игры (хранит id комнат)
players = [] # все игроки в комнатах
deck = [] # колода
field = [] # поле

id = 0

for count in range(1, 4):
    for color in range(1, 4):
        for shape in range(1, 4):
            for fill in range(1, 4):
                deck.append({"id": id, "count": count, "shape": shape, "fill": fill})
                id += 1

print(deck)

@app.route("/user/register", methods=["POST", "GET"])
def register():
   data = request.get_json()

   nickname = data.get("nickname")
   password = data.get("password")

   if not nickname or not password:
       return jsonify({"message": "Please enter both username and password"}), 400

   for user in users:
       if user["nickname"] == nickname:
           return jsonify({"message": "This nickname is already taken, please choose another one"}), 400

   else:
        #accessToken = jwt.encode({"_id": nickname}, "key", algorithm="HS256")
        accessToken = secrets.token_hex(8)
        users.append({"nickname": nickname, "password": password, "accessToken": accessToken})
        return jsonify({"nickname": nickname, "accessToken": accessToken, "users": users}), 200

@app.route("/user/login", methods=["POST", "GET"])
def login():
   data = request.get_json()

   nickname = data.get("nickname")
   password = data.get("password")

   if not nickname or not password:
       return jsonify({"message": "Please enter both username and password"}), 400

   for user in users:
       if user["nickname"] == nickname and user["password"] == password:
           current_user.append(user)
           return jsonify({"success": "true", "exception": "null", "nickname": nickname, "accessToken": user["accessToken"]}), 200

   return jsonify({"success": "false", "exception": {"message": "Nickname or password is incorrect"}}), 400

@app.route("/set/room/create", methods=["POST", "GET"])
def create_room():
   data = request.get_json()

   accessToken = data.get("accessToken")

   print(current_user)
   print(current_user[-1]["accessToken"])

   if not accessToken:
       return jsonify({"message": "Please enter your token"}), 400

   elif accessToken == current_user[-1]["accessToken"]:
        if rooms == []:
            game_id = 0
        else:
            game_id = rooms[-1]["gameId"] + 1

        rooms.append({"gameId": game_id, "creator": current_user[-1]["nickname"]})
        games.append({"gameId": game_id})
        print(rooms)
        print(games)
        return jsonify({"nickname": current_user[-1]["nickname"], "success": "true", "exception": "null", "gameId": game_id, "rooms": rooms}), 200

   return jsonify({"message": "Room creation failed"}), 400

@app.route("/set/room/list", methods=["POST", "GET"])
def room_list():
   data = request.get_json()

   accessToken = data.get("accessToken")

   print(current_user)
   print(current_user[-1]["accessToken"])

   if not accessToken or accessToken != current_user[-1]["accessToken"]:
       return jsonify({"message": "Please enter your token"}), 400

   if accessToken == current_user[-1]["accessToken"]:
       if rooms == []:
           return jsonify({{"message": "Room's list is empty"}}), 200
       else:
           print(rooms)
           return jsonify({"games": games}), 200

   return jsonify({"message": "Failed"}), 400

@app.route("/set/room/enter", methods=["POST", "GET"])
def enter_room():
   data = request.get_json()

   accessToken = data.get("accessToken")
   gameId = data.get("gameId")

   if not accessToken or accessToken != current_user[-1]["accessToken"]:
       return jsonify({"message": "Please enter your token"}), 400

   print(rooms)

   for game in games:
       for room in rooms:
           if (accessToken == current_user[-1]["accessToken"] and gameId == game["gameId"] and
           current_user[-1]["nickname"] != room["creator"] and room["gameId"] == gameId and
           all(player.get("player") != current_user[-1]["nickname"] for player in players)):
               players.append({"gameId": game["gameId"], "player": current_user[-1]["nickname"]})
               return jsonify({"success": "true", "exception": "null", "gameId": game["gameId"]}), 200

           elif all(player.get("player") == current_user[-1]["nickname"] for player in players):
               return jsonify({"message": "You've already joined other room"}), 400

           elif rooms == []:
               return jsonify({"message": "Room's list is empty, so, you can't enter this room"}), 400

           elif current_user[-1]["nickname"] == room["creator"] and room["gameId"] == gameId:
               return jsonify({"message": "You're in this room now, because you're the creator of this room"}), 400

   return jsonify({"message": "Your token may be wrong or this room doesn't exist"}), 400

@app.route("/set/field", methods=["POST", "GET"])
def game_field():
   data = request.get_json()

   accessToken = data.get("accessToken")

   if not accessToken or accessToken != current_user[-1]["accessToken"]:
       return jsonify({"message": "Please enter your token"}), 400

   for player in players:
       if player["player"] == current_user[-1]["accessToken"] and field != [] and all(field.get("gameId") != player["roomId"] for player in players):
           return jsonify({"message": "Field for this room is already created"}), 400

       elif player["player"] == current_user[-1]["accessToken"] and field == []:
           sorted_deck = random.shuffle(deck)
           cards_for_first_time = []
           for i in range(1, 13):
               cards_for_first_time.append(sorted_deck[i])
           field.append({"gameId": player["gameId"], "cards": cards_for_first_time})

   return jsonify({"message": "Your token may be wrong or this room doesn't exist"}), 400

if __name__ == "__main__":
    app.run(debug=True)
