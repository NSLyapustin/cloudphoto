import os
import random
import shutil
import string
from pathlib import Path

from jinja2 import Template

from cloud.config import get_bucket_name, ROOT_DIRECTORY

SITE_CONFIGURATION = {
    "ErrorDocument": {"Key": "error.html"},
    "IndexDocument": {"Suffix": "index.html"},
}


def get_albums_data(session, bucket: str):
    albums = {}
    list_objects = session.list_objects(Bucket=bucket)
    for key in list_objects["Contents"]:
        album_img = key["Key"].split("/")
        if len(album_img) != 2:
            continue
        album, img = album_img
        if album in albums:
            albums[album].append(img)
        else:
            albums[album] = [img]

    return albums


def get_template(name):
    template_path = Path(ROOT_DIRECTORY) / "resources" / name
    with open(template_path, "r") as file:
        return file.read()


def save_temporary_template(template) -> str:
    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".html"
    path = Path(ROOT_DIRECTORY) / "temp" / filename
    if not path.parent.exists():
        os.mkdir(path.parent)

    with open(path, "w") as file:
        file.write(template)

    return str(path)


def remove_temporary_dir():
    path = Path(ROOT_DIRECTORY) / "temp"
    shutil.rmtree(path)


def mksite(session):
    bucket = get_bucket_name()
    url = f"https://{bucket}.website.yandexcloud.net"
    albums = get_albums_data(session, bucket)

    template = get_template("album.html")

    albums_rendered = []
    i = 1
    for album, images in albums.items():
        template_name = f"album{i}.html"
        rendered_album = Template(template).render(album=album, images=images, url=url)
        path = save_temporary_template(rendered_album)

        session.upload_file(path, bucket, template_name)
        albums_rendered.append({"name": template_name, "album": album})
        i += 1

    # index page
    template = get_template("index.html")
    rendered_index = Template(template).render(template_objects=albums_rendered)
    path = save_temporary_template(rendered_index)
    session.upload_file(path, bucket, "index.html")

    # error page
    template = get_template("error.html")
    path = save_temporary_template(template)
    session.upload_file(path, bucket, "error.html")

    # site configuration
    session.put_bucket_website(Bucket=bucket, WebsiteConfiguration=SITE_CONFIGURATION)

    remove_temporary_dir()

    print(url)
