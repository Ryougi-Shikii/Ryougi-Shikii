# ============================================================
# MODULE 3: SEMANTIC ANALYZER
# Scandium Language Mini-Compiler
# Builds an AST from tokens and performs semantic analysis
# ============================================================


# ─────────────────────────────────────────────
# AST Node Definitions
# ─────────────────────────────────────────────

class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = float(value) if '.' in str(value) else int(value)
    def __repr__(self):
        return f"Number({self.value})"

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"String({self.value!r})"

class BoolNode(ASTNode):
    def __init__(self, value):
        self.value = (value == "True")
    def __repr__(self):
        return f"Bool({self.value})"

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Identifier({self.name})"

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left  = left
        self.op    = op
        self.right = right
    def __repr__(self):
        return f"BinOp({self.left} {self.op} {self.right})"

class UnaryOpNode(ASTNode):
    def __init__(self, op, operand):
        self.op      = op
        self.operand = operand
    def __repr__(self):
        return f"UnaryOp({self.op} {self.operand})"

class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name  = name
        self.value = value
    def __repr__(self):
        return f"Assign({self.name} = {self.value})"

class LetNode(ASTNode):
    def __init__(self, name, value):
        self.name  = name
        self.value = value
    def __repr__(self):
        return f"Let({self.name} = {self.value})"

class PrintNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr
    def __repr__(self):
        return f"Print({self.expr})"

class IfNode(ASTNode):
    def __init__(self, condition, body, elif_clauses=None, else_body=None):
        self.condition    = condition
        self.body         = body
        self.elif_clauses = elif_clauses or []
        self.else_body    = else_body    or []
    def __repr__(self):
        return f"If({self.condition})"

class WhileNode(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body      = body
    def __repr__(self):
        return f"While({self.condition})"

class FuncDefNode(ASTNode):
    def __init__(self, name, params, body):
        self.name   = name
        self.params = params
        self.body   = body
    def __repr__(self):
        return f"FuncDef({self.name}({', '.join(self.params)}))"

class FuncCallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self):
        return f"FuncCall({self.name}({self.args}))"

