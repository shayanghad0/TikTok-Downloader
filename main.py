import yt_dlp
import os
import re

def is_profile_url(url):
    """
    Returns the username if the URL is a TikTok profile (e.g. https://www.tiktok.com/@user),
    otherwise returns None.
    """
    pattern = r'https?://(?:www\.)?tiktok\.com/@([A-Za-z0-9_.]+)/?(?:\?.*)?(?:#.*)?$'
    match = re.match(pattern, url.strip())
    return match.group(1) if match else None

def download_single_video(url, filename, folder="tdownload"):
    """Download a single video and save it as 'filename' inside 'folder'."""
    os.makedirs(folder, exist_ok=True)
    ydl_opts = {
        'outtmpl': os.path.join(folder, filename),
        'format': 'mp4/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def main():
    folder = "tdownload"
    file_path = input("Enter the path to your text file: ").strip()

    # Read the text file (one link per line)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            links = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("❌ File not found.")
        return

    if not links:
        print("⚠️ No links found in the file.")
        return

    global_counter = 1   # will name videos video1.mp4, video2.mp4, ...

    for link in links:
        username = is_profile_url(link)

        if username:
            # ---------- Profile link ----------
            print(f"\n📁 Profile detected: @{username}")

            # Ask the user how many videos to download
            while True:
                choice = input("How many videos to download? (all or a number): ").strip().lower()
                if choice == "all":
                    limit = None
                    break
                elif choice.isdigit() and int(choice) > 0:
                    limit = int(choice)
                    break
                else:
                    print("❌ Invalid input. Type 'all' or a positive number.")

            # Fetch video list from the profile (fast, flat extraction)
            print(f"🔍 Fetching video list for @{username}...")
            ydl_opts_flat = {
                'extract_flat': True,
                'quiet': True,
                'no_warnings': True,
            }
            if limit is not None:
                ydl_opts_flat['playlistend'] = limit   # only fetch needed amount

            try:
                with yt_dlp.YoutubeDL(ydl_opts_flat) as ydl:
                    info = ydl.extract_info(link, download=False)
            except Exception as e:
                print(f"❌ Failed to fetch profile: {e}")
                continue

            entries = info.get('entries')
            if not entries:
                print("⚠️ No videos found on this profile (private / empty).")
                continue

            total = len(entries)
            print(f"📥 Downloading {total} video(s)...")

            for entry in entries:
                # Get the direct video URL
                video_url = entry.get('url') or entry.get('webpage_url')
                if not video_url:
                    vid_id = entry.get('id')
                    if vid_id and username:
                        video_url = f"https://www.tiktok.com/@{username}/video/{vid_id}"
                    else:
                        print("⚠️ Skipping entry – no URL / ID available.")
                        continue

                current_name = f"video{global_counter}.mp4"
                global_counter += 1   # reserve the number even if download fails

                try:
                    download_single_video(video_url, current_name, folder)
                    print(f"✅ {current_name} downloaded.")
                except Exception as e:
                    print(f"❌ Failed {current_name}: {e}")

        else:
            # ---------- Single video link ----------
            current_name = f"video{global_counter}.mp4"
            global_counter += 1

            try:
                print(f"⬇️ Downloading {current_name}...")
                download_single_video(link, current_name, folder)
                print(f"✅ {current_name} downloaded.")
            except Exception as e:
                print(f"❌ Failed {current_name}: {e}")

    print(f"\n🎉 All done. Videos are saved in the '{folder}' folder.")

if __name__ == "__main__":
    main()