import traceback
from fastapi import APIRouter, HTTPException
from app.models import CodeRequest, FeedbackRequest, CodeTestsRequest, CodeTestsRunRequest, CodeTestsImproveRequest
from app.core.config import client, setup_message

# Define the router
router = APIRouter()


@router.post("/generate_code", response_model=dict)
async def generate_code(request: CodeRequest):
    if request.description.strip() != "":
        try:
            message = {
                'role': 'user',
                'content': (f"Generate runnable {request.language} code snippet (only function) with comments "
                            "without any extra message, "
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
    
    return {"code": "Please provide the code snippet description!"}


@router.post("/generate_tests", response_model=dict)
async def generate_tests(request: CodeTestsRequest):
    try:
        message = {
            'role': 'user',
            'content': (f"Generate only assert test cases for this {request.language} code snippet "
                        "and format would be differ as per the programming language. "
                        "for python programming language : `assert is_even(8) == True`, "
                        "for ruby programming language : `assert_equal false, is_even(5)`, "
                        "and for javascript language : `assert.isTrue(is_even(5))` "
                        "choose one test case format and generate minimum 5 test cases "
                        "with only assert statements without any other statements or comments "
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
    

@router.post("/improve_tests", response_model=dict)
async def improve_tests(request: CodeTestsImproveRequest):
    try:
        message = {
            'role': 'user',
            'content': (f"Generate test cases for this {request.language} code snippet "
                        "and format would be differ as per the programming language. "
                        "for python programming language : `assert is_even(8) == True`, "
                        "for ruby programming language : `assert_equal false, is_even(5)`, "
                        "and for javascript language : `assert.isTrue(is_even(5))` "
                        "choose one test case format and generate minimum 5 test cases "
                        "with only assert statements without any other statements or comments "
                        "also according to the feedback of previously generated test cases "
                        f"improve the test cases: \n\n{request.test_cases}  \n\nfeedback : \n\n{request.test_feedback} "
                        f"\n\nfor code snippet:\n\n{request.code}"),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[message]
        )

        improved_code_tests = response.choices[0].message.content.strip()
        return {"code_tests": improved_code_tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run_tests", response_model=dict)
async def run_tests(request: CodeTestsRunRequest):
    if request.language == 'python':
        full_code = f"{request.code}\n{request.test_cases}"
        try:
            # Prepare a local dictionary to execute the code
            local_vars = {}
            exec(full_code, {}, local_vars)
            # If we reach here, all assertions passed
            return {"test_result": "All tests passed successfully."}
        except AssertionError as e:
            return {"test_result": f"Test failed: {str(e)}"}
        except Exception:
            # Catch other errors, such as syntax errors
            return {"test_result": f"Error executing the tests: {traceback.format_exc()}"}
    
    return {"test_result": "run test functionality only available for python code snippet."}
    

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