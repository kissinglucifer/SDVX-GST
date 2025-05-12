from abc import ABC, abstractmethod

class gst_genMeta(ABC):

    @abstractmethod
    def parse_mdb(self, mdb, target_version, before_date, after_date):
        """From a provided music database, target version (in plaintext), and a range of dates [after_date,before_date], generate song information.
        
        Inputs:
        mdb - music database file location containing relevant song information.
        target_version - game version as a string that is intended to be generated from. I.E. "Gravity Wars" should be chosen when wanting to select Sound Voltex III: Gravity Wars.
        before_date - date in the form YYYYMMDD, expected to be None if no cutoff is desired.
        after_date - date in the form YYYYMMDD, expected to be None if no cutoff is desired.
        
        Returns:
        Array of tuples containing parsed information from the database file, including but not limited nor restricted to:
            song_id - Unique ID connected to the song.
            title - Title of the song as a string. 
            artist - Song artist as a string.
            filename - Location of the directory containing the song information.
            version - Version that the song (or difficulty) debuted in.
            release_date - Year song was released.
            genre_type - Array of genres that are connected to the song (must be nonempty).
        """
        pass


    @abstractmethod
    def get_song_info(self, song, in_path):
        """From a provided song (parsed by parse_mdb) and the location of the directory that contains ../data, produces all relevant song information for the soundtrack generation process.
        
        Inputs:
        song - tuple of song information matching the output of each individual member of parse_mdb.
        in_path - home directory that contains the ../data directory where song locations will be found.
        
        Returns tuple containing exactly the following
            song_id - Unique ID connected to the song.
            title - Title of the song as a string. 
            artist - Song artist as a string.
            genre_type - Array of genres that are connected to the song (must be nonempty).
            game - Game where the soundtrack is being taken from. I.E. "Sound Voltex" should be chosen when wanting to select Sound Voltex III Gravity Wars.
            version - Version that the song (or difficulty) debuted in. I.E. "Gravity Wars" should be chosen when wanting to select Sound Voltex III Gravity Wars.
            year - Year song was released in game.
            songs - array of tuples song_jackets with song_jackets[0] = {location of song}, song_jackets[1] = {location of jacket}, and song_jackets[3] = {difficulty associated with track}. Difficulties should either be of the form "" or " {diff}". I.e. Evans in Sound Voltex and BeatMania iiDX has one track for the lower difficulties and one track for the highest difficulty. The expected output, in sdvx for example, is [({s3v location for Evans NOV-EXH}, {png location for Evans jacket}, {""}), ({s3v location for Evans MXM}, {png location for Evans}, {" MXM"})]

        """
        pass

    @property
    @abstractmethod
    def genres(self):
        """ 
        Enum or Dictionary of genres so that for each entry, genre.name is the name of the genre as a string.
        """
        pass