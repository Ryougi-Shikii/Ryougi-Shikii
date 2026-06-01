
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Module1_LexerScandium    import scandium_lexer
from Module3_SemanticAnalyzer import build_ast, semantic_analysis
from Module4_TACGenerator     import TACInstruction, generate_tac, print_tac

class DAGNode:
    _id_counter = 0

    def __init__(self, label, children=None, is_leaf=False):
        DAGNode._id_counter += 1
        self.id       = DAGNode._id_counter
        self.label    = label
        self.children = children or []
        self.is_leaf  = is_leaf
        self.vars     = []   

    def __repr__(self):
        return (f"DAGNode(id={self.id}, label={self.label!r}, "
                f"vars={self.vars}, leaf={self.is_leaf})")

class DAGBuilder:
    def __init__(self):
        self.nodes    = []
        self.var_map  = {}   # var_name -> DAGNode
        self.expr_map = {}   # (op, id1, id2?) -> DAGNode for CSE

    def _get_or_create_leaf(self, val):
        if val in self.var_map:
            return self.var_map[val]
        node = DAGNode(label=val, is_leaf=True)
        self.nodes.append(node)
        node.vars.append(val)
        self.var_map[val] = node
        return node

    def _find_or_create_op(self, op, child1, child2=None):
        key = (op, child1.id, child2.id if child2 else None)
        if key in self.expr_map:
            return self.expr_map[key]
        children = [child1] + ([child2] if child2 else [])
        node = DAGNode(label=op, children=children)
        self.nodes.append(node)
        self.expr_map[key] = node
        return node

    def _assign_var(self, var, node):
        """Point var -> node, removing it from its old node."""
        if var in self.var_map:
            old = self.var_map[var]
            if var in old.vars:
                old.vars.remove(var)
        node.vars.append(var)
        self.var_map[var] = node

    def process_binop(self, result, op1, operator, op2):
        n1   = self._get_or_create_leaf(op1)
        n2   = self._get_or_create_leaf(op2)
        node = self._find_or_create_op(operator, n1, n2)
        self._assign_var(result, node)
        return node

    def process_unaryop(self, result, operator, op1):
        n1   = self._get_or_create_leaf(op1)
        node = self._find_or_create_op(operator, n1)
        self._assign_var(result, node)
        return node

    def process_copy(self, result, op1):
        """Alias result -> op1's node."""
        src = self.var_map.get(op1) or self._get_or_create_leaf(op1)
        self._assign_var(result, src)
        return src

    def canonical_name(self, name):
        """
        Return the canonical variable name for `name`.
        - Numeric/string literal leaf  -> return the literal value
        - Op-node shared by CSE        -> return vars[0] (first assigned)
        - Leaf pointing to a variable  -> return name itself
        """
        node = self.var_map.get(name)
        if node is None:
            return name
        if node.is_leaf:
            try:
                float(node.label)
                return node.label   # constant literal
            except (ValueError, TypeError):
                pass
            return name             # variable leaf — keep name
        # Op-node: canonical is the first variable on the node
        if node.vars:
            return node.vars[0]
        return name

    def promote_user_var(self, user_var, temp):
        """
        Copy folding: when we see  user_var = temp  and temp is an
        op-node result, rename temp's op-node canonical to user_var
        so future references use user_var directly.
        Removes temp from the node's vars and inserts user_var first.
        """
        node = self.var_map.get(temp)
        if node is None or node.is_leaf:
            return
        # Only promote if temp is currently the canonical (first) name
        if node.vars and node.vars[0] == temp:
            node.vars.remove(temp)
            node.vars.insert(0, user_var)
        self._assign_var(user_var, node)

def _is_temp(name):
    return name is not None and name.startswith("t") and not name.startswith("param_")

def _is_live(result, used_set):
    if result is None:
        return True
    if not _is_temp(result):    # user variable or param_ -> always live
        return True
    return result in used_set


