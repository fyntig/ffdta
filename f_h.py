Version = "0.1.1223"

"""
Тут оставлю комментарии по улучшению программы, которые сразу реализовывать не буду:
1) Загрузка списка путей из файла или по маске, аналогично удаление списка путей
2) Дополнительный мод CLEAR, который делает check для всех путей верхнего уровня (не вложенных в другие)
3) режим use, который отдаёт только те которые изменились после даты, не добавляя новые
4) может быть случай бд без таблицы (use до create), ошибка обрабатывается, но потом нельзя повторить create - сделать проверку с дропом файла и нормальным созданием в случае креэйт того что уже есть

рекомендованный алгоритм работы: создать базу, создать индекс, скопировать структуру каталогов, копировать пачками файлы

"""