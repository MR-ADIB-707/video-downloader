import os
from flask import Flask, render_template_string, request, jsonify, send_file
import yt_dlp
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ================= FRONTEND =================
HTML_CODE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Video Downloader</title>

<style>
/* ===== YOUR ORIGINAL DESIGN (UNCHANGED) ===== */
body {
    background-color: #000;
    margin: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-family: 'Arial', sans-serif;
    color: white;
}

.app-card {
    background: #111;
    padding: 40px;
    border-radius: 30px;
    border: 2px solid red;
    text-align: center;
}

input {
    padding: 15px;
    width: 300px;
    border-radius: 10px;
    border: none;
}

button {
    padding: 15px;
    margin-top: 15px;
    background: red;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
}

#progress {
    margin-top: 20px;
}
</style>

</head>
<body>

<div class="app-card">
    <h2>Social Media Video Downloader</h2>

    <input id="url" placeholder="Paste video link">
    <br>
    <button onclick="startDownload()">DOWNLOAD</button>

    <div id="progress"></div>
    <div id="result"></div>
</div>

<script>
async function startDownload() {
    let url = document.getElementById("url").value;

    if(!url){
        alert("Paste link first");
        return;
    }

    document.getElementById("progress").innerHTML = "Processing...";

    let formData = new URLSearchParams();
    formData.append("url", url);

    try {
        let res = await fetch('/download', {
            method: "POST",
            body: formData
        });

        let data = await res.json();

        if(data.success){
            document.getElementById("progress").innerHTML = "Download Ready!";

            document.getElementById("result").innerHTML = `
                <h3>${data.title}</h3>
                <img src="${data.thumbnail}" width="200"><br><br>
                <a href="${data.file}">
                    <button>Download File</button>
                </a>
            `;
        } else {
            alert(data.message);
        }

    } catch(err){
        alert("Server error");
    }
}
</script>

</body>
</html>
"""

# ================= ROUTES =================

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form.get('url')

    if not url:
        return jsonify({"success": False, "message": "No URL provided"})

    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")

        ydl_opts = {
            'format': 'best',
            'outtmpl': file_path,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        return jsonify({
            "success": True,
            "file": f"/get-file/{file_id}",
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail")
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)})

@app.route('/get-file/<file_id>')
def get_file(file_id):
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.mp4")

    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)

    return "File not found"

# ================= RUN =================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)