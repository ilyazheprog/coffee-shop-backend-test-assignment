from modules.crypto.main import encrypt

fields = [
    "id",
    "domain",
    "encrypt_login",
    "encrypt_password",
    "encrypt_path_to_panel",
    "location_id",
    "is_available",
    "limit_count_keys",
]

data = [
    [1, "test.ru", encrypt("log"), encrypt("pswd"), encrypt("path"), 1, True, 2],
]
