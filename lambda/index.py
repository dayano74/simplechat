# lambda/index.py

import json
import os
from urllib import request, parse

def lambda_handler(event, context):
    try:
        # 1) 受け取った JSON ボディを解析
        body = json.loads(event["body"])
        message = body.get("message", "")
        conversation_history = body.get("conversationHistory", [])
        
        # 2) FastAPI 側に投げるペイロードを作成
        payload_dict = {
            "message": message,
            "conversationHistory": conversation_history
        }
        payload = json.dumps(payload_dict).encode("utf-8")
        
        # 3) .env で設定した URL を取得
        fastapi_url = os.environ["FASTAPI_URL"]
        api_endpoint = fastapi_url.rstrip("/") + "/predict"
        
        # 4) urllib.request で POST リクエスト
        req = request.Request(
            api_endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with request.urlopen(req) as res:
            res_body = json.loads(res.read().decode())
        
        # 5) FastAPI のレスポンスを取り出して返却用にセット
        assistant_response    = res_body.get("response", "")
        new_conversation_hist = res_body.get("conversationHistory", [])
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers":  "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods":  "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": new_conversation_hist
            })
        }
        
    except Exception as error:
        # エラー発生時の返却
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers":  "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods":  "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
