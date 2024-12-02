from concurrent.futures import ThreadPoolExecutor
from threading import          Thread

import keyboard
import psutil
import ctypes
import socket
import time

SCAN_TIMEOUT = 1.5
VEYON_PORTS = [11100, 11200, 11300]

veyon_connetions = []

def msg_box(text: str):
    ctypes.windll.user32.MessageBoxW(None, text, 'Veyon connections', 0x40 | 0x1 | 0x1000)

def direct_show():
    msg_box(get_connections())

def get_connections():
    global veyon_connetions
    fixed_message = ''
    for ip in veyon_connetions:
        try:
            ip = socket.gethostbyaddr(ip)[0]
        except:
            pass
        fixed_message += f'{ip}\n'
    
    return fixed_message.strip()

def detector_service():
    global veyon_connetions
    old_connections = veyon_connetions
    with ThreadPoolExecutor(8) as executor:
        while True:
            if old_connections != veyon_connetions:
                fixed_message = get_connections()

                executor.submit(msg_box, fixed_message)
                old_connections = veyon_connetions

            time.sleep(SCAN_TIMEOUT/3)

def main():
    global veyon_connetions

    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    keyboard.add_hotkey('f10', callback=direct_show)
    Thread(target=detector_service, daemon=True).start()

    while True:
        pre_connections = []
        for conn in psutil.net_connections('tcp'):
            if conn.status == 'ESTABLISHED':
                if conn.laddr.port in VEYON_PORTS:
                    pre_connections.append(conn.raddr.ip)
        
        veyon_connetions = pre_connections
        
        time.sleep(SCAN_TIMEOUT)

if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        msg_box(f'ERROR: {err}')