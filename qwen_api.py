import os
from typing import Optional, Dict, Any, List
from config import DASHSCOPE_API_KEY, DASHSCOPE_BASE_URL, DEFAULT_MODEL

try:
    from dashscope import Generation
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


class QwenAPI:
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        self.api_key = api_key or DASHSCOPE_API_KEY
        self.model = model
        if DASHSCOPE_AVAILABLE and DASHSCOPE_BASE_URL:
            dashscope.base_http_api_url = DASHSCOPE_BASE_URL

    def call(
        self,
        messages: List[Dict[str, str]],
        enable_thinking: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        print(f"[DEBUG] 调用千问API，enable_thinking={enable_thinking}, model={self.model}")
        print(f"[DEBUG] API Key存在: {bool(self.api_key)}")

        if not DASHSCOPE_AVAILABLE:
            print("[DEBUG] DashScope不可用，返回Mock响应")
            return self._mock_response(messages)

        try:
            print(f"[DEBUG] 正在调用Generation.call...")
            response = Generation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message",
                enable_thinking=enable_thinking,
                temperature=temperature,
                max_tokens=max_tokens
            )

            print(f"[DEBUG] 响应状态码: {response.status_code}")
            if response.status_code == 200:
                try:
                    message_obj = response.output.choices[0].message
                    if isinstance(message_obj, dict):
                        content = message_obj.get('content', '')
                        reasoning = message_obj.get('reasoning_content', '')
                    else:
                        content = getattr(message_obj, 'content', str(message_obj))
                        reasoning = getattr(message_obj, 'reasoning_content', '')
                    return {
                        "status": "success",
                        "content": content,
                        "reasoning_content": reasoning,
                        "raw_response": response
                    }
                except Exception as e:
                    print(f"[DEBUG] 解析响应对象异常: {type(e).__name__}: {str(e)}")
                    return {
                        "status": "error",
                        "status_code": response.status_code,
                        "code": "parse_error",
                        "message": f"解析响应失败: {str(e)}"
                    }
            else:
                print(f"[DEBUG] API错误: status_code={response.status_code}, code={getattr(response, 'code', 'unknown')}, message={getattr(response, 'message', 'unknown')}")
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "code": getattr(response, "code", "unknown"),
                    "message": getattr(response, "message", "unknown error")
                }
        except Exception as e:
            print(f"[DEBUG] API调用异常: {type(e).__name__}: {str(e)}")
            return {
                "status": "exception",
                "error": str(e)
            }

    def _mock_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        return {
            "status": "mock",
            "content": f"[Mock响应] 收到了消息: {messages[-1]['content'] if messages else '无内容'}",
            "reasoning_content": "[Mock推理过程] 这是一个模拟的推理响应"
        }

    def generate_builder_prompt(self, topic: str, context: Optional[Dict] = None) -> List[Dict[str, str]]:
        system_prompt = """你是一个严谨的建构者智能体。
你的任务是对给定的主题进行分析，并按照以下JSON格式输出你的思考结果：

{
    "faith": {
        "我确信的": ["确信项1", "确信项2"],
        "我推测的": ["推测项1", "推测项2"],
        "我不知道的": ["未知项1", "未知项2"]
    },
    "reason": {
        "我确信的": ["支撑确信项1的理由", "支撑确信项2的理由"],
        "我推测的": ["支撑推测项1的理由", "支撑推测项2的理由"],
        "我不知道的": ["说明为何归类为未知的理由"]
    }
}

注意：
1. 必须严格使用JSON格式输出，不要包含任何其他文字
2. reason部分必须使用逻辑推导语言（如三段论、假言推理等），不能使用自然语言描述
3. 每个faith项必须有对应的reason支撑"""

        user_prompt = f"请分析以下主题：{topic}"
        if context:
            user_prompt += f"\n\n参考上下文：{context}"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def generate_questioner_prompt(self, builder_output: Dict, thinking_pool_context: Dict) -> List[Dict[str, str]]:
        system_prompt = """你是一个严谨的质疑者智能体。
你的任务是对建构者的输出进行质疑和评估，并按照以下JSON格式输出：

{
    "faith": {
        "我确信的": ["你支持的建构者确信项"],
        "我推测的": ["你降级为推测的项及原因"],
        "我不知道的": ["你质疑后仍不确定的项"]
    },
    "reason": {
        "我确信的": ["使用逻辑推导证明该项确实成立"],
        "我推测的": ["使用逻辑推导说明降级原因"],
        "我不知道的": ["使用逻辑推导说明仍不确定的原因"]
    },
    "modifications": [
        {"original": "原论断", "modified": "修改后论断", "change_type": "降级/升级/删除/保留"}
    ]
}

注意：
1. 必须严格使用JSON格式输出
2. 必须对建构者的每个faith项进行质疑或支持
3. reason部分必须使用逻辑推导语言（如三段论、假言推理等）
4. modifications数组记录所有修改意见"""

        builder_faith_str = str(builder_output.get("faith", {}))
        builder_reason_str = str(builder_output.get("reason", {}))
        pool_context_str = str(thinking_pool_context)

        user_prompt = f"""建构者输出：
信仰部分：{builder_faith_str}
理由部分：{builder_reason_str}

当前思考池上下文：
{pool_context_str}

请对上述内容进行质疑评估："""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    def generate_observer_prompt(self, builder_output: Dict, questioner_output: Dict, round_num: int) -> List[Dict[str, str]]:
        system_prompt = """你是一个严谨的观察者智能体。
你的任务是权衡建构者和质疑者的观点，做出最终决策，并按以下JSON格式输出：

{
    "decision": "接受质疑者修改意见" 或 "保留建构者提案",
    "reason": "决策的逻辑推导理由",
    "final_faith": {
        "我确信的": ["最终确认的确信项"],
        "我推测的": ["最终确认的推测项"],
        "我不知道的": ["最终确认的未知项"]
    },
    "reasoning": "综合推理过程"
}

注意：
1. 必须严格使用JSON格式输出
2. 决策必须基于逻辑推导
3. final_faith是综合两者后的最终结论"""

        builder_faith_str = str(builder_output.get("faith", {}))
        questioner_faith_str = str(questioner_output.get("faith", {}))
        questioner_mods = str(questioner_output.get("modifications", []))

        user_prompt = f"""第{round_num}轮辩论：

建构者立场：
{builder_faith_str}

质疑者立场（含修改意见）：
{questioner_faith_str}
修改意见：{questioner_mods}

请做出最终决策："""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]


qwen_api = QwenAPI()
