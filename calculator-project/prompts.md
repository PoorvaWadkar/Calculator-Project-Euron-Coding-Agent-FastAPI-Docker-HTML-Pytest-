# Prompts Used — Calculator Project

Every meaningful prompt used to build this project, in chronological order, with a short description of its outcome.

---

## PROMPT 1: Vague prompt comparison

Build a simple calculator application using Python and FastAPI. Include basic mathematical operations and make it runnable.

After generating the initial result, briefly explain:
- What files you created.
- What functionality you implemented.
- What assumptions you made because my instructions were not specific.

Do not spend too much time on this initial experiment. I will provide a more detailed specification next.

**Outcome:** The agent successfully created `main.py` and `requirements.txt`, and the API was running correctly. However, during my code review, I noticed that the Swagger documentation did not clearly specify the supported mathematical operations. The `operation` field accepted a generic string rather than explicitly defining the allowed operators. I identified this as an area for improvement.

---

## PROMPT 2: Master project specification

Act as a senior Python backend developer, Docker engineer, and coding mentor.

I am building an end-to-end Calculator API project as part of my Euron Super 30 assignment. I am using Euron Code as my coding agent.

Your responsibility is to help me build a complete, clean, working, beginner-friendly project that satisfies every requirement below.

### Important development instructions

1. First inspect the current project directory and existing files.
2. Understand the project requirements before writing code.
3. Provide a short implementation plan before making major changes.
4. Build the project in three phases: FastAPI, Docker, and Calculator UI.
5. Do not skip any requirement.
6. Write clean, modular, readable Python code with meaningful variable and function names.
7. Add beginner-friendly comments wherever the logic is not obvious.
8. Follow Python best practices and proper error handling.
9. Do not use unnecessary dependencies.
10. Never claim that tests, Docker builds, or API calls succeeded unless you actually execute and verify them.
11. If a command fails, investigate the error and fix the underlying problem.
12. Do not overwrite existing files without checking their contents first.
13. Explain important technical decisions in simple language because I am learning these concepts.

### PROJECT STRUCTURE

Create and maintain this structure:

calculator-project/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── templates/
│       └── index.html
│
├── tests/
│   ├── __init__.py
│   └── test_main.py
│
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md
├── prompts.md
└── .gitignore

You may add other files if genuinely required, but keep the project simple.

### PART 1: FASTAPI CALCULATOR API

Use Python and FastAPI.

Implement the following endpoints:

**1. GET /health**
- Return the application health status.
- Example response: {"status": "healthy"}

**2. POST /add**
- Accept two numbers in a JSON request body.
- Return their sum.

**3. POST /subtract**
- Accept two numbers.
- Return their difference.

**4. POST /multiply**
- Accept two numbers.
- Return their product.

**5. POST /divide**
- Accept two numbers.
- Return their division result.
- If the second number is zero, return HTTP 400 with a clear error message.

**6. POST /power**
- Accept two numbers.
- Calculate the first number raised to the power of the second number.
- Handle invalid mathematical results safely.

For all five mathematical operation endpoints:
- Use a consistent Pydantic request model.
- Use JSON request bodies with fields `a` and `b`.
- Return consistent JSON responses containing the operation and result.
- Reject invalid input types and non-finite numbers.
- Handle invalid mathematical operations with meaningful HTTP error messages.

**7. POST /calculate**

Accept an expression as a string.

Example request:

{"expression": "2 + 3 * 4"}

Expected response:

{"expression": "2 + 3 * 4", "result": 14}

Requirements:
- Support addition, subtraction, multiplication, division, and exponentiation.
- Follow standard mathematical operator precedence.
- Support parentheses and unary positive/negative numbers.
- Never use Python's eval() or exec().
- Implement a safe expression parser using Python's AST module.
- Allow only explicitly approved mathematical AST node types.
- Reject variable names, function calls, imports, attribute access, and unsupported expressions.
- Prevent unsafe or excessively large expressions, including unreasonable exponentiation.
- Return clear HTTP 400 errors for invalid expressions and division by zero.

**8. GET /history**

- Maintain calculation history in memory.
- Store successful mathematical calculations.
- Each history entry should include the expression or operation, input values where applicable, and result.
- Return the most recent 20 calculations.
- Use an appropriate data structure such as collections.deque.
- Do not use a database for this assignment.
- Explain that history resets when the application restarts.

