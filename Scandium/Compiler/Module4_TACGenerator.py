
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Module1_LexerScandium    import scandium_lexer
from Module3_SemanticAnalyzer import (
    build_ast, semantic_analysis,
    NumberNode, StringNode, BoolNode, IdentifierNode,
    BinOpNode, UnaryOpNode,
    AssignNode, LetNode, PrintNode,
    IfNode, WhileNode,
    FuncDefNode, FuncCallNode, ReturnNode,
    ProgramNode,
)

class TACInstruction:
    """
    Represents one Three-Address Code instruction.

    Forms:
        result = op1 operator op2   (BinOp)
        result = operator op1       (UnaryOp)
        result = op1                (Copy)
        print op1                   (Print)
        label  L:                   (Label)
        ifFalse op1 goto L          (ConditionalJump)
        goto L                      (UnconditionalJump)
        param op1                   (FuncArg)
        result = call name, n       (FuncCall)
        return op1                  (Return)
        func name:                  (FuncBegin)
        endfunc                     (FuncEnd)
    """
    def __init__(self, result=None, op1=None, operator=None, op2=None,
                 instruction_type="assign"):
        self.result          = result
        self.op1             = op1
        self.operator        = operator
        self.op2             = op2
        self.instruction_type = instruction_type

    def __str__(self):
        t = self.instruction_type
        if t == "binop":
            return f"{self.result} = {self.op1} {self.operator} {self.op2}"
        if t == "unaryop":
            return f"{self.result} = {self.operator}{self.op1}"
        if t == "copy":
            return f"{self.result} = {self.op1}"
        if t == "print":
            return f"print {self.op1}"
        if t == "label":
            return f"{self.result}:"
        if t == "ifFalse":
            return f"ifFalse {self.op1} goto {self.result}"
        if t == "goto":
            return f"goto {self.result}"
        if t == "param":
            return f"param {self.op1}"
        if t == "call":
            return f"{self.result} = call {self.op1}, {self.op2}"
        if t == "call_void":
            return f"call {self.op1}, {self.op2}"
        if t == "return":
            return f"return {self.op1}"
        if t == "func_begin":
            return f"func {self.result}:"
        if t == "func_end":
            return "endfunc"
        return f"(unknown TAC: {vars(self)})"

