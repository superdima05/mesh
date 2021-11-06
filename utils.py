import re


def convert_latex(string):
    string = string.replace("\\", "").replace("cdot", "*").replace("ge", ">=").replace("le", "<=")

    simple_transforms = {
        "\^circ": ["^circ", " градусов"],
        "bigtriangleup": ["bigtriangleup", "треугольник"],
        "angle": ["angle", "/_"],
    }

    for regex, changes in simple_transforms.items():
        index = re.compile(regex)

        for _ in index.findall(string):
            string = string.replace(changes[0], changes[1])

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


def remove_soft_hypen(sentence):
    sentence = sentence.replace('\xad', '')
    sentence = sentence.replace('\u00ad', '')
    sentence = sentence.replace('\N{SOFT HYPHEN}', '')

    return sentence


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