### TESTING REQUIREMENTS

Use pytest and FastAPI TestClient.

Write tests for every endpoint, including:

- Health endpoint.
- Addition.
- Subtraction.
- Multiplication.
- Division.
- Division by zero.
- Power.
- Valid expressions.
- Operator precedence.
- Parentheses.
- Invalid expressions.
- Unsafe expressions.
- Invalid JSON input and missing fields.
- Invalid numerical values.
- History functionality.
- History limited to the last 20 calculations.

Ensure tests are independent and do not rely on previous test execution order.

Run:

pytest -v

Fix all failing tests.

### DEPENDENCIES

Create requirements.txt with only the necessary dependencies, including:

- fastapi
- uvicorn
- pytest
- httpx

Include any additional dependency only if genuinely needed.

### PART 2: DOCKER IMAGE

Create a production-friendly Dockerfile.

Requirements:

1. Use a lightweight official Python slim base image.
2. Set an appropriate working directory.
3. Install Python dependencies using requirements.txt.
4. Copy requirements.txt before copying application source code to improve Docker layer caching.
5. Create a dedicated non-root Linux user.
6. Run the application as that non-root user.
7. Expose port 8000.
8. Start FastAPI using Uvicorn.
9. Do not include unnecessary development files or virtual environments in the image.

Create .dockerignore to exclude:

- .git/
- .venv/
- __pycache__/
- *.pyc
- .pytest_cache/
- local environment files containing secrets
- unnecessary documentation or development files

The Docker image must run the application correctly.

Commands to verify:

docker build -t calculator-api .

docker run --rm -p 8000:8000 calculator-api

Verify:
- GET /health
- POST /add
- GET /docs
- GET /history

Also explain how to stop the container.

Measure the image size using:

docker images

If the image size exceeds 200 MB, inspect the image and suggest or implement reasonable optimizations without breaking functionality.

Do not sacrifice security or functionality merely to reduce image size.

### PART 3: CALCULATOR USER INTERFACE

Build a simple, attractive, responsive calculator interface.

Preferred implementation:
- Serve a single HTML page using FastAPI at GET /.
- Use HTML, CSS, and JavaScript.
- Keep the frontend simple and avoid unnecessary frameworks.

The interface must contain:

1. Calculator display.
2. Number buttons from 0 to 9.
3. Decimal button.
4. Addition, subtraction, multiplication, division, and power buttons.
5. Clear button.
6. Delete/backspace button.
7. Equals button.
8. Calculation history panel.
9. Friendly error messages.

Functional requirements:

- Clicking buttons should construct a mathematical expression.
- When the user clicks equals, JavaScript should send the expression to POST /calculate.
- Display the result returned by the API.
- Retrieve calculation history from GET /history.
- Refresh history after successful calculations.
- Display clear error messages when the API returns HTTP 400 or another error.
- Handle network errors gracefully.
- Prevent unnecessary page reloads.

The frontend must communicate with the FastAPI backend using relative API paths so that it works from the same origin.

The complete application must work inside the Docker container.

### PART 4: PROJECT DOCUMENTATION AND AGENT WORKFLOW

Create a comprehensive but beginner-friendly README.md.

Include:

1. Project title and objective.
2. Technologies used.
3. Project folder structure.
4. Features and API endpoint descriptions.
5. Sample request and response JSON.
6. Local installation instructions.
7. Instructions to run FastAPI.
8. Instructions to open Swagger documentation at /docs.
9. Instructions to run pytest.
10. Docker image build and run instructions.
11. Instructions to access the calculator UI.
12. Instructions to check Docker image size.
13. Known limitations, including in-memory history resetting after restart.

Also document the following Euron Code assignment requirements:

**A. Vague vs precise prompts**

Compare the initial vague prompt with the detailed master prompt.

Write 2–3 simple lines in README.md explaining how the precise prompt helped the agent understand requirements, avoid assumptions, and generate more complete code.

**B. Agent review and correction**

Review every generated file.

Identify at least one genuine issue, missing requirement, weak implementation, or improvement in the generated code.

