from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load pretrained NLP model
model_name = "Salesforce/codet5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def explain_code(code, language):

    input_text = f"summarize {language} code: {code}"

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        inputs.input_ids,
        max_length=60,
        num_beams=4,
        early_stopping=True
    )

    explanation = tokenizer.decode(
        outputs[0],
        skip_special_tokens=True
    )

    return explanation

def summarize_code(code):

    prompt = f"summarize: {code}"

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=512
    )

    outputs = model.generate(
        inputs.input_ids,
        max_length=80,
        num_beams=4,
        early_stopping=True
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return summary

def analyze_code_quality(code):

    lines = code.split("\n")

    line_count = len(lines)

    functions = code.count("def ")

    loops = code.count("for") + code.count("while")

    conditionals = code.count("if")

    nesting = 0
    max_nesting = 0

    for line in lines:

        spaces = len(line) - len(line.lstrip())

        level = spaces // 4

        if level > max_nesting:
            max_nesting = level

    quality_score = 100

    if max_nesting > 3:
        quality_score -= 20

    if loops > 5:
        quality_score -= 10

    if line_count > 200:
        quality_score -= 20

    return {
        "lines_of_code": line_count,
        "functions": functions,
        "loops": loops,
        "conditionals": conditionals,
        "max_nesting_depth": max_nesting,
        "quality_score": quality_score
    }
