from modules.base.pluginbase import PluginBase
from modules.base.configbase import ConfigBase
from misc.configproperty import ConfigProperty
from misc.constants import Constants
from modules.convertmanager import ConvertManager
from modules.photomanager import PhotoManager
from modules.pidmanager import PIDManager
from misc.logs import Logs
from modules.backendmanager import BackendManager
from modules.usersmanager import UsersManager
from modules.webuimanager import WebUIManager
from modules.localsourcemanager import LocalSourceManager
from modules.filteringmanager import FilteringManager
from modules.indexmanager import IndexManager
from PIL import Image
from flask import request, send_file
from flask_login import login_required
import os
import shutil
import subprocess


class Plugin(PluginBase):
    name = "ePiSync"
    author = "ePiframe-plugin tutorial"
    description = (
        "Sync photos with rsync from remote location, generate thumbnails, then add watermark, "
        "API method and a website to view new photos"
    )
    site = "https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md"
    info = "All steps gathered here to create a multi-functional ePiframe plugin"

    # Config manager class.
    class PluginConfigManager(ConfigBase):
        def load_settings(self):
            self.SETTINGS = [
                ConfigProperty(
                    "is_enabled", self, prop_type=ConfigProperty.BOOLEAN_TYPE
                ),  # this setting is required!
                # local path to sync to, notice that convert method is used to pass value to the
                # create_directory method that creates the path if not exists
                # that's just a tricky way to use convert
                ConfigProperty(
                    "local_path",
                    self,
                    prop_type=ConfigProperty.FILE_TYPE,
                    dependency="is_enabled",
                    convert=LocalSourceManager.create_directory,
                ),
                ConfigProperty(
                    "remote_path", self, dependency="is_enabled"
                ),  # this is string (by default)
                ConfigProperty(
                    "remote_host", self, dependency="is_enabled"
                ),  # all are dependent to is_enabled
                ConfigProperty(
                    "remote_user", self, dependency="is_enabled"
                ),  # and will be enabled only if is_enabled is true
                ConfigProperty(
                    "sync_timeout",
                    self,
                    minvalue=2,
                    maxvalue=10,
                    prop_type=ConfigProperty.INTEGER_TYPE,
                    dependency="is_enabled",
                ),  # integer values with min and max thresholds
                ConfigProperty(
                    "thumb_width",
                    self,
                    minvalue=100,
                    maxvalue=400,
                    prop_type=ConfigProperty.INTEGER_TYPE,
                    dependency="is_enabled",
                ),
                ConfigProperty(
                    "thumb_height",
                    self,
                    minvalue=100,
                    maxvalue=300,
                    prop_type=ConfigProperty.INTEGER_TYPE,
                    dependency="is_enabled",
                ),
            ]

    # End of PluginConfigManager class.

    __THUMB_NAME = "thumb_"

    def __init__(
        self,
        path: str,
        pid_manager: PIDManager,
        logging: Logs,
        global_config: ConfigBase,
    ):

        super().__init__(path, pid_manager, logging, global_config)

    # ---------------------------------------------------------------------------------------------------------------------------

    # method that adds new photo source
    def add_photo_source(
        self,
        id_label: str,
        creation_label: str,
        source_label: str,
        photo_manager: PhotoManager,
    ):
        cmd = "rsync --timeout={} --ignore-existing {}@{}:{}* {} 2>&1 > /dev/null"  # command string
        source = (
            self.config.get("remote_path")
            if self.config.get("remote_path").endswith("/")
            else self.config.get("remote_path") + "/"
        )  # adding / at the end if not exists
        os.system(
            cmd.format(
                self.config.get("sync_timeout"),
                self.config.get("remote_user"),
                self.config.get("remote_host"),
                source,
                self.config.get("local_path"),
            )
        )  # starting command with args

        local_source = LocalSourceManager(
            self.config.get("local_path"), False, Constants.EXTENSIONS
        )  # getting synced files with LocalSourceManager
        self.SOURCE = "'{}' plugin source".format(
            self.name
        )  # it is required to set the source name
        return local_source.get_local_photos(
            id_label, creation_label, source_label, self.SOURCE
        )  # returning dataframe of photos with needed labels

    # method that retrieves the file from new photo source
    def add_photo_source_get_file(
        self,
        photo,
        path: str,
        filename: str,
        id_label: str,
        creation_label: str,
        source_label: str,
        photo_manage: PhotoManager,
    ):
        returned_filename = filename
        # getting image MIME type with ImageMagick
        error, image_type = ConvertManager().get_image_format(
            self.global_config.get("convert_bin_path"),
            photo[id_label],
            Constants.FIRST_FRAME_GIF,
        )  # if this is a GIF then just check the first frame
        if not error and image_type:
            returned_filename = (
                filename
                + "."
                + Constants.TYPE_TO_EXTENSION[Constants.MIME_START + image_type.lower()]
            )  # converting MIME type to extension
        returned_filename = os.path.join(path, returned_filename)  # combining filename
        shutil.copy(photo[id_label], returned_filename)  # copying to target path
        return returned_filename

    # ---------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def __subproc(arguments):
        # method to start process with arguments.
        # it needs a list of arguments
        argument = arguments.split()
        process = subprocess.Popen(argument, stdout=subprocess.PIPE)
        process.wait()
        out, error = process.communicate()
        return out, error

    # method that changes collected photo list
    def change_photos_list(
        self,
        id_label: str,
        creation_label: str,
        source_label: str,
        photo_list,
        photo_manager: PhotoManager,
        index_manager: IndexManager,
        filtering_manager: FilteringManager,
    ):
        size = self.config.get("thumb_width") + "x" + self.config.get("thumb_height")
        thumb_cmd = "{} {} -background white -gravity center -sample {} -extent {} {}"  # thumbnail generation command
        rows = photo_list[
            photo_list[source_label] == self.SOURCE
        ]  # getting rows only from the source of this plugin
        LocalSourceManager.create_directory(
            os.path.join(self.config.get("local_path"), self.__THUMB_NAME + "/")
        )  # creating thumbnails directory

        for index, row in rows.iterrows():  # iterating through rows
            thumb_file = os.path.join(
                os.path.dirname(row[id_label]),
                self.__THUMB_NAME + "/",
                self.__THUMB_NAME + os.path.basename(row[id_label]),
            )  # getting thumb path
            if not os.path.exists(thumb_file):
                out, error = self.__subproc(
                    thumb_cmd.format(
                        self.global_config.get("convert_bin_path"),
                        row[id_label],
                        size,
                        size,
                        thumb_file,
                    )
                )  # creating thumbnail
                if error:
                    raise Exception(error)

        return photo_list  # returning initial photo_list as nothing has changed

    # ---------------------------------------------------------------------------------------------------------------------------

    # method that postprocesses the photo
    def postprocess_photo(
        self,
        final_photo: str,
        width: int,
        height: int,
        is_horizontal: bool,
        convert_manager: ConvertManager,
        photo,
        id_label: str,
        creation_label: str,
        source_label: str,
    ):
        if self.SOURCE and not photo.empty and photo[source_label] == self.SOURCE:
            image = Image.open(final_photo)
            mode = image.mode  # get photo mode
            if not is_horizontal:
                image = image.transpose(
                    Image.ROTATE_90
                    if self.global_config.getint("rotation") == 90
                    else Image.ROTATE_270
                )  # rotating image if frame not in horizontal position
            new_image = image.convert("RGBA")  # converting to RGB with alpha

            watermark = Image.open(
                os.path.join(self.path, "static/images/watermark.png")
            ).convert(
                "RGBA"
            )  # self.path is a plugin path
            watermark = watermark.resize(
                (width // 10, height // 10)
            )  # resizing watermark to 1/10 of width and height
            new_image.paste(
                watermark,
                (width - 10 - width // 10, height - 10 - height // 10),
                watermark,
            )  # pasting watermark on the photo and with watermark mask
            new_image = new_image.convert(mode)  # convert back to original photo mode

            if not is_horizontal:
                new_image = new_image.transpose(
                    Image.ROTATE_270
                    if self.global_config.getint("rotation") == 90
                    else Image.ROTATE_90
                )  # rotating back if in vertical position

            new_image.save(final_photo)  # saving as final photo

    # ---------------------------------------------------------------------------------------------------------------------------

    def get_files(self):
        return LocalSourceManager(
            self.config.get("local_path"), False, Constants.EXTENSIONS
        ).get_files()  # get all files with LocalSourceManager

    # login is required to use this API entry
    @login_required
    def get_sync_image(self):
        filename = str()
        file_number = (
            int(request.args.get("file"))
            if "file" in request.args and request.args.get("file").isdigit()
            else 0
        )  # if file=<value> in URL then read file number
        files = self.get_files()

        try:
            # get filename or thumbnail filename if URL contains thumb argument
            filename = (
                files[file_number]
                if "thumb" not in request.args
                else os.path.join(
                    os.path.dirname(files[file_number]),
                    self.__THUMB_NAME + "/",
                    self.__THUMB_NAME + os.path.basename(files[file_number]),
                )
            )
        except Exception:
            pass
        return (
            send_file(
                filename,
                mimetype=Constants.EXTENSION_TO_TYPE[
                    str(filename).rsplit(".")[-1].lower()
                ],
            )
            if filename
            else "No Photo!"
        )  # send file if exists and message if it doesn't

    # method that adds new API method
    def extend_api(
        self,
        web_manager: WebUIManager,
        users_manager: UsersManager,
        backend: BackendManager,
    ):
        return [
            WebUIManager.SiteBind("/api/get_sync_image", self.get_sync_image)
        ]  # bind API method with URL

    # ---------------------------------------------------------------------------------------------------------------------------

    # method that adds new website and menu entry
    def add_website(
        self,
        web_manager: WebUIManager,
        users_manager: UsersManager,
        backend: BackendManager,
    ):
        from plugins.ePiSync_code_tutorial.show import Show

        web_manager.add_menu_entries(
            [
                WebUIManager.MenuEntry(
                    "ePiSync", "/episync", "episync-menu", "bi bi-image"
                )
            ]
        )  # create menu entry with name, URL, menu id and icon
        site = Show(self)  # create site class and pass plugin
        return [site.get_show_bp()]  # return list of websites to add
