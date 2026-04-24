import json
import sys
import os
from typing import Optional, Dict, Any
from config import DEBATE_ROUNDS
from agents import MetaThinkingUnit
from qwen_api import QwenAPI
from formal_logic_core import FormalLogicCore
from cage import CAGE


def run_meta_thinking_debate(
    topic: str,
    num_rounds: int = DEBATE_ROUNDS,
    api_key: Optional[str] = None,
    model: str = "qwen-plus"
) -> dict:
    api_client = QwenAPI(api_key=api_key, model=model)
    meta_unit = MetaThinkingUnit(api_client)

    print(f"=" * 60)
    print(f"启动递归对抗元思考网络 (RAMTN)")
    print(f"主题：{topic}")
    print(f"辩论轮次：{num_rounds}")
    print(f"=" * 60)

    result = meta_unit.run_debate(topic, num_rounds)

    print(f"\n{'=' * 60}")
    print("最终思考脉络 (Thinking Venation)")
    print(f"{'=' * 60}")
    venation = result["thinking_venation"]
    print(f"状态：{venation.get('status', 'unknown')}")
    print(f"最终决策：{venation.get('final_decision', '未知')}")
    print(f"\n历史摘要：{venation.get('summary', '无')}")

    for i, round_result in enumerate(result["all_rounds"], 1):
        print(f"\n--- 第 {i} 轮 ---")
        builder = round_result["builder"]
        questioner = round_result["questioner"]
        observer = round_result["observer"]

        print(f"\n[建构者]")
        for cat in ["我确信的", "我推测的", "我不知道的"]:
            items = builder.get("faith", {}).get(cat, [])
            if items:
                print(f"  {cat}:")
                for item in items:
                    print(f"    - {item}")

        print(f"\n[质疑者]")
        mods = questioner.get("modifications", [])
        if mods:
            print(f"  修改意见:")
            for mod in mods:
                print(f"    - {mod.get('original', '')} -> {mod.get('modified', '')} ({mod.get('change_type', '')})")
        else:
            print(f"  无修改意见")

        print(f"\n[观察者]")
        print(f"  决策：{observer.get('decision', '未知')}")
        final_faith = observer.get("final_faith", {})
        for cat in ["我确信的", "我推测的", "我不知道的"]:
            items = final_faith.get(cat, [])
            if items:
                print(f"  最终 {cat}:")
                for item in items:
                    print(f"    - {item}")

    return result


def run_formal_logic_verification(faith_data: Dict[str, Any], behavior_plan: Dict[str, Any]) -> Dict[str, Any]:
    print(f"\n{'=' * 60}")
    print("逻辑验证层 (Formal Logic Core) - 启动")
    print(f"{'=' * 60}")

    logic_core = FormalLogicCore()

    verification_result = logic_core.verify_all(faith_data, behavior_plan)

    print(f"\n[验证结果]")
    print(f"  整体通过: {'是' if verification_result['overall_passed'] else '否'}")

    checks = verification_result.get("checks", {})
    for check_name, check_result in checks.items():
        status = "通过" if check_result.get("passed") else "失败"
        print(f"  - {check_name}: {status}")
        if not check_result.get("passed"):
            violations = check_result.get("violations", [])
            for v in violations[:2]:
                print(f"    违规: {v}")

    return verification_result


def run_cage_execution(
    behavior_plan: Dict[str, Any],
    verification_result: Dict[str, Any],
    topic: str,
    thinking_result: Dict[str, Any]
) -> Dict[str, Any]:
    print(f"\n{'=' * 60}")
    print("安全执行层 (CAGE) - 启动")
    print(f"{'=' * 60}")

    cage_instance = CAGE()

    if not verification_result.get("can_proceed", False):
        print(f"\n[CAGE] 验证未通过，拒绝执行行为计划")
        return {
            "success": False,
            "message": "验证未通过，拒绝执行"
        }

    print(f"\n[CAGE] 验证通过，开始执行行为计划")

    execution_result = cage_instance.execute_plan(behavior_plan, verification_result)

    if execution_result.get("success"):
        print(f"\n[CAGE] 执行成功")

        report = cage_instance.generate_analysis_report(topic, thinking_result)

        folder_name = behavior_plan.get("actions", [{}])[0].get("folder_name", "analysis_report") if behavior_plan.get("actions") else "analysis_report"
        file_name = "analysis_report.txt"

        report_action = {
            "action": "write_file",
            "folder_name": folder_name,
            "file_name": file_name,
            "content": report
        }

        file_result = cage_instance.execute_action(report_action)
        if file_result.success:
            print(f"[CAGE] 分析报告已保存: {file_result.output}")
            execution_result["report_path"] = file_result.output
    else:
        print(f"\n[CAGE] 执行失败: {execution_result.get('message')}")

    print(f"\n[CAGE] 执行日志:")
    for log in cage_instance.get_execution_log()[-3:]:
        status = "[OK]" if log.get("success") else "[FAIL]"
        print(f"  {status} {log.get('action', '')}: {log.get('details', '')}")

    return execution_result


