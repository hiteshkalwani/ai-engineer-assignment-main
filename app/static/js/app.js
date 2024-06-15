// Import utility functions from 'utils.js' module
import { escapeHTML, showLoading, updateCodeClass, validateRunTestVisibility } from './utils.js';

// Add event listener for language selection changes
document.getElementById("language").addEventListener("change", function() {
    const language = this.value;
    const codeSnippet = document.getElementById("code-snippet");
    updateCodeClass(codeSnippet, language);  // Update code syntax highlighting based on selected language
});

// Add event listener for generating code
document.getElementById("generate-button").addEventListener("click", async () => {
    const description = document.getElementById("description").value;
    const language = document.getElementById("language").value;
    showLoading(true);  // Show loading animation

    const response = await fetch("/generate_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, language })
    });
    const result = await response.json();

    const codeElement = document.getElementById("code-snippet");
    codeElement.innerHTML = escapeHTML(result.code);  // Display escaped code to prevent XSS

    validateRunTestVisibility(language, false);
    updateCodeClass(codeElement, language);
    showLoading(false);  // Hide loading animation
});

// Add event listener for improving code
document.getElementById("improve-code-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const feedback = document.getElementById("feedback").value;
    const language = document.getElementById("language").value;
    showLoading(true);

    const response = await fetch("/improve_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, feedback, language })
    });
    const result = await response.json();

    const codeElement = document.getElementById("code-snippet");
    codeElement.innerHTML = escapeHTML(result.code);

    validateRunTestVisibility(language, false);
    updateCodeClass(codeElement, language);
    showLoading(false);
});

// Add event listener for generating test cases
document.getElementById("generate-tests-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const language = document.getElementById("language").value;
    showLoading(true);

    const response = await fetch("/generate_tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language })
    });
    const result = await response.json();

    document.getElementById("test-snippet").innerHTML = escapeHTML(result.code_tests);
    validateRunTestVisibility(language);
    showLoading(false);
});

// Add event listener for improving test cases
document.getElementById("improve-tests-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const language = document.getElementById("language").value;
    const testCases = document.getElementById("test-snippet").innerText;
    const testFeedback = document.getElementById("test-feedback").value;
    showLoading(true);

    const response = await fetch("/improve_tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, test_cases: testCases, test_feedback: testFeedback, language: language })
    });
    const result = await response.json();

    document.getElementById("test-snippet").innerHTML = escapeHTML(result.code_tests);
    validateRunTestVisibility(language);
    showLoading(false);
});

// Add event listener for running test cases
document.getElementById("run-tests-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const language = document.getElementById("language").value;
    const testCases = document.getElementById("test-snippet").innerText;
    showLoading(true);

    const response = await fetch("/run_tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, test_cases: testCases, language: language })
    });
    const result = await response.json();

    document.getElementById("test-results").innerText = result.test_result;
    if (result.error === true) {
        const regenerateButton = document.getElementById("regenerate-button");
        regenerateButton.disabled = false;
        regenerateButton.classList.remove("bg-gray-500");
        regenerateButton.classList.add("bg-teal-500");
    }
    showLoading(false);
});

// Add event listener for regenerating code based on test results
document.getElementById("regenerate-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const feedback = document.getElementById("test-results").innerText;
    const language = document.getElementById("language").value;
    showLoading(true);

    const response = await fetch("/regenerate_code_based_on_tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, feedback, language })
    });
    const result = await response.json();

    document.getElementById("code-snippet").innerHTML = escapeHTML(result.new_code);

    const regenerateButton = document.getElementById("regenerate-button");
    regenerateButton.disabled = true;
    regenerateButton.classList.remove("bg-teal-500");
    regenerateButton.classList.add("bg-gray-500");
    validateRunTestVisibility(language, false);
    showLoading(false);
});
