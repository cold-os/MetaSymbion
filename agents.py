from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import json
from thinking_pool import ThinkingPool, FaithCategory
from qwen_api import QwenAPI, qwen_api
from logic_generator import logic_generator


class BaseAgent(ABC):
    def __init__(self, name: str, api_client: Optional[QwenAPI] = None):
        self.name = name
        self.api_client = api_client or qwen_api

    @abstractmethod
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def parse_json_output(self, response_content: str) -> Dict[str, Any]:
        try:
            json_str = response_content.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            return {
                "faith": {
                    "我确信的": [],
                    "我推测的": [f"JSON解析失败: {str(e)}，原始内容: {response_content[:100]}"],
                    "我不知道的": []
                },
                "reason": {
                    "我确信的": [],
                    "我推测的": [],
                    "我不知道的": ["解析失败"]
                }
            }


class BuilderAgent(BaseAgent):
    ROLE_NAME = "建构者"

    def __init__(self, api_client: Optional[QwenAPI] = None):
        super().__init__("Builder", api_client)

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        topic = context.get("topic", "")
        thinking_pool_context = context.get("thinking_pool_context", {})
        history = thinking_pool_context.get("thinking_history", [])

        if history:
            context_prompt = f"参考前几轮思考历史，对主题'{topic}'进行深化分析"
            prompt_context = {
                "history_summary": thinking_pool_context.get("history_summary", ""),
                "previous_rounds": len(history)
            }
        else:
            context_prompt = None
            prompt_context = None

        messages = self.api_client.generate_builder_prompt(topic, prompt_context)

        if context_prompt:
            messages[1]["content"] = context_prompt + "\n\n" + messages[1]["content"]

        response = self.api_client.call(messages)
        print(f"[DEBUG] {self.ROLE_NAME} API响应状态: {response['status']}")

        if response["status"] == "success":
            parsed = self.parse_json_output(response["content"])
            reasoning_content = response.get("reasoning_content", "")
            print(f"[DEBUG] {self.ROLE_NAME} 解析成功")
        else:
            print(f"[DEBUG] {self.ROLE_NAME} API调用失败，使用fallback输出")
            print(f"[DEBUG] 失败详情: {response}")
            parsed = self._generate_fallback_output(topic)
            reasoning_content = "基于预设逻辑生成"

        return {
            "role": self.ROLE_NAME,
            "faith": parsed.get("faith", {
                "我确信的": [],
                "我推测的": [],
                "我不知道的": []
            }),
            "reason": parsed.get("reason", {
                "我确信的": [],
                "我推测的": [],
                "我不知道的": []
            }),
            "reasoning_content": reasoning_content,
            "raw_response": response
        }

    def _generate_fallback_output(self, topic: str) -> Dict[str, Any]:
        certain = [f"关于'{topic}'的基本定义是明确的"]
        speculated = [f"'{topic}'可能具有某些深层特性"]
        unknown = [f"'{topic}'的完整影响范围尚不确定"]

        return {
            "faith": {
                "我确信的": certain,
                "我推测的": speculated,
                "我不知道的": unknown
            },
            "reason": {
                "我确信的": [logic_generator.syllogism("概念A", "有明确定义", topic)],
                "我推测的": [logic_generator.modus_ponens("观察到的特征", "存在深层特性")],
                "我不知道的": [f"由于信息不足，依据认知谦逊原则，归类为未知"]
            }
        }


class QuestionerAgent(BaseAgent):
    ROLE_NAME = "质疑者"

    def __init__(self, api_client: Optional[QwenAPI] = None):
        super().__init__("Questioner", api_client)

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        builder_output = context.get("builder_output", {})
        thinking_pool_context = context.get("thinking_pool_context", {})

        messages = self.api_client.generate_questioner_prompt(
            builder_output,
            thinking_pool_context
        )

        response = self.api_client.call(messages)
        print(f"[DEBUG] {self.ROLE_NAME} API响应状态: {response['status']}")

        if response["status"] == "success":
            parsed = self.parse_json_output(response["content"])
            reasoning_content = response.get("reasoning_content", "")
            print(f"[DEBUG] {self.ROLE_NAME} 解析成功")
        else:
            print(f"[DEBUG] {self.ROLE_NAME} API调用失败，使用fallback输出")
            print(f"[DEBUG] 失败详情: {response}")
            parsed = self._generate_fallback_output(builder_output)
            reasoning_content = "基于预设逻辑生成"

        modifications = parsed.get("modifications", [])

        return {
            "role": self.ROLE_NAME,
            "faith": parsed.get("faith", {
                "我确信的": [],
                "我推测的": [],
                "我不知道的": []
            }),
            "reason": parsed.get("reason", {
                "我确信的": [],
                "我推测的": [],
                "我不知道的": []
            }),
            "modifications": modifications,
            "reasoning_content": reasoning_content,
            "raw_response": response
        }

    def _generate_fallback_output(self, builder_output: Dict) -> Dict[str, Any]:
        builder_certain = builder_output.get("faith", {}).get("我确信的", [])
        modifications = []

        speculated = []
        for item in builder_certain[:1]:
            modifications.append({
                "original": item,
                "modified": item,
                "change_type": "保留"
            })
            speculated.append(f"[降级] {item}")

        return {
            "faith": {
                "我确信的": [builder_certain[1]] if len(builder_certain) > 1 else [],
                "我推测的": speculated,
                "我不知道的": builder_output.get("faith", {}).get("我不知道的", [])
            },
            "reason": {
                "我确信的": [logic_generator.generate_support_reason("论断", "证据充分")],
                "我推测的": [logic_generator.generate_demotion_reason("原论断", "推测", "证据不足")],
                "我不知道的": ["信息不充分，维持未知分类"]
            },
            "modifications": modifications
        }


