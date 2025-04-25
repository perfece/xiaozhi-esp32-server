import json
from config.logger import setup_logging
import requests
from core.providers.llm.base import LLMProviderBase
from core.providers.intent.base import IntentProviderBase

from core.providers.intent.intent_llm.intent_llm import IntentProvider

TAG = __name__
logger = setup_logging()

class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.api_key = config["api_key"]
        self.base_url = config.get("url")
        self.kb_name = '' #config.get("kb_name")

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
                                        print(f'-->dc intent llm answer:{data["choices"][0]["message"]["content"]}', end="", flush=True)
                                        yield data["choices"][0]["message"]["content"]
                                else:
                                    if "answer" in data:
                                        print(f'-->dc intent llm answer:{data["choices"][0]["message"]["content"]}', end="", flush=True)
                                        yield data["answer"]

                        except json.JSONDecodeError as e:
                            print("-->dc intent llm answer JSONDecodeError")
                            continue
                        except Exception as e:
                            print(f"-->dc intent llm answer Error:{e}")
                            continue

        except Exception as e:
            logger.bind(tag=TAG).error(f"-->dc intent llm Error in response generation: {e}")
            yield "【服务响应异常】"