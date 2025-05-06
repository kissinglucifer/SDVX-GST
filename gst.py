import os
import argparse
import ffmpeg
import music_tag
from pathlib import Path
from xml.etree import ElementTree as ET
from joblib import Parallel, delayed
from pathvalidate import sanitize_filename

parser = argparse.ArgumentParser(prog='gst')
parser.add_argument('-i input_folder', dest='input', help='Path to contents folder. This is the folder containing data\\.', required=True)
parser.add_argument('-o output_folder', dest='output', help='Path to output folder. This is where the GST will be.', required=True)
parser.add_argument('-v game_ver', dest='version', help='Generate GST for only one version. (Default: Generate all versions\' GST)')
parser.add_argument('-d after_date', dest='date', help='Only add songs added past this date as YYYYMMDD.')
parser.add_argument('-vid as_video', dest='vid', help='Save GST as MP4 files for YouTube uploading (0=No, 1=Yes; Default: 0).')
parser.add_argument('-j jobs', dest='jobs', help='Number of jobs active at once (Dependent on CPU cores) (Default: 2)')

args = parser.parse_args()

in_path = Path(args.input)
out_path = Path(args.output)
target_version = args.version
target_date = int(args.date) if args.date else None
as_video = int(args.vid) if args.vid else 0
jobs = int(args.jobs) if args.jobs else 2

# Exclude these IDs (automation paradise)
excluded_ids = ['1259', '1438']

# For shift-jis/cp932, accented letters need to be corrected.
accent_decode = {
    '驩':'Ø',
    '齲':'♥',
    '齶':'♡',
    '趁':'Ǣ',
    '騫':'á',
    '曦':'à',
    '驫':'ā',
    '齷':'é',
    '曩':'è',
    '䧺':'ê',
    '骭':'ü',
    '隍':'Ü',
    '雋':'Ǜ',
    '鬻':'♃',
    '鬥':'Ã',
    '鬆':'Ý',
    '鬮':'¡',
    '龕':'€',
    '蹙':'ℱ',
    '頽':'ä',
    '黻':'*',
    '疉':'Ö',
    '鑒':'₩',
}

# Get version name from number, used for album title
version_decode = {
    '1':'BOOTH',
    '2':'INFINITE INFECTION',
    '3':'GRAVITY WARS',
    '4':'HEAVENLY HAVEN',
    '5':'VIVID WAVE',
    '6':'EXCEED GEAR'
}

# Get the highest difficulty jacket available.
def get_jk(id, filename):
    jk = f'{in_path}/data/music/{id.zfill(4)}_{filename}/jk_{id.zfill(4)}_1_b.png'
    for i in range(2, 6): 
        try:
            open(f'{in_path}/data/music/{id.zfill(4)}_{filename}/jk_{id.zfill(4)}_{i}_b.png')
        except:
            continue
        jk = f'{in_path}/data/music/{id.zfill(4)}_{filename}/jk_{id.zfill(4)}_{i}_b.png'
    return jk

def parse_mdb(musicdb):
    with open(musicdb, 'r', encoding='cp932') as mdb:
        root = ET.fromstring(mdb.read())
    
    music = []
    for song in root.findall('music'):
        id = song.attrib['id']
        if id in excluded_ids:
            continue
        info = song.find('info')
        version = info.find('version').text
        if target_version and version != target_version:  # If getting one version
            continue
        release_date = int(info.find('distribution_date').text)
        if target_date and release_date < target_date: # If getting after date
            continue
        title = info.find('title_name').text
        artist = info.find('artist_name').text
        for text, accent in accent_decode.items():
            title = title.replace(text, accent)
            artist = artist.replace(text, accent)
        filename = info.find('ascii').text
        music.append((id, title, artist, filename, version, release_date))
    return music

def add_song(song):
    (id, title, artist, filename, version, release_date) = song
    sani_title = sanitize_filename(title)
    sani_artist = sanitize_filename(artist)
    folder_name = f'{in_path}/data/music/{id.zfill(4)}_{filename}'
    jacket = get_jk(id, filename)
    s3v_file = f'{folder_name}/{id.zfill(4)}_{filename}.s3v'
    mp3_file = f'{out_path}/{id.zfill(4)}. {sani_artist} - {sani_title}.mp3'
    
    if as_video == 1:
        main = ffmpeg.input(s3v_file)
        cover = ffmpeg.input(jacket)
        (
            ffmpeg
            .output(main, cover, f'{out_path}/{sani_artist} - {sani_title}.mp4', acodec='aac', vcodec='libx264', ab='256k', pix_fmt='yuv420p')
            .run()
        )
        return
    
    # For audio file, also adds metadata
    (
        ffmpeg
        .input(s3v_file)
        .output(mp3_file)
        .run()
    )
    song_file = music_tag.load_file(mp3_file)
    song_file['title'] = title
    song_file['artist'] = artist
    song_file['tracknumber'] = id
    song_file['album'] = f'SOUND VOLTEX {version_decode.get(version)} GST'
    song_file['year'] = f'{release_date}'[:4]
    with open(jacket, 'rb') as jk:
        song_file['artwork'] = jk.read()
    song_file.save()


try:
    os.mkdir(f'{out_path}')
except:
    pass


Parallel(n_jobs=jobs)(delayed(add_song)(song) for song in parse_mdb(f'{in_path}/data/others/music_db.xml'))
