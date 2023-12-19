from f_h import Version
import sqlite3 
import os
import re

#-----------------------

# def f_swich(dict, exp, default=None):
#     '''получает на вход структуру например:
#     status_dict = {
#         200: 'OK',
#         400: 'Bad request',
#         404: 'Not Found',
#         500: 'Internal Server error'
#     }
#     значение (например 200) и значение по-умолчанию (не обязательное)
#     так как питон теоретически потдерживает стиль функционального программирования - может быть полезным сделать отдельной функцией
#     '''    
#     if not dict.get(exp):
#         dict.get(exp)
#     else:
#         return default # впринципе default-значение можно определить и в самом словаре

#-----------------------

def help(args):    
    print(f'Bременной архив v{Version}') 
    print("""Для вывод раздела помощи используйте команду с флагом -h или --help"""
    )

def create(args):
    if re.fullmatch(r'(^\w*)([A-Za-z0-9_-])', args.profile): # A-Z,a-z,0-9,-,_

        # os.getcwd() # получить путь текущего рабочего каталога

        try:
            if os.path.exists('db') & os.path.isdir('db'):

                if os.listdir('db').__contains__(f"{args.profile}.db"):
                    print(args.files)

                    #!!! тут добавление списка файлов в существующий список и потом этот же код скопировать в случаи где создаётся файл бд ис слр

                else:                                       
                    connection = sqlite3.connect(os.path.join('db', f"{args.profile}.db"))
                    connection.close()
                    print('[3]', "создана база данных", f"{args.profile}.db")

            else:
                os.mkdir('db')
                print('[1]', "создан каталог баз данных")

                connection = sqlite3.connect(os.path.join('db', f"{args.profile}.db"))
                connection.close()
                print('[3]', "создана база данных", f"{args.profile}.db")

        except:
            print('[2]', "ошибка создания каталога баз данных")


        # !!! проверить пути и если их не было добавить в профиль
        #
        #
        #
        #
    else:
         print('[4]', "недопустимые символы в имени профиля (разрешены: A-Z,a-z,0-9,-,_)")




def delete(args):
    print('Режим:', args.mode) #!!!
    print('test2')

def use(args):
    print('Режим:', args.mode) #!!!    
    print('test')

def list(args):
    print('Режим:', args.mode) #!!!
    print('test3')
