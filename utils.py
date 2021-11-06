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