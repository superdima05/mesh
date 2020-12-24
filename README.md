# РешуЦДЗ 

    
# Текущий статус
[:heavy_check_mark:] Работает (25.12.2020)
    
# Благодарности
 - Большое спасибо https://vk.com/6x88y9 за фикс библиотеки. Обсуждение было [тут](https://github.com/superdima05/mesh/issues/1)
    
# Установка
  1. Сколнировать репозиторий `git clone https://github.com/superdima05/mesh`
  2. Скопировать файл `mesh.py` в папку к своему проекту.
  3. В `mesh.py` найти "ЛОГИН К МЭШ" и "ПАРОЛЬ К МЭШ" и изменить их на ваш логин и пароль к МЭШ.
  3. Добавить `import mesh` в вашем проекте
  
# Использование
  [:x:] - Метод не работает
  [:heavy_check_mark:] - Метод работает
  1. [:heavy_check_mark:] Получить номер варинта (если тест имеет только идентификатор) `get_variant(Cсылка на тест. Пример ссылки: https://uchebnik.mos.ru/exam/test/test_by_binding/9792593/homework/120414331?generation_context_type=homework)`
  2. [:heavy_check_mark:] Получить ответы `get_answers(Номер варианта, тип (читать ниже))`
  3. В тип надо укзать либо 'spec', либо 'homework'. Указываем 'spec', если не использовали метод get_variant(). Если использовали, то используем тип 'homework'