class ReturnNode(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Return({self.value})"

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f"Program({self.statements})"


# ─────────────────────────────────────────────
# PARSER  (builds AST from token list)
# ─────────────────────────────────────────────

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos    = 0

    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def peek(self, offset=1):
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None

    def consume(self, type_=None, value=None):
        tok = self.current()
        if tok is None:
            raise SyntaxError("Unexpected end of input")
        if type_ and tok.type != type_:
            raise SyntaxError(
                f"Expected token type {type_!r}, got {tok.type!r} "
                f"('{tok.value}') at line {tok.line}"
            )
        if value and tok.value != value:
            raise SyntaxError(
                f"Expected '{value}', got '{tok.value}' at line {tok.line}"
            )
        self.pos += 1
        return tok

    def match(self, type_=None, value=None):
        tok = self.current()
        if tok is None:
            return False
        if type_ and tok.type != type_:
            return False
        if value and tok.value != value:
            return False
        return True

    # ── entry point ──────────────────────────
    def parse(self):
        stmts = []
        while self.current() is not None:
            stmts.append(self.parse_statement())
        return ProgramNode(stmts)

    # ── statements ───────────────────────────
    def parse_statement(self):
        tok = self.current()
        if tok is None:
            raise SyntaxError("Unexpected end of input in statement")

        if tok.type == "KEYWORD" and tok.value == "Let":
            return self.parse_let()
        if tok.type == "KEYWORD" and tok.value == "Print":
            return self.parse_print()
        if tok.type == "KEYWORD" and tok.value == "If":
            return self.parse_if()
        if tok.type == "KEYWORD" and tok.value == "While":
            return self.parse_while()
        if tok.type == "KEYWORD" and tok.value == "Func":
            return self.parse_func_def()
        if tok.type == "KEYWORD" and tok.value == "Return":
            return self.parse_return()

        # Assignment  (identifier followed by '=', but NOT '==')
        if (tok.type == "IDENTIFIER"
                and self.peek() is not None
                and self.peek().value == "="
                and (self.peek(2) is None or self.peek(2).value != "=")):
            return self.parse_assignment()

        # Expression statement (standalone function call, etc.)
        expr = self.parse_expression()
        if self.match("OPERATOR", ";"):
            self.consume()
        return expr

    def parse_let(self):
        self.consume("KEYWORD", "Let")
        name_tok = self.consume("IDENTIFIER")
        self.consume("OPERATOR", "=")
        value = self.parse_expression()
        if self.match("OPERATOR", ";"):
            self.consume()
        return LetNode(name_tok.value, value)

    def parse_assignment(self):
        name_tok = self.consume("IDENTIFIER")
        self.consume("OPERATOR", "=")
        value = self.parse_expression()
        if self.match("OPERATOR", ";"):
            self.consume()
        return AssignNode(name_tok.value, value)

    def parse_print(self):
        self.consume("KEYWORD", "Print")
        self.consume("OPERATOR", "(")
        expr = self.parse_expression()
        self.consume("OPERATOR", ")")
        if self.match("OPERATOR", ";"):
            self.consume()
        return PrintNode(expr)

    def parse_if(self):
        self.consume("KEYWORD", "If")
        self.consume("OPERATOR", "(")
        condition = self.parse_expression()
        self.consume("OPERATOR", ")")
        self.consume("OPERATOR", "{")
        body = self.parse_block()
        self.consume("OPERATOR", "}")

        elif_clauses = []
        while self.match("KEYWORD", "Elif"):
            self.consume("KEYWORD", "Elif")
            self.consume("OPERATOR", "(")
            elif_cond = self.parse_expression()
            self.consume("OPERATOR", ")")
            self.consume("OPERATOR", "{")
            elif_body = self.parse_block()
            self.consume("OPERATOR", "}")
            elif_clauses.append((elif_cond, elif_body))

        else_body = []
        if self.match("KEYWORD", "Else"):
            self.consume("KEYWORD", "Else")
            self.consume("OPERATOR", "{")
            else_body = self.parse_block()
            self.consume("OPERATOR", "}")

        return IfNode(condition, body, elif_clauses, else_body)

    def parse_while(self):
        self.consume("KEYWORD", "While")
        self.consume("OPERATOR", "(")
        condition = self.parse_expression()
        self.consume("OPERATOR", ")")
        self.consume("OPERATOR", "{")
        body = self.parse_block()
        self.consume("OPERATOR", "}")
        return WhileNode(condition, body)

    def parse_func_def(self):
        self.consume("KEYWORD", "Func")
        name_tok = self.consume("IDENTIFIER")
        self.consume("OPERATOR", "(")
        params = []
        if not self.match("OPERATOR", ")"):
            params.append(self.consume("IDENTIFIER").value)
            while self.match("OPERATOR", ","):
                self.consume()
                params.append(self.consume("IDENTIFIER").value)
        self.consume("OPERATOR", ")")
        self.consume("OPERATOR", "{")
        body = self.parse_block()
        self.consume("OPERATOR", "}")
        return FuncDefNode(name_tok.value, params, body)

    def parse_return(self):
        self.consume("KEYWORD", "Return")
        value = self.parse_expression()
        if self.match("OPERATOR", ";"):
            self.consume()
        return ReturnNode(value)

    def parse_block(self):
        stmts = []
        while self.current() is not None and not self.match("OPERATOR", "}"):
            stmts.append(self.parse_statement())
        return stmts

    # ── expressions (proper precedence climbing) ──
    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left = self.parse_logical_and()
        while self.match("KEYWORD", "OR"):
            self.consume()
            right = self.parse_logical_and()
            left  = BinOpNode(left, "OR", right)
        return left

    def parse_logical_and(self):
        left = self.parse_not()
        while self.match("KEYWORD", "AND"):
            self.consume()
            right = self.parse_not()
            left  = BinOpNode(left, "AND", right)
        return left

    def parse_not(self):
        if self.match("KEYWORD", "NOT"):
            self.consume()
            return UnaryOpNode("NOT", self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self):
        left    = self.parse_additive()
        cmp_ops = {"==", "!=", "<", ">", "<=", ">=",
                   "Eq", "Neq", "Gt", "Lt", "Ge", "Le"}
        while self.current() is not None and self.current().value in cmp_ops:
            op    = self.consume().value
            right = self.parse_additive()
            left  = BinOpNode(left, op, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while (self.current() is not None
               and self.current().value in ("+", "-", "Add", "Sub")):
            op    = self.consume().value
            right = self.parse_multiplicative()
            left  = BinOpNode(left, op, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while (self.current() is not None
               and self.current().value in ("*", "/", "%", "Mul", "Div", "Mod")):
            op    = self.consume().value
            right = self.parse_unary()
            left  = BinOpNode(left, op, right)
        return left

    def parse_unary(self):
        if self.match("OPERATOR", "-"):
            self.consume()
            return UnaryOpNode("-", self.parse_primary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()
        if tok is None:
            raise SyntaxError("Unexpected end of expression")

        if tok.type == "NUMBER":
            self.consume()
            return NumberNode(tok.value)

        if tok.type == "STRING":
            self.consume()
            return StringNode(tok.value)

        if tok.type == "KEYWORD" and tok.value in ("True", "False"):
            self.consume()
            return BoolNode(tok.value)

        if tok.type == "OPERATOR" and tok.value == "(":
            self.consume()
            expr = self.parse_expression()
            self.consume("OPERATOR", ")")
            return expr

        if tok.type == "IDENTIFIER":
            self.consume()
            if self.match("OPERATOR", "("):   # function call
                self.consume()
                args = []
                if not self.match("OPERATOR", ")"):
                    args.append(self.parse_expression())
                    while self.match("OPERATOR", ","):
                        self.consume()
                        args.append(self.parse_expression())
                self.consume("OPERATOR", ")")
                return FuncCallNode(tok.value, args)
            return IdentifierNode(tok.value)

        raise SyntaxError(
            f"Unexpected token '{tok.value}' ({tok.type}) at line {tok.line}"
        )


# ─────────────────────────────────────────────
# SEMANTIC ANALYZER
# ─────────────────────────────────────────────

class SemanticError(Exception):
    pass


class SymbolTable:
    def __init__(self, parent=None, scope_name="global"):
        self.symbols    = {}
        self.parent     = parent
        self.scope_name = scope_name

    def declare(self, name, sym_type="unknown"):
        self.symbols[name] = sym_type

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None

    def is_declared_locally(self, name):
        return name in self.symbols

    # Store declared param count alongside "func" type
    def declare_func(self, name, arity):
        self.symbols[name] = ("func", arity)

    def lookup_arity(self, name):
        entry = self.lookup(name)
        if isinstance(entry, tuple) and entry[0] == "func":
            return entry[1]
        return None


class SemanticAnalyzer:
    def __init__(self):
        self.global_scope  = SymbolTable(scope_name="global")
        self.current_scope = self.global_scope
        self.errors        = []
        self.warnings      = []
        self.in_function   = False

    def analyze(self, ast):
        self.visit(ast)
        return self.errors, self.warnings

    def visit(self, node):
        method  = "visit_" + type(node).__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        return "unknown"

    def visit_ProgramNode(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_LetNode(self, node):
        if self.current_scope.is_declared_locally(node.name):
            self.errors.append(
                f"SemanticError: Variable '{node.name}' already declared in this scope."
            )
        val_type = self.visit(node.value)
        self.current_scope.declare(node.name, val_type)
        return val_type

    def visit_AssignNode(self, node):
        if self.current_scope.lookup(node.name) is None:
            self.errors.append(
                f"SemanticError: Variable '{node.name}' used before declaration."
            )
        val_type = self.visit(node.value)
        self.current_scope.declare(node.name, val_type)
        return val_type

    def visit_PrintNode(self, node):
        self.visit(node.expr)

    def visit_IfNode(self, node):
        cond_type = self.visit(node.condition)
        if cond_type == "str":
            self.warnings.append(
                "SemanticWarning: If condition is a string — may produce unexpected results."
            )
        self._enter_scope("if-body")
        for stmt in node.body:
            self.visit(stmt)
        self._leave_scope()

        for (elif_cond, elif_body) in node.elif_clauses:
            self.visit(elif_cond)
            self._enter_scope("elif-body")
            for stmt in elif_body:
                self.visit(stmt)
            self._leave_scope()

        if node.else_body:
            self._enter_scope("else-body")
            for stmt in node.else_body:
                self.visit(stmt)
            self._leave_scope()

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        self._enter_scope("while-body")
        for stmt in node.body:
            self.visit(stmt)
        self._leave_scope()

    def visit_FuncDefNode(self, node):
        if self.current_scope.is_declared_locally(node.name):
            self.errors.append(
                f"SemanticError: Function '{node.name}' already declared."
            )
        # Store function with arity so call-sites can be checked
        self.current_scope.declare_func(node.name, len(node.params))
        self._enter_scope(f"func-{node.name}")
        prev = self.in_function
        self.in_function = True
        for param in node.params:
            self.current_scope.declare(param, "unknown")
        for stmt in node.body:
            self.visit(stmt)
        self.in_function = prev
        self._leave_scope()

    def visit_ReturnNode(self, node):
        if not self.in_function:
            self.errors.append(
                "SemanticError: 'Return' used outside of a function."
            )
        return self.visit(node.value)

    def visit_FuncCallNode(self, node):
        entry = self.current_scope.lookup(node.name)
        if entry is None:
            self.errors.append(
                f"SemanticError: Function '{node.name}' is not defined."
            )
        elif isinstance(entry, tuple) and entry[0] == "func":
            expected_arity = entry[1]
            if len(node.args) != expected_arity:
                self.errors.append(
                    f"SemanticError: '{node.name}' expects {expected_arity} argument(s), "
                    f"got {len(node.args)}."
                )
        elif entry != "func":
            self.errors.append(
                f"SemanticError: '{node.name}' is not callable (type: {entry})."
            )
        for arg in node.args:
            self.visit(arg)
        return "unknown"

    def visit_BinOpNode(self, node):
        lt = self.visit(node.left)
        rt = self.visit(node.right)

        numeric   = {"int", "float", "unknown"}
        arith_ops = {"+", "-", "*", "/", "%", "Add", "Sub", "Mul", "Div", "Mod"}
        cmp_ops   = {"==", "!=", "<", ">", "<=", ">=",
                     "Eq", "Neq", "Gt", "Lt", "Ge", "Le"}

        if node.op in arith_ops:
            if lt == "str" or rt == "str":
                if node.op in ("+", "Add") and lt == "str" and rt == "str":
                    return "str"
                self.errors.append(
                    f"SemanticError: Cannot apply arithmetic operator '{node.op}' "
                    f"to types '{lt}' and '{rt}'."
                )
            return "float" if "float" in (lt, rt) else "int"

        if node.op in cmp_ops:
            return "bool"

        if node.op in ("AND", "OR"):
            return "bool"

        return "unknown"

    def visit_UnaryOpNode(self, node):
        t = self.visit(node.operand)
        if node.op == "NOT":
            return "bool"
        if node.op == "-" and t == "str":
            self.errors.append("SemanticError: Unary '-' cannot be applied to a string.")
        return t

    def visit_NumberNode(self, node):
        return "float" if isinstance(node.value, float) else "int"

    def visit_StringNode(self, node):
        return "str"

    def visit_BoolNode(self, node):
        return "bool"

    def visit_IdentifierNode(self, node):
        sym = self.current_scope.lookup(node.name)
        if sym is None:
            self.errors.append(
                f"SemanticError: Variable '{node.name}' used before declaration."
            )
            return "unknown"
        return sym

    def _enter_scope(self, name):
        self.current_scope = SymbolTable(parent=self.current_scope, scope_name=name)

    def _leave_scope(self):
        self.current_scope = self.current_scope.parent


# ─────────────────────────────────────────────
# Public API used by Module 4 / Module 6
# ─────────────────────────────────────────────

def build_ast(tokens):
    return Parser(tokens).parse()

def semantic_analysis(ast):
    return SemanticAnalyzer().analyze(ast)


# ─────────────────────────────────────────────
# Stand-alone test driver
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from Module1_LexerScandium import scandium_lexer

    src = """
Let x = 2 * 3 + 4;
Let y = (2 + 3) * 4;
Print(x);
Print(y);

Func add(a, b) {
    Return a + b;
}
Let r = add(1, 2);
Print(r);
"""
    tokens = scandium_lexer(src)
    ast    = build_ast(tokens)
    print("=== AST ===")
    for stmt in ast.statements:
        print(" ", stmt)

    errors, warnings = semantic_analysis(ast)
    print("\n=== Semantic Analysis ===")
    if errors:
        for e in errors:   print("  [ERROR]  ", e)
    if warnings:
        for w in warnings: print("  [WARN]   ", w)
    if not errors and not warnings:
        print("  No errors or warnings.")
