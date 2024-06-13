document.getElementById("generate-button").addEventListener("click", async () => {
    const description = document.getElementById("description").value;
    const language = document.getElementById("language").value;
    const response = await fetch("/generate_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description, language })
    });
    const result = await response.json();
    document.getElementById("code-snippet").innerText = result.code;
});

document.getElementById("improve-code-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const feedback = document.getElementById("feedback").value;
    const language = document.getElementById("language").value;
    const response = await fetch("/improve_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, feedback, language })
    });
    const result = await response.json();
    document.getElementById("code-snippet").innerText = result.code;
});

document.getElementById("generate-tests-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const language = document.getElementById("language").value;
    const response = await fetch("/generate_tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language })
    });
    const result = await response.json();
    document.getElementById("test-snippet").innerText = result.code_tests;
});

document.getElementById("run-tests-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const language = document.getElementById("language").value;
    const testCases = document.getElementById("test-snippet").innerText;
    const response = await fetch("/run_tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: code, test_cases: testCases, language: language })
    });
    const result = await response.json();
    document.getElementById("test-results").innerText = result.test_results;
    if (result.error === true) {
        document.getElementById("regenerate-button").disabled = false;
        button.classList.remove("bg-gray-500");
        button.classList.add("bg-teal-500");
    }
});

document.getElementById("regenerate-button").addEventListener("click", async () => {
    const code = document.getElementById("code-snippet").innerText;
    const feedback = document.getElementById("test-results").innerText;
    const language = document.getElementById("language").value;
    const response = await fetch("/regenerate_code_based_on_tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, feedback, language })
    });
    const result = await response.json();
    document.getElementById("code-snippet").innerText = result.new_code;

    document.getElementById("regenerate-button").disabled = true;
    button.classList.remove("bg-teal-500");
    button.classList.add("bg-gray-500");
});
