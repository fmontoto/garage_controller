import logging
import serial
import sys
import threading

from flask import Flask


app = Flask(__name__)

door_interface = None
dev_path = '/dev/ttyUSB1'

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("server")


class DoorInterface():
    IS_ALIVE = b'AL'
    IS_DOOR_OPEN = b'IO'
    OPEN_DOOR = b'OD'
    CLOSE_DOOR = b'CD'

    def __init__(self, serial_port=dev_path):
        self._serial = self._StartSerial(serial_port)
        self.lock = threading.Lock()
        #TODO(fmontoto): Be smarter to wait for the connection to be ready.
        from time import sleep
        sleep(2)
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()
        if not self.IsAlive():
            raise Exception("Arduino is not alive :(")

    def IsAlive(self):
        with self.lock:
            self._serial.write(self.IS_ALIVE)
            bytes_got = self._serial.read(3)
            logging.debug(bytes_got)
            return bytes_got == b'YES'

    def IsDoorOpen(self):
        with self.lock:
            self._serial.write(self.IS_DOOR_OPEN)
            bytes_got = self._serial.read(3)
            logging.debug(bytes_got)
            return bytes_got == b'YES'

    def OpenDoor(self):
        with self.lock:
            self._serial.write(self.OPEN_DOOR)
            bytes_got = self._serial.read(3)
            logging.debug(bytes_got)
            return bytes_got == b'YES'

    def CloseDoor(self):
        with self.lock:
            self._serial.write(self.CLOSE_DOOR)
            bytes_got = self._serial.read(3)
            logging.debug(bytes_got)
            return bytes_got == b'YES'

    @staticmethod
    def _StartSerial(port=dev_path, baud_rate=9600, timeout_sec=10):
        return serial.Serial(
                port = port,
                baudrate=baud_rate,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=timeout_sec
        )


@app.route('/door/open', methods=['POST'])
def door_open_handler():
    if door_interface.OpenDoor():
        return 'Door opened!'
    else:
        return 'Door not opened, maybe already opened?'


@app.route('/door/close', methods=['POST'])
def door_close_handler():
    if door_interface.CloseDoor():
        return 'Door closed!'
    else:
        return 'Door not closed, maybe was already closed?'


@app.route('/door/status')
def door_status_handler():
    if door_interface.IsDoorOpen():
        return "Door is open!"
    else:
        return "Door is closed!"


@app.route('/')
def index_handler():
    ret = ''
    if door_interface.IsDoorOpen():
        ret += 'Door is open!'
    else:
        ret += 'Door is closed!'

    ret +=  '''
            <form action="door/open" method="post">
                <button name="open_door" value="">Open the Door!</button>
            </form>
            <form action="door/close" method="post">
                <button name="close_door" value="">Close the Door!</button>
            </form>
    '''
    return ret


def main():
    if len(sys.argv) < 3:
        sys.exit('Usage: %s http-port arduino-dev' % sys.argv[0])
    global door_interface
    door_interface = DoorInterface(sys.argv[2])
    app.run(host='0.0.0.0', port=int(sys.argv[1]))


if __name__ == '__main__':
    main()
