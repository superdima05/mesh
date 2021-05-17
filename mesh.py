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


def fetch_json (auth_data, test_variant, test_type):
    url = "https://uchebnik.mos.ru/exam/rest/secure/testplayer/group"

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
    
    return json.loads(task_responce.text)["training_tasks"]


def get_answers (mesh_url):
    answers = []
    broken_types = []
    
    auth_data = auth()
    test_variant = get_variant(mesh_url)
    test_type = get_type(mesh_url)

    task_contents = fetch_json(auth_data, test_variant, test_type)
    
    for question in task_contents:
        question_text = ""
        final_answer = ""

        answer_info = question["test_task"]["answer"]
        answer_type = answer_info["type"]

        # Составляем условие задания
        for que_entry in question["test_task"]["question_elements"]:
            if que_entry["type"] == "content/text":
                question_text += que_entry["text"] + " "

            elif que_entry["type"] == "content/atomic":
                if que_entry["atomic_type"] == "image": 
                    url = f'(https://uchebnik.mos.ru/cms{que_entry["preview_url"]})'
                
                elif que_entry["atomic_type"] == "video": 
                    url = f'({que_entry["preview_url"]})'

                question_text += f"\n{url}"

        # Просматриваем каждый вид заданий и находим верный ответ
        if answer_type == "answer/single":
            answer_id = answer_info["right_answer"]["id"]
            
            for entry in answer_info["options"]:
                if entry["id"] == answer_id: 
                    final_answer = entry["text"]

        
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

                    elif answer_entry["id"] == group["group_id"]: 
                        group_name = answer_entry["text"]

                final_answer += f"{group_name}:\n\t{group_elements}"
            
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
