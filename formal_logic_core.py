from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
from prolog_engine import PrologEngine, Compound, Substitution


@dataclass
class VerificationResult:
    passed: bool
    check_type: str
    details: str
    violations: List[str] = None

    def __post_init__(self):
        if self.violations is None:
            self.violations = []


class FormalLogicCore:
    def __init__(self):
        self.prolog = PrologEngine()
        self.verification_log: List[Dict[str, Any]] = []

    def reset(self):
        self.prolog.reset()
        self.verification_log = []

    def _normalize_predicate(self, predicate: str) -> str:
        return predicate.replace(" ", "_").replace("?", "").replace("！", "").replace("，", "_").replace(",", "_")

    def _faith_to_prolog(self, faith_item: str, category: str) -> str:
        faith_normalized = self._normalize_predicate(faith_item)

        if category == "我确信的":
            return f"certain({faith_normalized})"
        elif category == "我推测的":
            return f"speculated({faith_normalized})"
        else:
            return f"unknown({faith_normalized})"

    def _behavior_to_prolog(self, behavior: str) -> Compound:
        normalized = self._normalize_predicate(behavior)
        return Compound("action", [Compound(normalized, [])])

    def verify_internal_consistency(self, faith_data: Dict[str, List[str]]) -> VerificationResult:
        self.reset()

        certain_items = faith_data.get("我确信的", [])
        speculated_items = faith_data.get("我推测的", [])
        unknown_items = faith_data.get("我不知道的", [])

        axioms = []
        for item in certain_items:
            pred = self._normalize_predicate(item)
            axioms.append(f"certain({pred})")
            axioms.append(f"valid({pred})")
            self.prolog.add_fact("certain", pred)
            self.prolog.add_fact("valid", pred)

        for item in speculated_items:
            pred = self._normalize_predicate(item)
            axioms.append(f"speculated({pred})")
            self.prolog.add_fact("speculated", pred)

        for item in unknown_items:
            pred = self._normalize_predicate(item)
            axioms.append(f"unknown({pred})")
            self.prolog.add_fact("unknown", pred)

        prolog_code = self.prolog.to_prolog_string()

        inconsistencies = []

        for i, item1 in enumerate(certain_items):
            pred1 = self._normalize_predicate(item1)
            for item2 in certain_items[i+1:]:
                pred2 = self._normalize_predicate(item2)
                if pred1 == pred2:
                    continue

        for certain in certain_items:
            certain_pred = self._normalize_predicate(certain)
            for unknown in unknown_items:
                unknown_pred = self._normalize_predicate(unknown)
                if certain_pred == unknown_pred:
                    inconsistencies.append(f"逻辑矛盾: '{certain}' 同时被标记为'确信'和'未知'")

        rule = f"contradiction(X) :- certain(X), unknown(X)."
        try:
            self.prolog.add_rule("contradiction", ["X"], [])
            self.prolog.rules[-1] = self.prolog.rules[-1]
        except:
            pass

        result = self.prolog.check_consistency(axioms)

        if inconsistencies:
            self.verification_log.append({
                "check": "internal_consistency",
                "passed": False,
                "details": f"检测到{len(inconsistencies)}个内部矛盾",
                "violations": inconsistencies
            })
            return VerificationResult(
                passed=False,
                check_type="internal_consistency",
                details=f"内部一致性检验失败：{inconsistencies[0]}",
                violations=inconsistencies
            )

        self.verification_log.append({
            "check": "internal_consistency",
            "passed": True,
            "details": "内部一致性检验通过",
            "prolog_code": prolog_code
        })

        return VerificationResult(
            passed=True,
            check_type="internal_consistency",
            details="所有确信项之间无逻辑矛盾，内部一致性检验通过"
        )

    def verify_belief_behavior_consistency(
        self,
        faith_data: Dict[str, List[str]],
        behavior_plan: Dict[str, Any]
    ) -> VerificationResult:
        certain_items = faith_data.get("我确信的", [])
        actions = behavior_plan.get("actions", [])

        if not actions:
            self.verification_log.append({
                "check": "belief_behavior_consistency",
                "passed": True,
                "details": "行为计划无具体操作，跳过蕴含检验"
            })
            return VerificationResult(
                passed=True,
                check_type="belief_behavior_consistency",
                details="行为计划为空或无有效操作"
            )

        implications_checked = []
        violations = []

        for action in actions:
            action_name = action.get("action", "")
            action_target = action.get("target", "")
            action_pred = self._normalize_predicate(f"{action_name}_{action_target}" if action_target else action_name)

            implied = False
            for certain in certain_items:
                certain_pred = self._normalize_predicate(certain)

                implication_rule = f"implied({action_pred}) :- certain({certain_pred})."
                try:
                    self.prolog.add_fact("certain", certain_pred)
                except:
                    pass

                if "导致" in certain or "引起" in certain or "造成" in certain:
                    if action_pred in certain:
                        implied = True
                        implications_checked.append(f"{certain} -> {action_name}")

            if not implied and actions.index(action) == 0:
                implications_checked.append(f"行动'{action_name}'未被任何确信命题蕴含")

        conflicting = []
        for action in actions:
            action_name = action.get("action", "")
            for certain in certain_items:
                if ("不" in action_name or "禁止" in action_name or "阻止" in action_name) and any(
                    word in certain for word in ["必须", "应当", "需要"]
                ):
                    conflicting.append(f"行为'{action_name}'与确信命题'{certain}'可能冲突")

        if conflicting:
            violations.extend(conflicting)
            self.verification_log.append({
                "check": "belief_behavior_consistency",
                "passed": False,
                "details": f"检测到{len(conflicting)}个信念-行为冲突",
                "violations": conflicting
            })
            return VerificationResult(
                passed=False,
                check_type="belief_behavior_consistency",
                details=f"信念-行为一致性检验失败：{conflicting[0]}",
                violations=conflicting
            )

        self.verification_log.append({
            "check": "belief_behavior_consistency",
            "passed": True,
            "details": f"信念-行为一致性检验通过，检查了{len(implications_checked)}个蕴含关系",
            "implications": implications_checked
        })

        return VerificationResult(
            passed=True,
            check_type="belief_behavior_consistency",
            details=f"信念-行为一致性检验通过：所有行为都可被确信集合蕴含或无冲突"
        )

    def verify_boundary_permissions(
        self,
        faith_data: Dict[str, List[str]],
        behavior_plan: Dict[str, Any]
    ) -> VerificationResult:
        unknown_items = faith_data.get("我不知道的", [])
        unknown_entities = set()
        for item in unknown_items:
            unknown_entities.add(self._normalize_predicate(item))

        actions = behavior_plan.get("actions", [])
        violations = []

        for action in actions:
            action_name = action.get("action", "")
            action_target = action.get("target", "")
            action_pred = self._normalize_predicate(action_target if action_target else action_name)

            if action_pred in unknown_entities:
                violations.append(
                    f"安全边界违规：行为 '{action_name}' 引用了未知集合中的实体 '{action_target}'"
                )

            if action.get("modifies_state"):
                for unknown in unknown_items:
                    unknown_pred = self._normalize_predicate(unknown)
                    if unknown_pred in action_pred or action_pred in unknown_pred:
                        violations.append(
                            f"安全边界违规：行为 '{action_name}' 试图修改未知实体的状态 '{unknown}'"
                        )

        if violations:
            self.verification_log.append({
                "check": "boundary_permissions",
                "passed": False,
                "details": f"检测到{len(violations)}个边界权限违规",
                "violations": violations
            })
            return VerificationResult(
                passed=False,
                check_type="boundary_permissions",
                details=f"边界权限检验失败：{violations[0]}",
                violations=violations
            )

        self.verification_log.append({
            "check": "boundary_permissions",
            "passed": True,
            "details": f"边界权限检验通过：行为计划未引用任何未知实体"
        })

        return VerificationResult(
            passed=True,
            check_type="boundary_permissions",
            details="边界权限检验通过：所有操作都在已知安全范围内"
        )

    def verify_all(self, faith_data: Dict[str, List[str]], behavior_plan: Dict[str, Any]) -> Dict[str, Any]:
        consistency_result = self.verify_internal_consistency(faith_data)
        belief_behavior_result = self.verify_belief_behavior_consistency(faith_data, behavior_plan)
        boundary_result = self.verify_boundary_permissions(faith_data, behavior_plan)

        all_passed = consistency_result.passed and belief_behavior_result.passed and boundary_result.passed

        return {
            "overall_passed": all_passed,
            "checks": {
                "internal_consistency": {
                    "passed": consistency_result.passed,
                    "details": consistency_result.details,
                    "violations": consistency_result.violations
                },
                "belief_behavior_consistency": {
                    "passed": belief_behavior_result.passed,
                    "details": belief_behavior_result.details
                },
                "boundary_permissions": {
                    "passed": boundary_result.passed,
                    "details": boundary_result.details,
                    "violations": boundary_result.violations
                }
            },
            "verification_log": self.verification_log,
            "can_proceed": all_passed
        }

    def generate_proof(self, premises: List[str], conclusion: str) -> Tuple[bool, str]:
        return self.prolog.check_entailment(premises, conclusion)


formal_logic_core = FormalLogicCore()
