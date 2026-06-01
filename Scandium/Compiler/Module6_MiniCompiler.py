#!/usr/bin/env python3
# ============================================================
# MODULE 6: MINI-COMPILER  --  FULL INTEGRATION
# Scandium Language Compiler
#
# Pipeline:
#   Source Code
#     -> [Phase 1] Lexer          (Module 1)
#     -> [Phase 2] Parser / AST   (Module 3)
#     -> [Phase 3] Semantic Anal  (Module 3)
#     -> [Phase 4] TAC Generator  (Module 4)
#     -> [Phase 5] DAG Optimizer  (Module 5)
#     -> [Phase 6] Assembly Gen   (this file)
#
# Usage:
#   python Module6_MiniCompiler.py <file.sc>
#   python Module6_MiniCompiler.py --demo
# ============================================================

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Module1_LexerScandium    import scandium_lexer
from Module3_SemanticAnalyzer import build_ast, semantic_analysis
from Module4_TACGenerator     import TACInstruction, generate_tac
from Module5_Optimizer        import optimize_tac


# ─────────────────────────────────────────────
# PHASE 6 -- Assembly Code Generator
# Targets NASM x86-64 (System V AMD64 ABI).
# ─────────────────────────────────────────────

REGISTERS = ["rbx", "rcx", "rdx", "rsi", "r8", "r9",
             "r10", "r11", "r12", "r13", "r14", "r15"]

# rax is reserved as scratch / return value; rdi is used for first arg.


