import re, requests, json, hashlib

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


def fetch_json (auth_data, mesh_url):
    url = "https://uchebnik.mos.ru/exam/rest/secure/testplayer/group"

    test_variant = get_variant(mesh_url)
    test_type    = get_type(mesh_url)

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
    task_response = requests.post(
        url = url,
        data = json.dumps(request_data),
        cookies = request_cookies,
        headers = {"Content-type": "application/json"}      
    )

    return task_response.json() 


def convert_latex (string):
    string = string.replace("\\", "").replace("cdot", "*").replace("ge", ">=").replace("le", "<=")

    simple_transforms = {
        "\^circ"       : ["^circ", " градусов"],
        "bigtriangleup": ["bigtriangleup", "треугольник"],
        "angle"        : ["angle", "/_"],
    }
    
    for regex, changes in simple_transforms.items():
        index = re.compile(regex)

        for _ in index.findall(string): 
            string = string.replace(changes [0], changes [1])
    

    fraction = re.compile("frac{(.*?)}{(.*?)}")
    square_root = re.compile("sqrt{(.*?)}")
    power = re.compile("(.*?)\^(.*)")

    for i in fraction.findall(string):
        string = string.replace("frac {" + str(i[0]) + "}{" + str(i[1]) + "}", str(i[0]) + "/" + str(i[1]))
    
    for i in square_root.findall(string):
        string = string.replace("sqrt{" + str(i) + "}", "корень из " + str(i))
    
    for i in power.findall(string):
        string = string.replace(str(i[0]) + "^" + str(i[1]), str(i[0]) + " в степени " + str(i[1]))
    
    return string


def generate_string (string_data):
    parameters = string_data.keys()

    if "text" in parameters:
        text = string_data ["text"]
        options = []

        move_point = 0

        for option in string_data ["content"]:
            insert_index = option ["position"] + move_point
            text = text [0:insert_index] + "{}" + text [insert_index:]
            move_point += 2

            option_type = option ["type"]

            if option_type == "content/math":
                option_text = convert_latex(option ["content"])
            else:
                option_text = option ["content"]

            options.append(f" {option_text} ")

        return text.format(*options)

    elif "string" in parameters:
        return convert_latex(string_data ["string"])
   
    elif "atomic_type" in parameters:
        if string_data ["atomic_type"] == "image": 
            return f' (https://uchebnik.mos.ru/cms{string_data ["preview_url"]}) '
                
        elif string_data ["atomic_type"] == "video": 
            return f' ({string_data ["preview_url"]}) '

    elif "file" in parameters:
        file_location = string_data ["file"] ["relative_url"]
        return f" (https://uchebnik.mos.ru/webtests/exam{file_location}) " 

    else:
        return ""


def get_answers (url, returnBorked = False):
    answers = []
    borked = []
    
    auth_data = auth()
    task_answers = fetch_json(auth_data, url)

    for exercise in task_answers ["training_tasks"]:
        statement = ""
        answer = ""

        question_data = exercise ["test_task"] ["question_elements"]
        answer_data   = exercise ["test_task"] ["answer"]
        answer_type   = answer_data ["type"]

        for string_chunk in question_data:
            statement += generate_string(string_chunk)

        if answer_type == "answer/single":
            answer_id = answer_data ["right_answer"] ["id"]
            
            for entry in answer_data ["options"]:
                if entry ["id"] == answer_id: 
                    answer = generate_string(entry)

        
        elif answer_type == "answer/string": 
            answer = generate_string(answer_data ["right_answer"])
        
        
        elif answer_type == "answer/order":
            order_ids = answer_data["right_answer"]["ids_order"]

            for correct_order_element in order_ids:
                for answer_entry in answer_data["options"]:
                    if answer_entry["id"] == correct_order_element:
                        answer += generate_string(answer_entry) + ", "


        elif answer_type == "answer/groups":
            correct_groups = answer_data["right_answer"]["groups"]

            for group in correct_groups:
                group_name = ""
                group_elements = ""

                for answer_entry in answer_data["options"]:
                    if answer_entry["id"] in group["options_ids"]:
                        group_elements += generate_string(answer_entry) + ",\n\t"

                    elif answer_entry["id"] == group["group_id"]: 
                        group_name = generate_string(answer_entry)

                answer += f"{group_name}:\n\t{group_elements}"
            
            answer = answer[:-2]


        elif answer_type == "answer/multiple":
            answer_ids = answer_data["right_answer"]["ids"]

            for answer_id in answer_ids:
                for answer_entry in answer_data["options"]:
                    if answer_entry["id"] == answer_id:
                        answer += f"{generate_string(answer_entry)}; "

            answer = answer[:-2]


        elif answer_type == "answer/inline/choice/single":
            answer_ids = answer_data["right_answer"]["text_position_answer"]

            for field_num, answer_id in enumerate(answer_ids):
                entry_options = answer_data["text_position"][field_num]["options"]
                
                for entry in entry_options:
                    if entry["id"] == answer_id["id"]:
                        answer += f"{generate_string(entry)}; "

            answer = answer[:-2]


        elif answer_type == "answer/number":
            answer = str(answer_data["right_answer"]["number"])


        elif answer_type == "answer/match":
            correct_elements = answer_data["right_answer"]["match"]

            for key, value in correct_elements.items():
                key_name = ""
                value_name = ""

                for answer_entry in answer_data["options"]:
                    if answer_entry["id"] == key: 
                        key_name = generate_string(answer_entry)
                    elif answer_entry["id"] == value[0]: 
                        value_name = generate_string(answer_entry)

                answer += f" \n{key_name}: {value_name}"


        elif answer_type == "answer/gap/match/text":
            answer_ids = answer_data["right_answer"]["text_position_answer"]

            for answer_id in answer_ids:
                for answer_option in answer_data["options"]:
                    if answer_id["id"] == answer_option["id"]: 
                        answer += f"{generate_string(answer_option)}; "

            answer = answer[:-2]

        else:
            borked.append([answer_type, question_data, answer_data])

        answers.append([statement, answer])
    
    if returnBorked:
        return answers, borked
    else:
        return answers


if __name__ == '__main__':
    uri = input('Введите ссылку: ').strip()
    answers = get_answers(uri)
    for question, answer in answers:
        print(question)
        print('\t', answer)
