# Python තියෙන පුංචි OS එකක් ගන්න
FROM python:3.11-slim

# වැඩ කරන folder එක
WORKDIR /app

# FFmpeg install කරගන්න (MP3 සහ 1080p සදහා අත්‍යවශ්‍යයි)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Files copy කරන්න
COPY . .

# Python libraries install කරන්න
RUN pip install --no-cache-dir -r requirements.txt

# Port 5000 විවෘත කරන්න
EXPOSE 5000

# App එක run කරන්න
CMD ["python", "app.py"]