# libmesh (mesh)

[![pyversion][pyversion-image]][pyversion-url]
[![pypi][pypi-image]][pypi-url]

[pyversion-image]: https://img.shields.io/pypi/pyversions/libmesh
[pyversion-url]: https://pypi.org/project/libmesh/
[pypi-image]: https://img.shields.io/pypi/v/libmesh.svg?style=flat
[pypi-url]: https://pypi.org/project/libmesh/

# Текущий статус 🗿
  [:heavy_check_mark:] Библиотека в рабочем состоянии (06.11.2021).
    
# Благодарности 🙏
 - [kinda-cookie-monster](https://github.com/kinda-cookie-monster)
 - [6x88y9](https://vk.com/6x88y9)
 - [mishailovic](https://github.com/mishailovic)
 - [Fedy1661](https://github.com/Fedy1661)

# Проекты, основанные на этой библиотеке
   - [Telegram бот](https://t.me/CDSansbot), Разработчик: [zsaz](https://github.com/superdima05)
   - [Сайт](https://mash.hotaru.ga/), Разработчик: [mishailovic](https://github.com/mishailovic)
   - `launcher.py` (Находится в этом репозитории), Разработчик: [kinda-cookie-monster](https://github.com/kinda-cookie-monster)

# Требования
- Python 3.9+
- requests (`pip install requests`)

# Установка ⚙️
## PyPI
- `pip install libmesh`
## GitHub
- `pip install git+git://github.com/superdima05/mesh`

# Пример получения ответов на тест
## Python код
```python
import mesh
answers = mesh.get_answers("https://uchebnik.mos.ru/exam/test/view_test/191202/")
for i in answers:
    print(i[0], i[1])
```

## meshLauncher
```meshLauncher https://uchebnik.mos.ru/exam/test/view_test/191202/```

# А что это за файл - `scripts/meshLauncher`?

Это отдельное приложение, которое основано на данной библтотеке, и является ярким примером использования различных функций, которые вам доступны. Также на случай, если вам быстро нужны ответы на тест или вы занимаетесь разработкой библиотеки, эта консольная программка также поможет в этом.

1. Установите библиотеку (см. выше)
3. Введите: `meshLauncher`, чтобы увидеть все доступные параметры.
