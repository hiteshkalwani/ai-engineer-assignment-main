from fastapi import APIRouter, HTTPException
from app.models import (
    CodeRequest,
    FeedbackRequest,
    CodeTestsRequest,
    CodeTestsRunRequest,
    CodeTestsImproveRequest,
)
from app.core.config import client, setup_message, dockerClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the API router from FastAPI
router = APIRouter()


@router.post("/generate_code", response_model=dict)
async def generate_code(request: CodeRequest):
    """
    Endpoint to generate code based on a description.
    Returns code that meets the description's requirements.
    """
    description = request.description.strip()
    if not description:
        logger.error("No description provided for code generation.")
        return {"code": "Please provide the code snippet description!"}

    try:
        message = {
            "role": "user",
            "content": (
                f"Generate a runnable {request.language} code snippet that defines a function, "
                "without any comments explaining the function's purpose and logic. "
                "Ensure the function relates directly to the provided description, "
                "excluding any extraneous messages or comments unrelated to the functionality. "
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
        logger.exception("Failed to generate code due to an error.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate_tests", response_model=dict)
async def generate_tests(request: CodeTestsRequest):
    """
    Endpoint to generate test cases for a given code snippet.
    Generates a minimum of five test cases based on the specified language.
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
        logger.exception("Failed to generate test cases due to an error.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/improve_tests", response_model=dict)
async def improve_tests(request: CodeTestsImproveRequest):
    """
    Endpoint to improve existing test cases based on user feedback.
    Adjusts test cases to better meet the functionality of the provided code snippet.
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
        logger.exception("Failed to improve test cases due to an error.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run_tests", response_model=dict)
async def run_tests(request: CodeTestsRunRequest):
    """
    Executes provided test cases for Python code snippets and reports the results.
    Only supports Python due to the use of a specific Python Docker container for execution.
    """
    if request.language != "python":
        logger.warning(
            "Attempted to run tests for unsupported language: %s",
            request.language,
        )
        return {
            "test_result": "Run test functionality is only available for Python code snippets.",
            "error": True,
        }

    full_code = f"{request.code}\n{request.test_cases}"
    container = None
    try:
        logger.info("Running Python code in a Docker container")
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
            logger.error(
                "Tests failed with output: %s", output.decode("utf-8")
            )
            return {"test_result": output.decode("utf-8"), "error": True}

        logger.info("Tests passed successfully")
        return {
            "test_result": "All tests passed successfully.",
            "error": False,
        }
    except Exception as e:
        # Handle exceptions that could occur during container run, wait or fetching logs
        logger.exception("Failed to run tests due to an error")
        return {"test_result": str(e), "error": True}
    finally:
        # Ensure container is removed if it was created
        if container:
            try:
                container.remove()
                logger.info("Docker container removed successfully")
            except Exception as e:
                logger.error("Failed to remove Docker container: %s", str(e))


@router.post("/improve_code", response_model=dict)
async def improve_code(request: FeedbackRequest):
    """
    Improves the provided code snippet based on user feedback focusing on specific issues highlighted.
    Strips any markdown syntax to return plain code.
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

        logger.info("Code improved based on feedback")
        return {"code": improved_code}
    except Exception as e:
        logger.exception("Failed to improve code due to an error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate_code_based_on_tests", response_model=dict)
async def regenerate_code_based_on_tests(request: FeedbackRequest):
    """
    Regenerates the code snippet by incorporating test results and feedback, ensuring it aligns with best practices and addresses noted issues.
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

        logger.info("Code regenerated based on test results and feedback")
        return {"new_code": new_code}
    except Exception as e:
        logger.exception("Failed to regenerate code due to an error")
        raise HTTPException(status_code=500, detail=str(e))
