from f_h import Version
import sqlite3 # не требуется установки отдельного пакета для SQLite3 при версии питона выше 2.5
import os
import re
import datetime
# import dateutil.parser # попробую сначала datetime.fromisoformat так как он применяет более старую версию питона

#-----------------------

OldestDate = "2000-01-01T00:00:00.000000"

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
    # в этом проекте не используется, но оставлю чтобы потом делать копипасту отсюда (из git)

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
                'FALSE',
                os.path.getsize(os.path.abspath(os.path.join(root, file))), 
                datetime.datetime.fromtimestamp(os.path.getctime(os.path.abspath(os.path.join(root, file)))).isoformat(), 
                datetime.datetime.fromtimestamp(os.path.getmtime(os.path.abspath(os.path.join(root, file)))).isoformat(), 
                #datetime.datetime.now().isoformat() - не подходит так как тогда будет путанница с последней использованной датой при добавлении после использования профиля
                #"" - плохо подходит так как тогда поиск максимального будет работать в строковом варианте а пустота выше цифры
                #datetime.MINYEAR.isoformat() - даёт ошибку, правильнее было бы указать дату и потом ронять её в исоформате к нулю
                OldestDate
            ])            
        for dir in dirs:
            file_list.append([
                os.path.abspath(os.path.join(root, dir)), 
                'TRUE',
                os.path.getsize(os.path.abspath(os.path.join(root, dir))), 
                datetime.datetime.fromtimestamp(os.path.getctime(os.path.abspath(os.path.join(root, dir)))).isoformat(), 
                datetime.datetime.fromtimestamp(os.path.getmtime(os.path.abspath(os.path.join(root, dir)))).isoformat(), 
                #datetime.datetime.now().isoformat()
                #""
                #datetime.MINYEAR.isoformat()
                OldestDate
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
# id   |  path    |     isdir   |   size    |   (cd) create_date-time   |   (md) modificated_date-time   |   (sd) selected_date-time
# DATE_TIME in TEXT as ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS")
def newTable(profile, files):
    newTableQuery = '''CREATE TABLE IF NOT EXISTS fdta (
                    id INTEGER PRIMARY KEY,
                    path TEXT NOT NULL,
                    isdir TEXT,
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
                    NULL, ?, ?, ?, ?, ?, ?) 
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

def lastDate(profile, files):
    '''скорее всего не нужная функция так как будет в любом случае назначаться для пустых и свежее указанной даты'''
    # не используется в проекте, но пока оставлю

    result = OldestDate

    connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()   
  
    query = f'''SELECT MIN(sd) FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' '''
    minDate = cursor.execute(query).fetchone()[0]
    query = f'''SELECT MAX(sd) FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' '''
    maxDate = cursor.execute(query).fetchone()[0]

    connection.close()

    if minDate == maxDate == OldestDate:
        pass # надо сделать дял всех
    elif minDate == OldestDate:
        pass # надо сделать только для тех кто ещё не делал и свежее указанной даты
    else:
        result = maxDate

    return result  
    
def getPathes(profile, files, date, n, nu, onlydirectories, onlyfiles, notempty):
    '''отдаёт ещё не отданные файлы и с датой изменения после указанной даты
        (теоретически нужен ещё режим который отдаёт только те которые изменились после даты, не добавляя новые)'''

    connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()
    result = None
    query = ""

    try:
        cursor.execute('BEGIN')

        if date == OldestDate or date == None:
            # только для тех укого не было
            query = f'''SELECT * FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' AND sd = '{OldestDate}' '''
          
        else:
            # для всех с олдест датой и свежее date апдейтить
            query = f'''SELECT * FROM fdta WHERE 
                            path LIKE '{os.path.join(os.path.abspath(files), '%')}' 
                                AND (sd = '{OldestDate}' 
                                    OR md > '{date}' ) '''          
           
        if onlydirectories != None and onlyfiles == None:
            query += "AND isdir = 'TRUE' "
        elif onlyfiles != None and onlydirectories == None:
            query += "AND isdir = 'FALSE' "

        if notempty != None:
            query += "AND size > 0 "

        if n != None:
            query += f"LIMIT '{n}' "   

        result = cursor.execute(query).fetchall()

        if nu == None:
            query = f'''UPDATE fdta SET sd = ? WHERE id IN (SELECT id FROM ({query})) '''
            cursor.execute(query, (datetime.datetime.now().isoformat(), ))

        cursor.execute('COMMIT')

    except:
        cursor.execute('ROLLBACK')
        result = None

    # тут также возможна запись с with:
        # with sqlite3.connect('my_database.db') as connection:
        #     cursor = connection.cursor()
        #     try:
        #         with connection:
        #             ...
        #     except
        #         pass # т.е не надо BEGIN и ROLLBACK

    connection.close()
    return result

def getPathesArray(profile, files, date, n, nu, onlydirectories, onlyfiles, notempty):
    '''отдаёт ещё не отданные файлы и с датой изменения после указанной даты в виде массива
        (теоретически нужен ещё режим который отдаёт только те которые изменились после даты, не добавляя новые)'''

    connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()
    result = None
    query = ""

    try:
        cursor.execute('BEGIN')

        if date == OldestDate or date == None:
            # только для тех укого не было
            query = f'''SELECT path FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' AND sd = '{OldestDate}' '''
          
        else:
            # для всех с олдест датой и свежее date апдейтить
            query = f'''SELECT path FROM fdta WHERE 
                            path LIKE '{os.path.join(os.path.abspath(files), '%')}' 
                                AND (sd = '{OldestDate}' 
                                    OR md > '{date}' ) '''
            
        if onlydirectories != None and onlyfiles == None:
            query += "AND isdir = 'TRUE' "
        elif onlyfiles != None and onlydirectories == None:
            query += "AND isdir = 'FALSE' "

        if notempty != None:
            query += "AND size > 0 "

        if n != None:
            query += f"LIMIT '{n}' "

        result = cursor.execute(query).fetchall()

        if nu == None:            
            subquery = f'''SELECT * FROM fdta WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' '''
            if  date == OldestDate or date == None:  
                subquery += f"AND sd = '{OldestDate}' "
            else:
                subquery += f"AND (sd = '{OldestDate}' OR md > '{date}' ) "

            if onlydirectories != None and onlyfiles == None:
                subquery += "AND isdir = 'TRUE' "
            elif onlyfiles != None and onlydirectories == None:
                subquery += "AND isdir = 'FALSE' "

            if notempty != None:
                subquery += "AND size > 0 "

            if n != None:
                subquery += f"LIMIT '{n}' "

            query = f'''UPDATE fdta SET sd = ? WHERE id IN (SELECT id FROM ({subquery})) '''
            cursor.execute(query, (datetime.datetime.now().isoformat(), ))

        cursor.execute('COMMIT')

    except:        
        cursor.execute('ROLLBACK')
        result = None

    connection.close()
    return result

def createIndex(profile):
    try:
        connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
        cursor = connection.cursor()

        query = f'''CREATE INDEX idx_path_sd ON fdta (path, isdir, size, md, sd) '''
        cursor.execute(query)

        connection.commit()
        connection.close()

    except:
        print('[15]', "индекс уже существует, при необходимости сначала удалите его и потом создайте снова")

def deleteIndex(profile):
    try:
        connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
        cursor = connection.cursor()
        
        query = f'''DROP INDEX idx_path_sd '''
        cursor.execute(query)

        connection.commit()
        connection.close()

    except:
        print('[16]', "индекс не создан или уже удалён ранее")

def refreshDate(profile, files):
    connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()   
  
    query = f'''UPDATE fdta SET sd = ? WHERE path LIKE '{os.path.join(os.path.abspath(files), '%')}' ''' 
    cursor.execute(query, (OldestDate, ))
    # cursor.execute(query, (datetime.datetime.now().isoformat(), ))

    connection.commit()
    connection.close()

def testmode10Query(profile):
    connection =  sqlite3.connect(os.path.join('db', f"{profile}.db"))
    cursor = connection.cursor()   
  
    query = f'''SELECT * FROM fdta LIMIT 10 '''
    result = cursor.execute(query).fetchall()

    connection.close()
    return result

#-----------------------

def checksDb(func):
    def wrapper(f_args):
        if os.path.exists('db') & os.path.isdir('db'):
            if os.listdir('db').__contains__(f"{f_args.profile}.db"):

                func(f_args)

            else:
                print('[5]', "профиль не найден", f_args.profile)
        else:
            print('[5]', "cозданных прфилей не найдено, но вы можете создать новый профиль или использовать default")    
    return wrapper

def checksPathes(func):
    def wrapper(f_args):
        try:       
            if pathesCount(f_args.profile) > 0:
                
                func(f_args)

            else:
                print('[12]', "попытка получения данных из пустой бд", f"{f_args.profile}.db")
        except:
            print('[13]', "ошибка подключения к бд", f"{f_args.profile}.db")                           
    return wrapper

#-----------------------

def help(args):    
    print(f'Bременной архив v{Version}') 
    print("""Для вывод раздела помощи используйте команду с флагом -h или --help"""
    )

def create(args):
    # может правильнее было бы использовать scandir и грузить целиком содежимое папок с атрибутами так как вроде оно работает быстрее, чем как я через listdir

    if re.fullmatch(r'(^\w*)([A-Za-z0-9_-])', args.profile): # A-Z,a-z,0-9,-,_
        # os.getcwd() # получить путь текущего рабочего каталога - просто оставлю здесь для копипасты
        try:
            if os.path.exists('db') & os.path.isdir('db'):
                if os.listdir('db').__contains__(f"{args.profile}.db"):
                    if os.path.exists(args.files):
                        if isPathAllreadyAdded(args.profile, args.files):
                            remove(args)
                            insertFiles(args.profile, args.files)

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
  
def lambda_use(l_args):
    # Отдаёт ссылки на N самых старых файлов, которые ещё не отдавались (либо файлов, изменённых после ДАТА-ВРЕМЯ)
    # f - только выбранные файлы, только изменённые после даты d, отдаватть n файлов

    if isPathAllreadyAdded(l_args.profile, l_args.files):           
        if l_args.array != None:
            print(getPathesArray(l_args.profile, l_args.files, l_args.date, l_args.n, l_args.noupdatedate, l_args.onlydirectories, l_args.onlyfiles, l_args.notempty))
        else:
            for file in getPathes(l_args.profile, l_args.files, l_args.date, l_args.n, l_args.noupdatedate, l_args.onlydirectories, l_args.onlyfiles, l_args.notempty):
                print(file[1])    
        
    else:
        print('[11]', f"в профиле {l_args.profile} не найден путь {l_args.files}")

def use(args):
    checksDb(checksPathes(lambda_use(args)))       

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

def lambda_check(l_args):     
    try:       
        if pathesCount(l_args.profile) > 0:
            removePath(l_args.profile, l_args.files)

        if os.path.exists(l_args.files):                
            insertFiles(l_args.profile, l_args.files)

    except:
        print('[13]', "ошибка подключения к бд", f"{l_args.profile}.db")         

def check(args):    
    checksDb(lambda_check(args)) 

def lambda_remove(l_args):  
    removePath(l_args.profile, l_args.files)

def remove(args):        
    checksDb(checksPathes(lambda_remove(args)))  
    
def lambda_refresh(l_args):      
    if isPathAllreadyAdded(l_args.profile, l_args.files):  
        refreshDate(l_args.profile, l_args.files)

    else:
        print('[11]', f"в профиле {l_args.profile} не найден путь {l_args.files}")        

def refresh(args):    
    checksDb(checksPathes(lambda_refresh(args)))

def lambda_index(l_args):   
    if l_args.createindex != None and l_args.deleteindex == None:
        createIndex(l_args.profile)

    elif l_args.deleteindex != None and l_args.createindex == None:
        deleteIndex(l_args.profile)

    else:
        print('[14]', "нельзя одновременно создавать и удалять индексы (использовать ключи -ci и -di)")  

def index(args):
    checksDb(checksPathes(lambda_index(args)))

def testmode10(args):
    '''Режим оставлен для тестирования в продуктовых средах, например с фс, не хранящих дату создания файла.
        Выводит 10 первых строк талицы в виде кортежа (массива)'''
    print(testmode10Query(args.profile))
    # с его помощью узнал что на fs без хранения даты создания файла она записывается датой модификации