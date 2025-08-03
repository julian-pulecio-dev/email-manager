def get_case_insensitive_value(dictionary:dict, key_word:str):
    return next((v for k, v in dictionary.items() if k.lower() == key_word.lower()), None)

