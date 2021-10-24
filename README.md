# РешуЦДЗ 

    
# Текущий статус 🗿
  [:heavy_check_mark:] - Метод работает<br>
  [:x:] - Метод не работает
  
  [:heavy_check_mark:] Библиотека в рабочем состоянии (31.08.2021).
    
# Благодарности 🙏
 - Большое спасибо [kinda-cookie-monster](https://github.com/kinda-cookie-monster) за полную переработку библиотеки. [Pull request #1](https://github.com/superdima05/mesh/pull/6) [Pull request #2](https://github.com/superdima05/mesh/pull/7)
 - Большое спасибо https://vk.com/6x88y9 за фикс библиотеки. Обсуждение было [тут](https://github.com/superdima05/mesh/issues/1)
 - Большое спасибо [mishailovic](https://github.com/mishailovic) за нахождения нового endpoint в МЭШ. Обсуждение было [тут](https://github.com/superdima05/mesh/issues/3)

# Проекты, основанные на этой библиотеке
   - [Telegram бот](https://t.me/CDSansbot), Разработчик: [zsaz](https://github.com/superdima05)
   - [Сайт](https://mash.hotaru.ga/), Разработчик: [mishailovic](https://github.com/mishailovic)
    
# Установка ⚙️
  1. Сколнировать репозиторий `git clone https://github.com/superdima05/mesh`
  2. Скопировать файл `mesh.py` в папку к своему проекту.
  3. Добавить `import mesh` в вашем проекте

# Пример
```python
    import mesh
    answers = mesh.get_answers("https://uchebnik.mos.ru/exam/test/view_test/191202/")
    for i in answers:
        print(i[0], i[1])
```
```
$ python mesh.py                                                                              
Введите ссылку: https://uchebnik.mos.ru/exam/test/test_by_binding/15353985/homework/149649387
```