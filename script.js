async function translateText() {
  const inputText = document.getElementById("input-text").value.trim();
  const inputLang = document.getElementById("input-language").value;
  const outputLang = document.getElementById("output-language").value;
  const outputArea = document.getElementById("output-text");
  const spinner = document.getElementById("loading-spinner");
  const translateBtn = document.getElementById("translate-btn");

  if (!inputText) {
    outputArea.value = "Please enter some text.";
    return;
  }

  spinner.style.display = "inline-block";
  translateBtn.disabled = true;
  translateBtn.style.opacity = 0.6;

  try {
    const response = await fetch("http://localhost:5000/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: inputText,
        source_lang: inputLang,
        target_lang: outputLang
      })
    });

    if (!response.ok) {
      outputArea.value = `Server error: ${response.status} ${response.statusText}`;
      return;
    }

    let result;
    try {
      result = await response.json();
    } catch (jsonErr) {
      outputArea.value = "Failed to parse server response.";
      return;
    }

    outputArea.value = result.translation || "No translation returned.";

  } catch (error) {
    console.error("Fetch error:", error);
    outputArea.value = "Error occurred during translation.";
  } finally {
    spinner.style.display = "none";
    translateBtn.disabled = false;
    translateBtn.style.opacity = 1;
  }
}

function copyToClipboard() {
  const outputText = document.getElementById("output-text").value;
  navigator.clipboard.writeText(outputText)
    .then(() => alert("Translation copied!"))
    .catch(() => alert("Failed to copy translation."));
}