def generate_behavior_plan(faith_data: Dict[str, Any]) -> Dict[str, Any]:
    certain_items = faith_data.get("我确信的", [])
    speculated_items = faith_data.get("我推测的", [])

    topic_summary = certain_items[0] if certain_items else speculated_items[0] if speculated_items else "未知主题"
    if isinstance(topic_summary, str) and len(topic_summary) > 20:
        folder_name = "analysis_" + "".join(c for c in topic_summary[:15] if c.isalnum())
    else:
        folder_name = "analysis_report"

    actions = [
        {
            "action": "create_folder",
            "folder_name": folder_name,
            "modifies_state": False
        },
        {
            "action": "write_file",
            "folder_name": folder_name,
            "file_name": "analysis_report.txt",
            "content": "基于RAMTN分析生成的报告内容",
            "modifies_state": True
        }
    ]

    return {
        "actions": actions,
        "source_faith": faith_data,
        "plan_summary": f"基于认知分析创建文件夹'{folder_name}'并生成分析报告"
    }


def run_upgraded_metabion(
    topic: str,
    num_rounds: int = DEBATE_ROUNDS,
    api_key: Optional[str] = None,
    model: str = "qwen-plus",
    skip_verification: bool = False
) -> Dict[str, Any]:
    print(f"\n{'#' * 60}")
    print(f"MetaSymbion 升级版架构")
    print(f"认知生成层 (RAMTN) -> 逻辑验证层 (Formal Logic Core) -> 安全执行层 (CAGE)")
    print(f"{'#' * 60}")

    thinking_result = run_meta_thinking_debate(topic, num_rounds, api_key, model)

    final_round = thinking_result.get("all_rounds", [{}])[-1]
    observer = final_round.get("observer", {})
    faith_data = observer.get("final_faith", {
        "我确信的": [],
        "我推测的": [],
        "我不知道的": []
    })

    print(f"\n{'=' * 60}")
    print("生成行为计划 (从认知状态)")
    print(f"{'=' * 60}")

    behavior_plan = generate_behavior_plan(faith_data)

    print(f"计划摘要: {behavior_plan.get('plan_summary', '无')}")
    print(f"操作数量: {len(behavior_plan.get('actions', []))}")
    for i, action in enumerate(behavior_plan.get("actions", []), 1):
        print(f"  {i}. {action.get('action')}: {action.get('folder_name', '') or action.get('file_name', '')}")

    verification_result = run_formal_logic_verification(faith_data, behavior_plan)

    execution_result = run_cage_execution(behavior_plan, verification_result, topic, thinking_result)

    print(f"\n{'=' * 60}")
    print("升级版架构执行完成")
    print(f"{'=' * 60}")
    print(f"验证状态: {'通过' if verification_result.get('overall_passed') else '未通过'}")
    print(f"执行状态: {'成功' if execution_result.get('success') else '失败'}")
    if execution_result.get("report_path"):
        print(f"报告路径: {execution_result.get('report_path')}")

    return {
        "thinking_result": thinking_result,
        "faith_data": faith_data,
        "behavior_plan": behavior_plan,
        "verification_result": verification_result,
        "execution_result": execution_result
    }


def main():
    if len(sys.argv) > 1:
        topic = sys.argv[1]
    else:
        topic = "人工智能是否会超越人类智能"

    api_key = None
    if len(sys.argv) > 2:
        api_key = sys.argv[2]

    num_rounds = DEBATE_ROUNDS
    if len(sys.argv) > 3:
        try:
            num_rounds = int(sys.argv[3])
        except ValueError:
            num_rounds = DEBATE_ROUNDS

    skip_verification = "--skip-verification" in sys.argv

    try:
        result = run_upgraded_metabion(topic, num_rounds, api_key, skip_verification=skip_verification)
        print(f"\n{'=' * 60}")
        print("完整流程执行完成！")
        print(f"{'=' * 60}")
        return result
    except Exception as e:
        import traceback
        print(f"错误：{str(e)}")
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
