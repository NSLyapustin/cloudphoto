import logging
from pathlib import Path

from cloud.config import get_bucket_name
from botocore.exceptions import ClientError
from cloud.session import create_s3_session
from cloud.config import create_config
from .utils import is_album_exist, is_image_exist, get_all_images_key, IMG_EXTENSIONS, DEFAULT_REGION, DEFAULT_ENDPOINT


def is_image(file):
    return file.is_file() and file.suffix in IMG_EXTENSIONS


def upload_img(session, album: str, path: str):
    path = Path(path)
    count = 0

    if not path.is_dir():
        raise Exception(f"Не найдена директория {str(path)}")

    for file in path.iterdir():
        if is_image(file):
            try:
                print(f"Загружаю {file.name}...")
                key = f"{album}/{file.name}"
                session.upload_file(str(file), get_bucket_name(), key)
                count += 1
            except Exception as ex:
                logging.warning(ex)

    if not count:
        raise Exception(f"Не найдены допустимые изображения, подходящие форматы: {IMG_EXTENSIONS}")


def download_img(session, album: str, path: str):
    path = Path(path)
    bucket = get_bucket_name()
    if not is_album_exist(session, bucket, album):
        raise Exception("Album не существует")

    if not path.is_dir():
        raise Exception(f"{str(path)} не является директорией")

    list_object = session.list_objects(Bucket=bucket, Prefix=album + '/', Delimiter='/')
    for key in list_object["Contents"]:
        obj = session.get_object(Bucket=bucket, Key=key["Key"])
        filename = Path(key['Key']).name

        filepath = path / filename
        with filepath.open("wb") as file:
            file.write(obj["Body"].read())


def initialize():
    access_key = input("Введите идентификатор ключа: ")
    secret_access_key = input("Введите ваш секретный ключ: ")
    bucket_name = input("Введите наименование бакета: ")
    try:
        s3 = create_s3_session(access_key, secret_access_key, DEFAULT_ENDPOINT, DEFAULT_REGION)
        s3.create_bucket(Bucket=bucket_name, ACL='public-read-write')
    except ClientError as clientError:
        if clientError.response["Error"]["Code"] != "BucketAlreadyOwnedByYou":
            raise clientError

    create_config(access_key=access_key, secret_key=secret_access_key, bucket_name=bucket_name)


def list_img(session, album):
    bucket = get_bucket_name()

    if not is_album_exist(session, bucket, album):
        raise Exception(f"Альбом '{album}' не существует")

    list_objects = session.list_objects(
        Bucket=bucket,
        Prefix=album + '/',
        Delimiter='/'
    )
    images = []
    for key in list_objects["Contents"]:
        images.append(Path(key["Key"]).name)

    if not len(images):
        raise Exception("Нет изображений.")

    print(f"Изображения в альбоме {album}:")
    for photo_name in images:
        print(f"# {photo_name}")


def list_albums(session):
    bucket = get_bucket_name()
    list_objects = session.list_objects(Bucket=bucket)
    albums = set()
    if "Contents" in list_objects:
        for key in list_objects["Contents"]:
            albums.add(Path(key["Key"]).parent)

    if not len(albums):
        raise Exception(f"В {bucket} нет доступных альбомов")

    print(f"Albums in bucket {bucket}:")
    for album in albums:
        if album.name != "" and album.name != "config":
            print(f"# {album}")


def delete_img(session, album: str, image: str):
    img_key = album + '/' + image
    bucket = get_bucket_name()

    if not is_album_exist(session, bucket, album):
        raise Exception(f"Альбом {album} не существует")

    if not is_image_exist(session, bucket, album, image):
        raise Exception(f"Изображение {image} не сущесвует")

    session.delete_objects(Bucket=bucket, Delete={"Objects": [{"Key": img_key}]})


def delete_album(session, album: str):
    bucket = get_bucket_name()

    if not is_album_exist(session, bucket, album):
        raise Exception(f"Альбом {album} не существует")

    img_keys = get_all_images_key(session, bucket, album)

    session.delete_objects(Bucket=bucket, Delete={"Objects": img_keys})
