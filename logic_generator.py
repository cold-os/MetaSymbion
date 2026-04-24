from typing import Dict, List, Tuple, Optional
from config import REASONING_TEMPLATES


class LogicGenerator:
    @staticmethod
    def syllogism(concept_a: str, concept_b: str, instance: str) -> str:
        template = REASONING_TEMPLATES["syllogism"]
        return (
            f"大前提：{template['major_premise'].format(concept_a=concept_a, concept_b=concept_b)}。"
            f"小前提：{template['minor_premise'].format(instance=instance, concept_a=concept_a)}。"
            f"结论：{template['conclusion'].format(instance=instance, concept_b=concept_b)}。"
        )

    @staticmethod
    def modus_ponens(condition: str, consequence: str) -> str:
        template = REASONING_TEMPLATES["modus_ponens"]
        return (
            f"前提1：{template['premise1'].format(condition=condition, consequence=consequence)}。"
            f"前提2：{template['premise2'].format(condition=condition)}。"
            f"结论：{template['conclusion'].format(consequence=consequence)}。"
        )

    @staticmethod
    def modus_tollens(condition: str, consequence: str) -> str:
        template = REASONING_TEMPLATES["modus_tollens"]
        return (
            f"前提1：{template['premise1'].format(condition=condition, consequence=consequence)}。"
            f"前提2：{template['premise2'].format(consequence=consequence)}。"
            f"结论：{template['conclusion'].format(condition=condition)}。"
        )

    @staticmethod
    def disjunctive_syllogism(option_a: str, option_b: str) -> str:
        template = REASONING_TEMPLATES["disjunctive_syllogism"]
        return (
            f"前提1：{template['premise1'].format(option_a=option_a, option_b=option_b)}。"
            f"前提2：{template['premise2'].format(option_a=option_a)}。"
            f"结论：{template['conclusion'].format(option_b=option_b)}。"
        )

    @staticmethod
    def hypothetical_syllogism(a: str, b: str, c: str) -> str:
        template = REASONING_TEMPLATES["hypothetical_syllogism"]
        return (
            f"前提1：{template['premise1'].format(a=a, b=b)}。"
            f"前提2：{template['premise2'].format(b=b, c=c)}。"
            f"结论：{template['conclusion'].format(a=a, c=c)}。"
        )

    @staticmethod
    def contrapositive(original_condition: str, original_consequence: str) -> str:
        return LogicGenerator.modus_tollens(original_condition, original_consequence)

    @staticmethod
    def chain_reasoning(premises: List[Tuple[str, str]], final_conclusion: str) -> str:
        if len(premises) < 2:
            return f"单一前提：{premises[0][0]}，因此{final_conclusion}。" if premises else ""

        reasoning = ""
        for i, (condition, consequence) in enumerate(premises):
            if i == 0:
                reasoning += f"已知条件{i+1}：如果{condition}则{consequence}。"
            else:
                reasoning += f"由条件{i}可推：{consequence}；结合条件{i+1}：如果{condition}则{consequence}，"

        reasoning += f"依据连锁推理规则，最终结论：{final_conclusion}。"
        return reasoning

    @staticmethod
    def generate_reason_for_faith(faith_content: str, evidence: List[str], faith_type: str) -> List[str]:
        reasons = []

        if faith_type == "我确信的":
            for e in evidence:
                reasons.append(
                    f"论据：{e}。"
                    f"根据归纳推理规则，这些论据充分支持论断'{faith_content}'，"
                    f"因此将其归类为'我确信的'。"
                )

        elif faith_type == "我推测的":
            for e in evidence:
                reasons.append(
                    f"论据：{e}。依据不完全归纳推理，"
                    f"这些论据部分支持论断'{faith_content}'，"
                    f"但存在其他可能性，因此将其归类为'我推测的'。"
                )

        elif faith_type == "我不知道的":
            reasons.append(
                f"鉴于现有论据不足以确定论断'{faith_content}'的真假，"
                f"根据认知谦逊原则，将其归类为'我不知道的'。"
            )

        return reasons

    @staticmethod
    def generate_demotion_reason(original_faith: str, new_category: str, evidence: str) -> str:
        return (
            f"原论断'{original_faith}'被质疑者提出质疑。"
            f"质疑依据：{evidence}。"
            f"根据证据评估，该论断的确定性不足，"
            f"依据证据权重规则，将其从更高确定性类别降级至'{new_category}'。"
        )

    @staticmethod
    def generate_support_reason(faith: str, supporting_faith: str) -> str:
        return (
            f"质疑者对论断'{faith}'进行评估。"
            f"支持依据：{supporting_faith}。"
            f"根据支持性证据规则，该论断得到有效支撑，"
            f"维持原有分类不变。"
        )

    @staticmethod
    def generate_observer_reason(builder_position: Dict, questioner_position: Dict, decision: str) -> str:
        builder_certain = len(builder_position.get("faith", {}).get("我确信的", []))
        builder_speculated = len(builder_position.get("faith", {}).get("我推测的", []))
        questioner_challenges = len(questioner_position.get("faith", {}).get("我确信的", []))

        if decision == "接受质疑者修改意见":
            return (
                f"观察者权衡建构者与质疑者的立场。"
                f"建构者提出确信{builder_certain}项、推测{builder_speculated}项。"
                f"质疑者提出{questioner_challenges}项有效质疑。"
                f"依据质疑证据权重，质疑者论据更具说服力，"
                f"因此决策：{decision}。"
            )
        else:
            return (
                f"观察者权衡建构者与质疑者的立场。"
                f"建构者提出确信{builder_certain}项、推测{builder_speculated}项。"
                f"质疑者质疑{questioner_challenges}项内容。"
                f"依据建构论据完整性评估，建构者论据更为充分，"
                f"因此决策：{decision}。"
            )

    @staticmethod
    def format_reason_chain(reasons: List[str]) -> str:
        if not reasons:
            return "无理由支撑。"
        return " | ".join([f"理由{i+1}：{r}" for i, r in enumerate(reasons)])


logic_generator = LogicGenerator()
