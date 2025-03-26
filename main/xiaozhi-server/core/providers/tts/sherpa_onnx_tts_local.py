import os
import uuid
import time
from datetime import datetime
from typing import Dict, Any

import sherpa_onnx
import soundfile as sf
from huggingface_hub import snapshot_download, hf_hub_download

from config.logger import setup_logging
from core.providers.tts.base import TTSProviderBase

TAG = __name__
logger = setup_logging()

class TTSProvider(TTSProviderBase):
    def __init__(self, config: Dict[str, Any], delete_audio_file: bool):
        super().__init__(config, delete_audio_file)
        self._load_config(config)
        self.tts = self._initialize_tts()

    def _load_config(self, config: Dict[str, Any]) -> None:
        """加载配置信息"""
        
        self.model_name = config.get("model_name")
        self.model_dir = os.path.join(config.get("model_dir", "models/sherpa_onnx_tts"), self.model_name)
        self.speaker = config.get("speaker", 0)
        self.speed = config.get("speed", 1)
        self.output_dir = config.get("output_dir", "tmp/")
        self.format = config.get("format", "wav")

    def _get_file(self, filename: str, subfolder: str = "") -> str:
        """直接读取本地模型文件"""
        local_path = os.path.join(self.model_dir, subfolder, filename)
        if not os.path.exists(local_path):
            logger.bind(tag=TAG).error(f"模型文件缺失: {local_path}")
            raise FileNotFoundError(f"模型文件不存在: {local_path}")
        return local_path

    def _initialize_tts(self) -> sherpa_onnx.OfflineTts:
        """初始化 TTS 模型"""
        if not self._model_exists():
            logger.bind(tag=TAG).error(f"本地模型不存在: {self.model_dir}")
            raise FileNotFoundError(f"模型目录不存在: {self.model_dir}")
        model_type = self._determine_model_type()
        tts_config = self._create_tts_config(model_type)  # 补上缺失的配置创建
        if not tts_config.validate():
            raise ValueError("TTS 配置验证失败，请检查您的配置")
        return sherpa_onnx.OfflineTts(tts_config)
    def _model_exists(self) -> bool:
        """检查模型是否已存在"""
        return os.path.exists(self.model_dir) and any(os.scandir(self.model_dir))
    def _determine_model_type(self) -> str:
        """根据模型名称关键词确定模型类型"""
        model_keywords = ["vits", "matcha", "kokoro"]
        for keyword in model_keywords:
            if keyword in self.model_name.lower():
                return keyword
        
        raise ValueError(
            f"无法识别的模型类型: {self.model_name}。"
            f"模型名称应包含以下关键词之一: {model_keywords}"
        )

    def _try_get_model_file(self) -> str:
        """尝试获取最大的onnx文件作为模型文件"""
        try:
            onnx_files = [f for f in os.listdir(self.model_dir) if f.endswith(".onnx")]
            if onnx_files:
                model = max(onnx_files, key=lambda f: os.path.getsize(os.path.join(self.model_dir, f)))
                return os.path.join(self.model_dir, model)
        except Exception as e:
            logger.bind(tag=TAG).error(f"获取模型文件失败: {e}", exc_info=True)

    def _create_tts_config(self, model_type: str) -> sherpa_onnx.OfflineTtsConfig:
        """根据模型类型创建 TTS 配置"""
        assert model_type in ["matcha", "vits", "kokoro"], f"不支持的模型类型: {model_type}"

        logger.bind(tag=TAG).info(f"初始化 SherpaTTS: {self.model_name}")
        logger.bind(tag=TAG).info(f"模型目录：{self.model_dir}")
        logger.bind(tag=TAG).info(f"模型类型：{model_type}")
        logger.bind(tag=TAG).info(f"语速：{self.speed}")
        logger.bind(tag=TAG).info(f"音色：{self.speaker}")

        config_mapping = {
            "matcha": self._create_matcha_config,
            "vits": self._create_vits_config,
            "kokoro": self._create_kokoro_config,
        }
        return config_mapping[model_type]()

    def _create_matcha_config(self) -> sherpa_onnx.OfflineTtsConfig:
        """创建 Matcha 模型配置"""
        matcha_config = sherpa_onnx.OfflineTtsMatchaModelConfig(
            acoustic_model=self._try_get_model_file(),
            vocoder=self._get_file("hifigan_v2.onnx"),
            lexicon=self._get_file("lexicon.txt"),
            tokens=self._get_file("tokens.txt"),
            dict_dir=os.path.join(self.model_dir, "dict"),
            length_scale=1.0 / self.speed,
        )
        return sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(matcha=matcha_config),
            rule_fsts=self._get_rule_fsts(["phone.fst", "date.fst", "number.fst"]),
        )

    def _create_vits_config(self) -> sherpa_onnx.OfflineTtsConfig:
        """创建 VITS 模型配置"""
        rule_fars = ""
        rule_fsts = ["phone.fst", "date.fst", "number.fst"]
        if "vits-zh-aishell3" in self.model_name:
            rule_far_path = os.path.join(self.model_dir, "rule.far")  # 改为本地路径
            if os.path.exists(rule_far_path):
                rule_fars = rule_far_path
            rule_fsts.append("new_heteronym.fst")

        kwargs = {
            "model": self._try_get_model_file(),
            "lexicon": self._get_file("lexicon.txt"),
            "tokens": self._get_file("tokens.txt"),
            "length_scale": 1.0 / self.speed
        }

        dict_dir = os.path.join(self.model_dir, "dict")
        if os.path.exists(dict_dir):
            kwargs["dict_dir"] = dict_dir

        vits_config = sherpa_onnx.OfflineTtsVitsModelConfig(**kwargs)
        return sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(vits=vits_config),
            rule_fsts=self._get_rule_fsts(rule_fsts),
            rule_fars=rule_fars
        )

    def _create_kokoro_config(self) -> sherpa_onnx.OfflineTtsConfig:
        """创建 Kokoro 模型配置"""
        kokoro_config = sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=self._try_get_model_file(),
            lexicon=self._get_rule_fsts(["lexicon-zh.txt", "lexicon-us-en.txt"]),
            voices=self._get_file("voices.bin"),
            tokens=self._get_file("tokens.txt"),
            data_dir=os.path.join(self.model_dir, "espeak-ng-data"),
            dict_dir=os.path.join(self.model_dir, "dict"),
            length_scale=1.0 / self.speed,
        )
        return sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(kokoro=kokoro_config),
            rule_fsts=self._get_rule_fsts(["date-zh.fst", "phone-zh.fst", "number-zh.fst"]),
        )

    def _get_rule_fsts(self, filenames: list) -> str:
        """获取 FST 规则文件列表"""
        return ",".join([self._get_file(f) for f in filenames])

    def generate_filename(self) -> str:
        """生成唯一的文件名"""
        return os.path.join(self.output_dir, f"tts-{datetime.now().date()}@{uuid.uuid4().hex}.{self.format}")
    async def text_to_speak(self, text: str, output_dir: str) -> None:
        """将文本转换为语音并保存到文件"""
        start = time.time()
        try:
            audio = self.tts.generate(text, sid=self.speaker, speed=self.speed)
        except ValueError as e:
            if "speaker ID" in str(e):  # 捕获音色ID错误
                logger.bind(tag=TAG).error(f"无效音色ID {self.speaker}: {str(e)}")
                return
            raise

        # 计算耗时
        elapsed_seconds = time.time() - start  # 添加耗时计算
        audio_duration = len(audio.samples) / audio.sample_rate
        real_time_factor = elapsed_seconds / audio_duration

        # 将音频保存到文件
        sf.write(output_dir, audio.samples, samplerate=audio.sample_rate, subtype="PCM_16")

