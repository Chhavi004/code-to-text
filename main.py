from fastapi import FastAPI
from pydantic import BaseModel
from model import summarize_code, analyze_code_quality,explain_code


app = FastAPI()


class CodeInput(BaseModel):
    code: str


# -------------------------------
# LANGUAGE DETECTION
# -------------------------------

from pygments.lexers import guess_lexer

def detect_language(code):

    try:
        lexer = guess_lexer(code)
        return lexer.name

    except:
        return "Unknown"


# -------------------------------
# TIME COMPLEXITY DETECTION
# -------------------------------

import re

def detect_complexity(code: str):

    code = code.replace(" ", "")

    loops = code.count("for") + code.count("while")

    # Detect nested loops
    nested_loops = code.count("for") > 1 or code.count("while") > 1

    # Detect logarithmic patterns
    log_patterns = [
        "i*=2",
        "i/=2",
        "mid=",
        "binarysearch",
        "while(low<=high)"
    ]

    # Detect recursion
    recursion = False
    function_match = re.search(r"def(\w+)\(", code)
    if function_match:
        func_name = function_match.group(1)
        if func_name in code.split("{")[-1]:
            recursion = True

    # Detect factorial recursion
    if recursion and "return" in code and "*" in code:
        return "O(n!) or O(2^n) (possible exponential recursion)"

    # Logarithmic
    for pattern in log_patterns:
        if pattern in code:
            if loops > 0:
                return "O(n log n)"
            return "O(log n)"

    # Nested loops
    if nested_loops:
        depth = loops
        return f"O(n^{depth})"

    # Single loop
    if loops == 1:
        return "O(n)"

    # No loops
    if loops == 0:
        return "O(1)"

    return "Unknown complexity"

# -------------------------------
# COMMENT GENERATOR
# -------------------------------

def generate_comments(code):

    lines = code.split("\n")
    result = []

    for line in lines:

        stripped = line.strip()

        if stripped.startswith("for"):
            result.append("# loop through elements")

        elif stripped.startswith("while"):
            result.append("# while loop execution")

        elif stripped.startswith("if"):
            result.append("# conditional check")

        result.append(line)

    return "\n".join(result)


# -------------------------------
# ERROR DETECTION
# -------------------------------

def detect_errors(code):

    errors = []

    # Parentheses check
    if code.count("(") != code.count(")"):
        errors.append("Unbalanced parentheses detected")

    # Curly braces check
    if code.count("{") != code.count("}"):
        errors.append("Unbalanced curly braces detected")

    # Square brackets check
    if code.count("[") != code.count("]"):
        errors.append("Unbalanced square brackets detected")

    # Quote check
    if code.count('"') % 2 != 0 or code.count("'") % 2 != 0:
        errors.append("Unmatched quotation marks detected")

    # Python loop syntax check
    if "for" in code and ":" not in code and "{" not in code:
        errors.append("Possible syntax error in loop (missing ':' or '{')")

    # Python condition check
    if "if" in code and ":" not in code and "{" not in code:
        errors.append("Possible syntax error in condition (missing ':' or '{')")

    # Else without if
    if "else" in code and "if" not in code:
        errors.append("Else statement without matching if")

    # Missing semicolon (C/Java style)
    lines = code.split("\n")
    for line in lines:
        line = line.strip()

        if (
            line and
            not line.endswith(";") and
            not line.endswith("{") and
            not line.endswith("}") and
            "print" not in line and
            "def" not in line and
            "for" not in line and
            "while" not in line and
            "if" not in line
        ):
            if "=" in line:
                errors.append("Possible missing semicolon")

    # Empty block detection
    if "{}" in code:
        errors.append("Empty code block detected")

    if not errors:
        return "No obvious syntax errors detected"

    return errors


# -------------------------------
# ROOT TEST
# -------------------------------

@app.get("/")
def home():
    return {"message": "AI Code Explainer API running"}


# -------------------------------
# MAIN API
# -------------------------------

@app.post("/explain")
def explain(data: CodeInput):

    code = data.code

    language = detect_language(code)

    explanation = explain_code(code, language)

    complexity = detect_complexity(code)

    comments = generate_comments(code)

    errors = detect_errors(code)

    summary = summarize_code(code)

    quality = analyze_code_quality(code)

    return {
        "language": language,
        "summary": summary,
        "explanation": explanation,
        "time_complexity": complexity,
        "commented_code": comments,
        "error_check": errors,
        "code_quality": quality
    }