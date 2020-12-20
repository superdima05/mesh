# МЭШ

    
# Текущий статус
[:warning:] В данный момент библиотека будет работать, если есть номер **варианта**.</br></br>
[:x:] 10.12.20 МЭШ изменила метод получения варианта. Раньше МЭШ отдавал **вариант** по запросу `"https://uchebnik.mos.ru/exam/rest/secure/api/binding/"+ID теста+"/spec"` и это работало с аккаунтом, созданным на сайте. Теперь этот метод работает только с аккаунтом, созданным школой. Последнего у нас нет.</br></br>
[:information_source:] Так как репозиторий свободный для всех, то можете предлагать свои идеи для решения этой проблемы. Этими действиями вы помежете нам в решении этой проблемы.
    
# Установка
  1. Сколнировать репозиторий `git clone https://github.com/superdima05/mesh`
  2. Скопировать файл mesh.py в папку к своему проекту.
  3. `import mesh`
  
# Использование
  [:x:] - Метод не работает
  [:heavy_check_mark:] - Метод работает
  1. [:x:] Получить номер варинта (если тест имеет только идентификатор) `get_variant(Cсылка на тест. Пример ссылки: https://uchebnik.mos.ru/exam/test/test_by_binding/9792593/homework/120414331?generation_context_type=homework)`
  2. [:heavy_check_mark:] Получить ответы `get_answers(Номер варианта)`
