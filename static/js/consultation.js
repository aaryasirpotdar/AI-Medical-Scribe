// ==========================
// Categories
// ==========================

const categories = [
    "Symptoms",
    "Duration",
    "Allergies",
    "Medical History",
    "Examination",
    "Diagnosis",
    "Medicines",
    "Tests"
];

// ==========================
// Global Variables
// ==========================

let consultationEntries = [];

let mediaRecorder = null;
let audioChunks = [];
let currentCategory = "";
let currentButton = null;

// ==========================
// Create Category Cards
// ==========================

const container = document.getElementById("categoryContainer");

categories.forEach(category => {

    const card = document.createElement("div");

    card.className = "category-card";

    card.innerHTML = `
        <div class="category-header">

            <h2>${category}</h2>

        <button class="recordBtn" data-recording="false">
            🎤 Record
        </button>

        <input
            type="file"
            class="uploadInput"
            accept="audio/*"
            style="display:none;">

        <button class="uploadBtn">
            📁 Upload
        </button>
        </div>

        <div
            class="entry-list"
            id="${category.replace(/\s/g,'')}">

        </div>
    `;

    container.appendChild(card);

});

// ==========================
// Record Button Events
// ==========================

document.querySelectorAll(".recordBtn").forEach(button => {

    button.addEventListener("click", async function () {

        currentButton = this;

        const card = this.closest(".category-card");

        currentCategory =
            card.querySelector("h2").innerText;

        // START RECORDING
        if (this.dataset.recording === "false") {

            try {

                const stream =
                    await navigator.mediaDevices.getUserMedia({
                        audio: true
                    });

                mediaRecorder =
                    new MediaRecorder(stream);

                audioChunks = [];

                mediaRecorder.ondataavailable = (event) => {

                    audioChunks.push(event.data);

                };

                mediaRecorder.onstop = uploadAudio;

                mediaRecorder.start();

                this.innerText = "⏹ Stop";

                this.dataset.recording = "true";

            }

            catch (err) {

                alert("Microphone permission denied!");

                console.error(err);

            }

        }

        // STOP RECORDING
        else {

            mediaRecorder.stop();

            this.innerText = "🎤 Record";

            this.dataset.recording = "false";

        }

    });

});

// ==========================
// Upload Recording
// ==========================

async function uploadAudio() {

    const blob = new Blob(audioChunks, {

        type: "audio/webm"

    });

    const formData = new FormData();

    formData.append(

        "audio",

        blob,

        "recording.webm"

    );

    formData.append(

        "category",

        currentCategory

    );

    try {

        const response = await fetch("/record", {

            method: "POST",

            body: formData

        });

        const data = await response.json();

        consultationEntries.push({

            category: data.category,

            text: data.transcript

        });

        displayEntry(

            data.category,

            data.transcript

        );

    }

    catch (err) {

        console.error(err);

        alert("Upload Failed");

    }

}

// ==========================
// Show Transcript
// ==========================

function displayEntry(category, text) {

    const id =
        category.replace(/\s/g,'');

    const div =
        document.getElementById(id);

    const p =
        document.createElement("p");

    p.className = "entry";

    p.innerHTML = "• " + text;

    div.appendChild(p);

}

// ==========================
// Generate Report
// ==========================

document
.getElementById("generateBtn")
.addEventListener("click", async () => {

    const consultation = {

        name:
        document.getElementById("patientName").value,

        age:
        document.getElementById("patientAge").value,

        gender:
        document.getElementById("patientGender").value,

        entries:
        consultationEntries

    };

    const response =
        await fetch("/generate", {

            method: "POST",

            headers: {

                "Content-Type":
                "application/json"

            },

            body:
            JSON.stringify(consultation)

        });

    const html =
        await response.text();

    document.open();

    document.write(html);

    document.close();

});