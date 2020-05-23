from datetime import datetime
from threading import Thread

import cv2
import numpy
import zmq


class PiVideoClient:

    def __init__(self, connect_to='tcp://192.168.1.10:5555', filter="b'\xff\xd8'"):
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.SUB)
        self.zmq_socket.connect(connect_to)
        self.zmq_socket.setsockopt(zmq.SUBSCRIBE, b'\xff\xd8')
        self.running = True
        self.starttime = datetime.now()
        self.totaltime = 0
        self.framecount = 0

    def start(self):
        Thread(target=self.update).start()

    def update(self):
        try:
            while self.running:
                self.stream = self.zmq_socket.recv()
                self.data = numpy.frombuffer(self.stream, dtype=numpy.uint8)
                self.image = cv2.imdecode(self.data, 1)
                cv2.imshow('AdeeptAWR', self.image)
                self.framecount += 1
                print(self.framecount)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except (KeyboardInterrupt, SystemExit):
            pass
        except Exception as ex:
            print('Python error with no Exception handler:')
            print('Traceback error:', ex)
            # traceback.print_exc()
        finally:
            self.stop()
            self.totaltime = datetime.now() - self.starttime
            print('Time: ', self.totaltime.seconds, 'FPS: ', self.framecount / self.totaltime.seconds)

    def stop(self):
        self.running = False
        self.zmq_context.destroy()
        cv2.destroyAllWindows()


def main():
    pvc = PiVideoClient().start()


if __name__ == '__main__':
    main()
