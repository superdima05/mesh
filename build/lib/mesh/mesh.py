import re, requests, json, hashlib
from mesh.answers import *


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
