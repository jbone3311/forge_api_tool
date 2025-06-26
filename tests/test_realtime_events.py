import unittest
import socketio
import time

class TestSocketIOEvents(unittest.TestCase):
    def setUp(self):
        self.sio = socketio.Client()
        self.events = []
        self.sio.on('status_update', self.on_status_update)
        self.sio.connect('http://localhost:5000')

    def tearDown(self):
        self.sio.disconnect()

    def on_status_update(self, data):
        self.events.append(data)

    def test_status_update_event(self):
        self.sio.emit('request_status')
        time.sleep(2)
        self.assertTrue(any('api' in e for e in self.events), "No status_update event received")

if __name__ == "__main__":
    unittest.main() 