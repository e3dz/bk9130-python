import sys
import glob
import serial


def serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class BK9130:
    def __init__(self, port_name='/dev/tty.usbserial-14230', baudrate=38400, timeout=1):
        self.port = None
        self.port_name = port_name
        self.baudrate = baudrate
        self.timeout = timeout

        self.channel_set_points_voltage = [0, 0, 0]
        self.channel_set_points_current = [0, 0, 0]

        self.channel_voltage = [0, 0, 0]
        self.channel_current = [0, 0, 0]

        self.channel_protect_voltage = [0, 0, 0]

        self.channel_state = [False, False, False]

    def connect(self):
        if self.port is None:
            self.port = serial.Serial(self.port_name, baudrate=self.baudrate, timeout=self.timeout)
        if not self.port.is_open:
            self.port.open()

    def disconnect(self):
        if self.port and self.port.is_open:
            self.port.close()

    def send_command(self, command, read_response=True):
        self.port.write((command + '\n').encode())
        print(f'Sent command: {command}')
        if read_response:
            response = self.port.read_until(b'\n').decode().strip()
            print(f'Received response: {response}')
            return response
        return None

    def get_status(self):
        return self.send_command('*STB?')

    def reset_device(self):
        self.send_command('*RST', read_response=False)

    def identify_device(self):
        return self.send_command('*IDN?')

    def get_voltage(self):
        response = self.send_command('MEAS:VOLT:ALL?')
        if response:
            voltages = list(map(float, response.split(',')))
            self.channel_voltage = voltages
            return response
        return None

    def get_current(self):
        response = self.send_command('MEAS:CURR:ALL?')
        if response:
            currents = list(map(float, response.split(',')))
            self.channel_current = currents
            return response
        return None
    
    def get_power(self):
        response = self.send_command('MEAS:POW:ALL?')
        if response:
            powers = list(map(float, response.split(',')))
            self.channel_power = powers
            return response
        return None
    
    def get_state(self):
        response = self.send_command('APP:OUT?')
        if response:
            states = list(map(int, response.split(',')))
            self.channel_state = [bool(s) for s in states]
            return response
        return None
    
    def set_protect_voltage(self):
        self.send_command(f'APP:PROT {self.channel_protect_voltage[0]},{self.channel_protect_voltage[1]},{self.channel_protect_voltage[2]}', read_response=False)
    
    def set_voltage(self):
        self.send_command(f'APP:VOLT {self.channel_set_points_voltage[0]},{self.channel_set_points_voltage[1]},{self.channel_set_points_voltage[2]}', read_response=False)

    def set_current(self):
        self.send_command(f'APP:CURR {self.channel_set_points_current[0]},{self.channel_set_points_current[1]},{self.channel_set_points_current[2]}', read_response=False)

    def set_output(self):
        self.send_command(f'APP:OUT {int(self.channel_state[0])},{int(self.channel_state[1])},{int(self.channel_state[2])}', read_response=False)

    
if __name__ == '__main__':

    print(serial_ports())
    
    bk = BK9130(port_name='/dev/tty.usbserial-1320')
    bk.connect()
    bk.identify_device()
    bk.get_status()

    
    bk.channel_set_points_voltage[0] = 1
    bk.channel_set_points_current[0] = 1
    bk.channel_set_points_voltage[1] = 2
    bk.channel_set_points_current[1] = 1
    bk.channel_set_points_voltage[2] = 3
    bk.channel_set_points_current[2] = 1
    bk.set_voltage()
    bk.set_current()
    bk.channel_state[0] = True
    bk.channel_state[1] = True
    bk.channel_state[2] = True
    bk.set_output()


    bk.get_voltage()
    bk.get_current()
    bk.get_state()

    bk.channel_state[0] = False
    bk.channel_state[1] = False
    bk.channel_state[2] = False
    bk.set_output()    

    bk.disconnect()