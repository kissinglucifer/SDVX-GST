import os
import glob
import argparse
import ffmpeg
import music_tag
from pathlib import Path
from xml.etree import ElementTree as ET
from joblib import Parallel, delayed, wrap_non_picklable_objects
from pathvalidate import sanitize_filename
from tqdm import tqdm

import sdvx


@wrap_non_picklable_objects
def add_song(gst_gen, song, in_path, out_path, args, loglevel):

    try:
        song_id, title, artist, genre_type, game, game_ver, year, song_jackets = gst_gen.get_song_info(song, in_path)
    except(AssertionError):
        return

    sani_title = sanitize_filename(title)
    sani_artist = sanitize_filename(artist)
        
    output_locations = []
    if args.genre:
        for genre in genre_type:
            output_locations.append(f'{out_path}\\{genre}')          
    else:
        output_locations.append(f'{out_path}')

    for triple in song_jackets:
        song_location = triple[0]
        jacket = triple[1]
        diff_abb = triple[2]

        # For audio file, also adds metadata
        for location in output_locations:

            if args.yt:
                main = ffmpeg.input(song_location)
                cover = ffmpeg.input(jacket)
                (
                    ffmpeg
                    .output(main, cover, f'{location}/{sani_artist} - {sani_title}{diff_abb}.mp4', acodec='aac', vcodec='libx264', ab='256k', pix_fmt='yuv420p', loglevel=loglevel)
                    .run(overwrite_output=True)
                )
                return

            mp3_file = f'{location}\\{song_id.zfill(4)}{diff_abb}. {sani_artist} - {sani_title}.mp3'

            (
                ffmpeg
                .input(song_location)
                .output(mp3_file, loglevel=loglevel)
                .run(overwrite_output=True)
            )

            song_file = music_tag.load_file(mp3_file)
            
            song_file['title'] = f"{title}{diff_abb}"
            song_file['artist'] = artist
            song_file['tracknumber'] = song_id
            song_file['album'] = f'{game} {game_ver} GST'
            song_file['year'] = f'{year}'
            song_file['genre'] =  ", ".join(genre_type)
            with open(jacket, 'rb') as jk:
                song_file['artwork'] = jk.read()
            song_file.save()


def generate_parser():

    parser = argparse.ArgumentParser(prog='gst')
    parser.add_argument('-i input_folder', dest='input', help='Path to contents folder. This is the folder containing data\\.', required=True)
    parser.add_argument('-o output_folder', dest='output', help='Path to output folder. This is where the GST will be.', required=True)
    parser.add_argument('-v game_ver', dest='version', type=int, help='Generate GST for only one version. Leave blank to generate full GST.')
    parser.add_argument('-d after_date', dest='after_date', type=int, help='Only add songs added after this date as YYYYMMDD.', default=None)
    parser.add_argument('-b before_date', dest='before_date', type=int, help='Only add songs added before this date as YYYYMMDD.', default=None)
    parser.add_argument('-y', '--youtube', dest='yt', action='store_true', help='Save GST as MP4 files for YouTube uploading.')
    parser.add_argument('-vb', '--verbose', dest='verbose', action='store_true', help='Verbose ffmpeg output. \\Disables progress bar')
    parser.add_argument('-j job', dest='job', type=int, help='Number of jobs active at once (cpu dependent). Defaults to 2.', default=2)
    parser.add_argument('-g', '--genre', dest='genre', action='store_true', help='Sorts songs into genre folders within output folder',)
    return parser


def main():
    parser = generate_parser()
    args = parser.parse_args()

    in_path = Path(args.input)    
    out_path = Path(args.output)
    target_version = args.version
    after_date = args.after_date
    before_date = args.before_date

    mdb_path = f"{in_path}/data/others/music_db.xml"

    if args.verbose:
        loglevel = "info"
    else:
        loglevel = "quiet"

    jobs = args.job



    gst_gen = sdvx.gst_gen()

    try:
        os.mkdir(f'{out_path}')
        if args.genre:
            for genre in gst_gen.genres:
                try:os.mkdir(f'{out_path}\\{genre.name}')
                except:pass
    except:pass




    # Disables progress bar if verbose
    Parallel(n_jobs=jobs)(delayed(add_song)(gst_gen, song, in_path, out_path, args, loglevel) for song in tqdm(gst_gen.parse_mdb(mdb_path, target_version, before_date, after_date), disable=args.verbose))

    print("GST Complete!")

if __name__=="__main__":
    main()