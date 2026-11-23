"""ePiframe plugin template (Plugin API v2, ePiframe 2.0).

Documentation, examples and a tutorial:
https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md

Every method below except the metadata is optional: override only what the
plugin needs - ePiframe calls only the methods a plugin overrides.
"""

from epiframe.config.property import ConfigProperty
from epiframe.plugins.base import Plugin as PluginBase

# Imports used by the commented examples below:
# from epiframe.config.property import PropertyType
# from datetime import datetime
# from pathlib import Path
# from epiframe.photos.model import Photo
# from epiframe.plugins.base import PhotoFile


class Plugin(PluginBase):
    # ----------------------------------------------------------------- metadata
    # shown in the ePiframe WebUI (Plugins) and in the logs; name is required
    name = "Plugin Name"
    author = "Author Name"
    description = "One sentence about what this plugin does"
    site = "Plugin site URL and documentation"
    info = "Additional info, license, etc."

    # Available everywhere in the plugin:
    #   self.config         - this plugin's config.cfg: self.config.get("entry"),
    #                         self.config.getint("entry")
    #   self.global_config  - ePiframe's config.cfg (read only), e.g.
    #                         self.global_config.get("convert_bin_path")
    #   self.logger         - logging.Logger: self.logger.info("text"),
    #                         self.logger.warning(...), self.logger.error(...)
    #   self.path           - pathlib.Path of the plugin folder (files, fonts...)
    #   self.source         - name of this plugin's photo source ("plugin:<folder>")

    # ------------------------------------------------------------ configuration

    def settings(self) -> list[ConfigProperty]:
        # The entries of config.cfg / default/config.default that need validation
        # (types, ranges, possible values, dependencies). They are also used to
        # render the plugin settings in the WebUI. Entries of the default file
        # that are not listed here are plain text values.
        return [
            *super().settings(),  # is_enabled - required, keep it
            # every entry listed here must be in default/config.default too:
            # ConfigProperty("example_number", PropertyType.INTEGER, min_value=1),
            # ConfigProperty("text_that_can_be_empty", not_empty=False),
            # ConfigProperty("used_only_when_enabled", dependency="is_enabled"),
            # ConfigProperty(
            #     "used_only_for_a_value",
            #     dependency="mode",
            #     dependency_value="advanced",
            # ),
            # ConfigProperty("position", PropertyType.INTEGER, possible=[0, 1, 2, 3]),
            # ConfigProperty("color", possible=["white", "black"]),
            # ConfigProperty("ratio", PropertyType.FLOAT, min_value=0.0, max_value=1.0),
            # ConfigProperty("photos_folder", PropertyType.FILE),  # must exist
            # ConfigProperty("ids", PropertyType.INT_LIST, delimiter=","),
            # ConfigProperty("names", PropertyType.STRING_LIST, delimiter=","),
            # ConfigProperty("token", PropertyType.PASSWORD),  # masked in the WebUI
            # ConfigProperty("address", check=my_check_function),  # raises on error
        ]

    # Renamed entries of older plugin versions (old config.cfg files keep working):
    # LEGACY = (LegacyEntry("old_name", "new_name", convert_function),)
    # (from epiframe.config.base import LegacyEntry)

    # ------------------------------------------------------------- photo source
    # A new photo source: e.g. a photo hosting site, a synced remote folder.
    # ePiframe keeps all photos in its photo index (sorting, filtering, random
    # pick) - the plugin only lists them and fetches the one picked for display.

    # def source_photos(self) -> list[Photo]:
    #     # All photos of the source: Photo(id, self.source, created).
    #     # id identifies the photo in the source (a path, an URL, a remote id),
    #     # created is a datetime (used for sorting and date filters).
    #     # Called on every refresh - the photo index stores only the changes.
    #     folder = Path(self.config.get("photos_folder"))
    #     photos = []
    #     for path in sorted(folder.glob("*.jpg")):
    #         created = datetime.fromtimestamp(path.stat().st_mtime)
    #         photos.append(Photo(str(path), self.source, created))
    #     return photos

    # def fetch_photo(self, photo: Photo, directory: Path, name: str) -> Path:
    #     # Put the file of the picked photo into directory as name + extension
    #     # and return its path, e.g. download it. Not needed when photo.id is a
    #     # local file path: ePiframe copies that file itself.
    #     from epiframe.core.network import download_file
    #     return download_file(photo.id, directory / f"{name}.jpg", timeout=30)

    # --------------------------------------------------------- photo processing
    # photo is a PhotoFile: photo.path (the file to edit in place), photo.photo
    # (the Photo from the index, None for --test-convert/--convert runs),
    # photo.width / photo.height (display size), photo.horizontal and
    # photo.rotation (vertical frames store the photo turned), photo.image_magick
    # (ImageMagick runner: .run([...]), .size(file), .image_format(file)).

    # def preprocess_photo(self, photo: PhotoFile) -> None:
    #     # The original photo, before ePiframe converts it for the display:
    #     # e.g. photo filters, effects. Mind the Raspberry Pi Zero: big photos
    #     # are slow to process.
    #     photo.image_magick.run([str(photo.path), "-paint", "3", str(photo.path)])

    # def postprocess_photo(self, photo: PhotoFile) -> None:
    #     # The converted photo, just before it is shown: e.g. text, frames.
    #     # It is already in the display size and colors (maybe black & white).
    #     from PIL import Image, ImageDraw
    #     with Image.open(photo.path) as source:
    #         image = source.copy()
    #     ImageDraw.Draw(image).text((10, 10), "Hello!", fill=0)
    #     image.save(photo.path)

    # ---------------------------------------------- WebUI, API, service threads
    # extend_api, add_website, add_action and add_service_thread still have their
    # ePiframe 1.x form (see the 1.x documentation) and will be redesigned
    # together with the new WebUI and service of ePiframe 2.0.
