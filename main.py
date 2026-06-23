import yt_dlp
import os

def download_tiktok_videos(file_path):
    """Reads a text file with TikTok links and downloads each video."""
    folder = "tdownload"
    os.makedirs(folder, exist_ok=True)   # create folder if it doesn't exist

    # Read links from the file, skipping empty lines
    with open(file_path, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        print("No links found in the file.")
        return

    for i, link in enumerate(links, start=1):
        output_path = os.path.join(folder, f"video{i}.mp4")
        ydl_opts = {
            "outtmpl": output_path,          # exact filename (no extra numbering)
            "format": "mp4/best",            # prefer mp4, fallback to best available
            "quiet": True,                   # suppress verbose logs
            "no_warnings": True,
            "noplaylist": True,              # only download the single video
            "merge_output_format": "mp4",    # ensure final container is .mp4
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            print(f"✅ Downloaded: video{i}.mp4")
        except Exception as e:
            print(f"❌ Failed to download {link}: {e}")

if __name__ == "__main__":
    file_path = input("Enter the path to your text file: ").strip()
    download_tiktok_videos(file_path)