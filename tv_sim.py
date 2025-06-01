import time
import json
from controller import Controller
from channel import Channel
from flask_restful import Resource, Api
from flask import Flask


# API resource for viewing current status
class Status(Resource):

    # GET current channel status
    def get(self):
        episode = controller.get_episode()
        channel = controller.get_current_channel()
        ep_time = time.strftime('%H:%M:%S', time.gmtime(int(controller.get_episode_position())))
        ep_dur = time.strftime('%H:%M:%S', time.gmtime(int(controller.get_episode_duration())))
                               
        data = {
            "channel": channel,
            "episode": episode,
            "episode_time": ep_time,
            "episode_duration": ep_dur
        }

        return {'message': 'Success', 'data': data}, 200


# API resource for changing channel state
class Change(Resource):

    # GET current status channel
    def get(self, number):

        controller.change_channel(channel_objects[int(number)])

        return {'message': 'Success', 'data': number}, 200
    

# API resource for providing a channel list
class ChannelList(Resource):

    def __init__(self):
        self.channel_info = {}

        for index, name in enumerate(channel_names):
        
            # Take total time in seconds and convert to 
            total_time = channel_objects[index].formatted_runtime
            episodes = len(channel_objects[index].file_list)
            self.channel_info[index] = {
                                        "name": name,
                                        "episodes": episodes,
                                        "total_time": total_time
                                        }

    # GET current channel list
    def get(self):

        return {'message': 'Success', 'data': self.channel_info}, 200
    

# Main code
if __name__ == '__main__':

    # Initialize a new MPV controller    
    controller = Controller()

    # Load the channels JSON file
    f = open('channels.json',)
    channel_json = json.load(f)
    channel_objects = []
    channel_names = []

    # Initialize each channel in the list
    for channel_data in channel_json['channels']:     
        # Initialize and process channel directories
        channel_objects.append(Channel(channel_data))
        channel_names.append(channel_data['name'])

    # Set global program start time within channels
    starttime = time.monotonic()
    for channel in channel_objects:
        channel.set_start_time(starttime)

    # Default playback to first channel
    controller.change_channel(channel_objects[0])

    # Setup Flask and API resources
    tv_controller = Flask(__name__)
    api = Api(tv_controller)

    api.add_resource(Status, '/api/status')
    api.add_resource(ChannelList, '/api/channel/list')
    api.add_resource(Change, '/api/channel/<string:number>')

    # Start web server for API
    tv_controller.run(host='0.0.0.0', port=8080, debug=False)
