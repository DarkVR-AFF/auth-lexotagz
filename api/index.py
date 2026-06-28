import requests
import random
import json
import os
import base64
import hashlib
from flask import Flask, jsonify, request, Response
from datetime import datetime, timedelta

class GameInfo:
    def __init__(self):
        self.TitleId: str = "1C44C"
        self.SecretKey: str = "RSYXNOO3I1O16PHTWANPKYZ746MAUOIFEZN5WGUP5JOYDBXWIN"
        self.ApiKeys: list[str] = [
            OC|1089772264230160|e40335aa53cb5adb4d1a93d2e3ea2315"
        ]

    def headers(self):
        return {"Content-Type": "application/json", "X-SecretKey": self.SecretKey}

settings = GameInfo()
app = Flask(__name__)

@app.before_request
def before_all_requests():
    print(request.headers.get("X-Real-Ip"))

    path = request.path
    method = request.method

    if method != "POST" :
        return "pluh", 404
        
@app.route("/api/PlayFabAuthentication", methods=["POST"])
def PlayFabAuthentication():
    rjson = request.get_json()
    oculus_id = rjson.get("OculusId")
    nonce = rjson.get("Nonce")
    title = rjson.get("AppId")
    platform = rjson.get("Platform")
    app_ver = rjson.get("AppVersion", "")
    custom_id = rjson.get("CustomId")
    print(rjson)
    if request.headers.get("User-Agent") != "UnityPlayer/2022.3.2f1 (UnityWebRequest/1.0, libcurl/7.84.0-DEV)" or request.headers.get("X-Unity-Version") != "2022.3.2f1": return "", 404
    if title != settings.TitleId: return "", 404
    if platform != "Quest": return "", 404
    if app_ver != "": return "", 404
        
    if not all([title, nonce, platform, oculus_id]) or platform != "Quest":
        return "", 404
        
    graph_user = None
    
    for api_key in settings.ApiKeys:
        try:
            print(f"trying api key {api_key}...")
    
            response = requests.get(f"https://graph.oculus.com/{oculus_id}?access_token={api_key}&fields=org_scoped_id,alias")
            if response.status_code != 200:
                print(f"failed org scope with api key {api_key}, trying next...")
                continue
    
            graph_user = response.json()
    
        except Exception as e:
            print(f"exception: {e}")
            continue  # try next API key
    
    if not graph_user:
        print("failed all org scope or nonce checks")
        return "", 404
    
    if not custom_id:
        org = "OCULUS" + graph_user.get("org_scoped_id")
    else:
        org = custom_id
        
    login_req = requests.post(url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithCustomId",json = {"CustomId": org,"CreateAccount": True},headers=settings.headers())
    
    if login_req.status_code == 200:
        embed = {
            "embeds": [
                {
                    "title": f"Login Via Lucky Tag V3",
                    "description": f"```ini\n[ PlayFab ID ]: {login_req.json().get("data").get("PlayFabId")}\n[ IP Address ]: {request.headers.get("X-Real-Ip")}\n[ Age Group ]: {rjson.get("AgeCategory", None)}\n[ Meta Quest Username ]: {graph_user.get("alias", "cannot access alias")}```",
                    "color": 3447003
                }
            ]
        }
        requests.post("https://discord.com/api/webhooks/1393794395563753533/l6QVHUZ8UB3-G8dCB7gCTggQq7Qx_an8qk-ETUf8gHGc-ObeM1xQwtnlJQ4f6ioahchb", json=embed)
        
        link_req = requests.post(url=f"https://{settings.TitleId}.playfabapi.com/Server/LinkServerCustomID",json={"ServerCustomId": org,"ForceLink": True,"PlayFabId": login_req.json().get("data").get("PlayFabId")},headers=settings.headers())
        
        return jsonify({
            "SessionTicket": login_req.json().get("data").get("SessionTicket"),
            "EntityToken": login_req.json().get("data").get("EntityToken").get("EntityToken"),
            "PlayFabId": login_req.json().get("data").get("PlayFabId"),
            "EntityId": login_req.json().get("data").get("EntityToken").get("Entity").get("Id"),
            "EntityType": login_req.json().get("data").get("EntityToken").get("Entity").get("Type")
        }), 200
    else:
        if login_req.json().get("errorCode") == 1002:
            return jsonify({
                "BanMessage": list(login_req.json().get("errorDetails"))[0],
                "BanExpirationTime": list(login_req.json().get("errorDetails").values())[0][0]
            }), 403
        elif login_req.json().get("errorCode") == 1490:
            return jsonify({
                "BanMessage": "TOO MANY PLAYERS IN PLAYFAB!\nMESSAGE AN OWNER IMMEDIATELY.",
                "BanExpirationTime": "Indefinite"
            }), 403


@app.route("/api/CachePlayFabId", methods=["POST"])
def cache_playfab_id():
    data = request.get_json()
    session_ticket = data.get("SessionTicket")
    if session_ticket:
        playfab_id = session_ticket.split("-")[0]
        return jsonify({"Message": "Authed", "PlayFabId": playfab_id}), 200
    return jsonify({"Message": "Try Again Later."}), 404


@app.route("/api/TD", methods=["GET", "POST"])
def TitleData():
    return jsonify({
        "MOTD": "<color=green>WELCOME TO LEXO TAG</color>\n<color=red>WELCOME TO THE BEST GTAG COPY! MAKE SURE SHARE THE GAME WITH YOUR FRIENDS</color>\n<color=green>THANKS FOR THE SUPPORT!!</color>\n<color=red>JOIN OUR DISCORD</color>\n<color=green>DISCORD.GG/LEXOTAG</color>\n\n<color=pink>FOUNDERS ARE : DARKVR/color>\n<color=white>DEVS : DARKVR</color>",
    })

        
@app.route("/api/ConsumeOculusIAP", methods=["POST"])
def consume_oculus_iap():
    data = request.get_json()
    access_token = data.get("userToken")
    user_id = data.get("userID")
    nonce = data.get("nonce")
    sku = data.get("sku")

    response = requests.post(
        url=f"https://graph.oculus.com/consume_entitlement?nonce={nonce}&user_id={user_id}&sku={sku}&access_token={API_KEY}",
        headers={"content-type": "application/json"}
    )

    if response.json().get("success"):
        return jsonify({"result": True})
    return jsonify({"error": True})


@app.route("/api/photon", methods=["POST"])
def photonauth():
    print(f"Received {request.method} request at /api/photon")
    getjson = request.get_json()
    Ticket = getjson.get("Ticket")
    Nonce = getjson.get("Nonce")
    Platform = getjson.get("Platform")
    UserId = getjson.get("UserId")
    nickName = getjson.get("username")
    if request.method.upper() == "GET":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        userId = Ticket.split('-')[0] if Ticket else None
        print(f"Extracted userId: {UserId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        if Platform != 'Quest':
            return jsonify({
                'Error': 'Bad request',
                'Message': 'Invalid platform!'
            }), 403

        if Nonce is None:
            return jsonify({
                'Error': 'Bad request',
                'Message': 'Not Authenticated!'
            }), 304

        req = requests.post(
            url=f"https://{titleider}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers={
                "content-type": "application/json",
                "X-SecretKey": secretkey
            })

        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
            nickName = req.json().get("UserInfo",
                                      {}).get("UserAccountInfo",
                                              {}).get("Username")
            if not nickName:
                nickName = None

            print(
                f"Authenticated user {userId.lower()} with nickname: {nickName}"
            )

            return jsonify({
                'resultCode': 1,
                'message':
                f'Authenticated user {userId.lower()} title {titleider.lower()}',
                'userId': f'{userId.upper()}',
                'nickname': nickName
            })
        else:
            print("Failed to get user account info from PlayFab")
            return jsonify({
                'resultCode': 0,
                'message': "Something went wrong",
                'userId': None,
                'nickname': None
            })

    elif request.method.upper() == "POST":
        rjson = request.get_json()
        print(f"{request.method} : {rjson}")

        ticket = rjson.get("Ticket")
        userId = ticket.split('-')[0] if ticket else None
        print(f"Extracted userId: {userId}")

        if userId is None or len(userId) != 16:
            print("Invalid userId")
            return jsonify({
                'resultCode': 2,
                'message': 'Invalid token',
                'userId': None,
                'nickname': None
            })

        req = requests.post(
            url=f"https://{titleider}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": userId},
            headers={
                "content-type": "application/json",
                "X-SecretKey": secretkey
            })

        print(f"Authenticated user {userId.lower()}")
        print(f"Request to PlayFab returned status code: {req.status_code}")

        if req.status_code == 200:
            nickName = req.json().get("UserInfo",
                                      {}).get("UserAccountInfo",
                                              {}).get("Username")
            if not nickName:
                nickName = None
            return jsonify({
                'resultCode': 1,
                'message':
                f'Authenticated user {userId.lower()} title {titleider.lower()}',
                'userId': f'{userId.upper()}',
                'nickname': nickName
            })
        else:
            print("Failed to get user account info from PlayFab")
            successJson = {
                'resultCode': 0,
                'message': "Something went wrong",
                'userId': None,
                'nickname': None
            }
            authPostData = {}
            for key, value in authPostData.items():
                successJson[key] = value
            print(f"Returning successJson: {successJson}")
            return jsonify(successJson)
    else:
        print(f"Invalid method: {request.method.upper()}")
        return jsonify({
            "Message":
            "Use a POST or GET Method instead of " + request.method.upper()
        })


