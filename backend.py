import yt_dlp
import os
import uuid
import glob

DOWNLOAD_FOLDER = "downloads"

def format_size(bytes_size):
    """Bytes ප්‍රමාණය MB වලට හරවන function එක"""
    if bytes_size is None:
        return "Unknown Size"
    mb_size = bytes_size / (1024 * 1024)
    return f"{mb_size:.1f} MB"

def get_video_data(video_url):
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # 1. Video Formats පෙරීම (Filter)
            formats = info.get('formats', [])
            available_qualities = {}

            for f in formats:
                # Video එකක්ද බලන්න (Audio නැති ඒවා වුනාට කමක් නෑ, අපි merge කරන නිසා)
                if f.get('vcodec') != 'none':
                    height = f.get('height')
                    if height:
                        # Size එක සොයාගැනීම (Filesize හෝ Approximate Size)
                        f_size = f.get('filesize') or f.get('filesize_approx')
                        
                        # දැනටමත් මේ Quality එක ලිස්ට් එකේ තියෙනවද? 
                        # තියෙනවා නම් සහ අලුත් එකේ size එක ලොකු නම් (Best bitrate), ඒක ගන්නවා.
                        if height not in available_qualities or (f_size and f_size > available_qualities[height]['raw_size']):
                            available_qualities[height] = {
                                'resolution': f"{height}p",
                                'size': format_size(f_size),
                                'raw_size': f_size if f_size else 0,
                                'value': str(height)
                            }

            # Dictionary එක List එකක් බවට හරවමු (Sort කරලා: ලොකු එක උඩට)
            sorted_qualities = sorted(available_qualities.values(), key=lambda x: int(x['value']), reverse=True)
            
            # Best quality එක උඩටම දාන්න option එකක්
            if sorted_qualities:
                sorted_qualities.insert(0, {'resolution': f"Best Available ({sorted_qualities[0]['size']})", 'value': 'best'})

            return {
                "title": info.get('title', 'Unknown'),
                "thumbnail": info.get('thumbnail', ''),
                "duration": info.get('duration_string', 'Unknown'),
                "webpage_url": info.get('webpage_url', video_url),
                "qualities": sorted_qualities, # <--- මේක තමයි අලුත් කොටස
                "status": "success"
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def download_media(video_url, format_type='mp4', quality='best'):
    try:
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)

        unique_id = str(uuid.uuid4())[:8]
        output_template = f'{DOWNLOAD_FOLDER}/%(title)s_{unique_id}.%(ext)s'

        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'restrictfilenames': True,
            'socket_timeout': 30, # Timeout to prevent hanging
        }

        if format_type == 'mp3':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            if quality == 'best':
                format_str = 'bestvideo+bestaudio/best'
            else:
                format_str = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best'
            
            ydl_opts.update({
                'format': format_str,
                'merge_output_format': 'mp4',
                'postprocessor_args': {'merger': ['-c:v', 'copy', '-c:a', 'aac']}, # Fix: Force AAC audio for compatibility
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
            except Exception as dl_error:
                return {"status": "error", "message": f"Download failed: {str(dl_error)}"}

            if format_type == 'mp3':
                pre, _ = os.path.splitext(filename)
                final_filename = pre + ".mp3"
            else:
                pre, _ = os.path.splitext(filename)
                final_filename = pre + ".mp4"

            if not os.path.exists(final_filename):
                if os.path.exists(filename):
                     final_filename = filename
            
            if not os.path.exists(final_filename):
                 return {"status": "error", "message": "File processing failed."}

            return {"status": "success", "file_path": final_filename}

    except Exception as e:
        return {"status": "error", "message": str(e)}