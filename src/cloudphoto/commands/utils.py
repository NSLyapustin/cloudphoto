from botocore.exceptions import ClientError

IMG_EXTENSIONS = [".jpg", ".jpeg"]
DEFAULT_ENDPOINT = "https://storage.yandexcloud.net"
DEFAULT_REGION = "ru-central1"

def is_album_exist(session, bucket, album):
    list_objects = session.list_objects(
        Bucket=bucket,
        Prefix=album + '/',
        Delimiter='/',
    )
    if "Contents" in list_objects:
        for _ in list_objects["Contents"]:
            return True
    return False

def is_image_exist(session, bucket, album, photo):
    try:
        key = album + '/' + photo
        session.get_object(Bucket=bucket, Key=key)
    except ClientError as error:
        if error.response["Error"]["Code"] != "NoSuchKey":
            raise error
        return False
    return True

def get_all_images_key(session, bucket: str, album: str):
    list_objects = session.list_objects(
        Bucket=bucket,
        Prefix=album + '/',
        Delimiter='/',
    )["Contents"]
    return [{"Key": img_key.get('Key')} for img_key in list_objects]