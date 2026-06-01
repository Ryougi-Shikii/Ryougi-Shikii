---

# Scandium Language: Lexer Documentation

Scandium is a custom language designed with a balance of functional keyword-based operations and traditional symbolic logic.

## 1. Token Categories

The Scandium Lexer classifies every piece of text into one of the following categories:

* **KEYWORD**: Reserved words that define the structure and built-in operations of the language.
* **IDENTIFIER**: User-defined names for variables and functions (must start with a letter or underscore).
* **OPERATOR**: Mathematical symbols, comparison signs, and punctuation for grouping or termination.
* **NUMBER**: Numeric literals, including integers, floating-point decimals, and negative values.
* **STRING**: Textual data enclosed in double quotes (`"..."`).

---

## 2. Operator Logic

Scandium uniquely supports two styles of operations to provide flexibility for the programmer:

### A. Functional Keywords

These are used for more descriptive code:

* **Arithmetic**: `Add`, `Sub`, `Mul`, `Div`, `Mod`
* **Comparison**: `Eq`, `Neq`, `Gt`, `Lt`, `Ge`, `Le`
* **Logical**: `AND`, `OR`, `NOT`

### B. Symbolic Operators

Traditional symbols are also supported for concise syntax:

* **Math**: `+`, `-`, `*`, `/`, `%`
* **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
* **Assignment**: `=`
* **Grouping/Delimiters**: `( )`, `{ }`, `[ ]`, `,`, `;`

---

## 3. Special Features

* **Single-line Comments**: Use the `#` symbol to ignore everything until the end of the line.
* **Multi-line Comments**: Use single quotes (`'...'`) to wrap comments that span across multiple lines.
* **Negative Numbers**: The lexer recognizes a leading `-` followed immediately by a digit as a single negative `NUMBER` token.

---

## 4. Usage

To run the lexer against a Scandium source file (`.sc`), use the following command in your terminal:

```bash
python Lexer.py your_program.sc

```

If the lexer encounters a character it does not recognize,
it will throw a `Scandium Lexer Error` specifying the illegal character and the line number.

---

### Example Scandium Code

# This is a sample Scandium program
Let x = 10;
Let y = -5.5;

Func calculate(x, y) {
    If (x Gt y) {
        Return x Add y; # Using functional Add
    } Else {
        Return x + y;   # Using symbolic +
    }
}