def _optimize_block(block):

    if not block:
        return block

    dag = DAGBuilder()

    # ── Pass 1: CSE rewrite ──────────────────────────────────────
    # Walk in original order; for each instruction emit a rewritten
    # version (or None to suppress it).
    rewritten = []   # list of TACInstruction or None

    NON_VALUE = {"print", "param", "call", "call_void", "return",
                 "label", "goto", "ifFalse", "func_begin", "func_end"}

    for instr in block:
        t = instr.instruction_type

        if t == "binop":
            dag.process_binop(instr.result, instr.op1, instr.operator, instr.op2)
            new_op1 = dag.canonical_name(instr.op1)
            new_op2 = dag.canonical_name(instr.op2)
            rewritten.append(TACInstruction(
                result=instr.result, op1=new_op1,
                operator=instr.operator, op2=new_op2,
                instruction_type="binop"
            ))

        elif t == "unaryop":
            dag.process_unaryop(instr.result, instr.operator, instr.op1)
            new_op1 = dag.canonical_name(instr.op1)
            rewritten.append(TACInstruction(
                result=instr.result, op1=new_op1,
                operator=instr.operator,
                instruction_type="unaryop"
            ))

        elif t == "copy":
            dag.process_copy(instr.result, instr.op1)
            new_op1 = dag.canonical_name(instr.op1)

            # Copy folding: if result is a user variable and op1 is a
            # temp that owns an op-node, promote the user variable to be
            # the canonical name for that node and suppress the copy.
            if (not _is_temp(instr.result)
                    and _is_temp(new_op1)
                    and instr.result != new_op1):
                dag.promote_user_var(instr.result, new_op1)
                # Rewrite the preceding binop/unaryop that produced new_op1
                # to use instr.result as its result instead.
                for prev in reversed(rewritten):
                    if prev is not None and prev.result == new_op1:
                        prev.result = instr.result
                        break
                rewritten.append(None)   # suppress copy itself
            elif new_op1 == instr.result:
                rewritten.append(None)   # self-assignment, drop
            else:
                rewritten.append(TACInstruction(
                    result=instr.result, op1=new_op1,
                    instruction_type="copy"
                ))

        else:
            # Non-value: rewrite op1 to canonical name, keep in place
            new_op1 = dag.canonical_name(instr.op1) if instr.op1 is not None else instr.op1
            rewritten.append(TACInstruction(
                result=instr.result,
                op1=new_op1,
                operator=instr.operator,
                op2=instr.op2,
                instruction_type=t
            ))

    # ── Pass 2: compute liveness from the REWRITTEN stream ───────
    used_after_cse = set()
    for instr in rewritten:
        if instr is None:
            continue
        if instr.op1 is not None:
            used_after_cse.add(instr.op1)
        if instr.op2 is not None:
            used_after_cse.add(instr.op2)

    # ── Pass 3: DCE — drop dead value instructions ────────────────
    result_block = []
    for instr in rewritten:
        if instr is None:
            continue
        if instr.instruction_type in NON_VALUE:
            result_block.append(instr)
        elif _is_live(instr.result, used_after_cse):
            result_block.append(instr)
        # else: dead temp result, drop

    return result_block

def _split_into_blocks(instructions):
    blocks  = []
    current = []
    terminators = {"goto", "return", "func_end"}
    leaders     = {"label", "func_begin"}

    for instr in instructions:
        t = instr.instruction_type
        if t in leaders:
            if current:
                blocks.append(current)
            current = [instr]
        elif t in terminators:
            current.append(instr)
            blocks.append(current)
            current = []
        else:
            current.append(instr)

    if current:
        blocks.append(current)
    return blocks

def optimize_tac(instructions):
    """Return optimised TAC (CSE + DCE + copy folding), per basic block."""
    blocks    = _split_into_blocks(instructions)
    optimised = []
    for block in blocks:
        optimised.extend(_optimize_block(block))
    return optimised


def print_comparison(original, optimised):
    print("\n  -- Original TAC ------------------------------------------")
    for i, instr in enumerate(original, 1):
        print(f"    {i:3d}:  {instr}")
    print(f"\n  -- Optimised TAC ({len(original)} -> {len(optimised)} instructions) --")
    for i, instr in enumerate(optimised, 1):
        print(f"    {i:3d}:  {instr}")

if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  Test 1 - Common Subexpression Elimination")
    print("=" * 55)
    raw_block = [
        TACInstruction("t1", "a", "*", "b", "binop"),
        TACInstruction("t2", "t1", "+", "c", "binop"),
        TACInstruction("t3", "a", "*", "b", "binop"),
        TACInstruction("t4", "t3", "+", "d", "binop"),
        TACInstruction(None, "t2", None, None, "print"),
        TACInstruction(None, "t4", None, None, "print"),
    ]
    optimised = optimize_tac(raw_block)
    print_comparison(raw_block, optimised)

    test_cases = [
        ("Prog1 - Arithmetic",   "Let a = 2 * 3 + 4;\nPrint(a);"),
        ("Prog2 - If/Else",
         "Let x = 10;\nLet y = 20;\nIf (x < y) {\n    Print(x);\n} Else {\n    Print(y);\n}"),
        ("Prog3 - While",
         "Let i = 0;\nWhile (i < 3) {\n    Print(i);\n    i = i + 1;\n}"),
        ("Prog4 - Function",
         "Func add(a, b) {\n    Return a + b;\n}\nLet result = add(3, 4);\nPrint(result);"),
        ("Prog5 - CSE Demo",
         "Let p = 5 * 6;\nLet q = 5 * 6;\nLet r = p + q;\nPrint(r);"),
        ("Prog6 - Negatives",
         "Let a = -5;\nLet b = 10;\nLet c = b - 3;\nPrint(c);"),
    ]
    for title, src in test_cases:
        print(f"\n{'=' * 55}")
        print(f"  {title}")
        print("=" * 55)
        tokens   = scandium_lexer(src)
        ast      = build_ast(tokens)
        errs, _  = semantic_analysis(ast)
        if errs:
            for e in errs: print("  [ERR]", e)
            continue
        print(src)
        original  = generate_tac(ast)
        optimised = optimize_tac(original)
        print_comparison(original, optimised)
