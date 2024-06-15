/**
 * Toggles the visibility of the extra section div based on the disabled flag.
 * @param {boolean} disabled - Flag indicating whether to disable (hide) or enable (show) the extra section.
 */
export function toggleExtraSection(disabled=true) {
    const extraSectionDiv = document.getElementById("extra-section");
    if (disabled) {
        extraSectionDiv.style.display = "none"; // Hide the extra section
    } else {
        extraSectionDiv.style.display = "block"; // Show the extra section
    }
}

/**
 * Toggles the background color of a button based on the disabled state.
 * @param {string} buttonId - The ID of the button element.
 * @param {boolean} disabled - Whether to disable the button (default: true).
 */
export function toggleButtonAttribute(buttonId, disabled=true) {
    const button = document.getElementById(buttonId);
    
    if (disabled) {
        // Disable button style
        button.classList.remove("bg-teal-500");
        button.classList.add("bg-gray-500");
        button.disabled = true; // Disable button functionality
    } else {
        // Enable button style
        button.classList.add("bg-teal-500");
        button.classList.remove("bg-gray-500");
        button.disabled = false; // Enable button functionality
    }
}

/**
 * Sanitizes user input to prevent prompt injection attacks.
 * Removes unsafe characters like < and > from the input.
 * @param {string} input - The user-provided input to sanitize.
 * @returns {string} The sanitized input.
 */
export function sanitizeInput(input) {
    // Define a regular expression to match unsafe characters or patterns
    const unsafePattern = /[<>]/g; // Matches < and >

    // Replace unsafe characters with safe alternatives or remove them
    const sanitizedInput = input.replace(unsafePattern, '');

    return sanitizedInput;
}

/**
 * Escapes HTML characters in a string to prevent XSS attacks.
 * @param {string} str - The string to escape.
 * @returns {string} The escaped string.
 */
export function escapeHTML(str) {
    return str.replace(/[&<>"']/g, function(match) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }[match];
    });
}

/**
 * Controls the visibility of the loading animation overlay.
 * @param {boolean} visible - Determines if the loading animation should be shown.
 */
export function showLoading(visible) {
    document.getElementById("fullPageLoading").style.display = visible ? "block" : "none";
}

/**
 * Updates the class for syntax highlighting based on the selected programming language.
 * Resets the highlighting state if it has already been highlighted.
 * @param {HTMLElement} codeElement - The DOM element that contains the code to be highlighted.
 * @param {string} language - The programming language of the code for syntax highlighting.
 */
export function updateCodeClass(codeElement, language) {
    if (codeElement.dataset.highlighted) {
        delete codeElement.dataset.highlighted; // Reset the highlighting state
    }

    // Set class name for syntax highlighting and re-apply highlighting
    codeElement.className = `hljs ${language.toLowerCase()} language-${language.toLowerCase()}`;
    hljs.highlightElement(codeElement);
}

/**
 * Validates and updates the visibility and style of the run tests button based on the selected language.
 * The button is only enabled for Python.
 * @param {string} language - The programming language selected.
 * @param {boolean} [visible=true] - Optionally specify if the test run button should be visible.
 */
export function validateRunTestVisibility(language, visible=true) {
    // Enable the run test button for Python and when visible is true
    if (language === "python" && visible) {
        toggleButtonAttribute("run-tests-button", false);
    } else {
        toggleButtonAttribute("run-tests-button")
    }
}

/**
 * Resets the test results display by clearing text and resetting background color.
 */
export function resetTestResult() {
    const testResult = document.getElementById("test-results");
    testResult.innerText = ""; // Clear any existing text content
    testResult.classList.remove("bg-red-300"); // Remove red background color
    testResult.classList.remove("bg-green-300"); // Remove green background color
    testResult.classList.add("bg-white-300"); // Add white background color (default)
}

/**
 * Sets the test result display based on the error flag.
 * @param {boolean} error - Flag indicating whether the test result is an error.
 */
export function setTestResult(error=false) {
    const testResult = document.getElementById("test-results");
    if (error) {
        testResult.classList.remove("bg-white-300"); // Remove default white background color
        testResult.classList.remove("bg-green-300"); // Remove green background color
        testResult.classList.add("bg-red-300"); // Add red background color for error
    } else {
        testResult.classList.remove("bg-white-300"); // Remove default white background color
        testResult.classList.remove("bg-red-300"); // Remove red background color
        testResult.classList.add("bg-green-300"); // Add green background color for success
    }
}


/**
 * Resets the attributes of various buttons to default state.
 */
export function resetButtons() {
    toggleButtonAttribute("improve-code-button");
    toggleButtonAttribute("generate-tests-button");
    toggleButtonAttribute("improve-tests-button");
    toggleButtonAttribute("run-tests-button");
    toggleButtonAttribute("regenerate-button");
}

/**
 * Resets all input fields and elements related to snippet generation and testing.
 */
export function resetData() {
    toggleExtraSection();

    // Reset input fields
    document.getElementById('language').value = "python";  // Reset language selection
    document.getElementById("feedback").value = "";       // Clear feedback input
    document.getElementById("test-feedback").value = "";    // Clear test feedback input
    document.getElementById("description").value = "";    // Clear snippet description
    
    // Clear output areas
    document.getElementById("test-results").innerText = "";  // Clear test results display
    document.getElementById("test-snippet").innerText = "";  // Clear test snippet display
    document.getElementById("code-snippet").innerText = "";  // Clear generated code display

    // Reset button states
    resetButtons();  // Calls resetButtons() to reset button styles and disabled states
}
