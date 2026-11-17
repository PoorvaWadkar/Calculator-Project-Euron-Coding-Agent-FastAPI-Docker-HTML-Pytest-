<!-- Written by Euron Code after each task. It is rewritten automatically: put your own rules in
     another file in .euron/rules/. -->

# Learned in this project

- Tests: `cd "D:\Universe\Euron\Euron Coding Agent\calculator-project" ; python -m pytest tests/test_main.py -v` works here (passed 15x, last 2026-11-17). Use it to verify changes.

## Security (from .euron/security/assessment.md)
- This code base has had: eval/exec of dynamic code (SEC010). Avoid eval/exec; parse the data (json, ast.literal_eval) or map inputs to known functions. Do not add more; fix the existing ones when you touch those files.
- This code base has had: html inserted without escaping (xss) (SEC050). Render text, or sanitise the HTML (DOMPurify / bleach) before inserting it. Do not add more; fix the existing ones when you touch those files.
