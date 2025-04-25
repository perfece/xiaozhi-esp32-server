import requests
from bs4 import BeautifulSoup
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action

TAG = __name__
logger = setup_logging()

GET_SYQ_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "get_syq",
        "description": (
            "获取水雨情实时数据意图，只包括以下场景：\n"
            "查询xx水库（当前/现在）的水位是多少\n"
            "查询xx水库（当前/现在）的雨量是多少\n"
            "查询xx市面雨量是多少\n"
            "查询xx水库最大x小时降雨量是多少\n"
            "分析xx市今日的降雨情况\n"
            "分析xx市江河水位情况\n"
            f"(注意区分，上述的“水位”是动态值，走此实时水雨情实时数据意图。与“校核水位”、“死水位”、“汛限水位”等静态水利工程属性是不同概念，而问到水利工程静态属性相关问题时不属于该意图，属于“continue_chat”继续聊天的意图；上述的雨量/降雨量查询场景跟天气没关系)"

        ),
        "parameters": {"type": "object", "properties": {
                "query": {
                    "type": "string",
                    "description": "用户问题"
                }
        }, "required": []},
    }
}

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    )
}


# 正则服务url
query_intent_by_reg_url = "https://zszx.dcyun.com:48468/water-kc-rasa/rasa/manage/regexQa/getRegexChat"

def get_intent_by_reg(query):
    '''
    获取意图_by reg
    :param query:
    :return:
    '''
    logger.info("-->调用reg正则服务")
    try:
        req_param = {
            "sender": "951ebff181194d389f2a46f50070bca1",
            "message": query
            #, "sessionId":"",
            # "index":1,
        }
        resp = requests.post(query_intent_by_reg_url, json=req_param, verify=False)
        if resp.status_code != 200:
            logger.error(f"--->reg正则接口响应错误：{resp.status_code}")
            return None
        data = resp.json()
        logger.info(f"--->reg正则接口响应：{data}")
        if data and 0 == data['status']:
            message = data['message']

            # 响应内容,优先从message.content中取
            content = message
            if 'content' in message:
                content = message['content']
            # 是否二次问询
            if 'secondQa' in message and "1" == message['secondQa']:
                logger.info("-->二次问询")
                # 接口名
                operation = message['operation']
                # 接口地址
                operation_url = message['operationUrl']
                # 入参取值
                list = message['list']
                # todo 处理二次问询
                logger.info("-->正则服务，需要二次问询", content)
                return content
            elif content:
                # 响应内容
                logger.info(f"-->正则服务响应内容:{content}")
                return content
        return None
    except Exception as e:
        logger.error("-->获取reg意图异常 {}".format(e))
        return None


@register_function('get_syq', GET_SYQ_FUNCTION_DESC, ToolType.SYSTEM_CTL)
def get_syq(conn, query: str):
    resp = get_intent_by_reg(query)
    if not resp:
        return ActionResponse(Action.RESPONSE, "未查询到相关实时数据", "未查询到相关实时数据")
    syq_resp = (
        f" {resp}\n"
        f"(直接给出答案)"
    )

    return ActionResponse(Action.RESPONSE, syq_resp, resp)