-- 本文件用于初始化模型供应器数据，无需手动执行，在项目启动时会自动执行
-- --------------------------------------------------------
-- 初始化模型供应器数据
DELETE FROM `ai_model_provider`;
INSERT INTO `ai_model_provider` (`id`, `model_type`, `provider_code`, `name`, `fields`, `sort`, `creator`, `create_date`, `updater`, `update_date`) VALUES
-- VAD模型供应器
('SYSTEM_VAD_SileroVAD', 'VAD', 'SileroVAD', 'SileroVAD语音活动检测', '[{"key":"threshold","label":"检测阈值","type":"number"},{"key":"model_dir","label":"模型目录","type":"string"},{"key":"min_silence_duration_ms","label":"最小静音时长","type":"number"}]', 1, 1, NOW(), 1, NOW()),

-- ASR模型供应器
('SYSTEM_ASR_FunASR', 'ASR', 'FunASR', 'FunASR语音识别', '[{"key":"model_dir","label":"模型目录","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"}]', 1, 1, NOW(), 1, NOW()),
('SYSTEM_ASR_SherpaASR', 'ASR', 'SherpaASR', 'SherpaASR语音识别', '[{"key":"model_dir","label":"模型目录","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"}]', 2, 1, NOW(), 1, NOW()),
('SYSTEM_ASR_DoubaoASR', 'ASR', 'DoubaoASR', '火山引擎语音识别', '[{"key":"appid","label":"应用ID","type":"string"},{"key":"access_token","label":"访问令牌","type":"string"},{"key":"cluster","label":"集群","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"}]', 3, 1, NOW(), 1, NOW()),

-- LLM模型供应器
('SYSTEM_LLM_openai', 'LLM', 'openai', 'OpenAI接口', '[{"key":"base_url","label":"基础URL","type":"string"},{"key":"model_name","label":"模型名称","type":"string"},{"key":"api_key","label":"API密钥","type":"string"},{"key":"temperature","label":"温度","type":"number"},{"key":"max_tokens","label":"最大令牌数","type":"number"},{"key":"top_p","label":"top_p值","type":"number"},{"key":"top_k","label":"top_k值","type":"number"},{"key":"frequency_penalty","label":"频率惩罚","type":"number"}]', 1, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_AliBL', 'LLM', 'AliBL', '阿里百炼接口', '[{"key":"base_url","label":"基础URL","type":"string"},{"key":"app_id","label":"应用ID","type":"string"},{"key":"api_key","label":"API密钥","type":"string"},{"key":"is_no_prompt","label":"是否不使用本地prompt","type":"boolean"},{"key":"ali_memory_id","label":"记忆ID","type":"string"}]', 2, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_ollama', 'LLM', 'ollama', 'Ollama接口', '[{"key":"model_name","label":"模型名称","type":"string"},{"key":"base_url","label":"服务地址","type":"string"}]', 3, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_dify', 'LLM', 'dify', 'Dify接口', '[{"key":"base_url","label":"基础URL","type":"string"},{"key":"api_key","label":"API密钥","type":"string"},{"key":"mode","label":"对话模式","type":"string"}]', 4, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_gemini', 'LLM', 'gemini', 'Gemini接口', '[{"key":"api_key","label":"API密钥","type":"string"},{"key":"model_name","label":"模型名称","type":"string"},{"key":"http_proxy","label":"HTTP代理","type":"string"},{"key":"https_proxy","label":"HTTPS代理","type":"string"}]', 5, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_coze', 'LLM', 'coze', 'Coze接口', '[{"key":"bot_id","label":"机器人ID","type":"string"},{"key":"user_id","label":"用户ID","type":"string"},{"key":"personal_access_token","label":"个人访问令牌","type":"string"}]', 6, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_fastgpt', 'LLM', 'fastgpt', 'FastGPT接口', '[{"key":"base_url","label":"基础URL","type":"string"},{"key":"api_key","label":"API密钥","type":"string"},{"key":"variables","label":"变量","type":"dict","dict_name":"variables"}]', 7, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_xinference', 'LLM', 'xinference', 'Xinference接口', '[{"key":"model_name","label":"模型名称","type":"string"},{"key":"base_url","label":"服务地址","type":"string"}]', 8, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_doubao', 'LLM', 'doubao', '火山引擎LLM', '[{"key":"base_url","label":"基础URL","type":"string"},{"key":"model_name","label":"模型名称","type":"string"},{"key":"api_key","label":"API密钥","type":"string"}]', 9, 1, NOW(), 1, NOW()),
('SYSTEM_LLM_chatglm', 'LLM', 'chatglm', 'ChatGLM接口', '[{"key":"model_name","label":"模型名称","type":"string"},{"key":"url","label":"服务地址","type":"string"},{"key":"api_key","label":"API密钥","type":"string"}]', 10, 1, NOW(), 1, NOW()),

