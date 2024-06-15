from fastapi import APIRouter, HTTPException
from app.models import (
    CodeRequest,
    FeedbackRequest,
    CodeTestsRequest,
    CodeTestsRunRequest,
    CodeTestsImproveRequest,
)
from app.core.config import client, setup_message, dockerClient

# Initialize the API router from FastAPI
router = APIRouter()


@router.post("/generate_code", response_model=dict)
async def generate_code(request: CodeRequest):
    """
    Generates code based on the description provided by the user.
    Strips any markdown syntax to ensure plain code is returned.
    """
    description = request.description.strip()
    if not description:
        return {"code": "Please provide the code snippet description!"}

    try:
        message = {
            "role": "user",
            "content": (
                f"Generate a runnable {request.language} code snippet that defines a function, without any comments explaining the function's purpose and logic. "
                "The function should be directly related to the provided description, without any extraneous messages or comments unrelated to the functionality. "
                "Also it should not include the test code for the function and no any import of external library."
                f"Description of the task:\n\n{description}"
            ),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[setup_message, message]
        )

        code = response.choices[0].message.content.strip()
        # Process to remove Markdown syntax if present
        if code.startswith("```") and code.endswith("```"):
            code = "\n".join(code.split("\n")[1:-1])

        return {"code": code}
    except Exception as e:
        # Capture and send detailed error messages
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_tests", response_model=dict)
async def generate_tests(request: CodeTestsRequest):
    """
    Generates test cases for a given code snippet based on the specified language.
    """
    try:
        message = {
            "role": "user",
            "content": (
                f"Generate only assert test cases for this {request.language} code snippet "
                "in the appropriate format. For example, use `assert is_even(8) == True` for Python. "
                "Please generate at least 5 test cases. Each test case should consist of a single assert statement, "
                "formatted on its own line. There should be no additional statements, no loops, lists, or any extraneous syntax. "
                "Focus solely on creating assert statements that directly test the functionality of the provided code snippet. "
                f"Code snippet to test:\n\n{request.code}"
            ),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[message]
        )

        code_tests = response.choices[0].message.content.strip()
        return {"code_tests": code_tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve_tests", response_model=dict)
async def improve_tests(request: CodeTestsImproveRequest):
    """
    Improves existing test cases based on the provided feedback and original test cases.
    """
    try:
        message = {
            "role": "user",
            "content": (
                f"Based on the provided feedback, improve the test cases for the {request.language} code snippet. "
                "Ensure that the test cases are formatted with only assert statements. For example, in Python: `assert is_even(8) == True`. "
                "The test cases should not include any extra statements, loops, or list formats. Each test should be on its own line. "
                "Focus solely on creating assert statements that directly test the functionality of the provided code snippet and the feedback.\n\n"
                f"Code snippet:\n{request.code}\n\n"
                f"Current tests:\n{request.test_cases}\n\n"
                f"Feedback on tests:\n{request.test_feedback}"
            ),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[message]
        )

        improved_code_tests = response.choices[0].message.content.strip()
        return {"code_tests": improved_code_tests}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run_tests", response_model=dict)
async def run_tests(request: CodeTestsRunRequest):
    """
    Executes provided test cases for Python code snippets and reports the results.
    """
    if request.language != "python":
        return {
            "test_result": "Run test functionality is only available for Python code snippets.",
            "error": True,
        }

    full_code = f"{request.code}\n{request.test_cases}"
    container = None
    try:
        # Run the container
        container = dockerClient.containers.run(
            "python:3.11-slim",
            command=["python", "-c", "import os; exec(os.getenv('CODE'))"],
            environment={"CODE": full_code},
            detach=True,
            remove=False,  # Set remove to False to manually handle container cleanup
        )
        # Wait for the container to finish executing
        result = container.wait()

        # Fetch the logs after the container execution completes
        output = container.logs()

        if result["StatusCode"] == 1:
            return {"test_result": output.decode("utf-8"), "error": True}
        return {
            "test_result": "All tests passed successfully.",
            "error": False,
        }
    except Exception as e:
        # Handle exceptions that could occur during container run, wait or fetching logs
        return {"test_result": str(e), "error": True}
    finally:
        # Ensure container is removed if it was created
        if container:
            try:
                container.remove()
            except Exception as e:
                # Log this error or handle it as needed
                print(f"Error removing container: {str(e)}")


@router.post("/improve_code", response_model=dict)
async def improve_code(request: FeedbackRequest):
    """
    Improves the provided code snippet based on user feedback.
    """
    try:
        message = {
            "role": "user",
            "content": (
                f"Improve this {request.language} code snippet based on the detailed feedback provided. "
                "Make specific changes to enhance functionality, performance, and adherence to best practices as per the feedback. "
                "Ensure that the changes precisely address the concerns and suggestions mentioned in the feedback. "
                "Below are the details:\n\n"
                f"Feedback Provided:\n{request.feedback}\n\n"
                f"Original Code:\n{request.code}\n\n"
                "Please revise the code accordingly and ensure that the modifications are clear and directly responsive to the feedback. "
                "Also it should not include the test code for the function, any comments and any external library import statements."
            ),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[message]
        )

        improved_code = response.choices[0].message.content.strip()
        # Remove Markdown syntax if present
        if improved_code.startswith("```") and improved_code.endswith("```"):
            improved_code = "\n".join(improved_code.split("\n")[1:-1])

        return {"code": improved_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate_code_based_on_tests", response_model=dict)
async def regenerate_code_based_on_tests(request: FeedbackRequest):
    """
    Regenerates code based on test results and user feedback.
    """
    try:
        message = {
            "role": "user",
            "content": (
                f"Regenerate this {request.language} code snippet by incorporating the feedback from the test results to improve its functionality and correctness. "
                "Also it should not include the test code for the function. "
                f"Please ensure that the regenerated code adheres to the best practices of the {request.language} "
                "programming style and optimally addresses the issues highlighted in the test results. "
                "The focus should be on enhancing the logic and fixing any errors pointed out, while maintaining the original intent of the code. \n\n"
                "Also it should not include the test code for the function, any comments and any external library import statements."
                f"Test Results:\n{request.feedback}\n\n"
                f"Original Code:\n{request.code}"
            ),
        }
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[message]
        )

        new_code = response.choices[0].message.content.strip()
        # Remove Markdown syntax if present
        if new_code.startswith("```") and new_code.endswith("```"):
            new_code = "\n".join(new_code.split("\n")[1:-1])

        return {"new_code": new_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
