from flask import Flask, request, jsonify, Response
import requests
import json
import hashlib
import os
import re
from datetime import datetime
from datetime import date
import traceback
import logging
import random

app = Flask(__name__)

VOTING_WEBHOOK = "https://discord.com/api/webhooks/1520123760647213247/05BCXYwJkkrw2_mpQxWaRL6wC8Clp2Ex6_-K9iWvlyxhy-px7-NDWey7MXnyf0-lKOHU"
BAD_NONCE_WEBHOOK = "https://discord.com/api/webhooks/1520123760647213247/05BCXYwJkkrw2_mpQxWaRL6wC8Clp2Ex6_-K9iWvlyxhy-px7-NDWey7MXnyf0-lKOHU"
GOOD_NONCE_WEBHOOK = "https://discord.com/api/webhooks/1520123760647213247/05BCXYwJkkrw2_mpQxWaRL6wC8Clp2Ex6_-K9iWvlyxhy-px7-NDWey7MXnyf0-lKOHU"

ALLOWED_HOSTS = {
    "le6o.vercel.app",
    "lexotag623.vercel.app",
    "lexotag1234.vercel.app",
    "lex6ztag12345.vercel.app",
    "lexotag126456.vercel.app",
    "auth-lexotagz.vercel.app",
    "lexoz--tag.vercel.app",
    "lexoz123456.vercel.app",
    "le5zxtag19.vercel.app",
}

ALLOW_SYZ_VERCEL_WILDCARD = True
SYZ_VERCEL_RE = re.compile(r"^syz[a-z0-9-]*\.vercel\.app$", re.IGNORECASE)

@app.before_request
def _host_allowlist():
    host = (request.host or "").split(":")[0].lower()

    if host in ALLOWED_HOSTS:
        return None

    if ALLOW_SYZ_VERCEL_WILDCARD and SYZ_VERCEL_RE.match(host):
        return None

    # If you don't want host restrictions, comment this out entirely.
    return jsonify({"Error": "BadHost", "Message": f"Host not allowed: {host}"}), 403

class Info:
    def __init__(self):
        self.TitleId: str = "1C44C"
        self.SecretKey: str = "RSYXNOO3I1O16PHTWANPKYZ746MAUOIFEZN5WGUP5JOYDBXWIN"
        self.AppCreds: str = "OC|1089772264230160|e40335aa53cb5adb4d1a93d2e3ea2315"

    def ServerAuthHeaders(self):
        return {
            "Content-Type": "application/json",
            "X-SecretKey": self.SecretKey
        }

settings = Info()
friend_requests = {}

def ExecuteScript(FunctionName, FunctionParameter):
    getfr = request.get_json()
    TitlePlayerAccountId = getfr.get("FunctionParameter").get("CallerEntityProfile").get("Entity").get("Id")
    execute_req = requests.post(
        url = f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json = {
            "FunctionName": FunctionName,
            "PlayFabId": TitlePlayerAccountId,
            "FunctionParameter": FunctionParameter
        },
        headers = settings.ServerAuthHeaders()
    )
    if execute_req.status_code == 200:
        json = execute_req.json()
        return jsonify(json.get("data").get("FunctionResult")), response.status_code
    else:
        return jsonify({})

