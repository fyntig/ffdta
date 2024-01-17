Bременной архив (Date-time file archive),
Используется в сочетании с другими программами для не срочного копирования большого числа файлов
Программа создаёт таблицу соответствий времени последнего изменения файлов,
Отдаёт ссылки на N самых старых файлов, которые ещё не отдавались (либо файлов, изменённых после ДАТА-ВРЕМЯ)
<br /><br />
Использовать можно например так:<br />
python3 ffdta create MyProfile -f /home/admin/myapp; python3 ffdta index MyProfile -ci yes<br />
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -od yes); do mkdir /mountedfsfornewserver$file -p; done<br />
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -of yes); do cp "$file" /mountedfsfornewserver$file; done<br />
Запускать можно в цикле по -n КОЛИЧЕСТВО_ФАЙЛОВ, тогда в случае прерывания можно будет продолжить с последнего фрагмента<br />
Затем через некоторое время когда всё будет скопировано:<br />
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -od yes -d 2023-10-20T00:00:00.000000); do mkdir /mountedfsfornewserver$file -p; done<br />
for file in $(python3 ffdta use MyProfile -f /home/admin/myapp -of yes -d 2023-10-20T00:00:00.000000); do cp "$file" /mountedfsfornewserver$file; done<br />
