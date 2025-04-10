import json
from config.logger import setup_logging
import requests
from core.providers.llm.base import LLMProviderBase
from core.providers.intent.base import IntentProviderBase

from core.providers.intent.intent_llm.intent_llm import IntentProvider

TAG = __name__
logger = setup_logging()


# def get_intent_system_prompt() -> str:
#     """
#     根据配置的意图选项动态生成系统提示词
#     Returns:
#         格式化后的系统提示词
#     """
#     intent_options = [
#         {
#             "name": "handle_exit_intent",
#             "desc": "结束聊天, 用户发来如再见之类的表示结束的话, 不想再进行对话的时候",
#         },
#         {
#             "name": "play_music",
#             "desc": "播放音乐, 用户希望你可以播放音乐, 只用于播放音乐的意图",
#         },
#         {"name": "get_time", "desc": "获取今天日期或者当前时间信息"},
#         {"name": "continue_chat", "desc": "继续聊天"},
#         {"name": "get_weather", "desc": "获取天气的意图"},
#         # ，参数location返回地名，如杭州；参数lang返回用户使用的语言code，例如zh_CN/zh_HK/en_US/ja_JP等，默认zh_CN"},
#         {"name": "get_news", "desc": "获取新闻的意图"},
#         {"name": "change_role", "desc": "切换角色意图"},
#     ]
#     prompt = (
#         "你是一个意图识别助手。请分析用户的最后一句话，判断用户意图属于以下哪一类：\n"
#         "<start>"
#         f"{str(intent_options)}"
#         "<end>\n"
#         "处理步骤:"
#         "1. 思考意图类型，生成function_call格式"
#         "\n\n"
#         "返回格式示例：\n"
#         '1. 播放音乐意图: {"function_call": {"name": "play_music", "arguments": {"song_name": "音乐名称"}}}\n'
#         '2. 结束对话意图: {"function_call": {"name": "handle_exit_intent", "arguments": {"say_goodbye": "goodbye"}}}\n'
#         '3. 获取当天日期时间: {"function_call": {"name": "get_time"}}\n'
#         '4. 继续聊天意图: {"function_call": {"name": "continue_chat"}}\n'
#         '5. 获取天气意图: {"function_call": {"name": "get_weather", "arguments": {"location": "地名","lang":"返回用户使用的语言code，例如zh_CN/zh_HK/en_US/ja_JP等，默认zh_CN"}}}\n'
#         '6. 获取新闻意图: {"function_call": {"name": "get_news", "arguments": {"category": "新闻类别","detail":"默认为false","lang":"返回用户使用的语言code，默认zh_CN"}}}\n'
#         '7. 切换角色意图: {"function_call": {"name": "change_role", "arguments": {"role_name": "要切换的角色名字","role":"要切换的角色，可选的角色有：[机车女友,英语老师,好奇小男孩]"}}}\n'
#         "\n"
#         "注意:\n"
#         '- 播放音乐：无歌名时，song_name设为"random"\n'
#         "- 如果没有明显的意图，应按照继续聊天意图处理\n"
#         "- 只返回纯JSON，不要任何其他内容\n"
#         "\n"
#         "示例分析:\n"
#         "```\n"
#         "用户: 你也太搞笑了\n"
#         '返回: {"function_call": {"name": "continue_chat"}}\n'
#         "```\n"
#         "```\n"
#         "用户: 现在是几号了?现在几点了？\n"
#         '返回: {"function_call": {"name": "get_time"}}\n'
#         "```\n"
#         "```\n"
#         "用户: 我们明天再聊吧\n"
#         '返回: {"function_call": {"name": "handle_exit_intent"}}\n'
#         "```\n"
#         "```\n"
#         "用户: 播放中秋月\n"
#         '返回: {"function_call": {"name": "play_music", "arguments": {"song_name": "中秋月"}}}\n'
#         "```\n"
#         "```\n"
#         "可用的音乐名称:\n"
#     )
#     return prompt
class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config.get("url")
        self.kb_name = config.get("kb_name")

    def response(self, session_id, dialogue):
        try:
            # 取最后一条用户消息
            last_msg = next(m for m in reversed(dialogue) if m["role"] == "user")
            logger.bind(tag=TAG).info(f"-->kb_name: {self.kb_name}")
            query = last_msg.get('content', '').translate(str.maketrans('', '', '。？！'))
            logger.bind(tag=TAG).info(f"-->query:{query}")
            stream = True
            prompt = IntentProvider(IntentProviderBase).get_intent_system_prompt()
            request_json = {
                "query": query,
                "prompt": prompt,
                "stream": stream
            }
            # 发起流式请求
            # logger.info(f"-->request_json:{json.dumps(request_json)}")
            with requests.post(
                    f"{self.base_url}",
                    headers={"Authorization": f"Bearer {self.api_key}","Content-Type": "application/json",
                            "Accept": "application/json"},
                    json=request_json,
                    stream=stream,
                    timeout=60

            ) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            if line.startswith(b''):

                                data = json.loads(line)
                                if stream:
                                    if 'docs' in data:
                                        break
                                    if "choices" in data:
                                        print(data["choices"][0]["message"]["content"], end="", flush=True)
                                        yield data["choices"][0]["message"]["content"]
                                else:
                                    if "answer" in data:
                                        print(data["answer"], end="", flush=True)
                                        yield data["answer"]

                        except json.JSONDecodeError as e:
                            print("-->llm answer JSONDecodeError")
                            continue
                        except Exception as e:
                            print(f"-->llm answer Error:{e}")
                            continue

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")
            yield "【服务响应异常】"