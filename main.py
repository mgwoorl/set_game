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
used_cards = [] # использованные карты

id = 0

for count in range(1, 4):
    for color in range(1, 4):
        for shape in range(1, 4):
            for fill in range(1, 4):
                deck.append({"id": id, "count": count, "color": color, "shape": shape, "fill": fill})
                id += 1

print(deck)

def find_set(cards):
    check = False

    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            third_card = {}

            for prop in ["color", "count", "fill", "shape"]:
                if cards[i][prop] == cards[j][prop]:
                    third_card[prop] = cards[i][prop]

                elif cards[i][prop] != cards[j][prop]:
                    third_card[prop] = 6 - cards[i][prop] - cards[j][prop]

            if third_card in cards:
                print('first card: ' + str(cards[i]) + ', \nsecond card: ' + str(cards[j]) + ', \nthird card: ' + str(
                    third_card) + '\n')

                check = True
                break

        if check == True:
            break

    if check == False:
        print('Сет не найден')

def is_set(cards):
    check = False

    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            for k in range (j + 1, len(cards)):
                for prop in ["color", "shape", "fill", "count"]:
                    if cards[i][prop] == cards[j][prop] and cards[j][prop] == cards[k][prop]:
                        check = True

                    elif cards[i][prop] != cards[j][prop] and cards[k][prop] == (6 - cards[i][prop] - cards[j][prop]):
                        check = True

                    else:
                        check = False

                    check = True

    if check == False:
        return False

    return True

def sort(count):
    if count == 0:
        cards_for_first_time = []
        while (find_set(cards_for_first_time) == False):
            random.shuffle(deck)
            cards_for_first_time = []
            count = 0
            for i in range(1, 13):
                j = random.randint(0, 80)
                cards_for_first_time.append(deck[j])
                count += 1
                field[0]["count"] = count

        return cards_for_first_time, field[0]["count"]

    elif count == 9:
        cards_to_add = []
        while (find_set(cards_to_add) == False):
            random.shuffle(deck)
            cards_to_add = []
            count = 0
            for i in range(1, 4):
                j = random.randint(0, 80)
                cards_to_add.append(deck[j])
                count += 1
                field[0]["count"] = count

        return cards_to_add, field[0]["count"]

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
        accessToken = secrets.token_hex(8)
        users.append({"nickname": nickname, "password": password, "accessToken": accessToken})
        return jsonify({"nickname": nickname, "accessToken": accessToken}), 200

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

   if not accessToken:
       return jsonify({"message": "Please enter your token"}), 400

   elif accessToken == current_user[-1]["accessToken"]:
        if rooms == []:
            game_id = 0
        else:
            game_id = rooms[-1]["gameId"] + 1

        rooms.append({"gameId": game_id, "creator": current_user[-1]["nickname"]})
        games.append({"gameId": game_id})
        players.append({"gameId": game_id, "player": current_user[-1]["nickname"], "score": 0})
        return jsonify({"success": "true", "exception": "null", "gameId": game_id}), 200

   return jsonify({"message": "Room creation failed"}), 400

@app.route("/set/room/list", methods=["POST", "GET"])
def room_list():
   data = request.get_json()

   accessToken = data.get("accessToken")

   if not accessToken or accessToken != current_user[-1]["accessToken"]:
       return jsonify({"message": "Please enter your token"}), 400

   if accessToken == current_user[-1]["accessToken"]:
       if rooms == []:
           return jsonify({{"message": "Room's list is empty"}}), 200
       else:
           return jsonify({"games": games}), 200

   return jsonify({"message": "Failed"}), 400

@app.route("/set/room/enter", methods=["POST", "GET"])
def enter_room():
   data = request.get_json()

   accessToken = data.get("accessToken")
   gameId = data.get("gameId")

   if not accessToken or accessToken != current_user[-1]["accessToken"]:
       return jsonify({"message": "Please enter your token"}), 400

   for game in games:
       for room in rooms:
           if (accessToken == current_user[-1]["accessToken"] and gameId == game["gameId"] and
           current_user[-1]["nickname"] != room["creator"] and room["gameId"] == gameId and
           all(player.get("player") != current_user[-1]["nickname"] for player in players)):
               players.append({"gameId": game["gameId"], "player": current_user[-1]["nickname"], "score": 0})
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

   if field == []:
       return jsonify({"message": "Fields didn't created for rooms in list"}), 400

   for player in players:
       for f in field:
            if player["player"] == current_user[-1]["nickname"] and f["cards"] == []:
                return jsonify({"cards": "[]", "status": "ongoing", "score": 0}), 200

            elif player["player"] == current_user[-1]["nickname"] and f["cards"] != [] and player["gameId"] == f[
                "gameId"] and f["count"] != 0:
                return jsonify({"cards": f["cards"], "status": "ongoing", "score": player["score"]}), 200

            elif player["player"] == current_user[-1]["nickname"] and f["cards"] != [] and player["gameId"] == f[
                "gameId"] and f["count"] == 0:
                return jsonify({"cards": f["cards"], "status": "ended", "score": player["score"]}), 200

   return jsonify({"message": "Error"}), 400

