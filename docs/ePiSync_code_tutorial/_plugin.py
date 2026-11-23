"""ePiSync: the plugin built in the ePiframe_plugin tutorial (Plugin API v2).

Syncs photos from a remote host with rsync, makes thumbnails, adds a watermark
to its photos and shows them on a new WebUI page through a new API endpoint.
https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md
"""

import dataclasses
import shutil
import subprocess
from pathlib import Path

from flask import Response, request, send_file
from flask_login import login_required
from PIL import Image

from epiframe.config.property import ConfigProperty, PropertyType
from epiframe.core.media_types import EXTENSION_TO_TYPE, EXTENSIONS, MIME_PREFIX
from epiframe.core.media_types import TYPE_TO_EXTENSION
from epiframe.photos.model import Photo
from epiframe.plugins.base import PhotoFile
from epiframe.plugins.base import Plugin as PluginBase
from epiframe.processing.imagemagick import ImageMagick, ImageMagickError
from epiframe.sources.local import LocalSource, create_directory
from modules.webuimanager import WebUIManager

THUMBS_DIR = "thumbs"  # inside local_path
THUMB_PREFIX = "thumb_"
WATERMARK = "static/images/watermark.png"  # inside the plugin folder
MARGIN = 10


class Plugin(PluginBase):
    name = "ePiSync"
    author = "ePiframe_plugin tutorial"
    description = (
        "Sync photos with rsync from remote location, generate thumbnails, then add"
        " watermark, API method and a website to view new photos"
    )
    site = "https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md"
    info = "All steps gathered here to create a multi-functional ePiframe plugin"

    # ------------------------------------------------- Step 7: configuration

    def settings(self) -> list[ConfigProperty]:
        enabled = "is_enabled"  # all entries are used only when the plugin is on
        return [
            *super().settings(),  # is_enabled: required
            ConfigProperty(
                "local_path",
                PropertyType.FILE,
                dependency=enabled,
                convert=create_directory,  # the folder is created if missing
            ),
            ConfigProperty("remote_path", dependency=enabled),
            ConfigProperty("remote_host", dependency=enabled),
            ConfigProperty("remote_user", dependency=enabled),
            ConfigProperty(
                "sync_timeout",
                PropertyType.INTEGER,
                min_value=2,
                max_value=10,
                dependency=enabled,
            ),
            ConfigProperty(
                "thumb_width",
                PropertyType.INTEGER,
                min_value=100,
                max_value=400,
                dependency=enabled,
            ),
            ConfigProperty(
                "thumb_height",
                PropertyType.INTEGER,
                min_value=100,
                max_value=300,
                dependency=enabled,
            ),
        ]

    @property
    def local_path(self) -> Path:
        return Path(self.config.get("local_path"))

    # ---------------------------------------------- Step 1: photo collection

    def source_photos(self) -> list[Photo]:
        self.sync()
        photos = self.synced_photos()
        self.make_thumbnails(photos)  # Step 3: thumbnails of new photos
        return photos

    def sync(self) -> None:
        # rsync gets only the files that are not here yet; an argument list (no
        # shell), so values from the configuration can't inject commands
        remote = self.config.get("remote_path").rstrip("/") + "/*"
        command = [
            "rsync",
            f"--timeout={self.config.getint('sync_timeout')}",
            "--ignore-existing",
            f"{self.config.get('remote_user')}@{self.config.get('remote_host')}:{remote}",
            f"{self.local_path}/",
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            # no network or host down: the photos synced before are still shown
            self.logger.warning(f"rsync failed: {result.stderr.strip()}")

    def synced_photos(self) -> list[Photo]:
        # LocalSource lists the photo files (known extensions, sorted); the
        # photos get this plugin's source name
        source = LocalSource(str(self.local_path), False, EXTENSIONS)
        return [dataclasses.replace(p, source=self.source) for p in source.photos()]

    # ---------------------------------------------- Step 2: retrieving photo

    def fetch_photo(self, photo: Photo, directory: Path, name: str) -> Path:
        # (ePiframe does the same when this method is missing: photo.id is a
        # local file - kept here to show the method)
        magick = ImageMagick(self.global_config.get("convert_bin_path"))
        image_format = magick.image_format(photo.id)  # e.g. "JPEG"
        extension = TYPE_TO_EXTENSION[MIME_PREFIX + image_format.lower()]
        target = directory / f"{name}.{extension}"
        shutil.copy(photo.id, target)
        return target

    # ---------------------------------------------------- Step 3: thumbnails

    def thumbnail(self, photo_path: str) -> Path:
        path = Path(photo_path)
        return path.parent / THUMBS_DIR / f"{THUMB_PREFIX}{path.name}"

    def make_thumbnails(self, photos: list[Photo]) -> None:
        size = f"{self.config.get('thumb_width')}x{self.config.get('thumb_height')}"
        magick = ImageMagick(self.global_config.get("convert_bin_path"))
        (self.local_path / THUMBS_DIR).mkdir(exist_ok=True)
        for photo in photos:
            thumbnail = self.thumbnail(photo.id)
            if thumbnail.exists():
                continue
            try:
                magick.run(
                    [photo.id, "-background", "white", "-gravity", "center"]
                    + ["-sample", size, "-extent", size, str(thumbnail)]
                )
            except ImageMagickError as error:
                self.logger.warning(f"No thumbnail of {photo.id}: {error}")

    # ------------------------------------------------- Step 4: watermark

    def postprocess_photo(self, photo: PhotoFile) -> None:
        # only the photos of this source get the watermark (photo.photo is None
        # when ePiframe converts a file from the command line)
        if photo.photo is None or photo.photo.source != self.source:
            return
        with Image.open(photo.path) as source:
            image = source.copy()
        mode = image.mode  # keep the display colors (e.g. black & white)
        image = self.upright(image, photo, back=False).convert("RGBA")
        with Image.open(self.path / WATERMARK) as source:
            watermark = source.convert("RGBA").resize(
                (image.width // 10, image.height // 10)
            )
        position = (
            image.width - MARGIN - watermark.width,
            image.height - MARGIN - watermark.height,
        )
        image.paste(watermark, position, watermark)  # its alpha is the mask
        self.upright(image.convert(mode), photo, back=True).save(photo.path)

    @staticmethod
    def upright(image: Image.Image, photo: PhotoFile, back: bool) -> Image.Image:
        # a vertical frame stores the photo turned: work on the upright photo
        if photo.horizontal:
            return image
        turn_left = (photo.rotation == 90) != back
        return image.transpose(
            Image.Transpose.ROTATE_90 if turn_left else Image.Transpose.ROTATE_270
        )

    # ---------------------------------------- Step 5: API (1.x hook form)

    def synced_files(self) -> list[str]:
        return [photo.id for photo in self.synced_photos()]

    @login_required  # only logged-in users (or with the API key)
    def get_sync_image(self) -> Response | str:
        # /api/get_sync_image?file=<index>[&thumb]
        files = self.synced_files()
        argument = request.args.get("file", "0")
        index = int(argument) if argument.isdigit() else 0
        if index >= len(files):
            return "No Photo!"
        path = Path(files[index])
        if "thumb" in request.args:
            path = self.thumbnail(files[index])
        if not path.exists():
            return "No Photo!"
        extension = path.suffix.lstrip(".").lower()
        return send_file(path, mimetype=EXTENSION_TO_TYPE[extension])

    def extend_api(
        self, web_manager: WebUIManager, users: object, backend: object
    ) -> list[WebUIManager.SiteBind]:
        return [WebUIManager.SiteBind("/api/get_sync_image", self.get_sync_image)]

    # ------------------------------------- Step 6: website (1.x hook form)

    def add_website(
        self, web_manager: WebUIManager, users: object, backend: object
    ) -> list[object]:
        from plugins.ePiSync_code_tutorial.show import Show

        web_manager.add_menu_entries(
            [WebUIManager.MenuEntry("ePiSync", "/episync", "episync-menu", "bi bi-image")]
        )
        return [Show(self).get_show_bp()]