Fix it and explain:
- What the original issue was.
- Why it was a problem.
- What you changed.
- How you verified the correction.

Do not invent a bug just to satisfy this requirement.

**C. Euron Code project memory**

I will execute `euron init` in the project directory.

Help maintain the project context and respect any project-level instructions created by initialization.

**D. Prompts documentation**

Maintain prompts.md.

Record every meaningful prompt used during this assignment in chronological order.

For each prompt, include:
- Prompt number.
- Prompt title.
- Actual prompt used.
- One line explaining what the prompt produced.

Include prompts used for implementation, debugging, improvements, testing, and review.

**E. Euron Code usage tracking**

I will check `/usage` before and after the assignment.

Create a section in README.md with:
- Initial allowance/usage.
- Final allowance/usage.
- Approximate allowance consumed.
- Brief observation about usage.

Do not invent usage values. Leave clearly marked placeholders until I provide the actual figures.

### FINAL QUALITY CHECK

Before declaring the project complete:

1. Inspect every project file.
2. Check that all required endpoints exist.
3. Check that all endpoints return the expected responses.
4. Run the complete pytest suite.
5. Verify safe expression parsing.
6. Verify division-by-zero handling.
7. Verify history behavior.
8. Build the Docker image.
9. Verify the container runs as a non-root user.
10. Verify the API and frontend work inside Docker.
11. Check the Docker image size.
12. Check README.md and prompts.md for completeness.

Create a final checklist showing each requirement as:
- Completed
- Not completed
- Requires manual verification

Never mark an unverified requirement as completed.

### HOW TO WORK WITH ME

I am a beginner learning FastAPI, Docker, and coding agents.

For each phase:
- Explain what you are going to create.
- Implement the required files.
- Explain the important code sections.
- Tell me which commands I should run.
- Show the expected output.
- Run and verify commands whenever your environment supports them.
- Explain errors in simple language.
- Wait for my confirmation before moving to the next major phase.

Do not generate the entire project blindly in one step. Help me understand, review, execute, and improve each phase.

Start by inspecting the project directory and presenting your implementation plan. Do not begin implementation until I approve the plan.

**Outcome:** The agent clearly understood the requirements and created a well-structured implementation plan. It identified all the API endpoints, validation requirements, safe expression parsing, testing, Docker, frontend, and documentation requirements. It also explained its technical decisions and divided the implementation into separate phases. This demonstrated how a detailed prompt helped reduce assumptions, improve clarity, and provide better control over the development process.

---

## PROMPT 3: FASTAPI IMPLEMENTATION

Now implement Part 1 of the approved specification.

Focus only on:
- FastAPI application.
- All eight endpoints.
- Pydantic validation.
- Safe AST-based expression parser.
- In-memory calculation history.
- requirements.txt.
- Complete pytest test suite.

Follow the approved project structure.

After implementation:
1. Show all files created or modified.
2. Explain the API architecture.
3. Explain the safe expression parser.
4. Run pytest -v.
5. Fix any failures.
6. Give me the commands to start the application and test endpoints through /docs.
7. Update prompts.md with this prompt and its outcome.

Do not start Docker or frontend implementation yet. Wait for my confirmation.

**Outcome:** Successfully guided Euron Code to build the FastAPI calculator backend with all eight endpoints, input validation, safe expression parsing, and in-memory calculation history. It also generated an automated test suite, with all 53 tests passing.

The agent followed the phased implementation approach and updated the project documentation as instructed. Initially, some errors occurred while running the test file, but the agent made the necessary changes to resolve them.

One additional observation was that the calculation history stores only successfully completed operations. Invalid inputs and failed calculations are not saved in memory.

---

## PROMPT 4: DOCKER IMPLEMENTATION

Now implement Part 2 of the project.

Create:
- Dockerfile.
- .dockerignore.

Follow every Docker requirement from the approved master specification.

Important:
- Use a Python slim image.
- Install requirements before copying source code.
- Create and use a non-root user.
- Exclude unnecessary files.
- Expose port 8000.
- Start the FastAPI application correctly.

Then guide me through:

docker build -t calculator-api .

docker run --rm -p 8000:8000 calculator-api

Verify the health endpoint, addition endpoint, and Swagger documentation from the running container.

