from fastapi import APIRouter, HTTPException
from app.models import CodeRequest, FeedbackRequest, CodeTestsRequest, CodeTestsRunRequest
from app.core.config import client, setup_message

# Define the router
router = APIRouter()


@router.post("/generate_code", response_model=dict)
async def generate_code(request: CodeRequest):
    try:
        message = {
            'role': 'user',
            'content': (f"Generate runnable {request.language} code snippet with comments "
                        "and only return the runnable code snippet without any extra message, "
                        f"for: {request.description}"),
        }
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[setup_message, message]
        )

        code = response.choices[0].message.content.strip()
        # Remove Markdown code block syntax
        if code.startswith("```") and code.endswith("```"):
            # Remove the first line (```language)
            code = "\n".join(code.split("\n")[1:-1])

        return {"code": code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_tests", response_model=dict)
async def generate_tests(request: CodeTestsRequest):
    try:
        message = {
            'role': 'user',
            'content': (f"Generate test cases for this {request.language} code snippet "
                        "and format would be differ as per the programming language. "
                        "for python programming language : `assert is_even(8) == True`, "
                        "for ruby programming language : `assert_equal false, is_even(5)`, "
                        "and for javascript language : `assert.isTrue(is_even(5))` "
                        "choose one test case format and generate minimum 5 test cases "
                        f"for code snippet:\n\n{request.code}"),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[message]
        )

        code_tests = response.choices[0].message.content.strip()
        return {"code_tests": code_tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/run_tests", response_model=dict)
async def run_tests(request: CodeTestsRunRequest):
    try:
        message = {
            'role': 'user',
            'content': (f"Run the provided test cases on {request.language} code snippet "
                        "and if found any issue then return the issue otherwise write only `All tests passed successfully!`, "
                        f"code :\n\n{request.code} \n\n And test cases:\n\n{request.test_cases}"),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[message]
        )

        code_tests_result = response.choices[0].message.content.strip()

        error = False
        if code_tests_result != 'All tests passed successfully!':
            error = True

        return {"test_results": code_tests_result, "error": error}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/improve_code", response_model=dict)
async def improve_code(request: FeedbackRequest):
    try:
        message = {
            'role': 'user',
            'content': (f"Improve this {request.language} code snippet with comments "
                        "and only return the runnable code snippet without any extra message "
                        f"based on the feedback: {request.feedback}\n\n{request.code}"),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[message]
        )

        improved_code = response.choices[0].message.content.strip()
        # Remove Markdown code block syntax
        if improved_code.startswith("```") and improved_code.endswith("```"):
            # Remove the first line (```language)
            improved_code = "\n".join(improved_code.split("\n")[1:-1])

        return {"code": improved_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/regenerate_code_based_on_tests", response_model=dict)
async def regenerate_code_based_on_tests(request: FeedbackRequest):
    try:
        message = {
            'role': 'user',
            'content': (f"Regenerate this {request.language} code snippet with comments "
                        "and only return the runnable code snippet without any extra message "
                        f"based on test results:\n\n{request.feedback}\n\nOriginal Code:\n{request.code}"),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[message]
        )

        new_code = response.choices[0].message.content.strip()
        # Remove Markdown code block syntax
        if new_code.startswith("```") and new_code.endswith("```"):
            # Remove the first line (```language)
            new_code = "\n".join(new_code.split("\n")[1:-1])

        return {"new_code": new_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))