import os
from random import shuffle
import subprocess
import time


class Channel():

    # Initialize channel class object
    def __init__(self, channel_data):

        # Store channel name and read files
        self.channel_name = channel_data["name"]
        self.file_list = self.absolute_file_paths(channel_data["directory"])
        shuffle(self.file_list)  # Shuffle list to randomize

        # Generate a list of all playlist episode lengths
        self.time_list = []
        for file in self.file_list:
            self.time_list.append(self.get_length(file))

        self.est = self.elapsed_start_times(self.time_list)
        self.total_runtime = sum(self.time_list)
        self.formatted_runtime = self.hms(int(self.total_runtime))

        # Write output playlist file for MPV to read
        self.channel_episode_list = channel_data["directory"]+'.txt'
        with open(self.channel_episode_list, 'w') as f:
            f.write("\n".join(self.file_list))

        print("Scanning", self.channel_name, "- found", len(self.file_list), 
              "episodes, total runtime:", self.formatted_runtime)

    # Use ffprobe to get the run time in seconds of a video file
    def get_length(self, filename):
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                "format=duration", "-of",
                                "default=noprint_wrappers=1:nokey=1", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        return float(result.stdout)
        
    # Format seconds to HH:MM:SS
    def hms(self, s):
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return '{:0>2}:{:0>2}:{:0>2}'.format(h, m, s)
    
    # Set global start time within channel
    def set_start_time(self, starttime):
        self.starttime = starttime

    # Return a list of all files within a directory
    def absolute_file_paths(self, directory):
        path = os.path.abspath(directory)
        file_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list

    # Return a list of the elapsed start times for each episode within a playlist
    def elapsed_start_times(self, time_list):
        elapsed_list = []
        previous_start_time = 0.0

        for index, ep_length in enumerate(time_list):
            elapsed_list.append(previous_start_time)
            previous_start_time = ep_length + elapsed_list[-1]
    
        return elapsed_list
    
    # Compute current time within the playlist
    def playlist_time(self):
        elapsed_time = (time.monotonic() - self.starttime)
        return round(elapsed_time % self.total_runtime, 2)
    
    # Compute current episode and episode seek time within playlist
    def episode_position(self):
        playlist_time = self.playlist_time()

        for index, episode_start_time in enumerate(self.est):
            if playlist_time >= episode_start_time:
                episode = index
                seek_time = round(playlist_time - episode_start_time, 1)

        return episode, seek_time
