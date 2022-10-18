import configparser
import pathlib
from os import path

ROOT_DIRECTORY = path.dirname(pathlib.Path(__file__).parent)
CONFIG_PATH_DIR = pathlib.Path.home() / ".config" / "cloudphoto"
CONFIG_FILENAME = "cloudphotorc"
CONFIGFILE_PATH = str(CONFIG_PATH_DIR / CONFIG_FILENAME)


def read_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(CONFIGFILE_PATH)

    return config


def create_config(access_key, secret_key, bucket_name):
    CONFIG_PATH_DIR.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "bucket": bucket_name,
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "region": "ru-central-1",
        "endpoint_url": "https://storage.yandexcloud.net"
    }

    with open(CONFIGFILE_PATH, "w") as file:
        config.write(file)


def is_configured():
    if path.exists(CONFIGFILE_PATH):
        config = read_config()
        if config["DEFAULT"]:
            return True

    raise Exception("Запустите init")


def get_bucket_name() -> str:
    is_configured()
    return read_config().get("DEFAULT", "bucket")
