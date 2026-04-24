from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass
import re


@dataclass
class Term:
    pass


@dataclass
class Atom(Term):
    name: str

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name


@dataclass
class Variable(Term):
    name: str

    def __str__(self):
        return f"?{self.name}"

    def __hash__(self):
        return hash(f"?{self.name}")

    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name


@dataclass
class Compound(Term):
    functor: str
    args: List[Term]

    def __str__(self):
        if not self.args:
            return self.functor
        args_str = ", ".join(str(a) for a in self.args)
        return f"{self.functor}({args_str})"

    def __hash__(self):
        return hash((self.functor, tuple(self.args)))

    def __eq__(self, other):
        return isinstance(other, Compound) and self.functor == other.functor and self.args == other.args


@dataclass
class Clause:
    head: Compound
    body: Optional[List[Compound]] = None

    def __str__(self):
        if self.body:
            body_str = ", ".join(str(p) for p in self.body)
            return f"{self.head} :- {body_str}."
        else:
            return f"{self.head}."


@dataclass
class Fact(Clause):
    def __init__(self, predicate: str, *args: str):
        self.head = Compound(predicate, [Atom(a) if not a.startswith("?") else Variable(a[1:]) for a in args])
        self.body = None


@dataclass
class Query:
    goals: List[Compound]

    def __str__(self):
        goals_str = ", ".join(str(g) for g in self.goals)
        return f"?- {goals_str}."


class Substitution:
    def __init__(self):
        self.bindings: Dict[str, Term] = {}

    def add(self, var: str, term: Term):
        self.bindings[var] = term

    def get(self, var: str) -> Optional[Term]:
        return self.bindings.get(var)

    def apply_to_term(self, term: Term) -> Term:
        if isinstance(term, Variable):
            bound = self.get(term.name)
            if bound:
                return self.apply_to_term(bound)
            return term
        elif isinstance(term, Compound):
            return Compound(term.functor, [self.apply_to_term(a) for a in term.args])
        return term

    def apply_to_compound(self, compound: Compound) -> Compound:
        return Compound(compound.functor, [self.apply_to_term(a) for a in compound.args])

    def merge(self, other: 'Substitution') -> 'Substitution':
        result = Substitution()
        for var, term in self.bindings.items():
            result.bindings[var] = other.apply_to_term(term)
        for var, term in other.bindings.items():
            if var not in self.bindings:
                result.bindings[var] = term
        return result

    def __str__(self):
        if not self.bindings:
            return "{}"
        return "{" + ", ".join(f"{v}={self.bindings[v]}" for v in self.bindings) + "}"