@app.route("/api/PlayFabAuthentication", methods = ["POST", "GET"])
def PlayFabAuthy():

    if "UnityPlayer" not in request.headers.get("User-Agent"):
        return Response(
            json.dumps({
                "BanMessage": "Your account has been traced and you have been banned.",
                "BanExpirationTime": "Indefinite"
            }, indent=1), mimetype="application/json"
        ), 403

    Required_Body_Stuff_Array = [
        "AppId",
        "Nonce",
        "OculusId",
        "Platform",
        "MothershipToken",
        "MothershipId"
    ]

    try:
        json_data = request.get_json()
        print(json.dumps(json_data, indent=2))
    except Exception as e:
        return jsonify({
            "Message": "Request body is missing or cannot be parsed.",
            "Error": "BadRequest-BadBody"
        }), 400

    AppId = json_data.get("AppId")
    AppVersion = json_data.get("AppVersion")
    Nonce = json_data.get("Nonce")
    OculusId = json_data.get("OculusId")
    Platform = json_data.get("Platform")
    AgeCategory = json_data.get("AgeCategory")
    MothershipEnvId = json_data.get("MothershipEnvId") or "prod"
    MothershipToken = json_data.get("MothershipToken")
    MothershipId = json_data.get("MothershipId")

    effective_mothership_id = MothershipId or (request.host.split(":")[0] if request.host else "unknown")
    
    if AppId is None:
        return jsonify({
            "Message": "Missing AppId parameter",
            "Error": "BadRequest-NoAppId"
        }), 400

    if AppId != settings.TitleId:
        return jsonify({
            "Message": "Wrong AppId parameter",
            "Error": "BadRequest-WrongAppId"
        }), 400

    if Nonce is None:
        return jsonify({
            "Message": "Missing Nonce parameter",
            "Error": "BadRequest-NoNonce"
        }), 400

    if Platform is None:
        return jsonify({
            "Message": "Missing Platform parameter",
            "Error": "BadRequest-NoPlatform"
        }), 400

    if Platform != "Quest":
        return jsonify({
            "Message": f"Invalid Platform parameter: {Platform}",
            "Error": "BadRequest-InvalidPlatform"
        }), 400

    if OculusId is None:
        return jsonify({
            "Message": "Missing OculusId parameter",
            "Error": "BadRequest-NoOculusId"
        }), 400

    
    VerifyNonceReq = requests.post(
        url="https://graph.oculus.com/user_nonce_validate",
        json={
            "access_token": settings.AppCreds,
            "nonce": Nonce,
            "user_id": OculusId
        },
        headers={
            "Content-Type": "application/json"
        }
    )

    print(json.dumps(VerifyNonceReq.json(), indent=2))

    OrgscopeIdReq = requests.get(
        url=f"https://graph.oculus.com/{OculusId}?access_token={settings.AppCreds}&fields=org_scoped_id",
        headers={
            "Content-Type": "application/json"
        }
    )

    print(json.dumps(OrgscopeIdReq.json(), indent=2))

    OrgScope = OrgscopeIdReq.json().get("org_scoped_id")
    CustomId = f"OCULUS{OrgScope}"

    BAD_NONCE_EMBED = {
        "embeds": [{
            "title": "-----❌ A User Has A Invalid Nonce + Custom Id ❌-----",
            "description": "**⬇️ Details ⬇️**" + "\n" + "```ini" + "\n" + "[Nonce] : " + str(Nonce) + "```",
            "color": 16711935
        }]
    }

    GOOD_NONCE_EMBED = {
        "embeds": [{
            "title": "-----🟢 A User Has Logged In With A Valid Nonce + Custom Id 🟢-----",
            "description": "**⬇️ Details ⬇️**" + "\n" + "```ini" + "\n" + "[Nonce] : " + Nonce + "```",
            "color": 65280
        }]
    }

    nonceJson = VerifyNonceReq.json()

    if VerifyNonceReq.status_code != 200 or nonceJson.get("is_valid") is not True:
        print(f"User: {CustomId} Has Failed The Nonce Verification. Nonce: {Nonce}")
        requests.post(url=BAD_NONCE_WEBHOOK, json=BAD_NONCE_EMBED)
        return jsonify({
            "Message": "Failed Nonce Verification",
            "Error": "BadRequest-InvalidNonce"
        }), 400

    if nonceJson.get("is_valid") == True:
        print(f"User: {CustomId} Has Passed The Nonce Verification. Nonce: {Nonce}")
        requests.post(url=GOOD_NONCE_WEBHOOK, json=GOOD_NONCE_EMBED)


    login_request = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId",
        json={
            "ServerCustomId": CustomId,
            "CreateAccount": True
        },
        headers=settings.ServerAuthHeaders()
    )

    if login_request.status_code == 200:
        luckywallsurfer = login_request.json().get("data")

        SessionTicket = luckywallsurfer.get("SessionTicket")
        EntityToken = luckywallsurfer.get("EntityToken").get("EntityToken")
        PlayFabId = luckywallsurfer.get("PlayFabId")
        EntityId = luckywallsurfer.get("EntityToken").get("Entity").get("Id")
        EntityType = luckywallsurfer.get("EntityToken").get("Entity").get("Type")

        print(json.dumps(luckywallsurfer, indent=2))

        link_request = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Client/LinkCustomID",
            json={
                "CustomId": CustomId,
                "ForceLink": True
            },
            headers={
                "Content-Type": "application/json",
                "X-Authorization": SessionTicket
            }
        )

        AccountCreationIsoTimestamp_req = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo",
            json={"PlayFabId": PlayFabId},
            headers=settings.ServerAuthHeaders()
        )

        AccountCreationIsoTimestamp = AccountCreationIsoTimestamp_req.json().get("data").get("UserInfo").get("Created")

        response_body = {
            "SessionTicket": SessionTicket,
            "EntityToken": EntityToken,
            "PlayFabId": PlayFabId,
            "EntityId": EntityId,
            "EntityType": EntityType,
            "AccountCreationIsoTimestamp": AccountCreationIsoTimestamp
        }

        print(json.dumps(response_body, indent = 2))

        return jsonify({
            "SessionTicket": SessionTicket,
            "EntityToken": EntityToken,
            "PlayFabId": PlayFabId,
            "EntityId": EntityId,
            "EntityType": EntityType,
            "AccountCreationIsoTimestamp": AccountCreationIsoTimestamp,

            "MothershipEnvId": MothershipEnvId,
            "MothershipId": effective_mothership_id
        }), 200

    elif login_request.status_code == 403:
        ban_info = login_request.json()

        if ban_info.get("errorCode") == 1002:
            BanDetails = ban_info.get("errorDetails", {})
            BanReason = next(iter(BanDetails.keys()), None)
            BanTime = BanDetails.get(BanReason, [])
            BanExpirationTime = BanTime[0] if BanTime else "NO EXPIRATION TIME PROVIDED."

            print(json.dumps(ban_info, indent=2))

            return jsonify({
                "BanMessage": BanReason,
                "BanExpirationTime": BanExpirationTime
            }), 403
    else:
        return jsonify({"Error": "Unknown", "Message": "Something Happened"}), login_request.status_code


