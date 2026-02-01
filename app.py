from flask import Flask, render_template, request
import yt_dlp

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    if request.method == 'POST':
        url = request.form.get('url')
        try:
            ydl_opts = {'format': 'best', 'outtmpl': 'downloads/%(title)s.%(ext)s'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            message = "Video eka 'downloads' folder ekata download wuna!"
        except Exception as e:
            message = f"Awulak giya: {e}"
            
    return render_template('index.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)