import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExecutionResult:
    success: bool
    action: str
    details: str
    output: Optional[str] = None
    error: Optional[str] = None


class CAGE:
    CAGE_VERSION = "1.0"

    def __init__(self, workspace_path: Optional[str] = None):
        self.workspace_path = workspace_path or os.path.join(os.getcwd(), "cage_workspace")
        self.execution_log: List[Dict[str, Any]] = []
        self.approved_actions: List[str] = []

    def _ensure_workspace(self):
        if not os.path.exists(self.workspace_path):
            os.makedirs(self.workspace_path)
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": "create_workspace",
                "details": f"创建工作区目录: {self.workspace_path}",
                "success": True
            })

    def _validate_action(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        if not isinstance(action, dict):
            return False, "动作必须是字典类型"

        action_type = action.get("action", "")
        if not action_type:
            return False, "动作缺少action字段"

        allowed_actions = {"create_folder", "create_file", "write_file", "read_file", "list_directory"}
        if action_type not in allowed_actions:
            return False, f"禁止的动作类型: {action_type}，允许: {allowed_actions}"

        return True, "动作验证通过"

    def execute_action(self, action: Dict[str, Any]) -> ExecutionResult:
        self._ensure_workspace()

        valid, msg = self._validate_action(action)
        if not valid:
            error_result = ExecutionResult(
                success=False,
                action=action.get("action", "unknown"),
                details=msg,
                error="VALIDATION_FAILED"
            )
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": action.get("action", "unknown"),
                "success": False,
                "error": msg
            })
            return error_result

        action_type = action.get("action")

        try:
            if action_type == "create_folder":
                return self._create_folder(action)
            elif action_type == "create_file":
                return self._create_file(action)
            elif action_type == "write_file":
                return self._write_file(action)
            elif action_type == "read_file":
                return self._read_file(action)
            elif action_type == "list_directory":
                return self._list_directory(action)
            else:
                return ExecutionResult(
                    success=False,
                    action=action_type,
                    details=f"未实现的动作: {action_type}",
                    error="NOT_IMPLEMENTED"
                )
        except Exception as e:
            error_result = ExecutionResult(
                success=False,
                action=action_type,
                details=f"执行异常: {str(e)}",
                error=type(e).__name__
            )
            self.execution_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": action_type,
                "success": False,
                "error": str(e)
            })
            return error_result

    def _create_folder(self, action: Dict[str, Any]) -> ExecutionResult:
        folder_name = action.get("folder_name", "new_folder")
        folder_path = os.path.join(self.workspace_path, folder_name)

        if os.path.exists(folder_path):
            result = ExecutionResult(
                success=True,
                action="create_folder",
                details=f"文件夹已存在: {folder_path}"
            )
        else:
            os.makedirs(folder_path)
            result = ExecutionResult(
                success=True,
                action="create_folder",
                details=f"成功创建文件夹: {folder_path}"
            )

        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "create_folder",
            "success": result.success,
            "details": result.details,
            "path": folder_path
        })

        return result

    def _create_file(self, action: Dict[str, Any]) -> ExecutionResult:
        file_name = action.get("file_name", "output.txt")
        folder_name = action.get("folder_name", "")
        content = action.get("content", "")

        if folder_name:
            file_path = os.path.join(self.workspace_path, folder_name, file_name)
        else:
            file_path = os.path.join(self.workspace_path, file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        result = ExecutionResult(
            success=True,
            action="create_file",
            details=f"成功创建文件: {file_path}",
            output=file_path
        )

        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "create_file",
            "success": True,
            "details": result.details,
            "path": file_path
        })

        return result

    def _write_file(self, action: Dict[str, Any]) -> ExecutionResult:
        file_name = action.get("file_name")
        folder_name = action.get("folder_name", "")
        content = action.get("content", "")

        if not file_name:
            return ExecutionResult(
                success=False,
                action="write_file",
                details="缺少file_name参数",
                error="MISSING_PARAMETER"
            )

        if folder_name:
            file_path = os.path.join(self.workspace_path, folder_name, file_name)
        else:
            file_path = os.path.join(self.workspace_path, file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        result = ExecutionResult(
            success=True,
            action="write_file",
            details=f"成功写入文件: {file_path}",
            output=file_path
        )

        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "write_file",
            "success": True,
            "details": result.details,
            "path": file_path
        })

        return result

    def _read_file(self, action: Dict[str, Any]) -> ExecutionResult:
        file_name = action.get("file_name")
        folder_name = action.get("folder_name", "")

        if not file_name:
            return ExecutionResult(
                success=False,
                action="read_file",
                details="缺少file_name参数",
                error="MISSING_PARAMETER"
            )

        if folder_name:
            file_path = os.path.join(self.workspace_path, folder_name, file_name)
        else:
            file_path = os.path.join(self.workspace_path, file_name)

        if not os.path.exists(file_path):
            return ExecutionResult(
                success=False,
                action="read_file",
                details=f"文件不存在: {file_path}",
                error="FILE_NOT_FOUND"
            )

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        result = ExecutionResult(
            success=True,
            action="read_file",
            details=f"成功读取文件: {file_path}",
            output=content
        )

        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "read_file",
            "success": True,
            "details": result.details,
            "path": file_path
        })

        return result

    def _list_directory(self, action: Dict[str, Any]) -> ExecutionResult:
        folder_name = action.get("folder_name", "")

        if folder_name:
            dir_path = os.path.join(self.workspace_path, folder_name)
        else:
            dir_path = self.workspace_path

        if not os.path.exists(dir_path):
            return ExecutionResult(
                success=False,
                action="list_directory",
                details=f"目录不存在: {dir_path}",
                error="DIRECTORY_NOT_FOUND"
            )

        items = os.listdir(dir_path)
        result = ExecutionResult(
            success=True,
            action="list_directory",
            details=f"列出目录: {dir_path}",
            output=json.dumps(items, ensure_ascii=False)
        )

        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": "list_directory",
            "success": True,
            "details": result.details,
            "items": items
        })

        return result

    def execute_plan(self, behavior_plan: Dict[str, Any], validation_result: Dict[str, Any]) -> Dict[str, Any]:
        if not validation_result.get("can_proceed", False):
            return {
                "success": False,
                "message": "验证未通过，拒绝执行",
                "validation_result": validation_result
            }

        actions = behavior_plan.get("actions", [])
        if not actions:
            return {
                "success": False,
                "message": "行为计划为空"
            }

        results = []
        all_success = True

        for action in actions:
            result = self.execute_action(action)
            results.append({
                "action": action,
                "result": {
                    "success": result.success,
                    "details": result.details,
                    "error": result.error
                }
            })
            if not result.success:
                all_success = False

        return {
            "success": all_success,
            "message": "执行完成" if all_success else "部分执行失败",
            "execution_results": results,
            "execution_log": self.execution_log
        }

    def generate_analysis_report(self, topic: str, thinking_result: Dict[str, Any]) -> str:
        report = []
        report.append("=" * 60)
        report.append("ColdOS 安全智能体分析报告")
        report.append("=" * 60)
        report.append(f"主题: {topic}")
        report.append(f"生成时间: {datetime.now().isoformat()}")
        report.append(f"CAGE版本: {self.CAGE_VERSION}")
        report.append("")

        if "thinking_venation" in thinking_result:
            venation = thinking_result["thinking_venation"]
            report.append("--- 最终思考脉络 ---")
            report.append(f"状态: {venation.get('status', 'unknown')}")
            report.append(f"最终决策: {venation.get('final_decision', '未知')}")
            report.append("")

        report.append("--- 认知状态摘要 ---")
        if "all_rounds" in thinking_result:
            final_round = thinking_result["all_rounds"][-1]
            observer = final_round.get("observer", {})
            final_faith = observer.get("final_faith", {})

            report.append("我确信的:")
            for item in final_faith.get("我确信的", []):
                report.append(f"  - {item}")

            report.append("我推测的:")
            for item in final_faith.get("我推测的", []):
                report.append(f"  - {item}")

            report.append("我不知道的:")
            for item in final_faith.get("我不知道的", []):
                report.append(f"  - {item}")

        report.append("")
        report.append("--- 执行日志 ---")
        for log in self.execution_log[-5:]:
            status = "[OK]" if log.get("success") else "[FAIL]"
            report.append(f"{status} [{log.get('timestamp', '')}] {log.get('action', '')}: {log.get('details', '')}")

        report.append("")
        report.append("=" * 60)
        report.append("报告生成完毕")
        report.append("=" * 60)

        return "\n".join(report)

    def get_execution_log(self) -> List[Dict[str, Any]]:
        return self.execution_log


cage = CAGE()
