import json

import requests

from app.logger import get_logger

logger = get_logger("tools")


def get_lark_token():
    app_id = "cli_a50254e4e43bd013"
    app_secret = "0PStyxmXLUnUKq5KvS5iCbmg8z4z6nkJ"
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    response = requests.post(url, json=payload)
    return response.json()["tenant_access_token"]


def post_msg(user_email, msg):
    logger.info(f"发送飞书消息：{msg}")
    token = get_lark_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    text = f"已调用修改工具，修改内容为：{msg}"
    params = {"receive_id_type": "email"}
    payload = {
        "receive_id": user_email,
        "content": json.dumps({"text": text}),
        "msg_type": "text",
    }
    try:
        response = requests.post(url, params=params, headers=headers, json=payload)
        response.raise_for_status()
        response_code = response.json()["code"]
        if response_code != 0:
            logger.error(f"飞书消息推送失败，错误代码：{response_code}")
            return False
        logger.info(f"飞书消息推送成功, Response: {response.json()}")
        return True
    except Exception as e:
        logger.error(f"飞书消息推送失败，错误信息：{e}")
        return False
