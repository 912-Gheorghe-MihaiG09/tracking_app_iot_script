import pygame
import requests
import time
import threading
import websocket


class LocationSender:
    def __init__(self, api_url, websocket_url):
        self.api_url = api_url
        self.websocket_url = websocket_url
        self.ws = None
        self.stop_event = threading.Event()
        self.serial_number = "TD1-0000000-00000"
        pygame.mixer.init()
        pygame.mixer.music.load('sound.mp3')

    def get_current_location(self):
        try:
            # Send a request to the ipapi.co API to get location data
            response = requests.get('https://ipapi.co/json/')
            data = response.json()

            # Extract location information
            latitude = data.get('latitude')
            longitude = data.get('longitude')

            if latitude is not None and longitude is not None:
                return {
                    'latitude': latitude,
                    'longitude': longitude,
                    "deviceSerialNumber": self.serial_number,
                }
            else:
                print("Failed to get location data")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def send_location(self):
        while not self.stop_event.is_set():
            location = self.get_current_location()
            if location:
                try:
                    response = requests.post(self.api_url, json=location)
                    if response.status_code == 200:
                        print("Location sent successfully")
                    else:
                        print(f"Failed to send location. Status code: {response.status_code}")
                except Exception as e:
                    print(f"Error sending location: {e}")
            self.stop_event.wait(120)  # Wait for 5 minutes

    def on_message(self, ws, message):
        if message == f"ping: {self.serial_number}":
            pygame.mixer.music.play()

            time.sleep(10)

            pygame.mixer.music.stop()

    def start_websocket(self):
        self.ws = websocket.WebSocketApp(
            self.websocket_url,
            on_message=self.on_message,
        )
        self.ws.run_forever()

    def run(self):
        # Start the location sending thread
        location_thread = threading.Thread(target=self.send_location)
        location_thread.start()

        # Start the WebSocket listening
        self.start_websocket()

    def stop(self):
        self.stop_event.set()
        if self.ws:
            self.ws.close()


if __name__ == '__main__':
    time.sleep(60)

    api_url = 'http://34.159.189.145:8080/api/iot'  # Replace with your actual endpoint URL
    websocket_url = 'ws://34.159.189.145:8080/websocketPath'  # Replace with your WebSocket URL

    location_sender = LocationSender(api_url, websocket_url)
    location_sender.run()
