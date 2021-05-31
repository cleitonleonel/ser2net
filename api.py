#!/usr/bin/python3
# -*- encoding: utf-8 -*-
#
import logging
import os
import platform
import socket
import threading
import time
from sys import platform as sys_platform

import nmap
import serial
import serial.tools.list_ports as ls

logg = logging
log = logging.getLogger('ser2net')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
log.addHandler(ch)

WEIGHT = False
LIST_PORTS = []


def test_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip, port))
    if result == 0:
        return True

    return False


def get_platform():
    if sys_platform in ('win32', 'cygwin'):
        return 'Windows'
    elif sys_platform == 'darwin':
        return 'Macosx'
    elif sys_platform.startswith('linux'):
        if platform.node() == 'raspberrypi':
            return 'Raspberrypi'
        return 'Linux'
    elif sys_platform.startswith('freebsd'):
        return 'Linux'
    return 'Unknown'


class Redirector(object):
    def __init__(self, serial_port, sock):
        self.serial = serial_port
        self.socket = sock
        self.alive = False
        self.thread_read = None

    def shortcut(self):
        """connect the serial port to the tcp port by copying everything
           from one side to the other"""
        self.alive = True
        self.thread_read = threading.Thread(target=self.reader)
        self.thread_read.setDaemon(False)
        self.thread_read.start()
        self.writer()

    def reader(self):
        """loop forever and copy serial->socket"""
        while self.alive:
            try:
                data = self.serial.read(1)
                n = self.serial.inWaiting()
                if n:
                    data = data + self.serial.read(n)
                if data:
                    self.socket.sendall(data)
            except socket.error as message:
                log.info(message)
                break
        self.alive = False

    def writer(self):
        """loop forever and copy socket->serial"""
        while self.alive:
            try:
                data = self.socket.recv(1024)
                if not data:
                    break
                if self.serial.write(data) > 0:
                    break
                # self.serial.write(data)
            except socket.error as message:
                log.info(message)
                break
            except Exception as err:
                log.warning(err)
                break

        self.alive = False
        self.thread_read.join()

    def stop(self):
        """Stop copying"""
        if self.alive:
            self.alive = False
            self.thread_read.join()


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.ser = None
        self.host = None
        self.port = None
        self._kill = False

    def run(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.settimeout(5)
        srv.listen(1)

        while True:

            if self._kill:
                log.info('Closing Server...')
                srv.close()
                break

            connection = ''
            try:
                log.info("Waiting for connection...")
                connection, addr = srv.accept()
                address, port = addr
                log.info('Connecting with tcp://{0}:{1}'.format(address, port))
                if address:
                    r = Redirector(self.ser, connection)
                    r.shortcut()
            except socket.error as msg:
                log.info(msg)
            finally:
                try:
                    connection.close()
                    log.info('Disconnecting')
                except NameError:
                    pass
                except Exception as e:
                    log.warning(repr(e))

    def kill(self):
        self._kill = True


def config(**kwargs):
    global WEIGHT

    if get_platform() in ['Linux', 'Raspberrypi']:
        os.system('sudo chmod 777 /dev/tty*')

    ser = serial.Serial()

    ser.port = kwargs['serial']
    ser.baudrate = kwargs['baudrate']
    ser.rtscts = kwargs['rtscts']
    ser.xonxoff = kwargs['xonxoff']
    ser.timeout = kwargs['timeout'] or 1

    try:
        ser.open()
    except serial.SerialException as e:
        log.fatal("Could not open serial port %s: %s" % (ser.portstr, e))
        result_dict = {
            "result": False,
            "message": "Não foi possível abrir a porta serial"
        }

        return result_dict

    if kwargs['server']:

        if get_platform() in ['Linux', 'Raspberrypi']:
            os.system('sudo lsof -t -i tcp:3333 | sudo xargs kill -9 2> /dev/null')

        host = '0.0.0.0'
        port = 3333

        log.info("TCP/IP to Serial redirector (Ctrl-C to quit)")

        thread_main = ServerThread()
        thread_main.ser = ser
        thread_main.host = host
        thread_main.port = port
        thread_main.start()

        return thread_main

    else:
        ser.write(chr(5).encode())

        try:
            data = ser.readline()
        except:
            result_dict = {
                "result": False,
                "message": "Dispositivo desconectado ou acesso múltiplo na porta."
            }
            return result_dict

        if len(data) == 7:
            line = data[1:6].decode()

            if line.isdigit():
                WEIGHT = int(line)

        if WEIGHT > 0:
            result_dict = {
                "result": True,
                "message": WEIGHT / 1000
            }
        else:
            result_dict = {
                "result": False,
                "message": "Não foi possível abrir a porta serial"
            }

    return result_dict


def get_remote_ports(list_ports):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    range_ip = '.'.join(my_ip.split('.')[:-1]) + '.0/24'

    nm = nmap.PortScanner()
    nm.scan(hosts=range_ip, arguments='-n -sP')

    for ip in nm.all_hosts():
        if test_port(str(ip), 3333):
            if ip != my_ip:
                remote_device = {'name': 'Net. Device', 'device': ip}
                list_ports.append(remote_device)
                break


def local_ports():
    for port in ls.comports():
        dict_ports = {'name': port.name, 'device': port.device}
        LIST_PORTS.append(dict_ports)

    return LIST_PORTS


def remote_ports():
    remote_port = threading.Thread(target=get_remote_ports, args=[LIST_PORTS])
    remote_port.start()


def get_ports():
    global LIST_PORTS

    LIST_PORTS = [
        {
            'name': 'Nenhuma',
            'device': ''
        },
    ]

    local_ports()
    remote_ports()

    return LIST_PORTS


def reload_list_ports():
    get_ports()
    return LIST_PORTS


def get_last_weight():
    if WEIGHT:
        return int(WEIGHT) / 1000

    return '0.000'


def get_current_weight(settings):
    if settings:
        config(**settings)

    time.sleep(0.2)
    if WEIGHT:
        return int(WEIGHT) / 1000

    return '0.000'


def get_weight_network(ip, port=3333):
    cont = 0
    global WEIGHT
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(b'\x05')
            data = s.recv(1024)
            if len(data) == 7:
                line = data[1:6].decode()
                if line.isdigit():
                    WEIGHT = int(line)
            time.sleep(0.2)
            if WEIGHT > 0:
                result_dict = {
                    "result": True,
                    "message": WEIGHT / 1000
                }
                return result_dict
            elif cont == 5:
                result_dict = {
                    "result": False,
                    "message": "Erro crítico na leitura de peso!!!"
                }
                return result_dict
        cont += 1