@app.route("/api/ReturnQueueStats", methods = ["POST"])
def ReturnQueueStats():
    rjson = request.get_json("FunctionArgument")
    QueueName = rjson.get("queueName")
    return jsonify({"QueueName": QueueName, "PlayerCount": -1}), 200


@app.route("/api/CheckForBadName", methods = ["POST"])
def CheckForBadName():
    rjson = request.get_json("FunctionArgument")
    name = rjson.get("name")
    forRoom = rjson.get("forRoom")
    return jsonify({"result": 0, "banLength": -1}), 200

@app.route("/", methods=["POST", "GET"])

def main():

  if request.method != "POST":
      return "", 404

@app.route("/api/GetAcceptedAgreements", methods = ["POST"])
def GetAcceptedAgreements():
    rjson = request.get_json("FunctionArgument")
    TOS = rjson.get("TOS", "11.05.22.2")
    PrivacyPolicy = rjson.get("PrivacyPolicy", "2024.03.07")
    return jsonify({"TOS": TOS, "PrivacyPolicy": PrivacyPolicy}), 200

@app.route("/api/photon", methods = ["POST", "GET"])
def LuckysAnyUpdatePhotonAuth():
    print(f"Received {request.method} request at /api/photon")
    
    AuthTicketUrl = f"https://{settings.TitleId}.playfabapi.com/Server/AuthenticateSessionTicket"

    # { ResultCode: 1, Message: "optional Auth OK message" }
    # { ResultCode: 2, Message: "optional Auth Failed message" }
    # { ResultCode: 3, Message: "optional Parameter invalid message" }
    # All Those Are From https://github.com/exitgames/photon.custom-authentication

    VALID_APPS = [f"{settings.TitleId}", "35D50", "35D50", "35D50", "35D50", "35D50"] # Replace With TitleIds That You Want This To Accept.
    
    # In OLD Updates The Method Is "GET" Rather Than "POST"
    if request.method == "GET":
        
        PlayerId = request.args.get("username")
        
        token = request.args.get("token")
        
        if not PlayerId or not token:
            return jsonify({
                "resultCode": 3,
                "message": "Failed to parse token from request",
                "userId": None,
                "nickname": None
            }), 400

        # If The User Did Not Set Off That Then Do This:
        print(f"Player: {PlayerId} Has Authed In Old Update.")
        return jsonify({
            "resultCode": 1,
            "message": f"User: {PlayerId} Was Authed.",
            "username": PlayerId,
            "token": token
        }), 200

    # In NEW Updates The Method Is "POST" Rather Than "GET"
    elif request.method == "POST":
        
        newData = request.get_json()
        
        AppId = newData.get("AppId")
        
        AppVersion = newData.get("AppVersion")
        
        Ticket = newData.get("Ticket")
        
        Token = newData.get("Token")
        
        Nonce = newData.get("Nonce")
        
        Platform = newData.get("Platform")

        print(json.dumps(newData, indent = 2))

        if AppId not in VALID_APPS:
            print(f"Invalid AppId: {AppId}")
            return jsonify({
                "ResultCode": 2,
                "Message": "Invalid AppId parameter",
                "Error": "BadRequest-WrongAppId"
            }), 403
    
        if Platform != "Quest":
            print("Users Platform Is Not Quest")
            return jsonify({
                "Error": "Bad request",
                "ResultCode": 3, 
                "Message": "Platform Must Be Quest Fella"
            }), 403
            

        AuthSessionTicketReq = requests.post(url = AuthTicketUrl, json = {"SessionTicket": Ticket}, headers = settings.ServerAuthHeaders())
        print(AuthSessionTicketReq)
        
        if AuthSessionTicketReq.status_code != 200:
            print(f"SessionTicket: {Ticket} Is Invalid")
            return jsonify({
                "ResultCode": 2,
                "Message": "Invalid SessionTicket parameter",
                "Error": "BadRequest-BadSessionTicket"
            }), 403

        if AuthSessionTicketReq.status_code == 200:
            
            getdata = AuthSessionTicketReq.json().get("data").get("UserInfo", {})

            UserId = getdata.get("PlayFabId")
            
            CustomId = getdata.get("CustomIdInfo", {}).get("CustomId")
            
            OrgScopedCustomId = CustomId.split("OCULUS")[1]
            
            print(f"OrgScopedCustomId: {OrgScopedCustomId}")

            OrgScopeUrl = f"https://graph.oculus.com/{OrgScopedCustomId}?access_token={settings.AppCreds}"

            GetOculusIdReq = requests.get(url = OrgScopeUrl, headers = {"Content-Type": "application/json"})

            if "error" in GetOculusIdReq.json():
                print("User Did Not Pass The OrgScope Check.")
                return jsonify({
                    "ResultCode": 3,
                    "Message": "Did Not Pass OrgScopeId Checker",
                    "Error": "BadRequest-IvalidOrgScopeId"
                }), 403

            if UserId is None or len(UserId) != 16:
                print(f"UserId: {UserId} Is Not 16 Characters Long.")
                return jsonify({
                    "ResultCode": 3,
                    "Message": "Did Not UserId Length Checker",
                    "Error": "BadRequest-BadUserId"
                }), 403

            OculusId = GetOculusIdReq.json().get("id")
            print(f"Users OculusId Is: {OculusId}")

            VerifyNonceReq = requests.post(

                url = "https://graph.oculus.com/user_nonce_validate", # Go To https://developers.meta.com/horizon/documentation/native/ps-ownership/ For The Docs For This
        
                json = {
                
                	"access_token": f"{settings.AppCreds}",
                	"nonce": newData.get("Nonce"),
                	"user_id": f"{OculusId}"
                    
                },
        
                headers = {
                    
                    "Content-Type": "application/json"
                    
                }
                
            )

            print(VerifyNonceReq.json())
            nonce_json_data = VerifyNonceReq.json()

            if VerifyNonceReq.status_code != 200 or "is_valid" not in nonce_json_data:
                print(f"User: {UserId} Has Failed The Nonce Verification. Nonce: {Nonce}")
                return jsonify({
                    "ResultCode": 1,
                    "Message": "Failed Nonce Verification",
                    "Error": "BadRequest-InvalidNonce"
                }), 403

            # If User Passes All Checks:
            print(f"{UserId} Was Authed Succesfully.")
            return jsonify({
                
                "ResultCode": 1,
                
                "Message": "Yay Servers Work Ig",
                
                "AppId": AppId,
                
                "AppVersion": AppVersion,
                
                "Nonce": Nonce,
                
                "OculusId": OculusId,
                
                "Ticket": Ticket,
                
                "Token": Token,
                
                "UserId": UserId
                
            }), 200

