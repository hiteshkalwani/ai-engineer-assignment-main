// Import utility functions from 'utils.js' module
import { 
    escapeHTML, showLoading, updateCodeClass, 
    validateRunTestVisibility, resetData, resetButtons, 
    sanitizeInput, toggleButtonAttribute, 
    toggleExtraSection, resetTestResult, setTestResult
} from './utils.js';

document.addEventListener('DOMContentLoaded', function() {
    loadSnippets();  // Load snippet
    toggleExtraSection();

    // Event listener for Create New Snippet button
    document.getElementById("create-snippet-button").addEventListener("click", function() {
        resetData();
    });
});

// Add event listener for language selection changes
document.getElementById("language").addEventListener("change", function() {
    const language = this.value;
    const codeSnippet = document.getElementById("code-snippet");
    updateCodeClass(codeSnippet, language);  // Update code syntax highlighting based on selected language
});

// Add event listener for generating code
document.getElementById("generate-button").addEventListener("click", async () => {
    const description = sanitizeInput(document.getElementById("description").value);
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
    saveSnippet(description, language, result.code);

    // reset the data
    resetButtons();
    resetTestResult();
    document.getElementById("feedback").value = "";
    document.getElementById("test-snippet").innerText = "";
    document.getElementById("test-feedback").value = "";
    document.getElementById("test-results").innerText = "";
    
    toggleButtonAttribute("improve-code-button", false);
    toggleButtonAttribute("generate-tests-button", false);
    toggleExtraSection(false);

    showLoading(false);  // Hide loading animation
});

// Add event listener for improving code
document.getElementById("improve-code-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const feedback = sanitizeInput(document.getElementById("feedback").value);
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
    toggleButtonAttribute("improve-tests-button", false);
    validateRunTestVisibility(language);
    showLoading(false);
});

// Add event listener for improving test cases
document.getElementById("improve-tests-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const language = document.getElementById("language").value;
    const testCases = document.getElementById("test-snippet").innerText;
    const testFeedback = sanitizeInput(document.getElementById("test-feedback").value);
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
        setTestResult(true);
        toggleButtonAttribute("regenerate-button", false);
    } else {
        setTestResult();
    }
    showLoading(false);
});

// Add event listener for regenerating code based on test results
document.getElementById("regenerate-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const description = sanitizeInput(document.getElementById("description").value);
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
    saveSnippet(description, language, result.new_code);

    // reset the data
    resetButtons();
    resetTestResult();

    document.getElementById("feedback").value = "";
    document.getElementById("test-feedback").value = "";
    document.getElementById("test-results").innerText = "";
    document.getElementById("test-snippet").innerText = "";
    toggleButtonAttribute("improve-code-button", false);
    toggleButtonAttribute("generate-tests-button", false);

    showLoading(false);
});

/**
 * Resets the styling of all snippets in the list and shows delete buttons.
 */
export function resetSnippetList() {
    const snippetElements = document.querySelectorAll("#snippet-list li a");
    snippetElements.forEach(el => {
        el.classList.remove("bg-purple-500", "text-white");
        el.classList.add("bg-gray-300", "text-black");
        el.nextElementSibling.style.display = ''; // Show delete button
    });
}

/**
 * Highlights the selected snippet, hiding its delete button.
 * @param {number} id  - The HTML element representing the snippet to highlight.
 */s
export function highlightSnippet(id) {
    resetSnippetList(); // Reset all snippets to default style
}

/**
 * Loads a specific snippet into the code editor based on its ID.
 * @param {number} id - The ID of the snippet to load.
 */
export function loadSnippet(id) {
    resetSnippetList(); // Reset all snippets to default style
    const snippets = JSON.parse(localStorage.getItem("snippets") || "[]");
    const snippet = snippets.find(s => s.id === id);

    if (snippet) {
        resetData();
        resetTestResult();
        const codeElement = document.getElementById("code-snippet");
        document.getElementById("description").value = snippet.description;
        document.getElementById("language").value = snippet.language;
        codeElement.innerHTML = escapeHTML(snippet.code);
        document.getElementById("description").setAttribute("data-snippet-id", snippet.id);
        toggleButtonAttribute("improve-code-button", false);
        toggleButtonAttribute("generate-tests-button", false);
        toggleExtraSection(false);
        updateCodeClass(codeElement, snippet.language);

        const snippetElement = document.getElementById(`snippet-${id}`);
        snippetElement.classList.remove("bg-gray-300", "text-black");
        snippetElement.classList.add("bg-purple-500", "text-white");
        document.getElementById(`delete-snippet-${id}`).style.display = 'none'; // Hide delete button
    } else {
        console.error(`Snippet with ID ${id} not found.`);
    }
}

/**
 * Loads all snippets from local storage and displays them in the UI.
 */
export function loadSnippets() {
    const snippets = JSON.parse(localStorage.getItem("snippets") || "[]");
    const list = document.getElementById("snippet-list");
    list.innerHTML = ''; // Clear existing list

    if (snippets.length === 0) {
        list.innerHTML = `
            <li id="no-snippets" class="flex justify-between mb-4">
                <p>No snippets available.</p>
            </li>
        `;
    } else {
        snippets.forEach(snippet => {
            const snippetElement = document.createElement("li");
            snippetElement.className = "flex justify-between mb-4";
            snippetElement.innerHTML = `
                <a id="snippet-${snippet.id}" class="w-full block p-2 bg-gray-300 rounded snippet-link cursor-pointer">
                    ${snippet.description} | ${snippet.language}
                </a>
                <button id="delete-snippet-${snippet.id}" class="bg-red-500 text-white px-2 py-1 rounded delete-button">
                    Delete
                </button>
            `;
            list.appendChild(snippetElement);

            // Attach event listener for clicking on snippet link
            const snippetLink = snippetElement.querySelector(`#snippet-${snippet.id}`);
            snippetLink.addEventListener("click", () => {
                highlightSnippet(snippet.id);
                loadSnippet(snippet.id);
            });

            // Attach event listener for clicking on delete button
            const deleteButton = snippetElement.querySelector(".delete-button");
            deleteButton.addEventListener("click", (event) => {
                event.stopPropagation(); // Prevent link click event from firing
                deleteSnippet(snippet.id);
            });
        });
    }
}

/**
 * Deletes a snippet from local storage based on its ID.
 * @param {number} id - The ID of the snippet to delete.
 */
export function deleteSnippet(id) {
    let snippets = JSON.parse(localStorage.getItem("snippets") || "[]");
    snippets = snippets.filter(snippet => snippet.id !== id);
    localStorage.setItem("snippets", JSON.stringify(snippets));

    // Reload snippet list in UI
    loadSnippets();

    // Clear editor if deleted snippet was displayed
    const displayedSnippetId = parseInt(document.getElementById("description").dataset.snippetId);
    if (displayedSnippetId === id) {
        document.getElementById("description").value = '';
        document.getElementById("language").value = 'python'; // Default or reset
        document.getElementById("code-snippet").textContent = '';
        document.getElementById("description").removeAttribute("data-snippet-id");
    }
}

/**
 * Saves a new snippet to local storage.
 * @param {string} description - The description of the new snippet.
 * @param {string} language - The programming language of the new snippet.
 * @param {string} code - The code content of the new snippet.
 */
export function saveSnippet(description, language, code) {
    const snippets = JSON.parse(localStorage.getItem("snippets") || "[]");
    const newSnippet = {
        id: Date.now(),
        description,
        language,
        code
    };
    snippets.push(newSnippet);
    localStorage.setItem("snippets", JSON.stringify(snippets));

    // Reload snippet list in UI
    loadSnippets();
}
