# ----> read "Read.txt" -----------------------------------
# ----> for more information about ------------------------
# --------- my scandium language------------------------------


import sys


class Token:
    def __init__(self, type_, value, line):
        self.type  = type_
        self.value = value
        self.line  = line

    def __str__(self):
        return f"Token({self.type}, {self.value}, line={self.line})"


def scandium_lexer(code):
    tokens = []
    i      = 0
    line   = 1
    length = len(code)

    keywords = {
        # Core
        "Print", "Func", "Return", "Let",
        "If", "Elif", "Else", "While",
        # Arithmetic
        "Add", "Sub", "Mul", "Div", "Mod",
        # Comparison
        "Eq", "Neq", "Gt", "Lt", "Ge", "Le",
        # Logical
        "AND", "OR", "NOT",
        # Bitwise
        "BAND", "BOR", "XOR", "LShift", "RShift",
        # Boolean
        "True", "False",
    }

    def _last_token_type():
        """Return the type of the most recently emitted token, or None."""
        return tokens[-1].type if tokens else None

    while i < length:
        char = code[i]

        # NEWLINE
        if char == '\n':
            line += 1
            i += 1
            continue

        # WHITESPACE
        if char in (' ', '\t', '\r'):
            i += 1
            continue

        # Single-line comment  #
        if char == '#':
            while i < length and code[i] != '\n':
                i += 1
            continue

        # Multi-line comment  '...'
        if char == "'":
            i += 1
            while i < length and code[i] != "'":
                if code[i] == '\n':
                    line += 1
                i += 1
            if i >= length:
                raise SyntaxError(
                    f"Scandium Lexer Error: Unterminated comment at line {line}"
                )
            i += 1
            continue

        # NUMBER
        # A '-' starts a negative literal ONLY when the previous token
        # cannot be the end of an expression (no prior token, or prior
        # token is an operator / opening paren).
        # In all other positions '-' is a binary subtraction operator.
        if char.isdigit() or (
            char == '-'
            and i + 1 < length
            and code[i + 1].isdigit()
            and _last_token_type() not in ("NUMBER", "IDENTIFIER")
        ):
            start   = i
            if char == '-':
                i += 1
            has_dot = False
            while i < length and (code[i].isdigit() or code[i] == '.'):
                if code[i] == '.':
                    if has_dot:
                        break
                    has_dot = True
                i += 1
            tokens.append(Token("NUMBER", code[start:i], line))
            continue

        # STRING
        if char == '"':
            i += 1
            start = i
            while i < length and code[i] != '"':
                if code[i] == '\n':
                    line += 1
                i += 1
            if i >= length:
                raise SyntaxError(
                    f"Scandium Lexer Error: Unterminated string at line {line}"
                )
            tokens.append(Token("STRING", code[start:i], line))
            i += 1
            continue

        # IDENTIFIER / KEYWORD
        if char.isalpha() or char == '_':
            start = i
            while i < length and (code[i].isalnum() or code[i] == '_'):
                i += 1
            value = code[start:i]
            ttype = "KEYWORD" if value in keywords else "IDENTIFIER"
            tokens.append(Token(ttype, value, line))
            continue

        # MULTI-CHARACTER OPERATORS
        if i + 1 < length:
            two_char = code[i:i + 2]
            if two_char in ("==", "!=", "<=", ">="):
                tokens.append(Token("OPERATOR", two_char, line))
                i += 2
                continue

        # SINGLE-CHARACTER OPERATORS
        if char in "+-*/%=<>!(){}[],;":
            tokens.append(Token("OPERATOR", char, line))
            i += 1
            continue

        raise SyntaxError(
            f"Scandium Lexer Error: Illegal character '{char}' at line {line}"
        )

    return tokens


def main():
    if len(sys.argv) != 2:
        print("Usage: python scandium.py <file.sc>")
        return
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
        tokens = scandium_lexer(source_code)
        for tok in tokens:
            print(tok)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Lexer Error: {e}")


if __name__ == "__main__":
    main()