@app.route("/api/SubmitAcceptedAgreements", methods = ["POST"])
def SubmitAcceptedAgreements():
    rjson = request.get_json("FunctionArgument")
    TOS = rjson.get("TOS", "11.05.22.2")
    PrivacyPolicy = rjson.get("PrivacyPolicy", "2024.03.07")
    return "Agreements submitted successfully", 200

@app.route('/api/TitleData', methods=['POST', 'GET'])
@app.route('/api/TD', methods=['POST', 'GET'])
def titledata():
    response_data = {
        "AutoMuteCheckedHours": {
            "hours": 169
        },
        "AutoName_Adverbs": [
            "Cool", "Fine", "Bald", "Bold", "Half", 
            "Only", "Calm", "Fab", "Ice", "Mad", 
            "Rad", "Big", "New", "Old", "Shy"
        ],
        "AutoName_Nouns": [
            "Gorilla", "Chicken", "Darling", "Sloth", "King", 
            "Queen", "Royal", "Major", "Actor", "Agent", 
            "Elder", "Honey", "Nurse", "Doctor", "Rebel", 
            "Shape", "Ally", "Driver", "Deputy"
        ],
        "CreditsData": [
            {
                "Title": "<color=blue>FOUNDERS</color>",
                "Entries": [
                    "DARKVR"                ]
            },
            {
                "Title": "<color=yellow>CREDITS TO</color>",
                "Entries": [
                    "DARKVR"                ]
            },
            {
                "Title": "<color=red>GOOD BOYS</color>",
                "Entries": [
                    "NOBODY"                ]
            }
        ],
        "BundleBoardSign": "<color=#ff4141>https://discord.gg/LEXOTAG</color>",
        "BundleKioskButton": "<color=#ff4141>https://discord.gg/LEXOTAG</color>",
        "BundleKioskSign": "<color=#ff4141>https://discord.gg/LEXOTAG</color>",
        "BundleLargeSign": "<color=#ff4141https://discord.gg/LEXOTAG</color>",
        "EmptyFlashbackText": "FLOOR TWO NOW OPEN\n FOR BUSINESS\n\nSTILL SEARCHING FOR\nBOX LABELED 2021",
        "EnableCustomAuthentication": True,
        "GorillanalyticsChance": 4320,
        "LatestPrivacyPolicyVersion": "2024.09.20",
        "LatestTOSVersion": "2024.09.20",
        "MOTD": "<color=#bb29ff>WELCOME TO LEXO TAG</color>\n\n<color=#07dde8>SNOWBALL FIGHT</color>\n\n<color=#ffff00>CREATOR/FOUNDER: DARKVR + LUXO</color>\n\n<color=#969696>BACKENDS CREDS: LICENSE + HATRED</color>\n\n<color=#ff8800>DISCORD: https://discord.gg/LEXOTAG</color>",
        "SeasonalStoreBoardSign": "<color=yellow>RATE THE GAME 5 STARS!</color>\n\n<color=aqua>https://discord.gg/LEXOTAG",
        "TOS_2024.09.20": "https://discord.gg/LEXOTAG",
        "TOBAlreadyOwnCompTxt": "https://discord.gg/LEXOTAG",
        "TOBAlreadyOwnPurchaseBundle": "LEXOTAG",
        "TOBDefCompTxt": "https://discord.gg/LEXOTAG",
        "TOBDefPurchaseBtnDefTxt": "LEXOTAG",
        "UseLegacyIAP": False
    }
    return jsonify(response_data)
    
