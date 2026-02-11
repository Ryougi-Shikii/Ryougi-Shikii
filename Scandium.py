
import sys
import re

# --- LEXER (The Scanner) ---

def scandium_lexer(code):
    # Mapping definitions for the Lexer
    token_specification = [
        # Keywords / Built-in Functions
        ('KEYWORD',    r'\b(Print|Add|Sub|Mul|Div|AND|BAND|OR|BOR|if|else|let)\b'),
        
        # Literals & Identifiers
        ('NUMBER',     r'\d+(\.\d+)?'),
        ('STRING',     r'"(?:\\.|[^"\\])*"'),
        ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        
        # Operators (Multi-char first like '==', then single char)
        ('OP_LOGIC',   r'==|!=|&&|\|\||!'),      # Boolean Logic
        ('OP_BIT',     r'&|\||\^|~|<<|>>'),       # Bitwise 
        ('OP_MATH',    r'[+\-*/%]'),              # Arithmetic
        ('ASSIGN',     r'='),
        
        # Structure
        ('PUNCT',      r'[\(\)\{\}\[\]\;,]'),     # Grouping and ending
        ('SKIP',       r'[ \t\n]+'),              # Whitespace
        ('MISMATCH',   r'.'),                     # Error catch
    ]

    master_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []

    for match in re.finditer(master_regex, code):
        kind = match.lastgroup
        value = match.group()

        if kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Scandium Lexer: Illegal character '{value}'")
        else:
            tokens.append((kind, value))
            
    return tokens

# --- PARSER ---

class ASTNode: pass

class BinOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

class AssignNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class ScandiumParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected_kind, expected_value=None):
        token = self.current_token()
        if not token:
            raise SyntaxError("Unexpected end of input")
        if token[0] != expected_kind or (expected_value and token[1] != expected_value):
            raise SyntaxError(f"Expected {expected_kind} {expected_value}, got {token}")
        self.pos += 1
        return token

    def parse_expression(self):
        token = self.current_token()
        
        # Handle Functions: Add(x, y), Sub(x, y), etc.
        if token[0] == 'KEYWORD' and token[1] in ['Add', 'Sub', 'Mul', 'Div', 'AND', 'BAND', 'OR', 'BOR']:
            op_func = self.eat('KEYWORD')[1]
            self.eat('PUNCT', '(')
            left = self.parse_expression()
            self.eat('PUNCT', ',')
            right = self.parse_expression()
            self.eat('PUNCT', ')')
            
            # Map Scandium functions to internal operators
            op_map = {
                'Add': '+', 'Sub': '-', 'Mul': '*', 'Div': '/',
                'AND': '&&', 'OR': '||', 'BAND': '&', 'BOR': '|'
            }
            return BinOpNode(left, op_map[op_func], right)
        
        # Handle Identifiers or Numbers
        elif token[0] in ['IDENTIFIER', 'NUMBER', 'STRING']:
            return self.eat(token[0])[1]

    def parse_statement(self):
        token = self.current_token()
        if not token: return None

        # Print(...)
        if token[1] == 'Print':
            self.eat('KEYWORD', 'Print')
            self.eat('PUNCT', '(')
            val = self.parse_expression()
            self.eat('PUNCT', ')')
            self.eat('PUNCT', ';')
            return PrintNode(val)

        # let x = ...
        elif token[1] == 'let':
            self.eat('KEYWORD', 'let')
            name = self.eat('IDENTIFIER')[1]
            self.eat('ASSIGN', '=')
            value = self.parse_expression()
            self.eat('PUNCT', ';')
            return AssignNode(name, value)

        # NEW: Handle standalone expressions like Add(2,2);
        else:
            expr = self.parse_expression()
            self.eat('PUNCT', ';') # Ensure it ends with a semicolon
            return expr

    def parse_program(self):
        statements = []
        while self.pos < len(self.tokens):
            statements.append(self.parse_statement())
        return statements

class SemanticAnalyser:
    def __init__(self):
        # Stores variable name -> properties
        self.symbol_table = {}

    def visit(self, node):
        """Recursive function to walk through the AST."""
        if isinstance(node, AssignNode):
            self.visit_assign(node)
        elif isinstance(node, BinOpNode):
            return self.visit_binop(node)
        elif isinstance(node, PrintNode):
            self.visit_print(node)
        elif isinstance(node, str): # Leaf node (variable or literal)
            return self.visit_leaf(node)

    def visit_assign(self, node):
        # 'let x = 10;'
        # Record the variable in the symbol table
        print(f"Checking: Declaring variable '{node.name}'")
        self.symbol_table[node.name] = {"type": "NUMBER", "initialized": True}

    def visit_leaf(self, node):
        # If it's a raw identifier (like 'x' in Add(x, 5))
        if not node.isdigit() and not node.startswith('"'):
            if node not in self.symbol_table:
                raise NameError(f"Semantic Error: Variable '{node}' used before declaration.")
            return self.symbol_table[node]["type"]
        return "NUMBER" if node.isdigit() else "STRING"

    def visit_binop(self, node):
        # Check Add(left, right)
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        # Principle: Type Consistency
        if left_type == "STRING" or right_type == "STRING":
            raise TypeError(f"Semantic Error: Cannot perform '{node.op}' on strings.")
        
        return "NUMBER"

    def visit_print(self, node):
        # Ensure the value being printed actually exists
        self.visit(node.value)

# --- CODE GENERATION ---

class CodeGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.output = []

    def generate(self):
        # 1. Boilerplate C header
        self.output.append("#include <stdio.h>\n")
        self.output.append("int main() {")

        # 2. Translate each AST node
        for node in self.ast:
            line = self.visit(node)
            self.output.append(f"    {line};")

        # 3. Boilerplate C footer
        self.output.append("    return 0;")
        self.output.append("}")
        return "\n".join(self.output)

    def visit(self, node):
        if isinstance(node, AssignNode):
            # let x = 10 -> int x = 10
            return f"int {node.name} = {self.visit(node.value)}"
        
        elif isinstance(node, BinOpNode):
            # Add(5, 10) -> (5 + 10)
            left = self.visit(node.left)
            right = self.visit(node.right)
            return f"({left} {node.op} {right})"
        
        elif isinstance(node, PrintNode):
            # Print("hello") -> printf("hello\n")
            val = self.visit(node.value)
            if val.startswith('"'):
                return f'printf("%s\\n", {val})'
            else:
                return f'printf("%d\\n", {val})'
                
        else: # It's a raw number, string, or identifier
            return str(node)

def compile_scandium(source_code):
    # 1. Lexical Analysis
    tokens = scandium_lexer(source_code)
    
    # 2. Syntax Analysis
    parser = ScandiumParser(tokens)
    ast = parser.parse_program()
    
    # 3. Semantic Analysis
    analyzer = SemanticAnalyser()
    for node in ast:
        analyzer.visit(node)
    
    # 4. Code Generation
    generator = CodeGenerator(ast)
    return generator.generate()

# --- THE DRIVER (scandium.py) ---
def main():
    if len(sys.argv) < 2:
        print("Usage: python scandium.py <file.sc>")
        return

    # 1. Read the file
    filename = sys.argv[1]
    with open(filename, 'r') as f:
        source_code = f.read()

    # 2. Compile Steps
    try:
        print("Compiling...")
        c_code = compile_scandium(source_code)
        
        with open("output.c", "w") as f:
            f.write(c_code)
            
        print("Successfully generated output.c!")
        print("Next step: Run 'gcc output.c -o my_app' and then './my_app'")
        
    except Exception as e:
        print(f"Scandium Compiler Error: {e}")

if __name__ == "__main__":
    main()
