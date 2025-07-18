from flask import Flask, request, send_file, render_template
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        format_type = request.form.get("format", "mp4")
        quality = request.form.get("quality", "best")

        if format_type == "mp3":
            ydl_format = "bestaudio/best"
        else:
            if quality == "best":
                ydl_format = "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b"
            else:
                ydl_format = f"bv*[height<={quality}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b"

        ydl_opts = {
            'format': ydl_format,
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
        }

        if format_type == "mp3":
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                if format_type == "mp3":
                    filename = filename.rsplit('.', 1)[0] + '.mp3'

                if filename.endswith(".mkv") and format_type == "mp4":
                    new_filename = filename.replace(".mkv", ".mp4")
                    os.rename(filename, new_filename)
                    filename = new_filename

                return send_file(filename, as_attachment=True)
        except Exception as e:
            return f"Error: {str(e)}"

    return render_template("index.html")

# 🔧 여기 수정
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ← Render 대응
    app.run(host="0.0.0.0", port=port)