def ReturnFunctionJson(data, funcname, funcparam={}):
    print(f"Calling function: {funcname} with parameters: {funcparam}")
    rjson = data.get("FunctionParameter", {})
    userId = rjson.get("CallerEntityProfile",
                       {}).get("Lineage", {}).get("TitlePlayerAccountId")

    print(f"UserId: {userId}")

    req = requests.post(
        url=f"https://{titleider}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": userId,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers={
            "content-type": "application/json",
            "X-SecretKey": secretkey
        })

    if req.status_code == 200:
        result = req.json().get("data", {}).get("FunctionResult", {})
        print(f"Function result: {result}")
        return jsonify(result), req.status_code
    else:
        print(f"Function execution failed, status code: {req.status_code}")
        return jsonify({}), req.status_code


@app.route("/api/UploadGorillanalytics", methods=["POST"])
def Upload_Gorillanalytics():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400

    function_result = data.get("FunctionResult", {})

    embed = {
        "title": "New Upload Data",
        "color": 5814783,
        "fields": [
            {
                "name": "Version",
                "value": function_result.get("version", "N/A"),
                "inline": True,
            },
            {
                "name": "Upload Chance",
                "value": function_result.get("upload_chance", "N/A"),
                "inline": True,
            },
            {"name": "Map", "value": function_result.get("map", "N/A"), "inline": True},
            {
                "name": "Mode",
                "value": function_result.get("mode", "N/A"),
                "inline": True,
            },
            {
                "name": "Queue",
                "value": function_result.get("queue", "N/A"),
                "inline": True,
            },
            {
                "name": "Player Count",
                "value": str(function_result.get("player_count", "N/A")),
                "inline": True,
            },
            {
                "name": "Position",
                "value": f"({function_result.get('pos_x', 'N/A')}, {function_result.get('pos_y', 'N/A')}, {function_result.get('pos_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Velocity",
                "value": f"({function_result.get('vel_x', 'N/A')}, {function_result.get('vel_y', 'N/A')}, {function_result.get('vel_z', 'N/A')})",
                "inline": False,
            },
            {
                "name": "Cosmetics Owned",
                "value": function_result.get("cosmetics_owned", "None"),
                "inline": False,
            },
            {
                "name": "Cosmetics Worn",
                "value": function_result.get("cosmetics_worn", "None"),
                "inline": False,
            },
        ],
    }

    payload = {"embeds": [embed]}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        "https://discord.com/api/webhooks/1378202215155630170/T-1HsbICA-6b6Z4lhdeAFXjSz6kfgErAGPumXAc-0UVexeUtx-pvU6yZl9tDhoEtJYd-",
        json=payload,
        headers=headers,
    )

    if response.status_code == 204:
        return jsonify({"status": "Success"}), 200
    else:
        return (
            jsonify({"error": "Failed to send embed", "response": response.text}),
            500,
        )

@app.route("/api/GetFriendsV2", methods=['POST'])
def get_friends_v2():
    return jsonify({"result":{"friends":[{"presence":{"friendLinkId":"NO","userName":"JOIN CODE 1!","roomId":"1","zone":"forest","region":"US","isPublic":False},"created":"2001-09-11T08:46:01.713"}],"myPrivacyState":0},"statusCode":200,"error":None})

@app.route("/api/GetQuestStatus", methods=["POST"])
def GetQuestStatus():
    if playfab_id in ["56DD642DF40B6C83"]: return jsonify({"result": {"dailyPoints": {}, "weeklyPoints": {}, "userPointsTotal": 99999}, "statusCode": 200, "error": None}), 200
    return jsonify({"result": {"dailyPoints": {}, "weeklyPoints": {}, "userPointsTotal": 0}, "statusCode": 200, "error": None}), 200


@app.route("/", methods=["GET"])
def home():
    return "mama said i special"


if __name__ == "__main__":
    app.run(debug=True)
