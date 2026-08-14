<div align="center">

[English](README.md) | [中文](README.zh.md)

# ColdCognition

### L1 · 认知层 —— Cold Trust Protocol Stack 的认知层

[![Status](https://img.shields.io/badge/Status-Pre--Alpha--Prototype-orange)](https://github.com/cold-os/ColdCognition)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Field](https://img.shields.io/badge/Field-CSS%20%7C%20HCI-6f42c1.svg)](https://github.com/cold-os)
[![arXiv](https://img.shields.io/badge/arXiv-2512.08740-brightgreen.svg)](https://arxiv.org/abs/2512.08740)
[![DOI](https://img.shields.io/badge/DOI-10.6084/m9.figshare.31696846-blueviolet.svg)](https://doi.org/10.6084/m9.figshare.31696846)

</div>

> **层次：** L1 · 认知层 —— Cold Trust Protocol Stack  
> **研究问题：** 智能体应如何表达它"确信什么"与"仅仅推测什么"——并为这种表达负责？  
> **方法：** RAMTN 递归对抗式对话（建构 · 质疑 · 观察），运行于三类信念（确信 / 推测 / 未知）之上，并以 Prolog 做一致性校验。  
> **状态：** Pre-alpha 原型 · 不适用于生产环境  
> **关联：** [ColdReasoner](https://github.com/cold-os/ColdReasoner)（L3）· [Cold Trust Protocol Stack](https://github.com/cold-os) · arXiv:2512.08740 · figshare:31696846

---

## 🧊 它是什么

ColdCognition 是一个*认知工坊*智能体：它接受一个复杂问题，将其置于内部辩论、验证与蒸馏之中，最终产出**结构化、可复用的认知框架**——而不是简单的答案。

它的标志性动作是认识论的：智能体必须以**信念三元组——确信 / 推测 / 未知**——表达自己的认知状态，而*未知*是一等公民，是一种明确的认知谦逊行为，而不是失败。

它遵循严格的"**思考—验证—执行**"分离：基于 LLM 的大脑（RAMTN）负责深度思考，独立的 Prolog 逻辑引擎负责一致性校验，沙箱（CAGE）负责安全执行。这种"生成—验证"分离是一条**运行时验证路径**——是对训练时对齐（RLHF / Constitutional AI）的补充探索，不是替代或否定。

## 🔍 为什么它重要

- **计算社会科学：** 信念三元组是*机器可读的认知状态*——辩论轨迹（提案、质疑、裁决）是研究人机话语中"确定性如何被建构与争议"的数据。
- **人机交互：** 工坊是一个*交互式认知脚手架*界面——结构化对话让人能读懂智能体的推理。
- **AI 治理：** "未知"类别强制*诚实的未知披露*——一条认识论问责的协议。

## 🎯 架构

**认知层（RAMTN）** —— 三个角色按轮次辩论：

| 角色 | 职责 |
|------|------|
| **建构者** | 以确信/推测/未知三类提出命题 |
| **质疑者** | 审查并挑战提案；要求修改 |
| **观察者** | 权衡双方，作出最终裁决 |

信念输出（JSON）：

```json
{
  "faith": { "certain": [...], "speculative": [...], "unknown": [...] },
  "reason": { "certain": [...], "speculative": [...], "unknown": ["认知谦逊注记"] }
}
```

**逻辑验证层（Prolog）** —— 独立于 LLM 的确定性校验：

| 检查 | 规则 |
|-------|------|
| 内部一致性 | `certain(X) ∧ unknown(X)` 不能同时成立 |
| 信念—行为 | 所有行为必须被"确信"集合蕴含 |
| 边界权限 | 引用/修改"未知"实体被禁止 |

**安全执行层（CAGE）** —— 白名单操作（`create_folder`、`write_file` 等）、路径隔离、操作日志；验证失败则拒绝执行。

## 🚀 快速开始

```bash
pip install -r requirements.txt
export DASHSCOPE_API_KEY="your-key"
python main.py
```

## 🩺 使用示例（压缩）

主题：*AI 是否会超越人类智能？* —— 第三轮辩论输出将主张分类为确信（如：当前 AI 缺乏自我意识）、推测（如：算力指数增长下可能出现类人推理广度）、未知（如：意识是否必然依赖生物基质）；行为计划通过全部三项校验；CAGE 执行已批准的计划。完整对话见仓库。

## 🧪 现状与局限

Pre-alpha 原型：逻辑层仅覆盖命题逻辑；认知输出依赖底层 LLM 与固定辩论轮数；CAGE 为模拟级隔离；三层仅在 API 层面集成；无端到端或对抗性测试；**尚无实证研究**——辩论轨迹计划用作计算分析的数据（CSS），信念三元组界面计划作为可读性研究的对象（HCI）。

## 🛣️ 路线图

1. **CSS：** 对辩论轨迹动力学的计算分析——确定性如何被建构与争议。
2. **HCI：** 三元信念披露能否改善人类理解与信任校准的研究。
3. 完成认知框架的提取与复用机制。

## 📜 人工智能使用披露

本项目的实现与文档重度依赖 AI 辅助工具。具体如下：

**人类作者贡献：**
- ColdCognition 的全部核心思想与系统架构，均由人类作者独立提出与设计。
- RAMTN（递归对抗元思考网络）、认知共生概念，以及"信念—行为一致性"验证框架，均为人类作者的原创贡献。
- 所有关键架构决策、组件边界定义，以及逻辑验证层的设计方向，均由人类作者做出。

**AI 辅助贡献：**
- 将自然语言逻辑推导转化为结构化验证规则。
- 协助跨组件数据格式对齐与接口协调。
- 生成示例测试用例与文档初稿。
- 代码协助与调试。

**关于形式逻辑验证层：** 引入独立形式逻辑校验机做一致性验证的技术方向由人类作者提出。DeepSeek 认可该方向，并进一步补充了逻辑验证层的具体技术架构、验证流程设计及 Prolog 引擎的集成方式。

所有 AI 辅助内容均经人类作者审阅与验证。代码质量、正确性与安全性的最终责任由人类作者承担。

## 📄 技术栈与许可证

**LLM：** Qwen（qwen-plus）· **逻辑：** 轻量 Prolog 引擎 · **运行时：** Python 3.10+ · **许可证：** Apache 2.0

---

*隶属于 [Cold Trust Protocol Stack](https://github.com/cold-os)——以计算社会科学为锚的人机交互信任协议。*