Also guide me to check:

docker images

If the image exceeds 200 MB, investigate and optimize it.

Explain the purpose of each important Dockerfile instruction in simple language.

Update prompts.md with this prompt and its outcome.

Do not start frontend implementation yet. Wait for my confirmation.

**Outcome:** The prompt successfully guided Euron Code through Docker image creation, container execution, and verification of the FastAPI application. The initial Docker image size was 249.63 MB, which exceeded the target of 200 MB. After optimization, switching to an Alpine-based image reduced the size to 127 MB, achieving a 49% reduction.

All verification checks, including application health, addition functionality, Swagger documentation, and pytest, passed successfully.

---

## PROMPT 5: CALCULATOR FRONTEND

Now implement Part 3.

Build a responsive HTML/CSS/JavaScript calculator served by FastAPI at GET /.

It must communicate with the existing backend API.

Implement:
- Number buttons.
- Mathematical operator buttons.
- Decimal input.
- Clear and backspace.
- Equals.
- Result display.
- Calculation history panel.
- Friendly error messages.
- API communication using fetch().

Use POST /calculate for evaluating expressions and GET /history for displaying history.

Keep the frontend simple, clean, and beginner-friendly.

Do not duplicate mathematical calculations in JavaScript. The backend must perform the calculations.

Ensure the frontend works when the application runs inside the Docker container.

After implementation:
1. Explain the frontend-to-backend communication.
2. Run the application.
3. Test the calculator in the browser.
4. Test history updates.
5. Test division by zero and invalid expressions.
6. Fix any issues found.
7. Update prompts.md.

Wait for my confirmation before the final review.

**Outcome:** During frontend testing, I noticed that the History tab was displayed on the right side, but it was not showing any calculation history. I reported this issue to the agent, and it made the necessary changes to fix it. The history was then displayed as expected.
---

## PROMPT 6: CODE REVIEW AND FINAL DOCUMENTATION

Now perform a complete review of the calculator project.

Inspect every file, including:
- app/main.py
- app/templates/index.html
- tests/test_main.py
- requirements.txt
- Dockerfile
- .dockerignore
- README.md
- prompts.md
- .gitignore

Check the implementation against the original master specification.

Identify at least one genuine issue or improvement in the code, fix it, and explain the correction.

Re-run the relevant tests after making changes.

Complete README.md with:
- Project overview.
- Technologies.
- API endpoints.
- Installation.
- Local execution.
- Swagger documentation.
- Testing instructions.
- Docker build and run.
- Docker image size.
- Frontend usage.
- Vague versus precise prompt comparison.
- Code review and correction details.
- Euron Code usage tracking placeholders.

Complete prompts.md with every meaningful prompt used in chronological order and a one-line description of its outcome.

Do not fabricate:
- Test results.
- Docker build results.
- Image size.
- Euron Code usage statistics.
- Code review findings.

Finally, provide a requirement-by-requirement completion checklist and identify anything I must manually verify.

Explain the final project in simple language so I can confidently demonstrate it in my Super 30 assignment video.

**Outcome:** Agent identified a Cross-Site Scripting (XSS) vulnerability in the frontend, which was the main security issue. It was successfully resolved.

---

## Prompt Quality Summary

| Prompt | Focus | Key Observation |
|-------|----------|--------|
| Prompt 1 | Vague calculator prompt | Created a basic working API, but Swagger documentation lacked clearly defined operations. |
| Prompt 2 | Master project specification | Created a structured implementation plan covering FastAPI, Docker, frontend, testing, and documentation. |
| Prompt 3 | FastAPI implementation | Implemented all 8 endpoints, validation, safe AST parsing, and history. All 53 tests passed. |
| Prompt 4 | Docker implementation | Optimized Docker image from 249.63 MB to 127 MB, reducing size by 49%. |
| Prompt 5 | Calculator frontend | Fixed the issue where the History tab was not displaying calculation history. |
| Prompt 6 | Code review and documentation | Identified and resolved the main frontend security issue: XSS vulnerability. |

**Key lesson:** A vague prompt can produce a basic working solution, but a precise prompt provides better clarity, structure, and control. Testing, reviewing, and refining the generated code are equally important for building a reliable application.
