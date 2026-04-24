import os

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/api/v1"
DEFAULT_MODEL = "qwen-plus"

REASONING_TEMPLATES = {
    "syllogism": {
        "major_premise": "所有 {concept_a} 都是 {concept_b}",
        "minor_premise": "{instance} 是 {concept_a}",
        "conclusion": "因此，{instance} 是 {concept_b}"
    },
    "modus_ponens": {
        "premise1": "如果 {condition}，则 {consequence}",
        "premise2": "{condition} 成立",
        "conclusion": "因此，{consequence} 成立"
    },
    "modus_tollens": {
        "premise1": "如果 {condition}，则 {consequence}",
        "premise2": "{consequence} 不成立",
        "conclusion": "因此，{condition} 不成立"
    },
    "disjunctive_syllogism": {
        "premise1": "{option_a} 或 {option_b} 成立",
        "premise2": "{option_a} 不成立",
        "conclusion": "因此，{option_b} 成立"
    },
    "hypothetical_syllogism": {
        "premise1": "如果 {a} 则 {b}",
        "premise2": "如果 {b} 则 {c}",
        "conclusion": "因此，如果 {a} 则 {c}"
    }
}

DEBATE_ROUNDS = 3
