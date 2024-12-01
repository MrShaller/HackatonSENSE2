document.getElementById("uploadForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById("fileInput");
    formData.append("file", fileInput.files[0]);

    const progressBarContainer = document.getElementById("progress-bar-container");
    const progressBar = document.getElementById("progress-bar");
    const resultDiv = document.getElementById("result");
    const downloadSection = document.getElementById("download-section");
    const downloadButton = document.getElementById("download-button");

    // Сбрасываем предыдущие результаты и показываем прогресс-бар
    resultDiv.innerHTML = "";
    progressBar.style.width = "0%";
    progressBarContainer.style.display = "block";
    downloadSection.style.display = "none";

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData,
        });

        // Обновляем прогресс-бар до 100% после завершения
        progressBar.style.width = "100%";

        const data = await response.json();

        if (data.status === "success") {
            resultDiv.innerHTML = "";
            downloadSection.style.display = "block";
            downloadButton.href = `/uploads/${data.filename}`; // Ссылка на скачивание файла
        } else {
            resultDiv.innerHTML = `<p>Ошибка: ${data.message}</p>`;
        }
    } catch (error) {
        console.error("Ошибка загрузки файла:", error);
        resultDiv.innerHTML = `<p>Ошибка: ${error.message}</p>`;
    } finally {
        // Убираем прогресс-бар через 2 секунды
        setTimeout(() => {
            progressBarContainer.style.display = "none";
        }, 2000);
    }
});
