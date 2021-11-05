import re, requests, json, hashlib

def auth ():
    url = "https://uchebnik.mos.ru/api/sessions/demo"
    session_data = {"login": "", "password_hash2": ""}

    session_response = requests.post(
        url = url,
        data = json.dumps(session_data),
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json; charset=UTF-8"
        }
    )

    return session_response.json()


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


def fetch_description(mesh_url):
    auth_data = auth()
    test_variant = get_variant(mesh_url)
    url = f"https://uchebnik.mos.ru/webtests/exam/rest/secure/api/spec/bind/{test_variant}"

    request_cookies = {
        "auth_token": auth_data["authentication_token"],
        "profile_id": str(auth_data["id"]),
        "profile_type": "student",
        "user_id": str(auth_data["id"]),
        "udacl": "resh"
    }

    task_response = requests.get(
        url = url,
        cookies = request_cookies,
        headers = {"Content-type": "application/json"}
    )

    response = task_response.json()

    description = {
        "name": remove_soft_hypen(response["name"]),
        "description": remove_soft_hypen(response["description"]),
        "questions_number": response["questions_per_variant_count"],
        "test_id": response ["spec_id"]
    }

    return description


def remove_soft_hypen(sentence):
    sentence = sentence.replace('\xad', '')
    sentence = sentence.replace('\u00ad', '')
    sentence = sentence.replace('\N{SOFT HYPHEN}', '')

    return sentence


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


def generate_string(string_data):
    parameters = string_data.keys()

    if "text" in parameters:
        text = string_data["text"]
        options = []

        move_point = 0

        for option in string_data["content"]:
            option_type = option["type"]

            if option_type == "content/math":
                option_text = convert_latex(option["content"])
            else:
                option_text = option["content"]

            insert_index = option["position"] + move_point
            text = text[:insert_index] + " " + option_text + " " + text[insert_index:]
            move_point += 2 + len(option_text)

        return text

    elif "string" in parameters:
        return convert_latex(string_data["string"])


    elif "atomic_id" in parameters:
        atomic_type = string_data["atomic_type"]

        if atomic_type == "image":
            return ' (https://uchebnik.mos.ru/cms' + string_data["preview_url"] + ') '

        elif atomic_type == "sound":
            return " (" + string_data["preview_url"] + ") "

        elif atomic_type == "video":
            return " (" + string_data["preview_url"] + ") "


    elif "file" in parameters:
        file_location = string_data["file"]["relative_url"]
        return f" (https://uchebnik.mos.ru/webtests/exam{file_location}) "


    else:
        return ""


def answer_single(answer_data):
    answer_id = answer_data["right_answer"]["id"]

    for entry in answer_data["options"]:
        if entry["id"] == answer_id:
            return generate_string(entry)


def answer_string(answer_data):
    return generate_string(answer_data["right_answer"])


def answer_order(answer_data):
    answer = ''
    order_ids = answer_data["right_answer"]["ids_order"]

    for correct_order_element in order_ids:
        for answer_entry in answer_data["options"]:
            if answer_entry["id"] == correct_order_element:
                answer += generate_string(answer_entry) + ", "
    return answer


def answer_groups(answer_data):
    answer = ''
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

    return answer[:-2]


def answer_table(answer_data):
    answer = ""
    answer_dict = {}

    cell_names = answer_data["options"][0]["content"][0]["table"]["cells"]
    answer_cells = answer_data["right_answer"]["cells"]

    for index in cell_names.keys():
        if index in answer_cells.keys():
            answer_dict[index] = cell_names[index] | answer_cells[index]
        else:
            answer_dict[index] = cell_names[index]

    for row in answer_dict.values():
        values = row.values()
        answer += "; ".join(values) + "\n\t"
    return answer


def answer_multiple(answer_data):
    answer = ''
    answer_ids = answer_data["right_answer"]["ids"]

    for answer_id in answer_ids:
        for answer_entry in answer_data["options"]:
            if answer_entry["id"] == answer_id:
                answer += f"{generate_string(answer_entry)}; "

    return answer[:-2]


def answer_inline_choice_single(answer_data):
    answer = ''
    answer_ids = answer_data["right_answer"]["text_position_answer"]

    for field_num, answer_id in enumerate(answer_ids):
        entry_options = answer_data["text_position"][field_num]["options"]

        for entry in entry_options:
            if entry["id"] == answer_id["id"]:
                answer += f"{generate_string(entry)}; "

    return answer[:-2]


def answer_number(answer_data):
    return str(answer_data["right_answer"]["number"])


def answer_match(answer_data):
    answer = ''
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
    return answer


def answer_gap_match_text(answer_data):
    answer = ''
    answer_ids = answer_data["right_answer"]["text_position_answer"]

    for answer_id in answer_ids:
        for answer_option in answer_data["options"]:
            if answer_id["id"] == answer_option["id"]:
                answer += f"{generate_string(answer_option)}; "

    return answer[:-2]


types_of_answers = {
    "answer/match": answer_match,
    "answer/order": answer_order,
    "answer/number": answer_number,
    "answer/groups": answer_groups,
    "answer/table": answer_table,
    "answer/string": answer_string,
    "answer/single": answer_single,
    "answer/multiple": answer_multiple,
    "answer/gap/match/text": answer_gap_match_text,
    "answer/inline/choice/single": answer_inline_choice_single,
}


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

        if answer_type in types_of_answers:
            answer = types_of_answers[answer_type](answer_data)
        else:
            borked.append([answer_type, question_data, answer_data])

        answers.append([statement, answer])
    
    if returnBorked: return answers, borked
    else:            return answers