class AssemblyGenerator:
    def __init__(self):
        self.asm_lines     = []
        self.reg_map       = {}    # var_name -> register
        self.reg_pool      = list(REGISTERS)
        self.used_regs     = {}    # reg -> var currently held
        self.string_consts = {}    # label -> string value
        self._str_count    = 0
        self._stack_offset = 0
        self.var_offsets   = {}    # var -> rbp-relative offset (spilled)
        self._param_queue      = []    # params waiting for next call
        self._in_func          = False # True while inside a func_begin..func_end
        self._func_param_count = 0     # counts param_X loads inside current func

    # ── low-level helpers ────────────────────

    def _emit(self, line=""):
        self.asm_lines.append(line)

    def _alloc_reg(self, var):
        if var in self.reg_map:
            return self.reg_map[var]
        if self.reg_pool:
            reg = self.reg_pool.pop(0)
        else:
            # Spill the oldest variable to stack
            reg, old_var = next(iter(self.used_regs.items()))
            self._spill(reg, old_var)
        self.reg_map[var] = reg
        self.used_regs[reg] = var
        return reg

    def _spill(self, reg, var):
        self._stack_offset += 8
        offset = self._stack_offset
        self.var_offsets[var] = offset
        self._emit(f"    mov  QWORD PTR [rbp-{offset}], {reg}  ; spill {var}")
        del self.reg_map[var]
        del self.used_regs[reg]
        self.reg_pool.insert(0, reg)

    def _load(self, operand):
        """Return register or immediate holding operand."""
        if operand is None:
            return "0"
        # Numeric literal
        try:
            float(operand)
            return operand
        except (ValueError, TypeError):
            pass
        # String literal
        if isinstance(operand, str) and operand.startswith('"'):
            label = self._intern_string(operand)
            return f"OFFSET {label}"
        # Already in a register
        if operand in self.reg_map:
            return self.reg_map[operand]
        # Spilled to stack
        if operand in self.var_offsets:
            reg = self._alloc_reg(operand)
            off = self.var_offsets[operand]
            self._emit(f"    mov  {reg}, QWORD PTR [rbp-{off}]  ; reload {operand}")
            return reg
        # Unknown operand — allocate and note the assumption
        reg = self._alloc_reg(operand)
        self._emit(f"    ; NOTE: {operand} assumed pre-loaded into {reg}")
        return reg

    def _intern_string(self, s):
        self._str_count += 1
        label = f"str_{self._str_count}"
        self.string_consts[label] = s
        return label

    def _reset_regs(self):
        """Reset register state at function boundaries."""
        self.reg_map            = {}
        self.used_regs          = {}
        self.reg_pool           = list(REGISTERS)
        self._stack_offset      = 0
        self.var_offsets        = {}
        self._func_param_count  = 0

    # ── main entry point ─────────────────────

    def translate(self, instructions):
        # .data section (string constants filled in later)
        self._emit("section .data")
        self._emit("")
        self._emit("section .text")
        self._emit("    global main")
        self._emit("")

        # Emit all function definitions FIRST (before main), then main body
        func_blocks = []     # list of (start_idx, end_idx) in instructions
        main_instrs = []
        func_instrs = []

        # Partition instructions into function bodies vs top-level code
        in_func = False
        for instr in instructions:
            t = instr.instruction_type
            if t == "func_begin":
                in_func = True
                func_instrs.append(instr)
            elif t == "func_end":
                func_instrs.append(instr)
                in_func = False
            elif in_func:
                func_instrs.append(instr)
            else:
                main_instrs.append(instr)

        # Emit function definitions first
        for instr in func_instrs:
            self._translate_one(instr)

        # Emit main prologue
        self._emit("")
        self._emit("main:")
        self._emit("    push rbp")
        self._emit("    mov  rbp, rsp")
        self._emit("    sub  rsp, 256        ; reserve stack space")
        self._emit("")

        self._reset_regs()

        # Emit top-level instructions
        for instr in main_instrs:
            self._translate_one(instr)

        # Epilogue
        self._emit("")
        self._emit("    ; --- program exit ---")
        self._emit("    xor  eax, eax        ; return 0")
        self._emit("    leave")
        self._emit("    ret")
        self._emit("")

        # Inject string constants into .data section
        if self.string_consts:
            insert_idx = self.asm_lines.index("section .data") + 1
            for label, val in self.string_consts.items():
                self.asm_lines.insert(insert_idx, f'    {label} db {val}, 0')
                insert_idx += 1

        return self.asm_lines

    # ── per-instruction translation ──────────

    def _translate_one(self, instr):
        t = instr.instruction_type
        self._emit(f"    ; TAC: {instr}")

        if t == "func_begin":
            self._reset_regs()
            self._in_func = True
            self._emit(f"{instr.result}:")
            self._emit("    push rbp")
            self._emit("    mov  rbp, rsp")
            self._emit("    sub  rsp, 128")
            # Load function arguments from System V AMD64 ABI registers.
            # op1 encodes the parameter list as "param1,param2,..." when
            # the assembler is called from translate() which sets it up.
            # We rely on the TAC copy instructions "a = param_a" that
            # immediately follow func_begin to do the actual loading —
            # those are handled by the "copy" branch below.

        elif t == "func_end":
            self._in_func = False
            # Ensure every function has a closing ret (in case there was
            # no explicit Return statement on all paths)
            self._emit("    ; (implicit return 0 if no earlier ret)")
            self._emit("    xor  eax, eax")
            self._emit("    leave")
            self._emit("    ret")
            self._emit("")

        elif t == "copy":
            # Special case: "a = param_a", "b = param_b", etc.
            # These are function-parameter loads.  We map them from the
            # System V AMD64 ABI argument registers (rdi, rsi, rdx, …)
            # in the order they appear inside the function body.
            if (isinstance(instr.op1, str)
                    and instr.op1.startswith("param_")
                    and self._in_func):
                abi_arg_regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
                param_idx = self._func_param_count
                self._func_param_count += 1
                dst = self._alloc_reg(instr.result)
                if param_idx < len(abi_arg_regs):
                    src_reg = abi_arg_regs[param_idx]
                    self._emit(f"    mov  {dst}, {src_reg}  ; {instr.result} = arg{param_idx}")
                else:
                    # Stack argument (7th param onward)
                    stack_offset = 16 + (param_idx - 6) * 8
                    self._emit(f"    mov  {dst}, QWORD PTR [rbp+{stack_offset}]  ; {instr.result} = stack arg{param_idx}")
            else:
                src = self._load(instr.op1)
                dst = self._alloc_reg(instr.result)
                if src != dst:
                    self._emit(f"    mov  {dst}, {src}")

        elif t == "binop":
            r1  = self._load(instr.op1)
            r2  = self._load(instr.op2)
            dst = self._alloc_reg(instr.result)

            op_map = {
                "+":  "add",  "-":  "sub",  "*":  "imul",
                "&&": "and",  "||": "or",
                "==": "sete_cmp", "!=": "setne_cmp",
                "<":  "setl_cmp", ">":  "setg_cmp",
                "<=": "setle_cmp",">=": "setge_cmp",
            }
            asm_op = op_map.get(instr.operator, instr.operator)

            if instr.operator == "/":
                self._emit(f"    mov  rax, {r1}")
                self._emit(f"    cqo")
                self._emit(f"    idiv {r2}")
                self._emit(f"    mov  {dst}, rax")
            elif instr.operator == "%":
                self._emit(f"    mov  rax, {r1}")
                self._emit(f"    cqo")
                self._emit(f"    idiv {r2}")
                self._emit(f"    mov  {dst}, rdx   ; remainder")
            elif asm_op.endswith("_cmp"):
                set_op = asm_op.replace("_cmp", "")
                # x86 cmp cannot have two immediate operands.
                # If r1 is a numeric literal, load it into a scratch register.
                def _is_immediate(v):
                    try:
                        float(v)
                        return True
                    except (ValueError, TypeError):
                        return False
                if _is_immediate(r1):
                    scratch = self._alloc_reg(f"_cmp_tmp_{instr.result}")
                    self._emit(f"    mov  {scratch}, {r1}")
                    r1 = scratch
                self._emit(f"    cmp  {r1}, {r2}")
                self._emit(f"    {set_op} al")
                self._emit(f"    movzx {dst}, al")
            else:
                self._emit(f"    mov  {dst}, {r1}")
                self._emit(f"    {asm_op}  {dst}, {r2}")

        elif t == "unaryop":
            r1  = self._load(instr.op1)
            dst = self._alloc_reg(instr.result)
            if instr.operator == "-":
                self._emit(f"    mov  {dst}, {r1}")
                self._emit(f"    neg  {dst}")
            elif instr.operator == "!":
                self._emit(f"    mov  {dst}, {r1}")
                self._emit(f"    xor  {dst}, 1")
            else:
                self._emit(f"    mov  {dst}, {r1}")

        elif t == "print":
            val = self._load(instr.op1)
            self._emit(f"    ; --- print({instr.op1}) ---")
            self._emit(f"    mov  rdi, {val}")
            self._emit(f"    call scandium_print")

        elif t == "label":
            self._emit(f"{instr.result}:")

        elif t == "goto":
            self._emit(f"    jmp  {instr.result}")

        elif t == "ifFalse":
            cond = self._load(instr.op1)
            # cmp cannot take an immediate as its first operand
            try:
                float(cond)
                scratch = self._alloc_reg(f"_if_tmp")
                self._emit(f"    mov  {scratch}, {cond}")
                cond = scratch
            except (ValueError, TypeError):
                pass
            self._emit(f"    cmp  {cond}, 0")
            self._emit(f"    je   {instr.result}")

        elif t == "param":
            self._param_queue.append(instr.op1)

        elif t in ("call", "call_void"):
            arg_regs = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
            for k, param in enumerate(self._param_queue):
                if k < len(arg_regs):
                    p = self._load(param)
                    if p != arg_regs[k]:
                        self._emit(f"    mov  {arg_regs[k]}, {p}")
                else:
                    p = self._load(param)
                    self._emit(f"    push {p}   ; stack arg {k}")
            self._param_queue.clear()
            self._emit(f"    call {instr.op1}")
            if t == "call" and instr.result:
                dst = self._alloc_reg(instr.result)
                self._emit(f"    mov  {dst}, rax   ; save return value")

        elif t == "return":
            val = self._load(instr.op1)
            self._emit(f"    mov  rax, {val}")
            self._emit(f"    leave")
            self._emit(f"    ret")

        else:
            self._emit(f"    ; (unhandled TAC type: {t})")


