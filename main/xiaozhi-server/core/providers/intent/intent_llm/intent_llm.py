from typing import List, Dict
from core.providers.intent.base import IntentProviderBase
from plugins_func.functions.play_music import initialize_music_handler
from config.logger import setup_logging
import re
import json
import hashlib
import time

TAG = __name__
logger = setup_logging()


class IntentProvider(IntentProviderBase):
    def __init__(self, config):
        super().__init__(config)
        self.llm = None
        self.promot = self.get_intent_system_prompt()
        # 添加缓存管理
        self.intent_cache = {}  # 缓存意图识别结果
        self.cache_expiry = 600  # 缓存有效期10分钟
        self.cache_max_size = 100  # 最多缓存100个意图

    def get_intent_system_prompt(self) -> str:
        """
        根据配置的意图选项动态生成系统提示词
        Returns:
            格式化后的系统提示词
        """

        prompt = (
            "你是一个意图识别助手。请分析用户的最后一句话，判断用户意图属于以下哪一类：\n"
            "<start>"
            f"{str(self.intent_options)}"
            "<end>\n"
            "处理步骤:"
            "1. 思考意图类型，生成function_call格式"
            "\n\n"
            "返回格式示例：\n"
            '1. 播放音乐意图: {"function_call": {"name": "play_music", "arguments": {"song_name": "音乐名称"}}}\n'
            '2. 结束对话意图: {"function_call": {"name": "handle_exit_intent", "arguments": {"say_goodbye": "goodbye"}}}\n'
            '3. 获取当天日期时间: {"function_call": {"name": "get_time"}}\n'
            '4. 继续聊天意图: {"function_call": {"name": "continue_chat"}}\n'
            '5. 获取天气意图: {"function_call": {"name": "get_weather", "arguments": {"location": "地名","lang":"返回用户使用的语言code，例如zh_CN/zh_HK/en_US/ja_JP等，默认zh_CN"}}}\n'
            '6. 获取新闻意图: {"function_call": {"name": "get_news", "arguments": {"category": "新闻类别","detail":"默认为false","lang":"返回用户使用的语言code，默认zh_CN"}}}\n'
            '7. 切换角色意图: {"function_call": {"name": "change_role", "arguments": {"role_name": "要切换的角色名字","role":"要切换的角色，可选的角色有：[机车女友,英语老师,好奇小男孩]"}}}\n'
            '8. 设备控制意图: {"function_call": {"name": "handle_device", "arguments":｛"device_type":"设备类型，可选值：Speaker(音量),Screen(亮度)","action":"动作名称，可选值：get(获取),set(设置),raise(提高),lower(降低)","value":"值大小，可选值：0-100之间的整数"｝}}\n'
            # '9. 设置homeassistant里设备的状态意图: {"function_call": {"name": "hass_set_state","arguments":{"entity_id":"需要操作的设备id,homeassistant里的entity_id",'
            # ' "state":{"type": "需要操作的动作,打开设备:turn_on,关闭设备:turn_off,增加亮度:brightness_up,降低亮度:brightness_down,设置亮度:brightness_value,增加>音量:,volume_up降低音量:volume_down,设置音量:volume_set,设备暂停:pause,设备继续:continue,静音/取消静音:volume_mute",'
            # '"input":"只有在设置音量,设置亮度时候 才需要,有效值为1-100","is_muted":"只有在设置静音操作时才需要,设置静音的时候该值为true,取消静音时该值为false"}}}}\n'
            "\n"
            "注意:\n"
            '- 播放音乐：无歌名时，song_name设为"random"\n'
            "- 如果没有明显的意图，应按照继续聊天意图处理\n"
            "- 只返回纯JSON，不要任何其他内容\n"
            "\n"
            "示例分析:\n"
            "```\n"
            "用户: 你也太搞笑了\n"
            '返回: {"function_call": {"name": "continue_chat"}}\n'
            "```\n"
            "```\n"
            "用户: 现在是几号了?现在几点了？\n"
            '返回: {"function_call": {"name": "get_time"}}\n'
            "```\n"
            "```\n"
            "用户: 我们明天再聊吧\n"
            '返回: {"function_call": {"name": "handle_exit_intent"}}\n'
            "```\n"
            "```\n"
            "用户: 播放中秋月\n"
            '返回: {"function_call": {"name": "play_music", "arguments": {"song_name": "中秋月"}}}\n'
            "```\n"
            "```\n"
            "可用的音乐名称:\n"
        )
        return prompt

    def clean_cache(self):
        """清理过期缓存"""
        now = time.time()
        # 找出过期键
        expired_keys = [
            k
            for k, v in self.intent_cache.items()
            if now - v["timestamp"] > self.cache_expiry
        ]
        for key in expired_keys:
            del self.intent_cache[key]

        # 如果缓存太大，移除最旧的条目
        if len(self.intent_cache) > self.cache_max_size:
            # 按时间戳排序并保留最新的条目
            sorted_items = sorted(
                self.intent_cache.items(), key=lambda x: x[1]["timestamp"]
            )
            for key, _ in sorted_items[: len(sorted_items) - self.cache_max_size]:
                del self.intent_cache[key]

    async def detect_intent(self, conn, dialogue_history: List[Dict], text: str) -> str:
        if not self.llm:
            raise ValueError("LLM provider not set")

        # 记录整体开始时间
        total_start_time = time.time()

        # 打印使用的模型信息
        model_info = getattr(self.llm, "model_name", str(self.llm.__class__.__name__))
        logger.bind(tag=TAG).debug(f"使用意图识别模型: {model_info}")

        # 计算缓存键
        cache_key = hashlib.md5(text.encode()).hexdigest()

        # 检查缓存
        if cache_key in self.intent_cache:
            cache_entry = self.intent_cache[cache_key]
            # 检查缓存是否过期
            if time.time() - cache_entry["timestamp"] <= self.cache_expiry:
                cache_time = time.time() - total_start_time
                logger.bind(tag=TAG).debug(
                    f"使用缓存的意图: {cache_key} -> {cache_entry['intent']}, 耗时: {cache_time:.4f}秒"
                )
                return cache_entry["intent"]

        # 清理缓存
        self.clean_cache()

        # 构建用户最后一句话的提示
        msgStr = ""

        # # 只使用最后两句即可
        # if len(dialogue_history) >= 2:
        #     # 保证最少有两句话的时候处理
        #     msgStr += f"{dialogue_history[-2].role}: {dialogue_history[-2].content}\n"
        # msgStr += f"{dialogue_history[-1].role}: {dialogue_history[-1].content}\n"

        # 只使用最后一句即可
        if len(dialogue_history) >= 1:
            # 保证最少有一句话的时候处理
            msgStr += f"{dialogue_history[-1].role}: {dialogue_history[-1].content}\n"

        msgStr += f"User: {text}\n"
        user_prompt = f"当前的对话如下：\n{msgStr}"
        music_config = initialize_music_handler(conn)
        music_file_names = music_config["music_file_names"]
        prompt_music = f"{self.promot}\n<start>{music_file_names}\n<end>"
        logger.bind(tag=TAG).debug(f"User prompt: {prompt_music}")

        # 记录预处理完成时间
        preprocess_time = time.time() - total_start_time
        logger.bind(tag=TAG).debug(f"意图识别预处理耗时: {preprocess_time:.4f}秒")

        # 使用LLM进行意图识别
        llm_start_time = time.time()
        logger.bind(tag=TAG).debug(f"开始LLM意图识别调用, 模型: {model_info}")

        intent = self.llm.response_no_stream(
            system_prompt=prompt_music, user_prompt=user_prompt
        )

        # 记录LLM调用完成时间
        llm_time = time.time() - llm_start_time
        logger.bind(tag=TAG).debug(
            f"LLM意图识别完成, 模型: {model_info}, 调用耗时: {llm_time:.4f}秒"
        )

        # 记录后处理开始时间
        postprocess_start_time = time.time()

        # 清理和解析响应
        intent = intent.strip()
        # 尝试提取JSON部分
        match = re.search(r"\{.*\}", intent, re.DOTALL)
        if match:
            intent = match.group(0)

        # 记录总处理时间
        total_time = time.time() - total_start_time
        logger.bind(tag=TAG).debug(
            f"【意图识别性能】模型: {model_info}, 总耗时: {total_time:.4f}秒, LLM调用: {llm_time:.4f}秒, 查询: '{text[:20]}...'"
        )

        # 尝试解析为JSON
        try:
            intent_data = json.loads(intent)
            # 如果包含function_call，则格式化为适合处理的格式
            if "function_call" in intent_data:
                function_data = intent_data["function_call"]
                function_name = function_data.get("name")
                function_args = function_data.get("arguments", {})

                # 记录识别到的function call
                logger.bind(tag=TAG).info(
                    f"识别到function call: {function_name}, 参数: {function_args}"
                )

                # 添加到缓存
                self.intent_cache[cache_key] = {
                    "intent": intent,
                    "timestamp": time.time(),
                }

                # 后处理时间
                postprocess_time = time.time() - postprocess_start_time
                logger.bind(tag=TAG).debug(f"意图后处理耗时: {postprocess_time:.4f}秒")

                # 确保返回完全序列化的JSON字符串
                return intent
            else:
                # 添加到缓存
                self.intent_cache[cache_key] = {
                    "intent": intent,
                    "timestamp": time.time(),
                }

                # 后处理时间
                postprocess_time = time.time() - postprocess_start_time
                logger.bind(tag=TAG).debug(f"意图后处理耗时: {postprocess_time:.4f}秒")

                # 返回普通意图
                return intent
        except json.JSONDecodeError:
            # 后处理时间
            postprocess_time = time.time() - postprocess_start_time
            logger.bind(tag=TAG).error(
                f"无法解析意图JSON: {intent}, 后处理耗时: {postprocess_time:.4f}秒"
            )
            # 如果解析失败，默认返回继续聊天意图
            return '{"intent": "继续聊天"}'
