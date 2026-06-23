💡 Tip
This is private code for my YouTube channel.
I earn money from TikTok content, but you can still use it.

### How to use

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TikTok-Downloader
   cd TikTok-Downloader
   ```

2. **Install the required library**
   ```bash
   pip install yt-dlp
   ```

3. **Prepare your text file** (e.g., `links.txt`)  
   You can mix single video URLs and profile URLs (one per line):
   ```
   https://www.tiktok.com/@dramaticdogs22
   https://www.tiktok.com/@dramaticdogs22/video/123456789
   https://vm.tiktok.com/abc123/
   ```

4. **Run the script**
   ```bash
   python main.py
   ```
   When prompted, enter the path to your text file.

All videos will be saved in the `tdownload/` folder, numbered consecutively as `video1.mp4`, `video2.mp4`, etc., in the order they are processed.  
For profile links, the script asks how many videos to download (`all` or a number) and downloads the most recent ones.

---

### Notes

- Keep `yt-dlp` up to date (`pip install -U yt-dlp`) to handle TikTok’s frequent changes.
- If a video fails to download (private/deleted), it is **skipped automatically** and the script continues with the next link.
- The numbering is global across all links – profile videos are numbered after the previously downloaded single videos.

#### Todo

- [ ] 1. Add a webpanel
- [ ] 2. Add a GUI
- [ ] 3. Add a GUI + webpanel
- [ ] 4. Add a Telegram Bot
- [ ] Add a Node.js version
- [ ] Add a Go version
- [x] Add a Profile Downloader
