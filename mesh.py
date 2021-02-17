import requests, json, random, urllib.parse, os, hashlib, re


def auth(demo=True):
    login = "ЛОГИН К МЭШ"
    password = "ПАРОЛЬ К МЭШ"

    f = ""
    if os.path.exists("last"):
        f2 = open("last", "r")
        f = f2.read()
        f2.close()
    if demo:
        url = "https://uchebnik.mos.ru/api/sessions/demo"
    else:
        url = "https://uchebnik.mos.ru/api/sessions"
    if f != "":
        try:
            f = json.loads(f)
        except Exception:
            f = ""
        if "id" in f:
            url2 = "https://uchebnik.mos.ru/api/users/" + str(f["id"])
            cookies = {
                "auth_token": f["authentication_token"],
                "user_id": str(f["profiles"][0]["user_id"]),
                "profile_id": str(f["id"]),
                "udacl": "resh",
            }
            r = requests.get(
                url2, headers={"Content-type": "application/json"}, cookies=cookies
            )
            if r.status_code != 200:
                data = {
                    "login": login,
                    "password_hash2": hashlib.md5(password.encode()).hexdigest(),
                }
                r = requests.post(
                    url,
                    data=json.dumps(data),
                    headers={
                        "Content-type": "application/json",
                        "Accept": "application/json; charset=UTF-8",
                    },
                )
                if r.status_code == 200:
                    f2 = open("last", "w")
                    f2.write(r.text)
                    f2.close()
                    return json.loads(r.text)
            else:
                return f


def checkans(data, cookies):
    url = "https://uchebnik.mos.ru/exam/rest/secure/api/training/result_statistic"
    r = requests.post(
        url,
        data=json.dumps(data),
        cookies=cookies,
        headers={"Content-type": "application/json"},
    )
    r = json.loads(r.text)
    for i in data["answers"]:
        try:
            if data["answers"][i]["correct"] == 1:
                return True
        except Exception:
            pass
    if r["tasks_answered_correct_count"] == 1:
        return True
    else:
        return False


# Фикс. Спасибо, https://vk.com/6x88y9
def get_variant(url):
    url = urllib.parse.urlparse(url).path
    url = url.split("/")
    return url[4]


def math(string):
    string = string.replace("\\", "")
    r = re.compile("dfrac{(.*?)}{(.*?)}")
    for i in r.findall(string):
        string = string.replace(
            "dfrac{" + str(i[0]) + "}{" + str(i[1]) + "}", str(i[0]) + "/" + str(i[1])
        )
    string = string.replace("cdot", "*")
    r = re.compile("sqrt{(.*?)}")
    for i in r.findall(string):
        string = string.replace("sqrt{" + str(i) + "}", "Корень из " + str(i))
    r = re.compile("(.*?)\^(.*)")
    for i in r.findall(string):
        string = string.replace(
            str(i[0]) + "^" + str(i[1]), str(i[0]) + " в степени " + str(i[1])
        )
    return string


