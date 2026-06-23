### How to use

1. **Install the required package**  
   Open a terminal / command prompt and run:
   ```bash
   pip install yt-dlp
   ```

2. **Prepare your text file**  
   Create a `.txt` file with one TikTok video link per line, for example:
   ```
   https://www.tiktok.com/@user/video/123456789
   https://www.tiktok.com/@user/video/987654321
   https://vm.tiktok.com/abc123/
   ```

3. **Run the script**  
   Execute the script and enter the full path to your text file when prompted:
   ```bash
   python downloader.py
   ```
   All videos will be saved inside a newly created `tdownload` folder as `video1.mp4`, `video2.mp4`, etc.

---

### Notes

- The script uses **yt‑dlp**, a robust and up‑to‑date downloader that handles TikTok’s frequent changes.
- If a download fails, the error is printed and the script continues with the next link.
- Make sure your `yt-dlp` is kept up‑to‑date (`pip install -U yt-dlp`) to avoid issues with TikTok’s security measures.


#### Todo

[  ] 1. Add a webpanel
[  ] 2. Add a GIU
[  ] 1. Add a GIU + webpanel
