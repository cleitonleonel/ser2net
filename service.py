# -*- coding: utf-8 -*-
#
import os
import sys
import time
import PySimpleGUIQt as sg
from datetime import datetime
from pytz import timezone
from api import get_ports, \
    get_last_weight, get_weight_network, \
    config, logg, reload_list_ports, get_current_weight

logg.disable(logg.DEBUG)

__version__ = 'beta-001'
__author__ = 'Cleiton Leonel Creton'
__email__ = 'cleiton.leonel@gmail.com'

SERIAL_PORTS = []


def get_current_date():
    return datetime.now().astimezone(timezone("America/Sao_Paulo")).strftime("%d/%m/%Y %H:%M:%S")


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def checked(event):
    if not event or event == '' or event == 'False':
        return False
    else:
        return True


def get_serial_names():
    global SERIAL_PORTS

    SERIAL_PORTS = get_ports()
    list_names = [name['name'] for name in SERIAL_PORTS]

    return list_names


def update_list_serial():
    global SERIAL_PORTS

    list_names = [name['name'] for name in SERIAL_PORTS]
    SERIAL_PORTS = reload_list_ports()

    time.sleep(0.1)
    window.Refresh()

    return list_names


def get_balance_info():
    send_message = '05'

    response = f"""    >>> Initialize...
    >>> Send bytes: {send_message}
    >>> Awaiting...
    >>> Receive bytes: {get_last_weight()}
    >>> Closing connection...
    >>> Connection Close."""

    return response


