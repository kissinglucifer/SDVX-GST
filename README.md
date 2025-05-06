# SDVX GST Generator
Script that takes contents path and creates tagged songs or videos in output folder.
Requires ffmpeg to be installed and added to PATH.
```
python gst.py -i -o [-v] [-d] [-vid] [-j]
```

## Arguments
**-i: Input folder** (REQUIRED) Path to your contents folder. (Ex. ./KFC/contents)

**-o: Output folder** (REQUIRED) Path to your GST folder. (Ex. ./SDVX_GST/)

**-v: Version** Game version as an integer (Ex. 6 to generate only the Exceed Gear GST)

**-d: Date** Only get songs added after this date as YYYYMMDD. (Ex. 20240101 for songs added since 2024)

**-v: Video** Create GST as .mp4 video files instead of audio files. Automatically uses the song jacket as the video. (0= false, 1= true; defaults to false)

**-j: Jobs** Number of jobs. Dependent on CPU core count. (Defaults to 2)