-- TTS模型供应器
('SYSTEM_TTS_edge', 'TTS', 'edge', 'Edge TTS', '[{"key":"voice","label":"音色","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"}]', 1, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_doubao', 'TTS', 'doubao', '火山引擎TTS', '[{"key":"api_url","label":"API地址","type":"string"},{"key":"voice","label":"音色","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"authorization","label":"授权","type":"string"},{"key":"appid","label":"应用ID","type":"string"},{"key":"access_token","label":"访问令牌","type":"string"},{"key":"cluster","label":"集群","type":"string"}]', 2, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_siliconflow', 'TTS', 'siliconflow', '硅基流动TTS', '[{"key":"model","label":"模型","type":"string"},{"key":"voice","label":"音色","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"access_token","label":"访问令牌","type":"string"},{"key":"response_format","label":"响应格式","type":"string"}]', 3, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_cozecn', 'TTS', 'cozecn', 'COZECN TTS', '[{"key":"voice","label":"音色","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"access_token","label":"访问令牌","type":"string"},{"key":"response_format","label":"响应格式","type":"string"}]', 4, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_fishspeech', 'TTS', 'fishspeech', 'FishSpeech TTS', '[{"key":"output_dir","label":"输出目录","type":"string"},{"key":"response_format","label":"响应格式","type":"string"},{"key":"reference_id","label":"参考ID","type":"string"},{"key":"reference_audio","label":"参考音频","type":"dict","dict_name":"reference_audio"},{"key":"reference_text","label":"参考文本","type":"dict","dict_name":"reference_text"},{"key":"normalize","label":"是否标准化","type":"boolean"},{"key":"max_new_tokens","label":"最大新令牌数","type":"number"},{"key":"chunk_length","label":"块长度","type":"number"},{"key":"top_p","label":"top_p值","type":"number"},{"key":"repetition_penalty","label":"重复惩罚","type":"number"},{"key":"temperature","label":"温度","type":"number"},{"key":"streaming","label":"是否流式","type":"boolean"},{"key":"use_memory_cache","label":"是否使用内存缓存","type":"string"},{"key":"seed","label":"种子","type":"number"},{"key":"channels","label":"通道数","type":"number"},{"key":"rate","label":"采样率","type":"number"},{"key":"api_key","label":"API密钥","type":"string"},{"key":"api_url","label":"API地址","type":"string"}]', 5, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_gpt_sovits_v2', 'TTS', 'gpt_sovits_v2', 'GPT-SoVITS V2', '[{"key":"url","label":"服务地址","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"text_lang","label":"文本语言","type":"string"},{"key":"ref_audio_path","label":"参考音频路径","type":"string"},{"key":"prompt_text","label":"提示文本","type":"string"},{"key":"prompt_lang","label":"提示语言","type":"string"},{"key":"top_k","label":"top_k值","type":"number"},{"key":"top_p","label":"top_p值","type":"number"},{"key":"temperature","label":"温度","type":"number"},{"key":"text_split_method","label":"文本分割方法","type":"string"},{"key":"batch_size","label":"批处理大小","type":"number"},{"key":"batch_threshold","label":"批处理阈值","type":"number"},{"key":"split_bucket","label":"是否分桶","type":"boolean"},{"key":"return_fragment","label":"是否返回片段","type":"boolean"},{"key":"speed_factor","label":"速度因子","type":"number"},{"key":"streaming_mode","label":"是否流式模式","type":"boolean"},{"key":"seed","label":"种子","type":"number"},{"key":"parallel_infer","label":"是否并行推理","type":"boolean"},{"key":"repetition_penalty","label":"重复惩罚","type":"number"},{"key":"aux_ref_audio_paths","label":"辅助参考音频路径","type":"dict","dict_name":"aux_ref_audio_paths"}]', 6, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_gpt_sovits_v3', 'TTS', 'gpt_sovits_v3', 'GPT-SoVITS V3', '[{"key":"url","label":"服务地址","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"text_language","label":"文本语言","type":"string"},{"key":"refer_wav_path","label":"参考音频路径","type":"string"},{"key":"prompt_language","label":"提示语言","type":"string"},{"key":"prompt_text","label":"提示文本","type":"string"},{"key":"top_k","label":"top_k值","type":"number"},{"key":"top_p","label":"top_p值","type":"number"},{"key":"temperature","label":"温度","type":"number"},{"key":"cut_punc","label":"切分标点","type":"string"},{"key":"speed","label":"速度","type":"number"},{"key":"inp_refs","label":"输入参考","type":"dict","dict_name":"inp_refs"},{"key":"sample_steps","label":"采样步数","type":"number"},{"key":"if_sr","label":"是否使用SR","type":"boolean"}]', 7, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_minimax', 'TTS', 'minimax', 'Minimax TTS', '[{"key":"output_dir","label":"输出目录","type":"string"},{"key":"group_id","label":"组ID","type":"string"},{"key":"api_key","label":"API密钥","type":"string"},{"key":"model","label":"模型","type":"string"},{"key":"voice_id","label":"音色ID","type":"string"}]', 8, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_aliyun', 'TTS', 'aliyun', '阿里云TTS', '[{"key":"output_dir","label":"输出目录","type":"string"},{"key":"appkey","label":"应用密钥","type":"string"},{"key":"token","label":"访问令牌","type":"string"},{"key":"voice","label":"音色","type":"string"},{"key":"access_key_id","label":"访问密钥ID","type":"string"},{"key":"access_key_secret","label":"访问密钥密码","type":"string"}]', 9, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_ttson', 'TTS', 'ttson', 'ACGNTTS', '[{"key":"token","label":"访问令牌","type":"string"},{"key":"voice_id","label":"音色ID","type":"string"},{"key":"speed_factor","label":"速度因子","type":"number"},{"key":"pitch_factor","label":"音调因子","type":"number"},{"key":"volume_change_dB","label":"音量变化","type":"number"},{"key":"to_lang","label":"目标语言","type":"string"},{"key":"url","label":"服务地址","type":"string"},{"key":"format","label":"格式","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"emotion","label":"情感","type":"number"}]', 10, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_openai', 'TTS', 'openai', 'OpenAI TTS', '[{"key":"api_key","label":"API密钥","type":"string"},{"key":"api_url","label":"API地址","type":"string"},{"key":"model","label":"模型","type":"string"},{"key":"voice","label":"音色","type":"string"},{"key":"speed","label":"速度","type":"number"},{"key":"output_dir","label":"输出目录","type":"string"}]', 11, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_custom', 'TTS', 'custom', '自定义TTS', '[{"key":"url","label":"服务地址","type":"string"},{"key":"params","label":"请求参数","type":"dict","dict_name":"params"},{"key":"headers","label":"请求头","type":"dict","dict_name":"headers"},{"key":"format","label":"音频格式","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"}]', 12, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_302ai', 'TTS', '302ai', '302AI TTS', '[{"key":"api_url","label":"API地址","type":"string"},{"key":"authorization","label":"授权","type":"string"},{"key":"voice","label":"音色","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"access_token","label":"访问令牌","type":"string"}]', 13, 1, NOW(), 1, NOW()),
('SYSTEM_TTS_gizwits', 'TTS', 'gizwits', '机智云TTS', '[{"key":"api_url","label":"API地址","type":"string"},{"key":"authorization","label":"授权","type":"string"},{"key":"voice","label":"音色","type":"string"},{"key":"output_dir","label":"输出目录","type":"string"},{"key":"access_token","label":"访问令牌","type":"string"}]', 14, 1, NOW(), 1, NOW()),

-- Memory模型供应器
('SYSTEM_Memory_mem0ai', 'Memory', 'mem0ai', 'Mem0AI记忆', '[{"key":"api_key","label":"API密钥","type":"string"}]', 1, 1, NOW(), 1, NOW()),
('SYSTEM_Memory_nomem', 'Memory', 'nomem', '无记忆', '[]', 2, 1, NOW(), 1, NOW()),
('SYSTEM_Memory_mem_local_short', 'Memory', 'mem_local_short', '本地短记忆', '[]', 3, 1, NOW(), 1, NOW()),

-- Intent模型供应器
('SYSTEM_Intent_nointent', 'Intent', 'nointent', '无意图识别', '[]', 1, 1, NOW(), 1, NOW()),
('SYSTEM_Intent_intent_llm', 'Intent', 'intent_llm', 'LLM意图识别', '[{"key":"llm","label":"LLM模型","type":"string"}]', 2, 1, NOW(), 1, NOW()),
('SYSTEM_Intent_function_call', 'Intent', 'function_call', '函数调用意图识别', '[{"key":"functions","label":"函数列表","type":"dict","dict_name":"functions"}]', 3, 1, NOW(), 1, NOW());