def welcome_layout():
    frame_1 = [
        [sg.Text('Balança: ')], [sg.Combo(['Nenhuma', 'Toledo', 'Filizola', 'Urano'],
                                          font=("verdana", 11), key="balance_name", enable_events=True, size=(13, 0.8))],
        [sg.Text('Porta Serial: ')], [sg.Combo(get_serial_names(), font=("verdana", 13),
                                               key="serial_port", size=(13, 0.8))],
        [sg.Text('Baud Rate: ')], [sg.Combo([2400, 4800, 9600, 14400, 19200, 38400,
                                             56000, 57600], font=("verdana", 11), key="baudrate", size=(13, 0.8))],
        [sg.Text('Data Bits: ')], [sg.Combo([5, 6, 7, 8], font=("verdana", 11), key="data_bits", size=(13, 0.8))],
        [sg.Text('Parity: ')], [sg.Combo(['none', 'odd', 'even', 'mark', 'space'],
                                         font=("verdana", 11), key="parity", size=(13, 0.8))],
        [sg.Text('Stop Bits:')], [sg.Combo([1, 1.5, 2], font=("verdana", 11), key="stop_bits", pad=[1, 0], size=(13, 0.8))],
        [sg.Text('Handshaking: ')], [sg.Combo(['Nenhum', 'XON/XOFF', 'RTS/CTS', 'DTR/DSR'],
                                              font=("verdana", 11), key="handshaking", pad=[1, 0], size=(13, 0.8))]
    ]

    frame_2 = [
        [sg.Text('')],
        [sg.Input(get_last_weight(), do_not_clear=True, size=(25, 0.8), tooltip='Último Peso Lido', disabled=True, key='last_weight'),
         sg.Text(' '), sg.Input('1', do_not_clear=True, size=(15, 0.8), tooltip='Timeout', key='timeout'), sg.Stretch()],
        [sg.Text('')],
        [sg.Text('Última Resposta: ')], [sg.Multiline(size=(41.5, 8.6), key='Textbox')],
        [sg.Text('Pesagem Apurada: ')], [sg.Multiline(size=(41.5, 4.6), default_text=get_last_weight() + ' KG', font=('Helvetica Bold', 48), key='Textbox2')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
    ]

    frame_3 = [
        [sg.Text('')],
        [sg.Text(''), sg.Text(' ' * 2), sg.Button('Ativar', size=[14, 0.8],
                                                  button_color=('white', '#082567'), key="activate"), sg.Text(''), sg.Text('')],
        [sg.Text('')],
        [sg.Text(''), sg.Text(' ' * 2), sg.Button('Desativar', size=[14, 0.8],
                                                  button_color=('white', '#082567'),
                                                  key="deactivate", disabled=True), sg.Text(''), sg.Text('')],
        [sg.Text('')],
        [sg.Text(''), sg.Text(' ' * 2), sg.Button('Ler Peso', size=[14, 0.8],
                                                  button_color=('white', '#082567'), key="weight_read"), sg.Text(''), sg.Text('')],
        [sg.Text('')],
        [sg.Text(''), sg.Text(' ' * 2), sg.Button('Localizar Portas', size=[14, 0.8],
                                                  button_color=('white', '#082567'), key="find_ports"), sg.Text(''), sg.Text('')],
        [sg.Text('')],
        [sg.Text(''), sg.Text(' ' * 2), sg.Button('Limpar', size=[14, 0.8],
                                                  button_color=('white', '#082567'), key="clean"), sg.Text(''), sg.Text('')],
        [sg.Text('')],
        [sg.Text(''), sg.Text(' ' * 2), sg.Button('Sair', size=[14, 0.8],
                                                  button_color=('white', '#082567'), key="exit"), sg.Text(''), sg.Text('')],
        [sg.Text('')],
    ]

    layout_1 = [
        [sg.Text('')],
        [sg.Text(' '), sg.Frame('Ajustes Técnicos', frame_1, title_color='black'), sg.Text(' '),
         sg.Frame('Visualização de dados', frame_2, title_color='black'), sg.Text(' '),
         sg.Frame('Serviços', frame_3, title_color='black'), sg.Stretch()],
        [sg.Text(f'Versão: {__version__} by {__author__}', text_color="black"), sg.Text(get_current_date(), justification="right", text_color="black", key="clock")],
    ]

    return layout_1


def create_window(current_layout, title):
    return sg.Window(f'Ser2net | {title}',
                     font=('Helvetica', 13),
                     default_button_element_size=(100, 30),
                     auto_size_buttons=False,
                     default_element_size=(20, 22),
                     border_depth=1,
                     resizable=False,
                     size=(290, 50)
                     ).Layout(current_layout)


if __name__ == '__main__':
    layout = welcome_layout()
    window = create_window(layout, title='Servindo sua balança na rede')
    thread_weight = None
    serial_port = None
    timeout = None
    baudrate = None
    weight = None
    settings = None
    is_server = None
    while True:
        button, values = window.Read(timeout=1.5)
        window['clock'].Update(get_current_date())
        if button == sg.WIN_CLOSED:
            sys.exit(0)

        if button is None:
            break

        if button == 'find_ports':
            window['serial_port'].Update(values=update_list_serial())
            window.Refresh()

        if button == 'weight_read' or button == 'activate':
            is_server = False if button == 'weight_read' else True
            if values['serial_port'] != 'Nenhuma':
                for port in SERIAL_PORTS:
                    port_name = port['name']
                    if port_name == values['serial_port']:
                        serial_port = port['device']

                if '.' in serial_port:
                    octets = serial_port.strip().split(".")
                    if len([x for x in octets if int(x) < 256]) == 4:
                        weight = get_weight_network(serial_port)
                        print(weight)
                else:
                    baudrate = values['baudrate']
                    timeout = int(values['timeout'])
                    if values['handshaking']:
                        print(values)

                    weight = config(serial=serial_port, baudrate=baudrate, rtscts=None,
                                    xonxoff=None, timeout=timeout, server=is_server,
                                    )

                settings = {
                    "serial": serial_port,
                    "baudrate": baudrate,
                    "rtscts": None,
                    "xonxoff": None,
                    "timeout": timeout,
                    "server": is_server
                }

                if is_server:
                    thread_weight = weight
                    window['activate'].Update(button_color=('white', 'green'))
                    window['deactivate'].Update(disabled=False)
                    window['Textbox'].Update(get_balance_info())
                    window['Textbox2'].Update(f'{get_last_weight()} KG')
                    window['last_weight'].Update(get_last_weight())
                    window.Refresh()
                elif not weight['result']:
                    sg.popup(weight['message'], title="Erro", location=(420, 350))
                    window['Textbox'].Update('')
                    window['Textbox2'].Update('')
                    window['last_weight'].Update(get_last_weight())
                    window.Refresh()
                else:
                    window['Textbox'].Update(get_balance_info())
                    window['Textbox2'].Update(f'{get_last_weight()} KG')
                    window['last_weight'].Update(get_last_weight())
                    window.Refresh()
            else:
                sg.popup(f"Porta '{values['serial_port']}' ,não é válida!!! ",
                         title="Erro", location=(420, 350)
                         )

        if button == 'deactivate':
            window['activate'].Update(button_color=('white', '#082567'))
            window['deactivate'].Update(disabled=True)
            window.Refresh()
            thread_weight.kill()

        if button == 'clean':
            window['Textbox'].Update('')
            window['Textbox2'].Update('')
            window.Refresh()

        if button == 'exit':
            if sg.popup_ok_cancel('Deseja mesmo sair???',
                                  title="Sair", location=(420, 350)
                                  ) == "OK":
                thread_weight.kill()
                time.sleep(2)
                window.close()
                quit()
        if not is_server:
            window['Textbox2'].Update(f'{get_current_weight(settings=settings)} KG')

    window.close()
    quit()