class TACGenerator:
    def __init__(self):
        self.instructions = []
        self._temp_count  = 0
        self._label_count = 0

    # ── helpers ──────────────────────────────
    def new_temp(self):
        self._temp_count += 1
        return f"t{self._temp_count}"

    def new_label(self):
        self._label_count += 1
        return f"L{self._label_count}"

    def emit(self, instr):
        self.instructions.append(instr)

    # ── public entry point ───────────────────
    def generate(self, ast):
        self.visit(ast)
        return self.instructions

    # ── dispatch ─────────────────────────────
    def visit(self, node):
        method = "visit_" + type(node).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise NotImplementedError(
            f"TACGenerator: no visitor for {type(node).__name__}"
        )

    # ── visitors ─────────────────────────────
    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_NumberNode(self, node):
        return str(node.value)

    def visit_StringNode(self, node):
        return f'"{node.value}"'

    def visit_BoolNode(self, node):
        return "1" if node.value else "0"

    def visit_IdentifierNode(self, node):
        return node.name

    def visit_BinOpNode(self, node):
        # Map keyword operators to symbols
        op_map = {
            "Add": "+", "Sub": "-", "Mul": "*", "Div": "/", "Mod": "%",
            "Eq":  "==","Neq": "!=","Gt":  ">", "Lt":  "<", "Ge":  ">=","Le": "<=",
            "AND": "&&","OR":  "||",
        }
        op    = op_map.get(node.op, node.op)
        left  = self.visit(node.left)
        right = self.visit(node.right)
        temp  = self.new_temp()
        self.emit(TACInstruction(
            result=temp, op1=left, operator=op, op2=right,
            instruction_type="binop"
        ))
        return temp

    def visit_UnaryOpNode(self, node):
        operand = self.visit(node.operand)
        temp    = self.new_temp()
        op      = "!" if node.op == "NOT" else node.op
        self.emit(TACInstruction(
            result=temp, op1=operand, operator=op,
            instruction_type="unaryop"
        ))
        return temp

    def visit_LetNode(self, node):
        val = self.visit(node.value)
        self.emit(TACInstruction(
            result=node.name, op1=val,
            instruction_type="copy"
        ))
        return node.name

    def visit_AssignNode(self, node):
        val = self.visit(node.value)
        self.emit(TACInstruction(
            result=node.name, op1=val,
            instruction_type="copy"
        ))
        return node.name

    def visit_PrintNode(self, node):
        val = self.visit(node.expr)
        self.emit(TACInstruction(op1=val, instruction_type="print"))

    def visit_IfNode(self, node):
        cond       = self.visit(node.condition)
        false_label = self.new_label()
        end_label   = self.new_label()

        self.emit(TACInstruction(
            result=false_label, op1=cond, instruction_type="ifFalse"
        ))

        for stmt in node.body:
            self.visit(stmt)

        if node.elif_clauses or node.else_body:
            self.emit(TACInstruction(result=end_label, instruction_type="goto"))

        self.emit(TACInstruction(result=false_label, instruction_type="label"))

        for (elif_cond_node, elif_body) in node.elif_clauses:
            elif_cond   = self.visit(elif_cond_node)
            next_label  = self.new_label()
            self.emit(TACInstruction(
                result=next_label, op1=elif_cond, instruction_type="ifFalse"
            ))
            for stmt in elif_body:
                self.visit(stmt)
            self.emit(TACInstruction(result=end_label, instruction_type="goto"))
            self.emit(TACInstruction(result=next_label, instruction_type="label"))

        for stmt in node.else_body:
            self.visit(stmt)

        self.emit(TACInstruction(result=end_label, instruction_type="label"))

    def visit_WhileNode(self, node):
        start_label = self.new_label()
        end_label   = self.new_label()

        self.emit(TACInstruction(result=start_label, instruction_type="label"))
        cond = self.visit(node.condition)
        self.emit(TACInstruction(
            result=end_label, op1=cond, instruction_type="ifFalse"
        ))
        for stmt in node.body:
            self.visit(stmt)
        self.emit(TACInstruction(result=start_label, instruction_type="goto"))
        self.emit(TACInstruction(result=end_label, instruction_type="label"))

    def visit_FuncDefNode(self, node):
        self.emit(TACInstruction(result=node.name, instruction_type="func_begin"))
        # Declare parameters
        for param in node.params:
            self.emit(TACInstruction(result=param, op1=f"param_{param}",
                                     instruction_type="copy"))
        for stmt in node.body:
            self.visit(stmt)
        self.emit(TACInstruction(instruction_type="func_end"))

    def visit_FuncCallNode(self, node):
        for arg in node.args:
            val = self.visit(arg)
            self.emit(TACInstruction(op1=val, instruction_type="param"))
        temp = self.new_temp()
        self.emit(TACInstruction(
            result=temp, op1=node.name, op2=str(len(node.args)),
            instruction_type="call"
        ))
        return temp

    def visit_ReturnNode(self, node):
        val = self.visit(node.value)
        self.emit(TACInstruction(op1=val, instruction_type="return"))
        return val

def generate_tac(ast):
    """Return list of TACInstruction objects."""
    gen = TACGenerator()
    return gen.generate(ast)

def print_tac(instructions):
    print("=== Three-Address Code (TAC) ===")
    for idx, instr in enumerate(instructions, 1):
        print(f"  {idx:3d}:  {instr}")

if __name__ == "__main__":
    test_cases = [
        ('Basic Arithmetic',    'Let a = 2 * 3 + 4;'),
        ('Grouping',            'Let b = (2 + 3) * 4;'),
        ('Nested Grouping',     'Let c = ((3+3)+(2*4));'),
        ('Assign + Print',      'Let a = 2 * 3 + 4;\nPrint(a);'),
    ]

    for title, src in test_cases:
        print(f"\n{'='*50}")
        print(f"  Test: {title}")
        print(f"  Input: {src.strip()}")
        print(f"{'='*50}")
        tokens = scandium_lexer(src)
        ast    = build_ast(tokens)
        errs, warns = semantic_analysis(ast)
        if errs:
            for e in errs: print("  [SEM-ERR]", e)
            continue
        instrs = generate_tac(ast)
        print_tac(instrs)