@app.route("/api/GetQuestStatus", methods=["POST"])
def get_quest_status_norm():

  hawk2 = request.get_json()

  PlayFabId = hawk2.get("PlayFabId")
  PlayFabTicket = hawk2.get("PlayFabTicket")

  daily_points = {"quest1": random.randint(5, 20), "quest2": random.randint(5, 20)}
  weekly_points = {1: random.randint(10, 50), 2: random.randint(10, 50)}
  user_points_total = random.randint(100, 500)
  weekly_points_total = min(sum(daily_points.values()) + sum(weekly_points.values()), 100)

  return jsonify({
      "result": {
          "dailyPoints": daily_points,
          "weeklyPoints": weekly_points,
          "userPointsTotal": user_points_total,
          "weeklyPointsTotal": weekly_points_total
      }
  })

@app.route("/api/SetQuestComplete", methods=["POST", "GET"])
def setwestcompleter():

  json = request.get_json()

  PlayFabId = json.get("PlayFabId")
  PlayFabTicket = json.get("PlayFabTicket")
  QuestId = json.get("QuestId")
  ClientVersion = json.get("ClientVersion")

  daily_points = {"quest1": random.randint(5, 20), "quest2": random.randint(5, 20)}
  weekly_points = {1: random.randint(10, 50), 2: random.randint(10, 50)}
  user_points_total = random.randint(100, 500)
  weekly_points_total = min(sum(daily_points.values()) + sum(weekly_points.values()), 100)

  return jsonify({
      "result": {
          "dailyPoints": daily_points,
          "weeklyPoints": weekly_points,
          "userPointsTotal": user_points_total,
          "weeklyPointsTotal": weekly_points_total
      }
  })

