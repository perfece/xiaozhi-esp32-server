from abc import ABC, abstractmethod
from typing import List, Dict
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


class IntentProviderBase(ABC):
    def __init__(self, config):
        self.config = config
        self.intent_options = [
            {
                "name": "handle_exit_intent",
                "desc": "结束聊天, 用户发来如再见之类的表示结束的话, 不想再进行对话的时候",
            },
            {
                "name": "play_music",
                "desc": "播放音乐, 用户希望你可以播放音乐, 只用于播放音乐的意图",
            },
            {"name": "get_time", "desc": "获取今天日期或者当前时间信息"},
            {"name": "continue_chat", "desc": "继续聊天"},
            {"name": "get_weather", "desc": "获取天气的意图"}, #，参数location返回地名，如杭州；参数lang返回用户使用的语言code，例如zh_CN/zh_HK/en_US/ja_JP等，默认zh_CN"},
            {"name": "get_news", "desc": "获取新闻的意图"},
            {"name": "change_role", "desc": "切换角色意图"},
            {"name": "handle_device", "desc": "设置iot设备的状态意图,获取或设置设备的音量/亮度"},
            # {"name": "hass_set_state", "desc": "设置homeassistant里设备的状态意图,设置homeassistant里设备的状态,包括开、关,调整灯光亮度,调整播放器的音量,设备的暂停、继续、静音操作"},
        ]

    def set_llm(self, llm):
        self.llm = llm
        # 获取模型名称和类型信息
        model_name = getattr(llm, "model_name", str(llm.__class__.__name__))
        # 记录更详细的日志
        logger.bind(tag=TAG).info(f"意图识别设置LLM: {model_name}")

    @abstractmethod
    async def detect_intent(self, conn, dialogue_history: List[Dict], text: str) -> str:
        """
        检测用户最后一句话的意图
        Args:
            dialogue_history: 对话历史记录列表，每条记录包含role和content
        Returns:
            返回识别出的意图，格式为:
            - "继续聊天"
            - "结束聊天"
            - "播放音乐 歌名" 或 "随机播放音乐"
            - "查询天气 地点名" 或 "查询天气 [当前位置]"
        """
        pass
