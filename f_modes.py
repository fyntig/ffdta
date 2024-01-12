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

def insertFiles(profile, files):
    connection = sqlite3.connect(os.path.join('db', f"{profile}.db"))

    cursor = connection.cursor()
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

    # тут могло бы быть insertFiles, но повторять конекшен бессмысленно - экономии не будет
    cursor.executemany('''INSERT INTO fdta VALUES(
                    NULL, ?, ?, ?, ?, ?) 
                    ''', get_all_files(files)
    )             

    connection.commit()
    connection.close()
    # print('[3]', "создана база данных", f"{profile}.db")

def dropDatabase(profile):
    ''' Не работает, выдаёт:
        sqlite3.OperationalError: near "DATABASE": syntax error'''
    connection = sqlite3.connect(os.path.join('db', f"{profile}.db")) 
    cursor = connection.cursor()
    cursor.execute(f"DROP DATABASE {profile}") # хз надо ли добавлять .db
    connection.commit()
    connection.close()

def isPathAllreadyAdded(profile, files):
    '''проверяет есть ли этот путь в БД, если есть, то возвращает True, иначе False'''
    connection = sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()

    query = f'''SELECT COUNT(*) FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' LIMIT 1 ''' 
    #print(cursor.execute(query).fetchall())   # если без COUNT
    result = cursor.execute(query).fetchone()[0]

    connection.close()

    if result > 0:
        return True
    return False

def removePath(profile, files):
    """удалить путь из профиля"""
    if isPathAllreadyAdded(profile, files):
        connection = sqlite3.connect(os.path.join('db', f"{profile}.db"))
        cursor = connection.cursor()

        query = f'''DELETE FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' '''
      
        cursor.execute(query)
        # result = cursor.execute(query).fetchall() - получить массив удалённых

        connection.commit()
        connection.close()

        # print('[10]', "успешно удалён путь",  result")       

            # для выполнения без результатов можно использовать форму с автоматической финализацией,
            # но так сделаю всё однообразно. Оставлю ниже пример для копипасты:
            #   with sqlite3.connect(os.path.join('db', f"{profile}.db")) as connection:
            #       connection.cursor().execute(f'''SELECT COUNT(*) FROM fdta LIMIT 1 ''')
            
    else:
        print('[11]', f"в профиле {profile} не найден путь {files}")       

def pathesCount(profile):
    connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()
    
    query = f'''SELECT COUNT(*) FROM fdta LIMIT 1 '''
    result = cursor.execute(query).fetchone()[0]

    connection.close()

    return result
        
#-----------------------

def help(args):    
    print(f'Bременной архив v{Version}') 
    print("""Для вывод раздела помощи используйте команду с флагом -h или --help"""
    )

def create(args):
    if re.fullmatch(r'(^\w*)([A-Za-z0-9_-])', args.profile): # A-Z,a-z,0-9,-,_
        # os.getcwd() # получить путь текущего рабочего каталога - просто оставлю здесь для копипасты
        try:
            if os.path.exists('db') & os.path.isdir('db'):
                if os.listdir('db').__contains__(f"{args.profile}.db"):
                    if os.path.exists(args.files):
                        if isPathAllreadyAdded(args.profile, args.files):
                            # !!! тут вызвать ту же функцию что и в "use --check" (дропнуть всё с ним связанное и закинуть новыми файлами)



                            print('!!! ')
                        else:
                            insertFiles(args.profile, args.files)
                    else:
                        print('[7]', "директория недоступна,", f"{args.files}")
                else:                                       
                    newTable(args.profile, args.files)  
            else:               
                os.mkdir('db')
                # print('[1]', "создан каталог баз данных")

                newTable(args.profile, args.files)              
        except:
            print('[2]', "ошибка создания базы данных либо каталога для неё")
    else:
         print('[4]', "недопустимые символы в имени профиля (разрешены: A-Z,a-z,0-9,-,_)")

def delete(args):
    user_input = input(f'Do you realy want to delelte profile {args.profile}? (yes/no): ')

    yes_choices = ['yes', 'y']
    no_choices = ['no', 'n']

    if user_input.lower() in yes_choices:
        try:
            # dropDatabase(args.profile) # sqlite3.OperationalError: near "DATABASE": syntax error
            if os.path.exists(os.path.join('db', f"{args.profile}.db")):
                os.remove(os.path.join('db', f"{args.profile}.db"))
                # print('[9]', "успешно удалён профиль", f"{args.profile}")

        except:
            # Проблема в том, что могут быть открытые соединения с базой,
            # поэтому можно хранить все открытые соединения и дропать их.
            #   Минус этого подхода в том, что не известно какие соединения чем открыты,
            #   поэтому надо хранить коннекшены при открытии, чего нельзя сделать в двух открытых одновременно программах
            print('[6]', f"файл базы данных {args.profile}.db используется")

    elif user_input.lower() in no_choices:
        pass

    else:
        print('[8]', "введённый ответ не распознан, возможны варианты (в любых регистрах): yes, y, no , n")
  
def use(args):
    print('Режим:', args.mode) #!!!    
    #!!! обязателньо проверить если база полностью пустая вывести соответствующую ошибку и ничего ен делать так как из неё можно просто удалить все пути
    print(isPathAllreadyAdded(args.profile, args.files))

def list(args):   
    if os.path.exists('db') & os.path.isdir('db'):
        dblist = []
        for f in os.listdir('db'):
            if re.search(r'.db$', f):
                dblist.append(re.findall(r'.db$', f)[0])
                print(re.sub(r'\.db$', '', f))

    # не требуется выводить вообще ничего наверное в этом случае
        # if (len(dblist) == 0):
        #    print('[5]', "cозданных прфилей не найдено, но вы можете создать новый профиль или использовать default")        
    # else:
    #     print('[5]', "cозданных прфилей не найдено, но вы можете создать новый профиль или использовать default")
                
    #         Список текущих профилей:
    # availibleProfiles = [ 'default' ] 
    # if os.path.exists('db') & os.path.isdir('db'):
    #     for f in os.listdir('db'):
    #         availibleProfiles.append(re.sub(r'\.db$', '', f))
    # availibleProfiles = set(availibleProfiles)
                
def check(args):    
    print('Режим1:', args.mode) #!!! 
    
def remove(args):        
    if os.path.exists('db') & os.path.isdir('db'):
        if os.listdir('db').__contains__(f"{args.profile}.db"):
            try:       
                if pathesCount(args.profile) > 0:
                    removePath(args.profile, args.files)

                else:
                    print('[12]', "попытка получения данных из пустой бд", f"{args.profile}.db")

            except:
                print('[13]', "ошибка подключения к бд", f"{args.profile}.db")
        else:
            print('[5]', "профиль не найден", args.profile)
    # else:
    #   print('[5]', "cозданных прфилей не найдено, но вы можете создать новый профиль или использовать default")    
    