# Discord webhook URL for logging (replace with your actual webhook)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1520135788631822479/j_iEaHtzoHC1oDyEWQgu7nUZ9PngwKpJY53qErAP0REB-YAfvamdyzp0lQdVHpHBkiQv"

# Store friend relationships in memory (simple for demo)
friend_requests = {}        # { PlayFabId: set(friend_playfab_ids) }
friend_usernames = {}       # cache PlayFabId -> DisplayName
friend_presence = {}        # { PlayFabId: { Zone, RoomId, Region, IsPublic } }

def log_to_discord_webhook(message, webhook_url):
    try:
        requests.post(webhook_url, json={"content": message}, timeout=5)
    except Exception as e:
        print(f"Failed to send Discord log: {e}")

def get_username_from_playfab(playfab_id):
    url = f"https://{settings.TitleId}.playfabapi.com/Server/GetUserAccountInfo"
    payload = {"PlayFabId": playfab_id}
    headers = {
        "Content-Type": "application/json",
        "X-SecretKey": settings.SecretKey
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Log full response to Discord for debugging
        log_to_discord_webhook(f"PlayFab GetUserAccountInfo Response for {playfab_id}:\n```json\n{json.dumps(data, indent=2)}\n```", DISCORD_WEBHOOK_URL)

        username = data.get("data", {}).get("UserInfo", {}).get("TitleInfo", {}).get("DisplayName")
        if username:
            friend_usernames[playfab_id] = username
            return username

    except Exception as e:
        log_to_discord_webhook(f"PlayFab GetUserAccountInfo error for {playfab_id}: {e}", DISCORD_WEBHOOK_URL)

    # fallback username if no display name found
    return f"User_{playfab_id}"

@app.route("/api/RequestFriend", methods=["POST"])
def add_fwen():
    fwen = request.get_json()

    id = fwen.get("PlayFabId")
    ticket = fwen.get("PlayFabTicket")
    my_link_id = fwen.get("MyFriendLinkId")
    their_link_id = fwen.get("FriendFriendLinkId")

    if id and their_link_id:
        if id not in friend_requests:
            friend_requests[id] = set()
        friend_requests[id].add(their_link_id)

        if their_link_id not in friend_requests:
            friend_requests[their_link_id] = set()
        friend_requests[their_link_id].add(id)

    response = {
        "success": True,
        "message": "Friend request sent.",
        "PlayFabId": id,
        "FriendFriendLinkId": their_link_id
    }

    log_to_discord_webhook(f"/api/RequestFriend Request:\n{json.dumps(fwen)}\nResponse:\n{json.dumps(response)}", DISCORD_WEBHOOK_URL)

    return jsonify(response)

@app.route("/api/GetFriendsV2", methods=["POST"])
def get_fwens_v2():
    fwen = request.get_json()

    id = fwen.get("PlayFabId")

    if not id or id not in friend_requests:
        response = {
            "result": {"Friends": [], "myPrivacyState": 0},
            "PlayFabId": id,
            "PlayFabTicket": fwen.get("PlayFabTicket")
        }
        log_to_discord_webhook(f"/api/GetFriendsV2 Request:\n{json.dumps(fwen)}\nResponse:\n{json.dumps(response)}", DISCORD_WEBHOOK_URL)
        return jsonify(response), 200

    friends_list = []
    for friend_id in friend_requests[id]:
        username = friend_usernames.get(friend_id)
        if not username:
            username = get_username_from_playfab(friend_id)

        presence_info = friend_presence.get(friend_id, {
            "Zone": fwen.get("Zone"),
            "RoomId": fwen.get("RoomId"),
            "Region": fwen.get("Region"),
            "IsPublic": fwen.get("IsPublic")
        })

        friends_list.append({
            "Presence": {
                "FriendLinkId": friend_id,
                "UserName": username,
                **presence_info
            },
            "Created": "2025-03-21T08:46:01.713"
        })

    response = {
        "result": {
            "Friends": friends_list,
            "myPrivacyState": 1
        },
        "PlayFabId": id,
        "PlayFabTicket": fwen.get("PlayFabTicket")
    }

    log_to_discord_webhook(f"/api/GetFriendsV2 Request:\n{json.dumps(fwen)}\nResponse:\n{json.dumps(response)}", DISCORD_WEBHOOK_URL)

    return jsonify(response), 200

@app.route("/api/RemoveFriend", methods=["POST"])
def remove_fren():
    r = request.get_json()

    pf_id = r.get("PlayFabId")
    pf_ticket = r.get("PlayFabTicket")
    my_link_id = r.get("MyFriendLinkId")
    their_fren_id = r.get("FriendFriendLinkId")

    if pf_id in friend_requests and their_fren_id in friend_requests[pf_id]:
        friend_requests[pf_id].remove(their_fren_id)
        if their_fren_id in friend_requests and pf_id in friend_requests[their_fren_id]:
            friend_requests[their_fren_id].remove(pf_id)

    response = {
        "success": True,
        "message": "Friend removed.",
        "PlayFabId": pf_id,
        "FriendFriendLinkId": their_fren_id
    }

    log_to_discord_webhook(f"/api/RemoveFriend Request:\n{json.dumps(r)}\nResponse:\n{json.dumps(response)}", DISCORD_WEBHOOK_URL)

    return jsonify(response)

@app.route("/api/SetPrivacyState", methods=["POST"])
def set_privacy_state():
    f = request.get_json()

    pf_id = f.get("PlayFabId")
    ticket = f.get("PlayFabTicket")
    priv_state = f.get("PrivacyState")

    # You may want to store privacy state somewhere; currently just returning success

    response = {
        "StatusCode": 200,
        "Error": None
    }

    log_to_discord_webhook(f"/api/SetPrivacyState Request:\n{json.dumps(f)}\nResponse:\n{json.dumps(response)}", DISCORD_WEBHOOK_URL)

    return jsonify(response)


@app.route("/api/GetUserAge", methods = ["POST"])
def GetUserAge():
    return -1


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
