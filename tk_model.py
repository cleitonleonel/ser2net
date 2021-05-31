# -*- coding: utf-8 -*-
#
import os
import sys
import time
import PySimpleGUI as sg
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


def set_border_color(listkey, color, border_size):
    result = False
    for key in listkey:
        window[key].Widget.configure(highlightbackground=color, highlightcolor=color, highlightthickness=border_size)
        result = True
    return result


def welcome_layout():
    frame_1 = [
        [sg.Text('')],
        [sg.Text('Balança: ')], [sg.Combo(['Nenhuma', 'Toledo', 'Filizola', 'Urano'],
                                          default_value='Nenhuma', font=("verdana", 11), key="balance_name", enable_events=True, size=(14, 1))],
        [sg.Text('Porta Serial: ')], [sg.Combo(get_serial_names(), font=("verdana", 11),
                                               default_value='Nenhuma', key="serial_port", size=(14, 1))],
        [sg.Text('Baud Rate: ')], [sg.Combo([2400, 4800, 9600, 14400, 19200, 38400,
                                             56000, 57600], font=("verdana", 11), default_value=2400, key="baudrate", size=(14, 1))],
        [sg.Text('Data Bits: ')], [sg.Combo([5, 6, 7, 8], font=("verdana", 11), default_value=5, key="data_bits", size=(14, 1))],
        [sg.Text('Parity: ')], [sg.Combo(['none', 'odd', 'even', 'mark', 'space'],
                                         font=("verdana", 11), default_value='none', key="parity", size=(14, 1))],
        [sg.Text('Stop Bits:')], [sg.Combo([1, 1.5, 2], font=("verdana", 11), default_value=1, key="stop_bits", size=(14, 1))],
        [sg.Text('Handshaking: ')], [sg.Combo(['Nenhum', 'XON/XOFF', 'RTS/CTS', 'DTR/DSR'],
                                              font=("verdana", 11), default_value='Nenhum', key="handshaking", size=(14, 1))],
        [sg.Text('')]
    ]

    frame_2 = [
        [sg.Text('\n')],
        [sg.Input(get_last_weight(), do_not_clear=True, size=(14, 1), tooltip='Último Peso Lido', disabled=True, key='last_weight', font=('Helvetica Bold', 13), pad=(0, 1)),
         sg.Text(' '), sg.Input('1', do_not_clear=True, size=(14, 1), tooltip='Timeout', key='timeout', font=('Helvetica Bold', 13), pad=(0, 1)), sg.Stretch()],
        [sg.Text('Última Resposta: ')], [sg.Multiline(size=(33, 10), key='Textbox', font=('Helvetica Bold', 12), disabled=True, no_scrollbar=True, border_width=2)],
        [sg.Text('Pesagem Apurada: ')], [sg.Multiline(size=(8, 1),
                                                      default_text=get_last_weight() + ' KG', font=('Helvetica Bold', 48), key='Textbox2', disabled=True, no_scrollbar=True, border_width=2)],
        [sg.Text('')]
    ]

    frame_3 = [
        [sg.Text('\n')],
        [sg.Button('Ativar', size=(14, 1), button_color=('white', '#082567'), key="activate")],
        [sg.Text('')],
        [sg.Button('Desativar', size=(14, 1), button_color=('white', '#082567'), key="deactivate", disabled=True)],
        [sg.Text('')],
        [sg.Button('Ler Peso', size=(14, 1), button_color=('white', '#082567'), key="weight_read")],
        [sg.Text('')],
        [sg.Button('Localizar Portas', size=(14, 1), button_color=('white', '#082567'), key="find_ports")],
        [sg.Text('')],
        [sg.Button('Limpar', size=(14, 1), button_color=('white', '#082567'), key="clean")],
        [sg.Text('')],
        [sg.Button('Sair', size=(14, 1), button_color=('white', '#082567'), key="exit")],
        [sg.Text('')]
    ]

    layout_1 = [
        [sg.Text('')],
        [sg.Text(''), sg.Frame('Ajustes Técnicos', frame_1, title_color='black', element_justification="c", key='frame_1'), sg.Text(''),
         sg.Frame('Visualização de dados', frame_2, title_color='black', element_justification="c", key='frame_2'), sg.Text(''),
         sg.Frame('Serviços', frame_3, title_color='black', element_justification="c", key='frame_3'), sg.Text('')],
        [sg.Text('')],
        [sg.Text('\n' * 2)],
        [sg.Text(f'Versão: {__version__} by {__author__}', justification="left", text_color="black", key='version', font=("verdana", 8), size=(100, 1)),
         sg.Text(get_current_date(), justification="right", text_color="black", key="clock", font=("verdana", 8), size=(100, 1))
         ]
    ]

    frames = [[sg.Text('')], [sg.Frame('', layout_1)]]

    return frames


def create_window(current_layout, title):
    return sg.Window(f'Ser2net | {title}',
                     current_layout,
                     font=('Helvetica', 13),
                     default_button_element_size=(100, 30),
                     auto_size_buttons=False,
                     default_element_size=(20, 22),
                     border_depth=2,
                     resizable=True,
                     size=(800, 650),
                     ).Finalize()


if __name__ == '__main__':
    layout = welcome_layout()
    window = create_window(layout, title='Servindo sua balança na rede')

    window['frame_1'].expand(True, True, True)
    window['frame_2'].expand(True, True, True)
    window['frame_3'].expand(True, True, True)
    window['version'].expand(True, True, True)
    window['clock'].expand(True, True, True)

    set_border_color(['Textbox', 'Textbox2'], color='black', border_size=2)

    width, height = window.size
    current_location = None
    thread_weight = None
    serial_port = None
    timeout = None
    baudrate = None
    weight = None
    settings = None
    is_server = None
    is_remote_port = False
    while True:
        button, values = window.read(timeout=1)

        window['clock'].Update(get_current_date())

        if button == sg.WIN_CLOSED:
            sys.exit(0)

        elif button is None:
            break
        else:
            x, y = window.current_location()

        if button == 'find_ports':
            window['serial_port'].Update(values=update_list_serial(), size=(14, 1))
            window.Refresh()

        if button == 'weight_read' or button == 'activate':
            is_server = False if button == 'weight_read' else True
            if values['serial_port'] != 'Nenhuma':
                for port in SERIAL_PORTS:
                    port_name = port['name']
                    if port_name == values['serial_port']:
                        serial_port = port['device']

                if '.' in serial_port:
                    is_remote_port = True
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
                    sg.Popup(weight['message'], title="Erro", location=(420, 350))
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
                sg.Popup(f"Porta '{values['serial_port']}' ,não é válida!!! ",
                         title="Erro", location=(width // 2 + x - 100, height // 2 + y - 100)
                         )

        if button == 'deactivate':
            window['activate'].Update(button_color=('white', '#082567'))
            window['deactivate'].Update(disabled=True)
            window.Refresh()
            if thread_weight:
                thread_weight.kill()

        if button == 'clean':
            window['Textbox'].Update('')
            window['Textbox2'].Update('')
            window.Refresh()

        if button == 'exit':
            if sg.PopupOKCancel('Deseja mesmo sair???',
                                title="Sair", location=(width // 2 + x - 100, height // 2 + y - 100)
                                ) == "OK":
                if thread_weight:
                    thread_weight.kill()
                time.sleep(2)
                window.close()
                quit()
        if not is_server and not is_remote_port:
            window['Textbox2'].Update(f'{get_current_weight(settings=settings)} KG')

    window.close()
    quit()
