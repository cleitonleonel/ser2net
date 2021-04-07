# -*- coding: utf-8 -*-
#
import os
import sys
import time
import PySimpleGUIQt as sg
from api import get_ports, get_last_weight, config, logg

logg.disable(logg.DEBUG)

__version__ = 'beta-001'


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def checked(event):
    if not event or event == '' or event == 'False':
        return False
    else:
        return True


def get_serial_names():
    list_names = [name['name'] for name in get_ports()]
    return list_names


def get_balance_info():
    send_message = '05'

    response = f"""
    >>> Initialize...
    >>> Send bytes: {send_message}
    >>> Awaiting...
    >>> Receive bytes: {get_last_weight()}
    >>> Closing connection...
    >>> Connection Close.
    """

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
         sg.Text(' '), sg.Input('2', do_not_clear=True, size=(15, 0.8), tooltip='Timeout', key='timeout'), sg.Stretch()],
        [sg.Text('')],
        [sg.Text('Última Resposta: ')], [sg.Multiline(size=(41.5, 14.5), key='Textbox')],
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
    server_base = None
    serial_port = None
    while True:
        button, values = window.Read()
        if button == sg.WIN_CLOSED:
            sys.exit(0)

        if button is None:
            break

        if button == 'find_ports':
            window['serial_port'].Update(values=get_serial_names())
            window.Refresh()

        if button == 'weight_read' or button == 'activate':
            is_server = False if button == 'weight_read' else True
            if values['serial_port'] != 'Nenhuma':
                for port in get_ports():
                    device = port['name']
                    if device == values['serial_port']:
                        serial_port = port['device']

                baudrate = values['baudrate']
                timeout = int(values['timeout'])
                if values['handshaking']:
                    print(values)

                weight = config(serial=serial_port, baudrate=baudrate, rtscts=None,
                                xonxoff=None, timeout=timeout, server=is_server,
                                )

                if is_server:
                    server_base = weight
                    window['activate'].Update(button_color=('white', 'green'))
                    window['deactivate'].Update(disabled=False)
                    window['Textbox'].Update(get_balance_info())
                    window['last_weight'].Update(get_last_weight())
                    window.Refresh()
                elif not weight['result']:
                    sg.popup(weight['message'], title="Erro", location=(420, 350))
                    window['Textbox'].Update('')
                    window['last_weight'].Update(get_last_weight())
                    window.Refresh()
                else:
                    window['Textbox'].Update(get_balance_info())
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
            server_base.kill()

        if button == 'clean':
            window['Textbox'].Update('')
            window.Refresh()

        if button == 'exit':
            if sg.popup_ok_cancel('Deseja mesmo sair???',
                                  title="Sair", location=(420, 350)
                                  ) == "OK":
                time.sleep(2)
                window.close()
                quit()

    window.close()
    quit()
