from mesh.utils import *


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
