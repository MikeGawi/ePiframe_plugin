<h1>ePiframe_plugin Documentation</h1>

Documentation of the **Plugin API v2** for **ePiframe 2.0**. Plugins written for ePiframe 1.x don't work
with ePiframe 2.0 - see [Migrating a 1.x plugin](#migrating-a-1x-plugin).

# Table of Contents
<!--ts-->
   * [Contribution](#contribution)
      * [Additional hints](#additional-hints)
   * [Get started](#get-started)
   * [Structure](#structure)
      * [Files](#files)
      * [The plugin class](#the-plugin-class)
      * [Plugin methods overview](#plugin-methods-overview)
      * [Errors](#errors)
   * [Plugin methods](#plugin-methods)
      * [Adding photo source](#adding-photo-source)
         * [Retrieving the photo file](#retrieving-the-photo-file)
      * [Photo preprocessing](#photo-preprocessing)
      * [Photo postprocessing](#photo-postprocessing)
      * [WebUI, API and service methods](#webui-api-and-service-methods)
   * [Creating configuration](#creating-configuration)
      * [Configuration entries](#configuration-entries)
      * [Configuration file](#configuration-file)
      * [Renamed entries](#renamed-entries)
   * [Testing](#testing)
   * [Plugin installation](#plugin-installation)
      * [Python packages](#python-packages)
      * [Plugins execution order](#plugins-execution-order)
   * [Migrating a 1.x plugin](#migrating-a-1x-plugin)
   * [Examples](#examples)
   * [License](#license)
   * [Tutorial](#tutorial)
<!--te-->

# Contribution

Please follow these rules if you want to create your own plugin:
* Include screenshot of visual changes made by the plugin (if any)
* Add a short, one sentence, clear description what it does and put this data in the plugin class as well
* Add what external APIs/sites/modules/projects it uses and if they have limitations or price
* Include a detailed installation instruction, what needs to be installed and configured
* List the Python packages the plugin needs (other than ePiframe's own) in *requirements.txt* in the plugin folder
  ([Python packages](#python-packages))
* Add plugin details in [this table](https://github.com/MikeGawi/ePiframe_plugin#plugins-list) and create a pull request

## Additional hints

* Keep in mind that most ePiframes work on a Raspberry Pi Zero, so include information what hardware is needed if
  this setup is not enough
* Allow users to configure as many options of the plugin as possible, e.g. if the plugin puts text somewhere, allow
  the user to pick the position, color, font size, etc.
* Keep the plugin configuration backward compatible, like ePiframe does (see [Renamed entries](#renamed-entries)),
  or describe what needs to be changed manually after an update
* A plugin that needs the network should still let the frame work without it (log a warning, skip the extra)

# Get started

* Start a new project with the GitHub [*ePiframe_plugin*](https://github.com/MikeGawi/ePiframe_plugin) project
  template and give it a name - it is also the plugin folder name, so use only letters, digits and `_` (no dots,
  dashes or spaces: ePiframe imports the plugin as a Python module)
* Inside `_plugin.py` fill in the basic data: `name`, `author`, `description`, `site`, `info`
* Override the methods the plugin needs (all of them are optional)
* Create the plugin configuration: [entries](#configuration-entries) in `settings()` and the
  [configuration file](#configuration-file)
* [Test](#testing) the plugin with ePiframe
* Add plugin details in [the table](https://github.com/MikeGawi/ePiframe_plugin#plugins-list) and create a pull
  request - it will appear on the main site

Requirements: ePiframe 2.0 or newer (Python 3.11+).

# Structure

The plugin base class is part of ePiframe (`epiframe.plugins.base.Plugin`) and the plugin class inherits from it.
ePiframe finds the plugins in its `plugins` folder, loads them and calls the plugin methods in different phases of
its work - only the methods the plugin overrides.

A plugin uses ePiframe through the `epiframe` package, e.g.:

| Module                             | What for                                                                                 |
|------------------------------------|------------------------------------------------------------------------------------------|
| `epiframe.plugins.base`            | `Plugin` (the base class), `PhotoFile` (the photo passed to the processing methods)      |
| `epiframe.config.property`         | `ConfigProperty`, `PropertyType`, `CrossCheck` - [configuration entries](#configuration-entries) |
| `epiframe.photos.model`            | `Photo(id, source, created)` - a photo of a [photo source](#adding-photo-source)          |
| `epiframe.processing.imagemagick`  | `ImageMagick` runner (`run([...])`, `size()`, `image_format()`), `ImageMagickError`      |
| `epiframe.sources.local`           | `LocalSource` - listing photo files of a folder, `create_directory`                      |
| `epiframe.core.network`            | `download_file(url, destination, timeout)` (atomic), `check_internet()`                  |
| `epiframe.core.media_types`        | `EXTENSIONS`, `TYPE_TO_EXTENSION`, `EXTENSION_TO_TYPE`, `MIME_PREFIX`                    |

Other files of the plugin are imported as `plugins.<plugin_folder>.<module>`, e.g.
`from plugins.my_plugin.helpers import something`.

## Files

```
plugins
└── plugin_name
    ├── _plugin.py
    ├── config.cfg
    ├── requirements.txt   (optional)
    └── default
        └── config.default
```

The `plugins` folder is in the ePiframe folder (or where the `EPIFRAME_PLUGINS_DIR` environment variable points).
*plugin_name* is the plugin folder: letters, digits and `_` only.

| File               | Description                                                                      |
|--------------------|----------------------------------------------------------------------------------|
| *_plugin.py*       | the plugin: `class Plugin(epiframe.plugins.base.Plugin)`                         |
| *config.cfg*       | plugin configuration (changed by the user)                                       |
| *config.default*   | default configuration, used to restore and validate the entries                  |
| *requirements.txt* | optional: Python packages the plugin needs ([Python packages](#python-packages)) |

Initially *config.cfg* and *config.default* should be the same. A plugin can have more files (modules, fonts,
images, templates...) - `self.path` is its folder.

## The plugin class

```python
from epiframe.config.property import ConfigProperty, PropertyType
from epiframe.plugins.base import PhotoFile
from epiframe.plugins.base import Plugin as PluginBase


class Plugin(PluginBase):
    name = "My plugin"  # required
    author = "Me"
    description = "One sentence about what this plugin does"
    site = "https://github.com/me/my_plugin"
    info = "License, used services, etc."

    def settings(self) -> list[ConfigProperty]:
        return [*super().settings(), ConfigProperty("size", PropertyType.INTEGER)]

    def postprocess_photo(self, photo: PhotoFile) -> None:
        ...
```

Available in every plugin method:

| Attribute            | Description                                                                                     |
|----------------------|-------------------------------------------------------------------------------------------------|
| `self.config`        | the plugin configuration: `self.config.get("entry")`, `self.config.getint("entry")`            |
| `self.global_config` | ePiframe configuration ([config.cfg](https://github.com/MikeGawi/ePiframe/blob/master/config.cfg)), read only: `get()`, `getint()` |
| `self.logger`        | a `logging.Logger` writing to the ePiframe log: `self.logger.info("text")`, `.warning()`, `.error()` |
| `self.path`          | `pathlib.Path` of the plugin folder                                                             |
| `self.source`        | the name of the plugin's photo source (`"plugin:<plugin_folder>"`)                              |
| `self.enabled`       | the `is_enabled` entry                                                                          |

The plugin doesn't need an `__init__`. If it has one, it must call `super().__init__(context)` first.

## Plugin methods overview

Photo methods:

| Method              | Description                                                             |
|---------------------|-------------------------------------------------------------------------|
| `source_photos`     | all photos of a new photo source                                        |
| `fetch_photo`       | retrieving the file of the photo picked from that source                |
| `preprocess_photo`  | editing the original photo before it is converted for the display       |
| `postprocess_photo` | editing the converted photo just before it is shown                     |

WebUI, API and service methods (`extend_api`, `add_action`, `add_website`, `service_thread`) are described in
[WebUI, API and service methods](#webui-api-and-service-methods).

The 1.x method `change_photos_list` doesn't exist anymore: ePiframe 2.0 doesn't load the whole photo list (a
library can have hundreds of thousands of photos) - sorting, filtering and picking are done in its photo index.

## Errors

* An error in a photo method (an exception) is logged and stops the current photo change - raise when the photo
  can't be shown correctly.
* For optional extras (e.g. a price from a web API) catch the error, log it with `self.logger.warning(...)` and
  return: the photo is shown without the extra.
* A plugin that can't be loaded (e.g. an import error, a 1.x plugin) is logged and skipped - the frame keeps working.
* An invalid configuration value is reported by `epiframe check-config` and in the WebUI.

# Plugin methods

## Adding photo source

* **Method to override:** `source_photos(self) -> Iterable[Photo]`
* **Usage cases:** a new image hosting site, a folder synced from a cloud or another computer, etc.
* **Returns:** all photos of the source as `Photo(id, self.source, created)`
* **Current functionality of ePiframe:** a local folder and Google Drive folders

`Photo` (from `epiframe.photos.model`):

| Field     | Description                                                                                   |
|-----------|-----------------------------------------------------------------------------------------------|
| `id`      | identifies the photo within the source: a path, an URL, an id of the hosting site             |
| `source`  | always `self.source` - ePiframe uses it to find the plugin of a picked photo                  |
| `created` | `datetime` of the photo (e.g. EXIF date or file time) - used for sorting and date filtering   |

The method is called on every frame refresh. ePiframe stores the photos in its photo index and writes only the
changes (new, removed, changed photos), so returning the whole list is fine. The photos of a disabled plugin are
removed from the index.

ePiframe works only on the photo list, not on the files: only the photo picked for the display is retrieved (see
[below](#retrieving-the-photo-file)). Keep `source_photos` fast and light - it runs on a Raspberry Pi Zero; don't
download photos here.

Example (photos of a folder, with the help of ePiframe's `LocalSource`):

```python
import dataclasses

from epiframe.core.media_types import EXTENSIONS
from epiframe.photos.model import Photo
from epiframe.sources.local import LocalSource


def source_photos(self) -> list[Photo]:
    # LocalSource lists photo files (known extensions), created = file time;
    # the photos get this plugin's source name
    folder = LocalSource(self.config.get("photos_folder"), False, EXTENSIONS)
    return [dataclasses.replace(p, source=self.source) for p in folder.photos()]
```

Example (a web API):

```python
from datetime import datetime

import requests


def source_photos(self) -> list[Photo]:
    response = requests.get("https://example.com/api/photos", timeout=10)
    response.raise_for_status()  # an error stops this photo change (see the note)
    return [
        Photo(item["url"], self.source, datetime.fromisoformat(item["taken"]))
        for item in response.json()
    ]
```

__*NOTE:*__ An error in `source_photos` is logged and stops the photo change. If the frame should keep showing the
photos found before (e.g. without network), catch the error, log a warning and return the photos you can.

### Retrieving the photo file

* **Method to override:** `fetch_photo(self, photo: Photo, directory: Path, name: str) -> Path`
* **Usage cases:** downloading the picked photo, getting it from a sync, etc.
* **Returns:** the path of the file: `directory / (name + "." + extension)`
* **Current functionality of ePiframe:** copying from the local folder, downloading from Google Drive

The method is called only for photos of this plugin's source, when one of them is picked for the display.

Without `fetch_photo` ePiframe copies the local file `photo.id` itself (and finds its extension), so a source of
local files needs nothing more.

Example (download):

```python
from pathlib import Path

from epiframe.core.network import download_file


def fetch_photo(self, photo: Photo, directory: Path, name: str) -> Path:
    return download_file(photo.id, directory / f"{name}.jpg", timeout=30)
```

`download_file` writes to a temporary file first, so no broken photo is left after a network error.

## Photo preprocessing

* **Method to override:** `preprocess_photo(self, photo: PhotoFile) -> None`
* **Usage cases:** photo filters and effects on the original, high quality photo, e.g. cartoon style, oil paint
* **Returns:** nothing - edit the file `photo.path` in place
* **Current functionality of ePiframe:** auto-orientation of the photo

`PhotoFile` (from `epiframe.plugins.base`), passed to both processing methods:

| Field                | Description                                                                                     |
|----------------------|-------------------------------------------------------------------------------------------------|
| `photo.path`         | `Path` of the photo file to edit in place                                                       |
| `photo.photo`        | the `Photo` from the index, or `None` (the `test-convert` and `convert` commands work on a given file)  |
| `photo.width`        | display width in pixels (`image_width` of ePiframe)                                             |
| `photo.height`       | display height in pixels (`image_height` of ePiframe)                                           |
| `photo.horizontal`   | `False` for a vertical frame                                                                    |
| `photo.rotation`     | rotation of a vertical frame: `90` or `270`                                                     |
| `photo.image_magick` | ImageMagick runner: `run([arguments])`, `size(file)`, `image_format(file)`; raises `ImageMagickError` |

Example (ImageMagick effect):

```python
def preprocess_photo(self, photo: PhotoFile) -> None:
    # resizing to the display size first makes the effect much faster
    photo.image_magick.run(
        [str(photo.path), "-resize", f"{photo.width}x{photo.height}",
         "-paint", "3", str(photo.path)]
    )
```

ImageMagick gets an argument list (no shell), so paths with spaces work.

__*NOTE:*__ To process only the photos of this plugin's source:
`if photo.photo is None or photo.photo.source != self.source: return`

**_❗ IMPORTANT ❗_** Processing big, high quality photos is very resource consuming - ePiframe usually works on a
Raspberry Pi Zero.

References:
* [Cartoon plugin](https://github.com/MikeGawi/cartoon_ePiframe)

## Photo postprocessing

* **Method to override:** `postprocess_photo(self, photo: PhotoFile) -> None`
* **Usage cases:** adding text, frames, watermarks to the photo converted for the display
* **Returns:** nothing - edit the file `photo.path` in place
* **Current functionality of ePiframe:** the weather stamp

The photo is already in the display size and colors (e.g. black & white for an e-Paper display). On a vertical
frame the file is stored turned by `photo.rotation` - draw on the upright photo and turn it back.

Example (text in the corner):

```python
from PIL import Image, ImageColor, ImageDraw, ImageFont


def postprocess_photo(self, photo: PhotoFile) -> None:
    with Image.open(photo.path) as source:
        image = source.copy()
    if not photo.horizontal:  # draw on the upright photo
        image = image.transpose(
            Image.Transpose.ROTATE_90 if photo.rotation == 90 else Image.Transpose.ROTATE_270
        )
    font = ImageFont.truetype(str(self.path / "fonts/MyFont.ttf"), 20)
    ImageDraw.Draw(image).text(
        (10, 10),
        "Hello!",
        font=font,
        fill=ImageColor.getcolor("white", image.mode),  # in the photo's color mode
        stroke_width=2,
        stroke_fill=ImageColor.getcolor("black", image.mode),
    )
    if not photo.horizontal:  # turn back
        image = image.transpose(
            Image.Transpose.ROTATE_270 if photo.rotation == 90 else Image.Transpose.ROTATE_90
        )
    image.save(photo.path)
```

References:
* [Cryptocurrency plugin](https://github.com/MikeGawi/cryptocurrency_ePiframe) - text in a corner, a web API
* [Decor plugin](https://github.com/MikeGawi/decor_ePiframe) - images over the photo, quotes

## WebUI, API and service methods

| Method                                           | Returns                                                                     |
|--------------------------------------------------|-----------------------------------------------------------------------------|
| `extend_api(self, frame)`                        | a list of `Route(url, method)` - new REST API endpoints under `/api/`       |
| `add_action(self, frame)`                        | a list of `Action(id, label, function, icon)` - WebUI Tools buttons, also run with `/api/action=<id>` |
| `add_website(self, web_manager, users, backend)` | a list of Flask blueprints - new WebUI pages (menu entries with `web_manager.add_menu_entries([MenuEntry(name, url, id, icon)])`) |
| `service_thread(self, frame, stop)`              | nothing - the method runs once as a thread of the ePiframe service          |

`frame` is the frame (`epiframe.service.frame.Frame`: configuration, photo files, `next_photo()`, `reboot()`…).
`Route`, `Action` and `MenuEntry` come from `epiframe.web.extensions`.

API methods are declared with the `@api` decorator of `epiframe.web.api`: it requires the login (or a user's API
key), reads the parameters into dataclasses (wrong values are answered with HTTP status 400 and
`{"error": "<message>"}`), answers returned dataclasses as JSON and adds the method to ePiframe's OpenAPI document
(`/api/openapi.json`). Routes outside `/api/` or without `@api` are skipped. See
[tutorial step 5](TUTORIAL.md#step-5-extending-api).

A tool button:
```python
from epiframe.service.frame import Frame
from epiframe.web.extensions import Action


def add_action(self, frame: Frame) -> list[Action]:
    return [Action("lightoff", "Turn Light Off", self.light_off, "bi bi-lightbulb")]
```

A service thread runs once, in the background of the ePiframe service, from its start until it stops. `stop` is a
`threading.Event` set when the service stops (`systemctl stop`, Ctrl+C): return then - the service doesn't wait long
for its threads. An exception is logged and ends the thread (it is not started again).
```python
from threading import Event

from epiframe.service.frame import Frame


def service_thread(self, frame: Frame, stop: Event) -> None:
    while not stop.wait(60):  # every minute until the service stops
        self.logger.info(f"Next photo {frame.next_update_text()}")
```

**_🚧 Being redesigned 🚧_** `add_website` will change together with the new WebUI of ePiframe 2.0. Until then it
keeps its ePiframe 1.x form (`web_manager` is ePiframe's `epiframe.web.app.WebUI`, `users` its users store,
`backend` the frame). The [tutorial](TUTORIAL.md) (step 6) shows a
WebUI page that works with ePiframe 2.0 today.

# Creating configuration

The configuration of a plugin is validated like ePiframe's own: types, ranges, possible values, dependencies. The
WebUI renders the settings from the same description. Two things are needed:
* [Configuration entries](#configuration-entries) - the `settings()` method
* [Configuration file](#configuration-file) - `default/config.default` and `config.cfg`

Check the configuration (of ePiframe and all plugins) with:

```epiframe check-config```

## Configuration entries

`settings()` returns the entries that need validation as `ConfigProperty` objects. It must contain `is_enabled`,
so start with `super().settings()`. Entries of the default file that are not listed are plain text values.

```python
from epiframe.config.property import ConfigProperty, CrossCheck, PropertyType


def settings(self) -> list[ConfigProperty]:
    return [
        *super().settings(),  # is_enabled
        ConfigProperty("position", PropertyType.INTEGER, possible=[0, 1, 2, 3]),
        ConfigProperty("font", PropertyType.INTEGER, min_value=8, dependency="is_enabled"),
        ConfigProperty("font_color", possible=["white", "black"]),
        ConfigProperty("quotes", not_empty=False),
        ConfigProperty("border", dependency="random_border", dependency_value="0"),
        ConfigProperty("api_key", PropertyType.PASSWORD),
    ]
```

`ConfigProperty(name, type, ...)` parameters:

| Parameter          | Default    | Description                                                                                         |
|--------------------|------------|-----------------------------------------------------------------------------------------------------|
| `name`             | _required_ | name of the entry in the configuration file                                                         |
| `type`             | `STRING`   | `PropertyType` (below): validation and the WebUI field                                              |
| `not_empty`        | `True`     | `False` allows an empty value                                                                       |
| `dependency`       | `None`     | the entry is used only when this BOOLEAN entry is `1`...                                            |
| `dependency_value` | `None`     | ...or, if given, only when the `dependency` entry has this value                                    |
| `min_value`        | `None`     | minimum of a numeric entry                                                                          |
| `max_value`        | `None`     | maximum of a numeric entry                                                                          |
| `possible`         | `()`       | the allowed values (also a select box in the WebUI)                                                 |
| `length`           | `None`     | number of values of a list entry (with `delimiter`)                                                 |
| `delimiter`        | `None`     | separator of a list entry, e.g. `","`                                                               |
| `check`            | `None`     | function `check(value)` raising an exception for an invalid value (a raised `Warning` is only a warning) |
| `cross_check`      | `None`     | `CrossCheck(function, [names])`: `function(values)` checks several entries together, e.g. a start/end pair |
| `convert`          | `None`     | function converting the value when the file is loaded (e.g. an old value format); the result is saved |
| `reset_needed`     | `False`    | the WebUI shows "restart needed" after a change                                                     |

An entry that is not used (its dependency is off) is not validated.

`PropertyType` values:

| Type          | Description                                                              |
|---------------|--------------------------------------------------------------------------|
| `STRING`      | text (default)                                                           |
| `FILE`        | a path that must exist                                                   |
| `INTEGER`     | whole number, with `min_value`/`max_value`                               |
| `FLOAT`       | real number, with `min_value`/`max_value`, e.g. `-0.5`, `120.8`          |
| `BOOLEAN`     | `0` or `1`                                                               |
| `STRING_LIST` | text values separated by `delimiter`                                     |
| `INT_LIST`    | whole numbers separated by `delimiter`                                   |
| `PASSWORD`    | text masked in the WebUI                                                 |

__*NOTE:*__ Get values with `self.config.get(name)` (text) and `self.config.getint(name)` (numbers, booleans).
ePiframe's own values: `self.global_config.get(name)` - see
[ePiframe config.cfg](https://github.com/MikeGawi/ePiframe/blob/master/config.cfg).

## Configuration file

Fill in *<plugin_name>/default/config.default* with the entries and copy it to *<plugin_name>/config.cfg* (the
default file restores default values, the other one is changed by the user).

```
; Lines starting with "; " are comments for people reading the file (not shown in the WebUI).
; The file is in the INI format: sections in [brackets] and name=value entries.
; Names must be unique in the whole file.

[General]

# Set 1 to enable plugin, 0 to disable.
; Lines starting with "# " above an entry are its help text in the WebUI (joined into one line).
# Default: 1 (enabled)
is_enabled=1
```

* `# ` lines above an entry: its description in the WebUI - say what it does, the possible values and the default
* `; ` lines: remarks for people reading the file only

__*NOTE:*__ New entries of the default file are added to *config.cfg* with their default values; entries are
matched by name, so moving an entry to another section works too.

## Renamed entries

To rename an entry and keep old *config.cfg* files working, list it in `LEGACY`:

```python
from epiframe.config.base import LegacyEntry


class Plugin(PluginBase):
    LEGACY = (LegacyEntry("old_name", "new_name", convert_function),)  # str for no conversion
```

The old value is converted and saved under the new name.

# Testing

Test the plugin well before the release - it runs on someone's working frame.

* Put the plugin into the `plugins` folder of a test ePiframe (stop the
  [service](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#service-control) of a working frame first)
  or point `EPIFRAME_PLUGINS_DIR` to a test folder.
* `epiframe check-config` checks the plugin configuration.
* `epiframe test` runs a whole photo change without the display (also on a non-Pi computer) - the log shows
  the plugin methods; the result is `photo.bmp`.
* `epiframe test-convert <photo>` runs the processing on a given file (`photo.photo` is `None`).
* More in the [ePiframe command line](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#command-line).

Remember that:
* ePiframe works with high quality HDMI displays and with e-Paper displays with a limited color palette and size
* the frame can be horizontal or vertical
* ePiframe usually works on a Raspberry Pi Zero - the code must be light on resources
* the frame can be triggered from the WebUI, Telegram bot, command line and the ePiframe service
* the WebUI has a dark theme - custom colors outside the Bootstrap color schema may not work there
* other plugins may work on the same frame
* the configuration must stay backward compatible after a plugin update ([Renamed entries](#renamed-entries))

# Plugin installation

The plugin documentation should describe ([contribution](#contribution)):
>* What external APIs/sites/modules/projects it uses and if they have limitations or price
>* Include a detailed installation instruction, what needs to be installed and configured

The basic steps are the same for all plugins:
* Clone/download/extract the plugin to *<ePiframe_path>/plugins/<plugin_folder>* (letters, digits and `_` only)
* If the plugin has a *requirements.txt*: install its Python packages with `sudo ./install.sh --plugins` in the
  ePiframe folder ([Python packages](#python-packages))
* Configure the plugin in *<plugin_folder>/config.cfg* or in the ePiframe WebUI under *Plugins - <plugin_name>*
* Check the configuration in the WebUI or with `epiframe check-config`

## Python packages

ePiframe runs in its own Python environment (a virtual environment in *<ePiframe_path>/.venv*), so packages
installed with `sudo pip3 install` (1.x instructions) are not visible to it, and Raspberry Pi OS blocks system wide
pip installs anyway. A plugin that needs Python packages lists them in *requirements.txt* in its folder (pip
format, one package per line):

```
qrcode>=7.4
```

* Leave out what ePiframe already has: Pillow, requests, Flask, numpy, ...
  (see [*pyproject.toml*](https://github.com/MikeGawi/ePiframe/blob/v2/pyproject.toml)).
* Don't pin exact versions: the packages are installed within the versions ePiframe uses (its *uv.lock*). A
  requirement that conflicts with them is refused and nothing is installed (the error says why).
* Prefer pure Python packages or packages with wheels for the Raspberry Pi: on 32-bit Raspberry Pi OS (Pi Zero)
  the installer also uses [piwheels](https://www.piwheels.org/), anything else is built on the Pi (slow, needs a
  compiler).

The user installs them with `sudo ./install.sh --plugins` in the ePiframe folder after adding the plugin, then
restarts the service (`sudo systemctl restart ePiframe`). `./install.sh --update` installs them again (the update
rebuilds the Python environment). A plugin whose packages are missing is skipped with an error in the log. System
programs (`apt` packages) are not covered: describe them in the plugin documentation.

## Plugins execution order

Plugins changing the photo can overlap, e.g. a frame can be drawn over a text of another plugin. The execution order
is kept in *plugins/order.cfg* (one `plugins.<plugin_folder>` per line), created on the first run with new plugins.
Change the order there or in the WebUI under *Plugins - Execution Order*.

# Migrating a 1.x plugin

| ePiframe 1.x                                                            | ePiframe 2.0                                                                     |
|-------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| `from modules.base.pluginbase import PluginBase`                        | `from epiframe.plugins.base import Plugin as PluginBase`                         |
| `__init__(self, path, pid_manager, logging, global_config)`             | no `__init__` needed (`self.path`, `self.logger`, `self.global_config` are set)  |
| `class PluginConfigManager(ConfigBase)` + `load_settings()` / `self.SETTINGS` | `def settings(self) -> list[ConfigProperty]` (starting with `super().settings()`) |
| `ConfigProperty("x", self, prop_type=ConfigProperty.INTEGER_TYPE, minvalue=1)` | `ConfigProperty("x", PropertyType.INTEGER, min_value=1)`                    |
| `notempty`, `maxvalue`, `checkfunction`, `resetneeded`                  | `not_empty`, `max_value`, `check`, `reset_needed`                                |
| `dependency=["entry", value]`                                           | `dependency="entry", dependency_value=value`                                     |
| `special=ConfigProperty.Special(function, [names])`                     | `cross_check=CrossCheck(function, [names])`                                      |
| `self.main_class` (in the config class)                                 | `self` (settings are a method of the plugin)                                     |
| `legacy_convert()`                                                      | `LEGACY = (LegacyEntry(old, new, convert),)`                                     |
| `self.logging.log(text)`                                                | `self.logger.info(text)` (or `.warning()`, `.error()`)                           |
| `from misc.constants import Constants`                                  | `epiframe.core.media_types` (`EXTENSIONS`, `TYPE_TO_EXTENSION`, ...)             |
| `Connection.download_file(...)`                                         | `epiframe.core.network.download_file(url, destination, timeout)`                 |
| `add_photo_source(id_label, ...)` returning a pandas DataFrame, `self.SOURCE` | `source_photos()` returning `Photo(id, self.source, created)` objects        |
| `add_photo_source_get_file(photo, path, filename, ...)`                 | `fetch_photo(photo, directory, name) -> Path`                                    |
| `change_photos_list(...)`                                               | removed (the photo index sorts, filters and picks)                               |
| `preprocess_photo(original_photo, is_horizontal, convert_manager, photo, ...)` | `preprocess_photo(photo: PhotoFile)`                                      |
| `postprocess_photo(final_photo, width, height, is_horizontal, convert_manager, photo, ...)` | `postprocess_photo(photo: PhotoFile)`                         |
| `ConvertManager().get_image_size(binary, file, Constants.FIRST_FRAME_GIF)` | `photo.image_magick.size(file)`                                               |
| `self.global_config.getint("rotation")` for vertical frames             | `photo.horizontal`, `photo.rotation`                                             |
| ePiframe fonts in `static/fonts` (relative to the working folder)      | your font in the plugin (`self.path / "fonts/..."`) or ePiframe's stamp font `epiframe.weather.stamp.TEXT_FONT` |
| `UsersManager` in the web methods                                       | `epiframe.users.store.Users`                                                     |

The [example plugins](#examples) were migrated this way - compare their 1.x and 2.0 versions.

# Examples

* [Cryptocurrency Information](https://github.com/MikeGawi/cryptocurrency_ePiframe) - postprocessing, a web API
* [Frames and Quotes](https://github.com/MikeGawi/decor_ePiframe) - postprocessing, images and fonts of the plugin
* [Photo Filters](https://github.com/MikeGawi/cartoon_ePiframe) - preprocessing with ImageMagick

# License

The default license of the ePiframe_plugin base code is the
[LGPL-2.1 License](https://github.com/MikeGawi/ePiframe_plugin/blob/master/LICENSE), but it's up to the plugin
author what license the plugin has. The plugin should not violate any copyright rules of used components and the
author should take care to respect them. Some parts of the plugin code may be a valuable intellectual property and
ePiframe will not claim any part of it and will not take responsibility for its functionality. Long story short:
*plugin is yours, do what you want as long as you don't harm anyone, especially yourself*.

# Tutorial

The [tutorial](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md) gathers all steps needed to
implement a plugin with many different functions.
