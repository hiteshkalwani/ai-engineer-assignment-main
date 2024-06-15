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
    const runTestButton = document.getElementById("run-tests-button");

    // Enable the run test button for Python and when visible is true
    if (language === "python" && visible) {
        runTestButton.disabled = false;
        runTestButton.classList.remove("bg-gray-500");
        runTestButton.classList.add("bg-teal-500");
    } else {
        runTestButton.disabled = true;
        runTestButton.classList.remove("bg-teal-500");
        runTestButton.classList.add("bg-gray-500");
    }
}