# Фикс. Спасибо, https://vk.com/6x88y9
def get_answers(variant, c_type="spec"):
    allanswers = ""

    skip = 0

    unknown = []

    url = "https://uchebnik.mos.ru/exam/rest/secure/api/training/generate"
    data = {"generation_context_type": c_type, "generation_by_id": variant}

    if c_type == "spec":
        url = "https://uchebnik.mos.ru/exam/rest/secure/testplayer/group"  # Спасибо, https://github.com/mishailovic, за нахождение нового endpoint'а в МЭШ! https://github.com/superdima05/mesh/issues/3
        data = {
            "test_type": "training_test",
            "generation_context_type": c_type,
            "generation_by_id": variant,
        }
    if c_type == "homework":
        url = "https://uchebnik.mos.ru/exam/rest/secure/testplayer/group"  # Спасибо, https://github.com/mishailovic, за нахождение нового endpoint'а в МЭШ! https://github.com/superdima05/mesh/issues/3
        data = {
            "test_type": "training_test",
            "generation_context_type": "homework",
            "generation_by_id": variant,
        }

    authd = auth()

    cookies = {
        "auth_token": authd["authentication_token"],
        "profile_id": str(authd["profiles"][0]["user_id"]),
        "profile_id": str(authd["id"]),
        "udacl": "resh",
    }

    r = requests.post(
        url,
        data=json.dumps(data),
        cookies=cookies,
        headers={"Content-type": "application/json"},
    )
    r = json.loads(r.text)["training_tasks"]

    data2 = {"answers": {}}
    for i in r:
        # print(i['test_task'])
        data2["answers"][i["test_task"]["id"]] = None

    for i in r:
        if i["test_task"]["answer"]["type"] == "answer/string":
            data2["answers"][i["test_task"]["id"]] = {
                "string": i["test_task"]["answer"]["right_answer"]["string"],
                "@answer_type": i["test_task"]["answer"]["type"],
                "correct": 1,
            }
            if checkans(data2, cookies):
                temp2 = ""
                wa = 0
                for n in i["test_task"]["question_elements"]:
                    if "text" in n:
                        temp2 = temp2 + n["text"].strip() + " "
                    if "content" in n:
                        if n["content"] == []:
                            continue
                        if n["content"][0]["type"] == "content/math":
                            temp2 = temp2 + math(n["content"][0]["content"]) + " "
                    if "relative_url" in n:
                        if wa == 0:
                            temp2 = temp2 + n["relative_url"]
                            wa = 1
                temp2 = (
                    "title: "
                    + temp2
                    + " answer:"
                    + i["test_task"]["answer"]["right_answer"]["string"]
                )
                allanswers = allanswers + temp2 + "\n"
        elif i["test_task"]["answer"]["type"] == "answer/single":
            for x in i["test_task"]["answer"]["options"]:
                if i["test_task"]["answer"]["right_answer"]["id"] != None:
                    if i["test_task"]["answer"]["right_answer"]["id"] != x["id"]:
                        continue
                    else:
                        data2["answers"][i["test_task"]["id"]] = {
                            "id": x["id"],
                            "@answer_type": i["test_task"]["answer"]["type"],
                            "correct": 1,
                        }
                else:
                    data2["answers"][i["test_task"]["id"]] = {
                        "id": x["id"],
                        "@answer_type": i["test_task"]["answer"]["type"],
                    }
                if checkans(data2, cookies):
                    temp = ""
                    temp2 = ""
                    wa = 0
                    for c in i["test_task"]["question_elements"]:
                        if "text" in c:
                            temp = temp + c["text"].strip() + " "
                        if "content" in c:
                            if c["content"] != []:
                                if c["content"][0]["type"] == "content/math":
                                    temp = temp + math(c["content"][0]["content"]) + " "
                        if "relative_url" in c:
                            if wa == 0:
                                temp = temp + c["relative_url"]
                                wa = 1
                    if x["content"] != []:
                        if x["content"][0]["type"] == "content/math":
                            x["text"] = x["text"] + math(x["content"][0]["content"])
                    temp2 = "title: " + temp2 + temp + " answer: " + x["text"]
                    temp2 = temp2.strip() + "\n"
                    allanswers = allanswers + temp2
        elif i["test_task"]["answer"]["type"] == "answer/order":
            c = i["test_task"]["answer"]["options"]
            if i["test_task"]["answer"]["right_answer"]["ids_order"] != None:
                data2["answers"][i["test_task"]["id"]] = {
                    "id": i["test_task"]["answer"]["right_answer"]["ids_order"],
                    "@answer_type": i["test_task"]["answer"]["type"],
                    "correct": 1,
                }
            while checkans(data2, cookies) == False:
                random.shuffle(c)
                temp = []
                for x in c:
                    temp.append(x["id"])
                data2["answers"][i["test_task"]["id"]] = {
                    "ids_order": temp,
                    "@answer_type": i["test_task"]["answer"]["type"],
                }
            temp2 = ""
            wa = 0
            for n in i["test_task"]["question_elements"]:
                if "text" in n:
                    temp2 = temp2 + n["text"].strip() + " "
                if n["content"] != []:
                    if n["content"][0]["type"] == "content/math":
                        temp = temp + math(n["content"][0]["content"]) + " "
                if "relative_url" in n:
                    if wa == 0:
                        temp2 = temp2 + n["relative_url"]
                        wa = 1
            temp2 = "title: " + temp2 + " answer:"
            for x in c:
                for b in temp:
                    if x["id"] == b:
                        if x["content"] != []:
                            if x["content"][0]["type"] == "content/math":
                                x["text"] = x["text"] + math(x["content"][0]["content"])
                        temp2 = temp2 + x["text"] + ", "
            temp2 = temp2[:-2]
            allanswers = allanswers + temp2 + "\n"
        elif i["test_task"]["answer"]["type"] == "answer/number":
            if i["test_task"]["answer"]["right_answer"]["number"] != None:
                data2["answers"][i["test_task"]["id"]] = {
                    "number": i["test_task"]["answer"]["right_answer"]["number"],
                    "@answer_type": i["test_task"]["answer"]["type"],
                    "correct": 1,
                }
            for b in range(0, 100):
                temp2 = ""
                if i["test_task"]["answer"]["right_answer"]["number"] == None:
                    data2["answers"][i["test_task"]["id"]] = {
                        "number": b,
                        "@answer_type": i["test_task"]["answer"]["type"],
                    }
                if checkans(data2, cookies):
                    temp2 = str(b)
                    break
                else:
                    data2["answers"][i["test_task"]["id"]] = None
            if temp2 == "":
                b = "No answer. Out of range (0-100)."
            temp2 = ""
            wa = 0
            for n in i["test_task"]["question_elements"]:
                if "text" in n:
                    temp2 = temp2 + n["text"].strip() + " "
                if n["content"] != []:
                    if n["content"][0]["type"] == "content/math":
                        temp2 = temp2 + math(n["content"][0]["content"]) + " "
                if "relative_url" in n:
                    if wa == 0:
                        temp2 = temp2 + n["relative_url"]
                        wa = 1
            temp2 = "title: " + temp2 + " answer:" + str(b)
            allanswers = allanswers + temp2 + "\n"
        elif i["test_task"]["answer"]["type"] == "answer/multiple":
            if i["test_task"]["answer"]["right_answer"]["ids"] != None:
                data2["answers"][i["test_task"]["id"]] = {
                    "ids": i["test_task"]["answer"]["right_answer"]["ids"],
                    "@answer_type": i["test_task"]["answer"]["type"],
                    "correct": 1,
                }
            c = i["test_task"]["answer"]["options"]
            while checkans(data2, cookies) == False:
                data2["answers"][i["test_task"]["id"]] = {
                    "ids": [],
                    "@answer_type": i["test_task"]["answer"]["type"],
                }
                for b in c:
                    if random.randint(0, 1) == 1:
                        data2["answers"][i["test_task"]["id"]]["ids"].append(b["id"])
            temp2 = ""
            wa = 0
            for n in i["test_task"]["question_elements"]:
                if "text" in n:
                    temp2 = temp2 + n["text"].strip() + " "
                if n["content"] != []:
                    if n["content"][0]["type"] == "content/math":
                        temp2 = temp2 + math(n["content"][0]["content"]) + " "
                if "relative_url" in n:
                    if wa == 0:
                        temp2 = temp2 + n["relative_url"]
                        wa = 1
            temp2 = "title: " + temp2 + " answer:"
            for x in c:
                for b in data2["answers"][i["test_task"]["id"]]["ids"]:
                    if x["id"] == b:
                        if x["content"] != []:
                            if x["content"][0]["type"] == "content/math":
                                x["text"] = x["text"] + math(x["content"][0]["content"])
                        temp2 = temp2 + x["text"] + ", "
            temp2 = temp2[:-2]
            allanswers = allanswers + temp2 + "\n"
        elif i["test_task"]["answer"]["type"] == "answer/groups":
            while checkans(data2, cookies) == False:
                data2["answers"][i["test_task"]["id"]] = {
                    "groups": [],
                    "@answer_type": i["test_task"]["answer"]["type"],
                }
                for b in i["test_task"]["answer"]["options"]:
                    if "type" in b and b["type"] == "option_type/group":
                        data2["answers"][i["test_task"]["id"]]["groups"].append(
                            {"group_id": b["id"], "options_ids": []}
                        )
                for x in i["test_task"]["answer"]["options"]:
                    data2["answers"][i["test_task"]["id"]]["groups"][
                        random.randint(
                            0, len(data2["answers"][i["test_task"]["id"]]["groups"]) - 1
                        )
                    ]["options_ids"].append(x["id"])
                print(data2["answers"][i["test_task"]["id"]])
            continue
        elif i["test_task"]["answer"]["type"] == "answer/match":
            if i["test_task"]["answer"]["right_answer"]["match"] != None:
                data2["answers"][i["test_task"]["id"]] = {
                    "match": i["test_task"]["answer"]["right_answer"]["match"],
                    "@answer_type": i["test_task"]["answer"]["type"],
                    "correct": 1,
                }
            while checkans(data2, cookies) == False:
                data2["answers"][i["test_task"]["id"]] = {
                    "match": {},
                    "@answer_type": i["test_task"]["answer"]["type"],
                }
                c = []
                for x in i["test_task"]["answer"]["options"]:
                    if x["type"] == "option_type/match/source":
                        data2["answers"][i["test_task"]["id"]]["match"][x["id"]] = []
                    if x["type"] == "option_type/match/target":
                        c.append(x)
                random.shuffle(c)
                took = []
                for b in c:
                    v = random.choice(
                        list(data2["answers"][i["test_task"]["id"]]["match"].items())
                    )
                    while v in took:
                        v = random.choice(
                            list(
                                data2["answers"][i["test_task"]["id"]]["match"].items()
                            )
                        )
                    took.append(v)
                    data2["answers"][i["test_task"]["id"]]["match"][v[0]].append(
                        b["id"]
                    )
            temp2 = dict(data2["answers"][i["test_task"]["id"]]["match"])
            temp3 = ""
            for n in data2["answers"][i["test_task"]["id"]]["match"].items():
                for x in i["test_task"]["answer"]["options"]:
                    if n[1][0] == x["id"]:
                        if x["content"] != []:
                            if x["content"][0]["type"] == "content/math":
                                x["text"] = x["text"] + math(x["content"][0]["content"])
                        temp2[n[0]] = x["text"]
            for n in data2["answers"][i["test_task"]["id"]]["match"].items():
                for x in i["test_task"]["answer"]["options"]:
                    if n[0] == x["id"]:
                        if x["content"] != []:
                            if x["content"][0]["type"] == "content/math":
                                x["text"] = x["text"] + math(x["content"][0]["content"])
                        temp3 = (
                            "title: "
                            + temp3
                            + x["text"]
                            + " answer:"
                            + temp2[n[0]]
                            + ", "
                        )
            temp3 = temp3[:-2]
            allanswers = allanswers + temp3 + "\n"
        elif i["test_task"]["answer"]["type"] == "answer/inline/choice/single":
            if i["test_task"]["answer"]["right_answer"]["text_position_answer"] != None:
                data2["answers"][i["test_task"]["id"]] = {
                    "match": i["test_task"]["answer"]["right_answer"][
                        "text_position_answer"
                    ],
                    "@answer_type": i["test_task"]["answer"]["type"],
                    "correct": 1,
                }
            temp = (
                "title: " + i["test_task"]["question_elements"][0]["text"] + " answer:"
            )
            while checkans(data2, cookies) == False:
                data2["answers"][i["test_task"]["id"]] = {
                    "text_position_answer": [],
                    "@answer_type": i["test_task"]["answer"]["type"],
                }
                for n in i["test_task"]["answer"]["text_position"]:
                    data2["answers"][i["test_task"]["id"]][
                        "text_position_answer"
                    ].append(
                        {
                            "text_id": n["text_id"],
                            "position_id": n["position_id"],
                            "id": n["options"][
                                random.randint(0, len(n["options"]) - 1)
                            ]["id"],
                        }
                    )
            for n in data2["answers"][i["test_task"]["id"]]["text_position_answer"]:
                for b in i["test_task"]["answer"]["text_position"]:
                    for c in b["options"]:
                        if n["id"] == c["id"]:
                            if c["content"] != []:
                                if c["content"][0]["type"] == "content/math":
                                    c["text"] = c["text"] + math(
                                        c["content"][0]["content"]
                                    )
                            temp = temp + c["text"] + ", "
            temp = temp[:-2]
            allanswers = allanswers + temp + "\n"
        elif i["test_task"]["answer"]["type"] == "answer/gap/match/text":
            temp = (
                "title: " + i["test_task"]["question_elements"][0]["text"] + " answer:"
            )
            c = i["test_task"]["answer"]["options"]

            while skip == 0 and checkans(data2, cookies) == False:
                data2["answers"][i["test_task"]["id"]] = {
                    "text_position_answer": [],
                    "@answer_type": i["test_task"]["answer"]["type"],
                }
                for n in i["test_task"]["answer"]["text_position"]:
                    data2["answers"][i["test_task"]["id"]][
                        "text_position_answer"
                    ].append(
                        {
                            "text_id": n["text_id"],
                            "position_id": n["position_id"],
                            "id": None,
                        }
                    )
                random.shuffle(c)
                if len(i["test_task"]["answer"]["options"]) != len(
                    data2["answers"][i["test_task"]["id"]]["text_position_answer"]
                ):
                    data2["answers"][i["test_task"]["id"]] = None
                    skip = 1
                    continue
                for n in range(
                    0,
                    len(data2["answers"][i["test_task"]["id"]]["text_position_answer"]),
                ):
                    data2["answers"][i["test_task"]["id"]]["text_position_answer"][n][
                        "id"
                    ] = i["test_task"]["answer"]["options"][n]["id"]
            if skip == 1:
                continue
            for n in data2["answers"][i["test_task"]["id"]]["text_position_answer"]:
                for b in i["test_task"]["answer"]["options"]:
                    if n["id"] == b["id"]:
                        if b["content"] != []:
                            if b["content"][0]["type"] == "content/math":
                                b["text"] = b["text"] + math(b["content"][0]["content"])
                        temp = temp + b["text"] + ", "
            temp = temp[:-2]
            allanswers = allanswers + temp + "\n"
        else:
            unknown.append(i["test_task"]["answer"]["type"])
        data2["answers"][i["test_task"]["id"]] = None
    return allanswers, unknown
