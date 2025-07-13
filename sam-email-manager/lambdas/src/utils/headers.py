import os

def get_case_insensitive_value(dictionary:dict, key_word:str):
    return next((v for k, v in dictionary.items() if k.lower() == key_word.lower()), None)

def get_headers():
    return {
        "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,Accept,Accept-Encoding,Accept-Language,User-Agent,Access-Control-Allow-Origin",
        "Content-Type": "application/json"
    }