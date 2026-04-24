from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class FaithCategory(Enum):
    CERTAIN = "我确信的"
    SPECULATED = "我推测的"
    UNKNOWN = "我不知道的"


class PoolSection(Enum):
    CONSTRUCTION = "construction"
    QUESTIONING = "questioning"


@dataclass
class FaithItem:
    content: str
    faith_type: FaithCategory
    source_agent: str
    supporting_reasons: List[str] = field(default_factory=list)


@dataclass
class AgentOutput:
    agent_role: str
    faith: Dict[str, List[str]]
    reason: Dict[str, List[str]]
    raw_response: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps({
            "agent_role": self.agent_role,
            "faith": self.faith,
            "reason": self.reason
        }, ensure_ascii=False, indent=2)


class ThinkingPool:
    def __init__(self):
        self.construction = {
            FaithCategory.CERTAIN.value: [],
            FaithCategory.SPECULATED.value: [],
            FaithCategory.UNKNOWN.value: []
        }
        self.questioning = {
            FaithCategory.CERTAIN.value: [],
            FaithCategory.SPECULATED.value: [],
            FaithCategory.UNKNOWN.value: []
        }
        self.thinking_history: List[Dict[str, Any]] = []
        self.current_round: int = 0

    def add_to_construction(self, faith_category: FaithCategory, faith_item: str, agent_role: str):
        item = {
            "content": faith_item,
            "agent": agent_role,
            "category": faith_category.value
        }
        self.construction[faith_category.value].append(item)

    def add_to_questioning(self, faith_category: FaithCategory, faith_item: str, agent_role: str):
        item = {
            "content": faith_item,
            "agent": agent_role,
            "category": faith_category.value
        }
        self.questioning[faith_category.value].append(item)

    def add_history(self, round_num: int, builder_output: Dict, questioner_output: Dict, observer_decision: Dict):
        self.thinking_history.append({
            "round": round_num,
            "builder": builder_output,
            "questioner": questioner_output,
            "observer_decision": observer_decision
        })

    def get_construction_by_category(self, faith_category: FaithCategory) -> List[Dict]:
        return self.construction[faith_category.value]

    def get_questioning_by_category(self, faith_category: FaithCategory) -> List[Dict]:
        return self.questioning[faith_category.value]

    def get_all_construction(self) -> Dict:
        return self.construction

    def get_all_questioning(self) -> Dict:
        return self.questioning

    def get_history(self) -> List[Dict]:
        return self.thinking_history

    def get_history_summary(self, round_num: Optional[int] = None) -> str:
        if round_num is not None:
            history_items = [h for h in self.thinking_history if h["round"] == round_num]
        else:
            history_items = self.thinking_history

        summary_parts = []
        for h in history_items:
            round_summary = f"第{h['round']}轮辩论："
            builder = h.get("builder", {})
            questioner = h.get("questioner", {})
            observer = h.get("observer_decision", {})

            round_summary += f"建构者提出确信{len(builder.get('faith', {}).get('我确信的', []))}项、"
            round_summary += f"推测{len(builder.get('faith', {}).get('我推测的', []))}项、"
            round_summary += f"未知{len(builder.get('faith', {}).get('我不知道的', []))}项；"

            round_summary += f"质疑者质疑确信{len(questioner.get('faith', {}).get('我确信的', []))}项、"
            round_summary += f"推测{len(questioner.get('faith', {}).get('我推测的', []))}项；"

            decision = observer.get("decision", "未知")
            round_summary += f"观察者决策：{decision}"
            summary_parts.append(round_summary)

        return " | ".join(summary_parts)

    def clear_for_new_round(self):
        self.current_round += 1

    def to_dict(self) -> Dict:
        return {
            "round": self.current_round,
            "construction": self.construction,
            "questioning": self.questioning,
            "thinking_history": self.thinking_history
        }

    def get_final_venation(self) -> Dict[str, Any]:
        if not self.thinking_history:
            return {"status": "no_history", "content": "无思考历史"}

        final_round = self.thinking_history[-1]
        return {
            "status": "complete",
            "final_decision": final_round.get("observer_decision", {}).get("decision", "未知"),
            "all_rounds": self.thinking_history,
            "summary": self.get_history_summary()
        }
