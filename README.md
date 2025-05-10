# SDVX GST Generator
Script that takes contents path and creates tagged songs or videos in output folder.
Requires ffmpeg to be installed and added to PATH.
```
python gst.py -i -o [-v] [-d] [=b] [-yt] [-j] [-vb]
```

## Arguments
**-i: Input folder** (REQUIRED) Path to your contents folder. (Ex. ./KFC/contents)

**-o: Output folder** (REQUIRED) Path to your GST folder. (Ex. ./SDVX_GST/)

**-v: Version** Game version as an integer (Ex. 6 to generate only the Exceed Gear GST)

**-d: After Date** Only get songs added after this date as YYYYMMDD. (Ex. 20240101 for songs added since 2024)

**-b: Before Date** Only get songs added before this date as YYYYMMDD. (Ex. 20240101 for songs added before 2024)

**-yt: Video** Create GST as .mp4 video files instead of audio files, similarly to how they're uploaded on YouTube. Automatically uses the song jacket as the video. (Defaults false)

**-vb: Verbose** Verbose ffmpeg output. Disables progress bar. (Defaults false)

**-j: Jobs** Number of jobs. Dependent on CPU core count. (Defaults to 2)
