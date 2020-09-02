def prediction_score(prediction):
    return int(round(prediction, 2) * 100)


def predicted(prediction_score):
    if prediction_score < 50:
        return "No"
    else:
        return "Yes"


def age_range_groups(range_groups_ages, age):
    for age_range in range_groups_ages:
        min_age = int(age_range[0])
        max_age = int(age_range[1])
        if age >= min_age and age <= max_age:
            age = f"{min_age}-{max_age}"
            break
    return age


def gen_squares_code(number):
    return number
