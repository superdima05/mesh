import os
import sys
import json
from getpass import getpass
import mesh

RUNTIME_ARGS = {
    "debug": False,
    "json": False
}

def cache_authentication (login, password):
    login_file = open(".mesh_login", "wr")
    login_file.write(login, password)
    login_file.close()


def authenticate (login = "", password = ""):
    # Currently, this function is pointless due to the fact that mesh.auth()
    # function can't work with login data correctly

    if os.path.exists(".mesh_login"):
        login_file.open(".mesh_login", "r")
        data = login_file.read()
        login_file.close()

        login = data.split(" ") [0]
        password = data.split(" ") [1]
        demo = False
    else:
        login = ""
        password = ""
        demo = True

    return mesh.auth(demo, login, password)


def display_answers(link):
    if RUNTIME_ARGS ["json"]:
        json_data = mesh.fetch_json(authenticate(), link)
        print(json.dumps(json_data, ensure_ascii = False))
    
    else:
        answers = mesh.get_answers(link)
        
        for task_number, task in enumerate(answers):
            print("Вопрос %d: %s" % (task_number + 1, task [0]))
            print("\tОтвет: %s\n" % task [1])


def print_test_info(test_url):
    information = mesh.fetch_description(test_url)

    if RUNTIME_ARGS ["json"]:
        print(json.dumps(information, ensure_ascii = False))
    
    else:
        print("Название:", information ["name"])
        print("Описание:", information ["description"])
        print("Кол-во вопросов:", information ["questions_number"])
        print("ID теста:", information ["test_id"])


def print_help ():
    print("\nИспользование: python(3) launcher.py [ПАРАМЕТРЫ] *test_url")
    print("\nДоступные параметры:")
    print("\t*test_url      Запускает интерактивный режим. Программа попросит вас ввести ссылку на тест")
    print("\t--json         Выводит информацию в виде JSON")
    print("\t--debug        Включает режим отладки (Пока не работает)")
    print("\t--info         Выводит информацию о тесте")
    print("\t--cache-auth   Локально сохраняет ваши данные входа для последующих запросов")
    print("\t--help         Эм... Это меню. Показывет все возможные опции")
    print("\nДанная программа и зависящая от неё библиотека mesh лицензирована под GNU General Public Licence v3 (https://antirao.ru/gpltrans/fdlru.pdf). ")


def main ():
    program_args = sys.argv
    
    if "--help" in program_args:
        print_help()
        exit()

    if "--cache-auth" in program_args:
        login = input("Your username: ")
        password = getpass("Your password: ")

        cache_authentication(login, password)
        exit()
   
    if "--debug" in program_args:
        print("Warning! Currently, debugging is not implemented in the library!")
        RUNTIME_ARGS ["debug"] = True
    
    if "--json" in program_args:
        RUNTIME_ARGS ["json"] = True
  
    
    if "uchebnik.mos.ru" in program_args [-1]:
        link = program_args [-1]
    else:
        link = input("Введите ссылку на тест: ")

    
    if "--info" in program_args:
        print_test_info(link)
    else:
        display_answers(link)

main()