# ─────────────────────────────────────────────
# FULL COMPILER PIPELINE
# ─────────────────────────────────────────────

def compile_scandium(source_code, source_name="<source>", verbose=True):
    """Run all 6 phases. Returns assembly lines, or None on error."""

    def hdr(n, title):
        if verbose:
            print(f"\n{'-'*60}")
            print(f"  PHASE {n}: {title}")
            print(f"{'-'*60}")

    hdr(1, "LEXER")
    try:
        tokens = scandium_lexer(source_code)
    except SyntaxError as e:
        print(f"  [LEXER ERROR] {e}")
        return None
    if verbose:
        print(f"  Tokens produced: {len(tokens)}")
        # for tok in tokens:
            # print(f"    {tok}")

    hdr(2, "PARSER / AST CONSTRUCTION")
    try:
        ast = build_ast(tokens)
    except SyntaxError as e:
        print(f"  [PARSE ERROR] {e}")
        return None
    if verbose:
        print("  AST Nodes:")
        for stmt in ast.statements:
            print(f"    {stmt}")

    hdr(3, "SEMANTIC ANALYSIS")
    errors, warnings = semantic_analysis(ast)
    if verbose:
        for w in warnings:
            print(f"  [WARN]  {w}")
        for e in errors:
            print(f"  [ERROR] {e}")
        if not errors:
            print("  Semantic analysis passed — no errors.")
    if errors:
        return None

    hdr(4, "INTERMEDIATE CODE (TAC)")
    tac = generate_tac(ast)
    if verbose:
        for i, instr in enumerate(tac, 1):
            print(f"  {i:3d}:  {instr}")

    hdr(5, "DAG OPTIMISER")
    opt_tac = optimize_tac(tac)
    if verbose:
        reduction = len(tac) - len(opt_tac)
        print(f"  Instructions: {len(tac)} -> {len(opt_tac)} ({reduction} eliminated)")
        for i, instr in enumerate(opt_tac, 1):
            print(f"  {i:3d}:  {instr}")

    # hdr(6, "ASSEMBLY CODE GENERATION")
    gen = AssemblyGenerator()
    asm = gen.translate(opt_tac)
    if False:
        for line in asm:
            print(f"  {line}")

    return asm