class PrologEngine:
    def __init__(self):
        self.facts: List[Clause] = []
        self.rules: List[Clause] = []
        self.axioms: Set[str] = set()

    def reset(self):
        self.facts = []
        self.rules = []
        self.axioms = set()

    def add_fact(self, predicate: str, *args: str):
        args_terms = []
        for arg in args:
            if arg.startswith("?"):
                args_terms.append(Variable(arg[1:]))
            else:
                args_terms.append(Atom(arg))
        self.facts.append(Clause(Compound(predicate, args_terms)))

    def add_rule(self, head_predicate: str, head_args: List[str],
                 body_predicates: List[Tuple[str, List[str]]]):
        head_args_terms = []
        for arg in head_args:
            if arg.startswith("?"):
                head_args_terms.append(Variable(arg[1:]))
            else:
                head_args_terms.append(Atom(arg))
        head = Compound(head_predicate, head_args_terms)

        body = []
        for pred, pred_args in body_predicates:
            args_terms = []
            for arg in pred_args:
                if arg.startswith("?"):
                    args_terms.append(Variable(arg[1:]))
                else:
                    args_terms.append(Atom(arg))
            body.append(Compound(pred, args_terms))

        self.rules.append(Clause(head, body))

    def add_axiom(self, statement: str):
        self.axioms.add(statement)

    def parse_term(self, term_str: str) -> Term:
        term_str = term_str.strip()
        if not term_str:
            raise ValueError("Empty term")

        if term_str.startswith("?") and len(term_str) > 1:
            return Variable(term_str[1:])
        elif "(" in term_str:
            match = re.match(r"(\w+)\((.*)\)", term_str)
            if match:
                functor = match.group(1)
                args_str = match.group(2)
                args = self._parse_args(args_str)
                return Compound(functor, args)
        elif "," in term_str:
            args = self._parse_args(term_str)
            return Compound("tuple", args)
        return Atom(term_str)

    def _parse_args(self, args_str: str) -> List[Term]:
        args = []
        depth = 0
        current = ""
        for char in args_str:
            if char == "(":
                depth += 1
                current += char
            elif char == ")":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                if current.strip():
                    args.append(self.parse_term(current.strip()))
                current = ""
            else:
                current += char
        if current.strip():
            args.append(self.parse_term(current.strip()))
        return args

    def parse_clause(self, clause_str: str) -> Clause:
        clause_str = clause_str.strip().rstrip(".")
        if ":-" in clause_str:
            head_str, body_str = clause_str.split(":-", 1)
            head = self.parse_term(head_str.strip())
            if isinstance(head, Compound):
                body_parts = [p.strip() for p in body_str.split(",")]
                body = [self.parse_term(p) for p in body_parts]
                return Clause(head, body)
            else:
                raise ValueError(f"Head must be compound: {head_str}")
        else:
            head = self.parse_term(clause_str)
            if isinstance(head, Compound):
                return Clause(head)
            else:
                raise ValueError(f"Fact must be compound: {clause_str}")

    def unify(self, term1: Term, term2: Term, subst: Substitution) -> Optional[Substitution]:
        term1 = subst.apply_to_term(term1)
        term2 = subst.apply_to_term(term2)

        if isinstance(term1, Variable):
            subst.add(term1.name, term2)
            return subst
        if isinstance(term2, Variable):
            subst.add(term2.name, term1)
            return subst
        if isinstance(term1, Atom) and isinstance(term2, Atom):
            if term1.name == term2.name:
                return subst
            return None
        if isinstance(term1, Compound) and isinstance(term2, Compound):
            if term1.functor != term2.functor or len(term1.args) != len(term2.args):
                return None
            for a1, a2 in zip(term1.args, term2.args):
                subst = self.unify(a1, a2, subst)
                if subst is None:
                    return None
            return subst
        if isinstance(term1, Atom) and isinstance(term2, Compound):
            return None
        if isinstance(term1, Compound) and isinstance(term2, Atom):
            return None
        return None

    def prove(self, goal: Compound, subst: Substitution = None) -> List[Substitution]:
        if subst is None:
            subst = Substitution()

        results = []

        for fact in self.facts:
            new_subst = self.unify(fact.head, goal, Substitution())
            if new_subst is not None:
                merged = subst.merge(new_subst)
                results.append(merged)

        for rule in self.rules:
            new_subst = self.unify(rule.head, goal, Substitution())
            if new_subst is not None:
                if rule.body is None:
                    merged = subst.merge(new_subst)
                    results.append(merged)
                else:
                    all_results = [merged]
                    for subgoal in rule.body:
                        new_all_results = []
                        for s in all_results:
                            for r in self.prove(self._substitute_compound(subgoal, s), s):
                                new_all_results.append(r)
                        if not new_all_results:
                            break
                        all_results = new_all_results
                    for s in all_results:
                        merged = subst.merge(new_subst).merge(s)
                        results.append(merged)

        return results

    def _substitute_compound(self, compound: Compound, subst: Substitution) -> Compound:
        new_args = [subst.apply_to_term(a) for a in compound.args]
        return Compound(compound.functor, new_args)

    def query(self, predicate: str, *args: str) -> List[Substitution]:
        args_terms = [self.parse_term(a) for a in args]
        goal = Compound(predicate, args_terms)
        return self.prove(goal)

    def check_entailment(self, premises: List[str], conclusion: str) -> Tuple[bool, str]:
        self.reset()

        for premise in premises:
            try:
                clause = self.parse_clause(premise)
                if clause.body is None:
                    self.facts.append(clause)
                else:
                    self.rules.append(clause)
            except Exception as e:
                return False, f"解析前提失败: {str(e)}"

        try:
            conclusion_term = self.parse_term(conclusion)
            if isinstance(conclusion_term, Compound):
                results = self.prove(conclusion_term)
                if results:
                    return True, f"结论可从前提推导得出。替换: {[str(r) for r in results]}"
                else:
                    return False, "结论无法从前提推导得出"
            else:
                return False, f"结论必须是复合命题: {conclusion}"
        except Exception as e:
            return False, f"解析结论失败: {str(e)}"

    def check_consistency(self, statements: List[str]) -> Tuple[bool, str]:
        self.reset()

        for stmt in statements:
            try:
                clause = self.parse_clause(stmt)
                if clause.body is None:
                    self.facts.append(clause)
                else:
                    self.rules.append(clause)
            except Exception as e:
                return False, f"解析语句失败: {str(e)}"

        contradictions = []

        for i, fact1 in enumerate(self.facts):
            for fact2 in self.facts[i+1:]:
                if fact1.head.functor == fact2.head.functor:
                    subst = self.unify(fact1.head, fact2.head, Substitution())
                    if subst is None and fact1.head.args == fact2.head.args:
                        if fact1.head.functor.startswith("not_") or "false" in fact1.head.functor:
                            contradictions.append(f"矛盾检测: {fact1.head} vs {fact2.head}")

        negated_facts = [f for f in self.facts if f.head.functor.startswith("not_")]
        for neg_fact in negated_facts:
            base_pred = neg_fact.head.functor[4:]
            base_args = neg_fact.head.args
            for fact in self.facts:
                if fact.head.functor == base_pred:
                    if self.unify(fact.head, Compound(base_pred, base_args), Substitution()) is not None:
                        contradictions.append(f"矛盾检测: {fact.head} vs {neg_fact.head}")

        if contradictions:
            return False, " | ".join(contradictions)
        return True, "一致性检验通过：无矛盾检测到"

    def to_prolog_string(self) -> str:
        lines = []
        for fact in self.facts:
            lines.append(f"{fact.head}.")
        for rule in self.rules:
            if rule.body:
                body_str = ", ".join(str(p) for p in rule.body)
                lines.append(f"{rule.head} :- {body_str}.")
        return "\n".join(lines)


prolog_engine = PrologEngine()
