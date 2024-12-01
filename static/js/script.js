document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) {
        alert("Выберите файл перед загрузкой.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const loadingContainer = document.getElementById("loading-container");
    const resultSection = document.getElementById("result");
    const downloadLink = document.getElementById("downloadLink");

    // Сбрасываем интерфейс
    loadingContainer.style.display = "block";
    resultSection.style.display = "none";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });
        const data = await response.json();

        if (data.status === "success") {
            loadingContainer.style.display = "none";
            downloadLink.href = `/download/${data.filename}`;
            resultSection.style.display = "block";
        } else {
            alert(`Ошибка: ${data.message}`);
            loadingContainer.style.display = "none";
        }
    } catch (error) {
        console.error("Ошибка загрузки файла:", error);
        alert("Произошла ошибка при обработке файла.");
        loadingContainer.style.display = "none";
    }
});
