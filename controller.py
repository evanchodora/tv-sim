from python_mpv_jsonipc import MPV


class Controller():
    def __init__(self):
        self.socket = "/tmp/mpvsocket"
        self.mpv = MPV(
            start_mpv=True,
            ipc_socket=self.socket,
            fs=True,
            idle="yes",
            force_window=True,
            loop_playlist="inf",
            audio_device="alsa/hdmi:CARD=HDMI",
            osc="no",
            sid="no"
        )

        self.current_channel = ""
        self.current_episode = ""
        
    # Function to have the controller change to specified channel
    def change_channel(self, channel):
        episode, seek_time = channel.episode_position()
        playlist = channel.channel_episode_list

        self.mpv.loadlist(playlist)
        self.mpv.playlist_play_index(episode)
        self.mpv.wait_for_property("duration")  # Wait for file to load before seeking
        self.mpv.seek(seek_time, "absolute")

        self.current_channel = channel.channel_name
        self.mpv.show_text(self.current_channel, "5000") # Display current channel on-screen
        self.current_episode = channel.file_list[episode]

    # Function to retrieve the currently playing channel name
    def get_current_channel(self):
        return self.current_channel
    
    # Function to get the currently playing episode
    def get_episode(self):
        return self.mpv.command("get_property", "filename")
    
    # Function to get the time within the currently playing episode
    def get_episode_position(self):
        return self.mpv.command("get_property", "time-pos")
    
    # Function to get the duration of the currently playing episode
    def get_episode_duration(self):
        return self.mpv.command("get_property", "duration")
