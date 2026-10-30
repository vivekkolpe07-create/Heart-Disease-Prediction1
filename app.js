
const form = document.getElementById("predictionForm");
const resultDiv = document.getElementById("result");
const predictBtn = document.getElementById("predictBtn");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    predictBtn.disabled = true;
    predictBtn.textContent = "Analyzing...";
    resultDiv.style.display = "none";

    try {
        const formData = new FormData(form);

        const patientData = {};

        const fields = [
            "age", "sex", "cp", "trestbps", "chol",
            "fbs", "restecg", "thalach", "exang",
            "oldpeak", "slope", "ca", "thal"
        ];

        fields.forEach(field => {
            patientData[field] = Number(formData.get(field));
        });

        const response = await fetch("http://127.0.0.1:5000/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(patientData)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Prediction failed");
        }

        resultDiv.className = "result success";

        resultDiv.innerHTML = `
            <h3>Prediction Result</h3>
            <p><strong>${data.result}</strong></p>
            <p>Class 0 probability: ${data.probability.class_0}%</p>
            <p>Class 1 probability: ${data.probability.class_1}%</p>
            <p><small>This is an educational ML prediction, not a medical diagnosis.</small></p>
        `;

    } catch (error) {
        resultDiv.className = "result error";
        resultDiv.textContent = "Error: " + error.message;
    }

    resultDiv.style.display = "block";
    predictBtn.disabled = false;
    predictBtn.textContent = "Predict Heart Disease Risk";
});
// Load Model Performance Metrics
async function loadMetrics() {
    try {
        const response = await fetch("/api/metrics");

        if (!response.ok) {
            throw new Error("Unable to load metrics");
        }

        const data = await response.json();

        document.getElementById("accuracy").textContent =
            (data.accuracy * 100).toFixed(2) + "%";

        document.getElementById("precision").textContent =
            (data.precision * 100).toFixed(2) + "%";

        document.getElementById("recall").textContent =
            (data.recall * 100).toFixed(2) + "%";

        document.getElementById("f1").textContent =
            (data.f1_score * 100).toFixed(2) + "%";

    } catch (error) {
        console.error("Metrics loading error:", error);
    }
}

loadMetrics();
const logoutBtn = document.getElementById("logoutBtn");

if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        const response = await fetch("/logout", {
            method: "POST"
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href = data.redirect;
        }
    });
}