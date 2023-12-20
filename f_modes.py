from f_h import Version
import sqlite3 # не требуется установки отдельного пакета для SQLite3 при версии питона выше 2.5
import os
import re
import datetime
# import dateutil.parser # попробую сначала datetime.fromisoformat так как он применяет более старую версию питона

#-----------------------

def f_switch(dictionary, exp, default=None):
    '''получает на вход структуру например:
    status_dict = {
        200: 'OK',
        400: 'Bad request',
        404: 'Not Found',
        500: 'Internal Server error'
    }
    значение (например 200) и значение по-умолчанию (не обязательное)
    так как питон теоретически потдерживает стиль функционального программирования - может быть полезным сделать отдельной функцией
    '''    
    if exp in dictionary:
        return dictionary[exp]
    else:
        return default # впринципе default-значение можно определить и в самом словаре

def get_all_files(dir_path):
    '''формирование списка файлов в директории и поддиректориях'''
    file_list = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_list.append([
                os.path.abspath(os.path.join(root, file)), 
                os.path.getsize(os.path.abspath(os.path.join(root, file))), 
                datetime.datetime.fromtimestamp(os.path.getctime(os.path.abspath(os.path.join(root, file)))).isoformat(), 
                datetime.datetime.fromtimestamp(os.path.getmtime(os.path.abspath(os.path.join(root, file)))).isoformat(), 
                datetime.datetime.now().isoformat()
            ])            
        for dir in dirs:
            file_list.append([
                os.path.abspath(os.path.join(root, dir)), 
                os.path.getsize(os.path.abspath(os.path.join(root, dir))), 
                datetime.datetime.fromtimestamp(os.path.getctime(os.path.abspath(os.path.join(root, dir)))).isoformat(), 
                datetime.datetime.fromtimestamp(os.path.getmtime(os.path.abspath(os.path.join(root, dir)))).isoformat(), 
                datetime.datetime.now().isoformat()
            ])

    return file_list

#-----------------------
# id   |  path    |   size    |   (cd) create_date-time   |   (md) modificated_date-time   |   (sd) selected_date-time
# DATE_TIME in TEXT as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS")
def newTable(profile, files):
    newTableQuery = '''CREATE TABLE IF NOT EXISTS fdta (
                    id INTEGER PRIMARY KEY,
                    path TEXT NOT NULL,
                    size INTEGER,
                    cd TEXT,
                    md TEXT,                    
                    sd TEXT                                   
                    )
                    '''

    connection = sqlite3.connect(os.path.join('db', f"{profile}.db"))

    cursor = connection.cursor()
    cursor.execute(newTableQuery)
    connection.commit()

    cursor.executemany('''INSERT INTO fdta VALUES(
                    NULL, ?, ?, ?, ?, ?) 
                    ''', get_all_files(files)
    )   
    # оставлю для копипасты варианты: 
    # cursor.execute('''INSERT INTO fdta VALUES(
    #                     NULL, 'asdas' ,5454 ,'fdfdf' ,'fdfd' ,'fdfd')  
    #                     ''')  
    # cursor.execute("INSERT INTO fdta VALUES(NULL, ?, ?, ?, ?, ?)", get_all_files(files)[0])           

    connection.commit()
    connection.close()
    print('[3]', "создана база данных", f"{profile}.db")

def isPathAllreadyAdded(profile, files):
    '''проверяет есть ли этот путь в БД, если есть, то возвращает True, иначе False'''
    connection = sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()

    query = f'''SELECT COUNT(*) FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' ''' 
    #print(cursor.execute(query).fetchall())   # если без COUNT
    result = cursor.execute(query).fetchone()[0]

    connection.close()

    if result > 0:
        return True
    return False

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

                    # !!! проверить есть ли этот путь уже, если есть то дропнуть всё с ним связанное и закинуть новыми файлами
                    #           isPathAllreadyAdded(profile, files): - готова
                    # !!! тут добавление списка файлов в существующий список

                else:                                       
                    newTable(args.profile, args.files)  

            else:               
                os.mkdir('db')
                print('[1]', "создан каталог баз данных")

                newTable(args.profile, args.files)              
        except:
            print('[2]', "ошибка создания базы данных либо каталога для неё")

    else:
         print('[4]', "недопустимые символы в имени профиля (разрешены: A-Z,a-z,0-9,-,_)")




def delete(args):
    print('Режим:', args.mode) #!!!
    print('test2')

def use(args):
    print('Режим:', args.mode) #!!!    
    isPathAllreadyAdded(args.profile, args.files)

def list(args):
    print('Режим:', args.mode) #!!!
    print('test3')
