import time
from io import BytesIO
from threading import Thread

import zmq
from picamera import PiCamera


class PiVideoStream:
    def __init__(self, connect_to='tcp://*:5555', resolution=(1280, 720), framerate=49):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PUB)
        self.zmq_socket.bind(connect_to)

        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.start_preview()
        time.sleep(2)

        self.stream = BytesIO()

    def start(self):
        Thread(target=self.update).start()
        return self

    def update(self):
        self.camera.start_recording(self, format='mjpeg')

    def write(self, buf):
        if buf.startswith(b'\xff\xd8') and self.stream.tell() > 0:
            self.stream.seek(0)
            self.zmq_socket.send_string('pvs')
            self.zmq_socket.send_pyobj(self.stream.read(), flags=0, copy=True, track=False)
            self.stream.seek(0)
            self.stream.truncate()
        self.stream.write(buf)

    def stop(self):
        self.camera.stop_recording()
        self.camera.close()
        self.stream.close()
        self.zmq_socket.close()


def main():
    try:
        pvs = PiVideoStream().start()
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        pass  # Ctrl-C was pressed to end program
    except Exception as ex:
        print('Python error with no Exception handler:')
        print('Traceback error:', ex)
        # traceback.print_exc()
    finally:
        pvs.stop()


if __name__ == '__main__':
    main()