class ObserverAgent(BaseAgent):
    ROLE_NAME = "观察者"

    def __init__(self, api_client: Optional[QwenAPI] = None):
        super().__init__("Observer", api_client)

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        builder_output = context.get("builder_output", {})
        questioner_output = context.get("questioner_output", {})
        round_num = context.get("round", 1)

        messages = self.api_client.generate_observer_prompt(
            builder_output,
            questioner_output,
            round_num
        )

        response = self.api_client.call(messages)
        print(f"[DEBUG] {self.ROLE_NAME} API响应状态: {response['status']}")

        if response["status"] == "success":
            parsed = self.parse_json_output(response["content"])
            reasoning_content = response.get("reasoning_content", "")
            print(f"[DEBUG] {self.ROLE_NAME} 解析成功")
        else:
            print(f"[DEBUG] {self.ROLE_NAME} API调用失败，使用fallback输出")
            print(f"[DEBUG] 失败详情: {response}")
            parsed = self._generate_fallback_output(builder_output, questioner_output)
            reasoning_content = "基于预设逻辑生成"

        decision = parsed.get("decision", "未知")
        final_faith = parsed.get("final_faith", builder_output.get("faith", {}))

        return {
            "role": self.ROLE_NAME,
            "decision": decision,
            "final_faith": final_faith,
            "reason": parsed.get("reason", ""),
            "reasoning": parsed.get("reasoning", ""),
            "reasoning_content": reasoning_content,
            "raw_response": response
        }

    def _generate_fallback_output(self, builder_output: Dict, questioner_output: Dict) -> Dict[str, Any]:
        builder_certain_count = len(builder_output.get("faith", {}).get("我确信的", []))
        questioner_modifications = len(questioner_output.get("modifications", []))

        if questioner_modifications > 0:
            decision = "接受质疑者修改意见"
        else:
            decision = "保留建构者提案"

        return {
            "decision": decision,
            "final_faith": builder_output.get("faith", {}),
            "reason": logic_generator.generate_observer_reason(
                builder_output,
                questioner_output,
                decision
            )
        }


class MetaThinkingUnit:
    def __init__(self, api_client: Optional[QwenAPI] = None):
        self.builder = BuilderAgent(api_client)
        self.questioner = QuestionerAgent(api_client)
        self.observer = ObserverAgent(api_client)
        self.thinking_pool = ThinkingPool()

    def run_round(self, round_num: int, topic: str) -> Dict[str, Any]:
        context = {
            "topic": topic,
            "round": round_num,
            "thinking_pool_context": {
                "construction": self.thinking_pool.get_all_construction(),
                "questioning": self.thinking_pool.get_all_questioning(),
                "thinking_history": self.thinking_pool.get_history(),
                "history_summary": self.thinking_pool.get_history_summary()
            }
        }

        builder_result = self.builder.think(context)

        for faith_type in [FaithCategory.CERTAIN.value, FaithCategory.SPECULATED.value, FaithCategory.UNKNOWN.value]:
            for item in builder_result.get("faith", {}).get(faith_type, []):
                self.thinking_pool.add_to_construction(
                    FaithCategory(faith_type),
                    item,
                    self.builder.ROLE_NAME
                )

        context["builder_output"] = builder_result

        questioner_result = self.questioner.think(context)

        for faith_type in [FaithCategory.CERTAIN.value, FaithCategory.SPECULATED.value, FaithCategory.UNKNOWN.value]:
            for item in questioner_result.get("faith", {}).get(faith_type, []):
                self.thinking_pool.add_to_questioning(
                    FaithCategory(faith_type),
                    item,
                    self.questioner.ROLE_NAME
                )

        context["questioner_output"] = questioner_result

        observer_result = self.observer.think(context)

        history_entry = {
            "round": round_num,
            "builder": {
                "faith": builder_result.get("faith", {}),
                "reason": builder_result.get("reason", {})
            },
            "questioner": {
                "faith": questioner_result.get("faith", {}),
                "reason": questioner_result.get("reason", {}),
                "modifications": questioner_result.get("modifications", [])
            },
            "observer_decision": {
                "decision": observer_result.get("decision", ""),
                "final_faith": observer_result.get("final_faith", {}),
                "reason": observer_result.get("reason", "")
            }
        }
        self.thinking_pool.add_history(
            round_num,
            history_entry["builder"],
            history_entry["questioner"],
            history_entry["observer_decision"]
        )

        return {
            "round": round_num,
            "builder": builder_result,
            "questioner": questioner_result,
            "observer": observer_result,
            "history_entry": history_entry
        }

    def run_debate(self, topic: str, num_rounds: int = 3) -> Dict[str, Any]:
        results = []

        for round_num in range(1, num_rounds + 1):
            round_result = self.run_round(round_num, topic)
            results.append(round_result)

            self.thinking_pool.clear_for_new_round()

        return {
            "topic": topic,
            "num_rounds": num_rounds,
            "all_rounds": results,
            "thinking_venation": self.thinking_pool.get_final_venation(),
            "thinking_pool": self.thinking_pool.to_dict()
        }


builder_agent = BuilderAgent()
questioner_agent = QuestionerAgent()
observer_agent = ObserverAgent()
