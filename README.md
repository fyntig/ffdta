Bременной архив (Date-time file archive),
Используется в сочетании с другими программами для не срочного копирования большого числа файлов
Программа создаёт таблицу соответствий времени последнего изменения файлов,
Отдаёт ссылки на N самых старых файлов, которые ещё не отдавались (либо файлов, изменённых после ДАТА-ВРЕМЯ)

Использовать можно например так:
python3 ffdta create MyProfile -f /home/admin/myapp; python3 ffdta index MyProfile -ci yes
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -od yes); do mkdir /mountedfsfornewserver$file -p; done
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -of yes); do cp "$file" /mountedfsfornewserver$file; done
Запускать можно в цикле по -n КОЛИЧЕСТВО_ФАЙЛОВ, тогда в случае прерывания можно будет продолжить с последнего фрагмента
Затем через некоторое время когда всё будет скопировано:
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -od yes -d 2023-10-20T00:00:00.000000); do mkdir /mountedfsfornewserver$file -p; done
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -of yes -d 2023-10-20T00:00:00.000000); do cp "$file" /mountedfsfornewserver$file; done