@app.route("/set/pick", methods=["POST", "GET"])
def pick_cards():
    data = request.get_json()

    accessToken = data.get("accessToken")
    cards = data.get("cards")

    if not accessToken or accessToken != current_user[-1]["accessToken"]:
        return jsonify({"message": "Please enter your token"}), 400

    if not cards:
        return jsonify({"message": "Please choose the cards you want"}), 400

    for player in players:
        for f in field:
            for i in f:
                for card in cards:
                    if player["player"] == current_user[-1]["nickname"] and player["gameId"] == f["gameId"] and f["cards"][i]["id"] == card and f["count"] == 12:
                        flag = is_set(cards)
                        if flag:
                            player["score"] += 1
                            print(f["count"])
                            f["count"] -= 3
                            print(f["count"])
                            f["cards"].remove(f["cards"][i])
                            return jsonify({"isSet": "true", "score": player["gameId"]}), 200

                        else:
                            return jsonify({"isSet": "false", "score": player["gameId"]}), 400

                    else:
                        return jsonify({"isSet": "false", "score": player["gameId"]}), 400

    return jsonify({"message": "Error"}), 400

@app.route("/set/add", methods=["POST", "GET"])
def add_cards():
   data = request.get_json()

   accessToken = data.get("accessToken")

   if not accessToken or accessToken != current_user[-1]["accessToken"]:
       return jsonify({"message": "Please enter your token"}), 400

   # for player in players:
   #     if field == []:
   #         if player["player"] == current_user[-1]["nickname"]:
   #             random.shuffle(deck)
   #             cards_for_first_time = []
   #             count = 0
   #             for i in range(1, 13):
   #                 j = random.randint(0, 80)
   #                 cards_for_first_time.append(deck[j])
   #                 count += 1
   #
   #             if find_set(cards_for_first_time):
   #                 used_cards.append({"gameId": player["gameId"], "cards": cards_for_first_time})
   #                 field.append({"gameId": player["gameId"], "cards": cards_for_first_time, "count": count})
   #                 return jsonify({"cards": cards_for_first_time, "status": "ongoing", "score": 0}), 200
   #
   #             else:
   #                 for i in range(1, 13):
   #                     j = random.randint(0, 80)
   #                     cards_for_first_time.append(deck[j])
   #                     count += 1
   #
   #                 if find_set(cards_for_first_time):
   #                     used_cards.append({"gameId": player["gameId"], "cards": cards_for_first_time})
   #                     field.append({"gameId": player["gameId"], "cards": cards_for_first_time, "count": count})
   #                     return jsonify({"cards": cards_for_first_time, "status": "ongoing", "score": 0}), 200

   for player in players:
       if field == []:
           if player["player"] == current_user[-1]["nickname"] and sort(0):
               cards, count =  map(input().split())
               used_cards.append({"gameId": player["gameId"], "cards": cards})
               field.append({"gameId": player["gameId"], "cards": cards, "count": count})
               return jsonify({"cards": cards, "status": "ongoing", "score": 0}), 200

   for player in players:
       for f in field:
           if player["player"] == current_user[-1]["nickname"] and f["count"] == 12 and all(f.get("gameId") == player["gameId"] for f in field):
               return jsonify({"message": "There are already 12 cards placed on this field"}), 400

           elif player["player"] == current_user[-1]["nickname"] and f["count"] == 9 and player["gameId"] == f["gameId"]:
               three_cards = []
               for i in range(len(used_cards), len(used_cards) + 1):
                   three_cards.append(deck[i])
               field.append({"gameId": player["gameId"], "cards": three_cards, "status": "ongoing", "score": 0})
               return jsonify({"cards": f["cards"], "status": "ongoing", "score": 0}), 200

   return jsonify({"message": "Error"}), 400

@app.route("/set/scores", methods=["POST", "GET"])
def game_scores():
   data = request.get_json()

   accessToken = data.get("accessToken")

   if not accessToken or accessToken != current_user[-1]["accessToken"]:
        return jsonify({"message": "Please enter your token"}), 400

   pl = []

   for player in players:
        pl.append({"name": player["player"], "score": player["score"]})

   if pl != []:
       return jsonify({"success": "true", "exception": "null", "users": pl}), 200

   return jsonify({"message": "Error"}), 400

if __name__ == "__main__":
    app.run(debug=True)
