import requests
from config.logger import setup_logging
from plugins_func.register import register_function, ToolType, ActionResponse, Action
import asyncio
import os,json
from core.utils.util import (
    get_string_no_punctuation_or_emoji,
)
TAG = __name__
logger = setup_logging()

GET_DIFY_GCJJ_FUNCTION_DESC = {
    "type": "function",
    "function": {
        "name": "get_dify_gcjj",
        "description": (
            "获取水库工程简历的意图，只包括以下场景：\n"
            "xx水库的工程简历简报|xx水库生命周期的历程\n"
        ),
        "parameters": {"type": "object", "properties": {
                "query": {
                    "type": "string",
                    "description": "用户问题"
                } ,
                # "inputs": {
                #     "type": "string",
                #     "description": "自定义参数,固定值为空dict：｛｝"
                # },
                # "response_mode": {
                #     "type": "string",
                #     "description": "响应模式，固定值为：streaming"
                # },
                # "user": {
                #     "type": "string",
                #     "description": "用户标识，固定值为：dcrobot"
                # }
        }, "required": []},
    }
}

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    ),
    'Authorization':'Bearer app-tbhxQOBRwmaHBKQDAGH5g9pd'

}


# 流式接口url(dify_工程简介)
STREAM_API_URL = "http://192.168.2.175:4080/v1/chat-messages"
API_KEY='app-tbhxQOBRwmaHBKQDAGH5g9pd'
STREAM = "stream"
async def get_stream_api(conn,query):
    '''
    查询流式接口
    :param query:
    :return:
    '''
    logger.info("-->调用dify_工程简介服务")
    request_json = {
        "query": query,
        "inputs": {},
        "response_mode": "streaming",
        "user": "dcrobot_0001"
    }
    try:
        # 发起流式请求
        with requests.post(
                f"{STREAM_API_URL}",
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json",
                         "Accept": "application/json"},
                json= request_json,
                stream= STREAM,
                timeout=60

        ) as r:
            text = ""
            is_finished = False
            for line in r.iter_lines():
                if line:
                    if line.startswith(b'data'):
                        data = json.loads(line[6:])
                        title_text = ""
                        ans_text = ""
                        if 'event' in data:
                            if data['event'] == 'node_started' and data['data']['node_type'] != 'answer':
                                logger.info(f"-->dify_工程简介服务节点：{data['data']['title']}")
                                title_text = "正在"+data['data']['title']
                            elif data['event'] == 'message':
                                logger.info(f"-->dify_工程简介服务message：{data['answer']}")
                                ans_text = data['answer']
                                text += ans_text.strip()
                            elif data['event'] == 'message_end':
                                logger.info(f"-->dify_工程简介服务message_end")
                                is_finished=True
                        text_index = 0
                        if title_text.strip():
                            # 进行播报: 节点标题
                            logger.info(f"-->dify_工程简介服务 title_text:{title_text}")
                            conn.recode_first_last_text(title_text.strip(), text_index)
                            future = conn.executor.submit(
                                conn.speak_and_play, title_text.strip(),text_index
                            )
                            conn.tts_queue.put(future)

                        # if len(text)>10 or (is_finished and len(text)>0):
                        #     # 进行播报: 节点标题 or 正文拼接长度>10 or 最后接收完了
                        #     logger.info(f"-->dify_工程简介服务 txt：{text},title_text:{title_text},is_f:{is_finished}")
                        #     conn.recode_first_last_text(text[:10], text_index)
                        #     future = conn.executor.submit(
                        #         conn.speak_and_play, text[:10],text_index
                        #     )
                        #     conn.tts_queue.put(future)
                        #     text = text[10:]

                        # 查找最后一个有效标点
                        punctuations = ("。", "？", "！", "；", "：")
                        last_punct_pos = -1
                        for punct in punctuations:
                            pos = text.rfind(punct)
                            if pos > last_punct_pos:
                                last_punct_pos = pos

                        # 找到分割点则处理
                        if last_punct_pos != -1:
                            segment_text_raw = text[: last_punct_pos + 1]
                            segment_text = get_string_no_punctuation_or_emoji(segment_text_raw)
                            if segment_text:
                                text_index += 1
                                conn.recode_first_last_text(segment_text, text_index)
                                future = conn.executor.submit(
                                    conn.speak_and_play, segment_text, text_index
                                )
                                conn.tts_queue.put(future)
                                logger.info(f"-->dify_工程简介服务 text：{text}")
                                # text = text[last_punct_pos:]

    except Exception as e:
        logger.error("-->调用dify_工程简介服务异常 {}".format(e))

@register_function('get_dify_gcjj', GET_DIFY_GCJJ_FUNCTION_DESC, ToolType.SYSTEM_CTL)
def get_dify_gcjj(conn, query: str):
    try:
        # 检查事件循环状态
        if not conn.loop.is_running():
            logger.bind(tag=TAG).error("事件循环未运行，无法提交任务")
            return ActionResponse(
                action=Action.RESPONSE, result="智小川忙不过来了", response="智小川忙不过来了"
            )

        # 提交异步任务
        future = asyncio.run_coroutine_threadsafe(
            get_stream_api(conn, query), conn.loop
        )

        # 非阻塞回调处理
        def handle_done(f):
            try:
                ret = f.result()  # 可在此处理成功逻辑
                logger.bind(tag=TAG).info(f"智能体_工程简历完成:{ret}")
            except Exception as e:
                logger.bind(tag=TAG).error(f"智能体_工程简历失败: {e}")

        future.add_done_callback(handle_done)

        return ActionResponse(
            action=Action.NONE, result="正在为您查询", response="正在为您查询"
        )
    except Exception as e:
        logger.bind(tag=TAG).error(f"处理智能体_工程简历意图错误: {e}")
        return ActionResponse(
            action=Action.RESPONSE, result=str(e), response="智能体_工程简历出错了"
        )