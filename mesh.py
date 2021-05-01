import requests, json, hashlib

def auth (demo = True, login = "", password = ""):
    if demo: 
        url = "https://uchebnik.mos.ru/api/sessions/demo"
    else:
        url = "https://uchebnik.mos.ru/api/sessions"

    session_data = {
        "login": login,
        "password_hash2": hashlib.md5(password.encode()).hexdigest()
    }

    session_response = requests.post(
        url = url,
        data = json.dumps(session_data),
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json; charset=UTF-8"
        }
    )

    if session_response.status_code == 200:
        return json.loads(session_response.text)
    else:
        raise Exception("Unable to log in to uchebnik.mos.ru with provided credentials.")


def get_variant (mesh_url):
    return mesh_url.split("/")[6]


def get_type (mesh_url):
    if mesh_url.split("/")[7] == "homework": return "homework"
    else: return "spec"


def get_answers (mesh_url):
    answers = []
    broken_types = []
    
    # Авторизируемся и отсылаем необходимые куки и данные для получения результатов
    auth_data = auth()
    url = "https://uchebnik.mos.ru/exam/rest/secure/testplayer/group"

    # Получаем номер варианта и тип задания для последующей работы
    test_variant = get_variant(mesh_url)
    test_type = get_type(mesh_url)

    request_data = {
        "test_type": "training_test",
        "generation_context_type": test_type,
        "generation_by_id": test_variant
    }
    request_cookies = {
        "auth_token": auth_data["authentication_token"],
        "profile_id": str(auth_data["id"]),
        "udacl": "resh"
    }
    task_responce = requests.post(
        url = url,
        data = json.dumps(request_data),
        cookies = request_cookies,
        headers = {"Content-type": "application/json"}      
    )

    task_contents = json.loads(task_responce.text)["training_tasks"]
    
    for question in task_contents:
        question_text = ""
        final_answer = ""

        answer_info = question["test_task"]["answer"]
        answer_type = answer_info["type"]

        # На случай если текст вопроса состоит из нескольких частей, добавляем из все
        for question_element in question["test_task"]["question_elements"]:
            question_text += question_element["text"] + " "        

        # Просматриваем каждый вид заданий и находим верный ответ
        if answer_type == "answer/single":
            answer_id = answer_info["right_answer"]["id"]
            
            for entry in answer_info["options"]:
                if entry["id"] == answer_id: final_answer = entry["text"]

        
        elif answer_type == "answer/string": 
            final_answer = answer_info["right_answer"]["string"]
        
        
        elif answer_type == "answer/order":
            order_ids = answer_info["right_answer"]["ids_order"]

            for correct_order_element in order_ids:
                for answer_entry in answer_info["options"]:
                    if answer_entry["id"] == correct_order_element:
                        final_answer += answer_entry["text"] + ", "


        elif answer_type == "answer/groups":
            correct_groups = answer_info["right_answer"]["groups"]

            for group in correct_groups:
                group_name = ""
                group_elements = ""

                for answer_entry in answer_info["options"]:
                    if answer_entry["id"] in group["options_ids"]:
                        group_elements += answer_entry["text"] + ",\n\t"

                    try: 
                        if answer_entry["type"] and answer_entry["id"] == group["group_id"]: 
                            group_name = answer_entry["text"]
                            final_answer += f"{group_name}:\n\t{group_elements} \n"
                    except Exception: 
                        pass

                final_answer = final_answer[:-2]


        elif answer_type == "answer/multiple":
            answer_ids = answer_info["right_answer"]["ids"]

            for answer_id in answer_ids:
                for answer_entry in answer_info["options"]:
                    if answer_entry["id"] == answer_id:
                        final_answer += f"{answer_entry['text']}; "

            final_answer = final_answer[:-2]


        elif answer_type == "answer/inline/choice/single":
            answer_ids = answer_info["right_answer"]["text_position_answer"]

            for field_num, answer_id in enumerate(answer_ids):
                entry_options = answer_info["text_position"][field_num]["options"]
                
                for entry in entry_options:
                    if entry["id"] == answer_id["id"]:
                        final_answer += f"{entry['text']}; "

            final_answer = final_answer[:-2]


        elif answer_type == "answer/number":
            final_answer = str(answer_info["right_answer"]["number"])


        elif answer_type == "answer/match":
            correct_elements = answer_info["right_answer"]["match"]

            for key, value in correct_elements.items():
                key_name = ""
                value_name = ""

                for answer_entry in answer_info["options"]:
                    if answer_entry["id"] == key: 
                        key_name = answer_entry["text"]
                    elif answer_entry["id"] == value[0]: 
                        value_name = answer_entry["text"]

                final_answer += f" \n{key_name}: {value_name}"


        elif answer_type == "answer/gap/match/text":
            answer_ids = answer_info["right_answer"]["text_position_answer"]

            for answer_id in answer_ids:
                for answer_option in answer_info["options"]:
                    if answer_id["id"] == answer_option["id"]: 
                        final_answer += f"{answer_option['text']}; "

            final_answer = final_answer[:-2]


        if final_answer:
            answers.append([question_text, final_answer])
        else:
            broken_types.append(answer_type)

    return answers, broken_types
