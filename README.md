Сервис доставки магазина "Сласти от всех напастей".


Запуск приложения на локальной машине:
1) Установка файлов 
   >git clone https://github.com/AntonovAleksandr/YandexSchoolProject
   
2) Загрузка связай 
   >pip3 install -r requirements.txt
   
3) Запустить файл 
   >main.py
   
4) Приступить к работе приложения по адресу
   >http://0.0.0.0:8080/


Запуск и создание виртуального окружения:
1) Установка файлов 
   >git clone https://github.com/AntonovAleksandr/YandexSchoolProject
   
2) Переход в директорию проекта 
   >cd YandexSchoolProject
   
3) Установка и активация venv 
   >pip install virtualenv
   >virtualenv venv 
   >source venv/bin/activate
   
4) Подготовка связей
   >pip insyall -r requirements.txt
   
5) Открыть в редакторе main.py и заменить строку app.run(host='0.0.0.0', port="8080") на 
   >serve(app, host='0.0.0.0', port="8080")
   
5) Запуск исполняймого файла
   >python 3 main.py
   

Приложение размещено на виртуальной машине. Доступ к работе с ним возможен по адресу: 
0.0.0.0:8080, или по адресу 130.193.59.78