# ─────────────────────────────────────────────
# DEMO PROGRAMS
# ─────────────────────────────────────────────

DEMO_PROGRAMS = [
    (
        "Program 1 - Arithmetic & Print",
        """
Let a = 2 * 3 + 4;
Print(a);
"""
    ),
    (
        "Program 2 - If/Else Branching",
        """
Let x = 10;
Let y = 20;
If (x < y) {
    Print(x);
} Else {
    Print(y);
}
"""
    ),
    (
        "Program 3 - While Loop",
        """
Let i = 0;
While (i < 3) {
    Print(i);
    i = i + 1;
}
"""
    ),
    (
        "Program 4 - Function Definition & Call",
        """
Func add(a, b) {
    Return a + b;
}
Let result = add(3, 4);
Print(result);
"""
    ),
    (
        "Program 5 - CSE Optimisation Demo",
        """
Let p = 5 * 6;
Let q = 5 * 6;
Let r = p + q;
Print(r);
"""
    ),
    (
        "Program 6 - Negative numbers & subtraction",
        """
Let a = -5;
Let b = 10;
Let c = b - 3;
Print(c);
"""
    ),
]


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--demo":
        for title, src in DEMO_PROGRAMS:
            output_dir = "DemoASM"
            banner = f"\n{'='*65}\n=>  {title}\n{'='*65}"
            print(banner)
            asm = compile_scandium(src.strip(), source_name=title)
            if asm is not None:
                clean_title = title.lower().replace(" - ", "_").replace(" ", "_").replace("/", "_")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                out_file = os.path.join(output_dir, f"{clean_title}.asm")
                
                with open(out_file, "w") as f:
                    f.write("\n".join(asm))
                print(f"\n[SUCCESS] Assembly written to: {out_file}\n")
            else:
                print(f"\n[FAILED]  Compilation failed for {title}. No file written.\n")
        return

    if len(sys.argv) == 2:
        fname = sys.argv[1]
        try:
            with open(fname, "r") as f:
                src = f.read()
        except FileNotFoundError:
            print(f"Error: file '{fname}' not found.")
            sys.exit(1)

        print(f"\nCompiling: {fname}")
        asm = compile_scandium(src, source_name=fname)
        if asm is None:
            print("Compilation FAILED.")
            sys.exit(1)

        out_file = fname.replace(".sc", ".asm")
        with open(out_file, "w") as f:
            f.write("\n".join(asm))
        print(f"\nAssembly written to: {out_file}")
        return

    print("Usage:")
    print("  python Module6_MiniCompiler.py <file.sc>   -- compile a file")
    print("  python Module6_MiniCompiler.py --demo       -- run 5 demo programs")


if __name__ == "__main__":
    main()
