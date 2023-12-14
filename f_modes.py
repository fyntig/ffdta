from f_h import Version

#-----------------------

def f_swich(dict, exp, default=None):
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
    if not dict.get(exp):
        dict.get(exp)
    else:
        return default # впринципе default-значение можно определить и в самом словаре

#-----------------------

def help(args):    
    print(f'Bременной архив v{Version}') 
    print("""Для вывод раздела помощи используйте команду с флагом -h или --help"""
    )

def create(args):
    print('Режим:', args.mode) #!!!

def delete(args):
    print('Режим:', args.mode) #!!!

def use(args):
    print('Режим:', args.mode,"fgfgf") #!!!    

def list(args):
    print('Режим:', args.mode) #!!!
