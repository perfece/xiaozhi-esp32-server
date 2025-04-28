import json
from config.logger import setup_logging
import requests
from core.providers.llm.base import LLMProviderBase
from core.providers.llm.system_prompt import get_system_prompt_for_function
TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config.get("url")
        self.kb_name = config.get("kb_name")
        self.prompt_name = "chat_robot"
        self.mode = "chat"
        self.stream = True
    def response(self, session_id, dialogue):
        try:
            # 取最后一条用户消息
            last_msg = next(m for m in reversed(dialogue) if m["role"] == "user")
            logger.bind(tag=TAG).info(f"-->kb_name: {self.kb_name}")
            query = last_msg.get('content', '').translate(str.maketrans('', '', '。？！'))
            logger.bind(tag=TAG).info(f"-->query:{query}")
            request_json = {
                "query": query,
                "knowledge_base_name": self.kb_name,
                "top_k": 3,
                "score_threshold": 0.5,
                "prompt_name": self.prompt_name,
                "stream": self.stream ,
                # "mode":self.mode,
                "temperature": 1,
                "use_reg": False,
                "history": []
            }
            # 发起流式请求
            with requests.post(
                    f"{self.base_url}",
                    headers={"Authorization": f"Bearer {self.api_key}","Content-Type": "application/json",
                            "Accept": "application/json"},
                    json=request_json,
                    stream=self.stream,
                    timeout=60

            ) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            if line.startswith(b'data: '):

                                data = json.loads(line[6:])
                                if 'docs' in data:
                                    break
                                if "answer" in data:
                                    logger.info(f"-->dcllm stream ans: {data['answer']}")
                                    yield data["answer"]
                            elif line.startswith(b'"{'):
                                data = json.loads(line)
                                if type(data)==str:
                                    data = json.loads(data)
                                if "answer" in data:
                                    logger.info(f"-->dcllm no stream ans: {data['answer']}")
                                    yield data["answer"]

                        except json.JSONDecodeError as e:
                            logger.info("-->llm answer JSONDecodeError")
                            continue
                        except Exception as e:
                            logger.info(f"-->llm answer Error:{e}")
                            continue

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")
            yield "【服务响应异常】"

    # def response_with_functions(self, session_id, dialogue, functions=None):
    #     logger.bind(tag=TAG).info(f"-->dcllm functions: {functions}")
    #     if len(dialogue) == 2 and functions is not None and len(functions) > 0:
    #         # self.prompt_name = "empty_q"
    #         # self.mode = "chat"
    #         # self.stream = False
    #         # 第一次调用llm， 取最后一条用户消息，附加tool提示词
    #         last_msg = dialogue[-1]["content"]
    #         function_str = json.dumps(functions, ensure_ascii=False)
    #         modify_msg = get_system_prompt_for_function(function_str) + last_msg
    #         dialogue[-1]["content"] = modify_msg
    #
    #         # 如果最后一个是 role="tool"，附加到user上
    #     if len(dialogue) > 1 and dialogue[-1]["role"] == "tool":
    #         assistant_msg = "\ntool call result: " + dialogue[-1]["content"] + "\n\n"
    #         while len(dialogue) > 1:
    #             if dialogue[-1]["role"] == "user":
    #                 dialogue[-1]["content"] = assistant_msg + dialogue[-1]["content"]
    #                 break
    #             dialogue.pop()
    #
    #     for token in self.response(session_id, dialogue):
    #         yield token, None