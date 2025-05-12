import glob
from pathlib import Path
from xml.etree import ElementTree as ET
from enum import Enum, EnumMeta

from gstmeta import gst_genMeta

class gst_gen(gst_genMeta):
    
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
        '盥':'⚙︎',
    }

    # Get version name from number, used for album title
    version_decode = {
        "1":'BOOTH',
        "2":'INFINITE INFECTION',
        "3":'GRAVITY WARS',
        "4":'HEAVENLY HAVEN',
        "5":'VIVID WAVE',
        "6":'EXCEED GEAR'
    }

    diff_decode = {
        "m": 'MXM',
        "n": 'NOV',
        "a": 'ADV',
        "e": 'EXH'
    }

    inf_decode = {
        "2": "INF",
        "3": "GRV",
        "4": "HVN",
        "5": "VVD",
        "6": "XCD"
    }


    #code from Tina-otoge
    class Genres(Enum):
        OTHER = 0
        EXIT_TUNES = 1
        FLOOR = 2
        TOUHOU = 4
        VOCALOID = 8
        BEMANI = 16
        ORIGINAL = 32
        POP_ANIME = 64
        HINABITA = 128

    # Get the highest difficulty jacket and song available if only one option is available.
    def get_song_info(self,song, in_path):

        (song_id, title, artist, filename, version, inf_ver, release_date, genre_type) = song

        folder_name = f'{in_path}/data/music/{song_id.zfill(4)}_{filename}'

        jk_pattern = f'{folder_name}/jk_{song_id.zfill(4)}_?_b.png'
        s3v_pattern = f'{folder_name}/*.s3v'
        jackets = glob.glob(jk_pattern)
        songs = glob.glob(s3v_pattern)
        
        assert len(jackets) >0 and len(songs) > 0, f"Jackets and Songs must be nonempty. {song_id} has an issue."
        song_jackets = []
        for song in songs:
            if "_pre" in song or "_fx" in song:
                continue
            try:
                # Verify s3v is dependent on difficulty
                diff = int(song[-6])
                    

                diff_abb = self.diff_decode.get(song[-5])
                if not diff_abb:
                    diff_abb = self.inf_decode.get(inf_ver)

                    
                try:
                    open(f'{folder_name}/jk_{song_id.zfill(4)}_{diff}_b.png')
                    song_jackets.append([song, f'{folder_name}/jk_{song_id.zfill(4)}_{diff}_b.png', f" {diff_abb}"])
                except:
                    song_jackets.append([song, jackets[-1], f" {diff_abb}"])

            except: #throws only if s3v is not of the form ..._{int}{diff}.s3v. Uses highest diff jacket.
                song_jackets.append([song, jackets[-1], ''])

        return song_id, title, artist, genre_type, "SOUND VOLTEX", self.version_decode[version], f'{release_date}'[:4], song_jackets

    def parse_mdb(self,musicdb, target_version, before_date, after_date):
        with open(musicdb, 'r', encoding='cp932') as mdb:
            root = ET.fromstring(mdb.read())
        
        music = []
        for song in root.findall('music'):
            song_id = song.attrib['id']
            if song_id in self.excluded_ids:
                continue
            info = song.find('info')
            version = info.find('version').text
            # TODO: ensure that infinites added to new versions with NEW songs are included here
            if target_version and version != target_version:  # If getting one version
                continue
            release_date = int(info.find('distribution_date').text)
            
            if before_date != None:
                if release_date > before_date: 
                    continue
            if after_date != None:
                if release_date < after_date:
                    continue
            title = info.find('title_name').text
            artist = info.find('artist_name').text
            for text, accent in self.accent_decode.items():
                title = title.replace(text, accent)
                artist = artist.replace(text, accent)
            filename = info.find('ascii').text
            inf_version = info.find('inf_ver').text # Get infinite version
            
            genre_value = int(info.find('genre').text)  # Get genre value
            genre_type = []
            
            for genre in self.Genres:
                if genre.value & genre_value: 
                    genre_type.append(genre.name) 
                    
            if genre_value == 0:
                genre_type.append('OTHER')

            music.append((song_id, title, artist, filename, version, inf_version, release_date, genre_type))
        return music

    @property
    def genres(self):
        return self.Genres


