import json
from config.logger import setup_logging
import requests
from core.providers.llm.base import LLMProviderBase

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config.get("url")
        self.kb_name = config.get("kb_name")

    def response(self, session_id, dialogue):
        try:
            # 取最后一条用户消息
            last_msg = next(m for m in reversed(dialogue) if m["role"] == "user")
            print(f"-->kb_name:{self.kb_name}")
            query = last_msg.get('content', '').translate(str.maketrans('', '', '。？！'))
            print(f"-->query:{query}")
            # 发起流式请求
            with requests.post(
                    f"{self.base_url}",
                    headers={"Authorization": f"Bearer {self.api_key}","Content-Type": "application/json",
                            "Accept": "application/json"},
                    json={
                        "query": query,
                        "knowledge_base_name": self.kb_name,
                        "top_k": 5,
                        "score_threshold": 1,
                        "prompt_name": "chat_robot",
                        "stream": True,
                        "temperature": 1,
                        "history": []
                    }
            ) as r:
                for line in r.iter_lines():
                    if line:
                        try:
                            if line.startswith(b'data: '):

                                data = json.loads(line[6:])
                                if 'docs' in data:
                                    break
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