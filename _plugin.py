from modules.base.pluginbase import PluginBase
from modules.base.configbase import ConfigBase
from misc.constants import Constants
from misc.connection import Connection
import os
from typing import List, Any
from ePiframe_service import Service
from misc.configproperty import ConfigProperty
from misc.logs import Logs
from modules.backendmanager import BackendManager
from modules.base.configbase import ConfigBase
from modules.convertmanager import ConvertManager
from modules.filteringmanager import FilteringManager
from modules.indexmanager import IndexManager
from modules.photomanager import PhotoManager
from modules.pidmanager import PIDManager
from modules.usersmanager import UsersManager
from modules.webuimanager import WebUIManager


# Main ePiframe plugin template class
# For more detailed documentation, examples and tutorial visit:
# https://github.com/MikeGawi/ePiframe.plugin/blob/master/docs/SETUP.md
# All commented methods are optional!
class Plugin(PluginBase):
    name = "Plugin Name"
    author = "Author Name"
    description = "One sentence about what this plugin does"
    site = "Plugin site URL and documentation"
    info = "Additional info, license, etc."

    ## Config manager class.
    class PluginConfigManager(ConfigBase):
        ## Use self.main_class to get to the main plugin class here

        def load_settings(self):
            ## List of settings, one-to-one accurate with config.cfg and default/config.default files.
            ## This structure allows validation, conversion, dependencies, value and type verification and more.
            ## Check https://github.com/MikeGawi/ePiframe/blob/master/modules/configmanager.py
            ## and https://github.com/MikeGawi/ePiframe/blob/master/misc/configproperty.py
            self.SETTINGS = [
                ## this setting is required!
                ConfigProperty(
                    "is_enabled", self, prop_type=ConfigProperty.BOOLEAN_TYPE
                )
                # ConfigProperty('some_integer_value', self, minvalue=1, maxvalue=1080, prop_type=ConfigProperty.INTEGER_TYPE),
                # ConfigProperty('some_string_value_that_can_be_empty_with_bool_dependency', self, notempty=False, dependency='is_enabled'),
                # ConfigProperty('verified_integer_type_with_possible_options', self, prop_type=ConfigProperty.INTEGER_TYPE, possible=get_positions() or [1, 2, 3, 4], checkfunction=verify_position),
                # ConfigProperty('ip_with_check_and_bool_dependency', self, dependency='use_web', checkfunction=Connection.is_ip),
                # ConfigProperty('delimited_list_of_integers', self, delimiter=',', prop_type=ConfigProperty.INTLIST_TYPE),
                # ConfigProperty('delimited_list_of_strings_with_mult_values_special_check_and_length', self, delimiter=',', prop_type=ConfigProperty.STRINGLIST_TYPE, length=7, special=check(verifyfunc, ['1st_entry', '2nd_entry'])),
                # ConfigProperty('value_based_dependency', self, minvalue=0, prop_type=ConfigProperty.INTEGER_TYPE, dependency=['config_entry_value_to_check', value_or_function_that_returns_value_to_get_true]),
                # ConfigProperty('path', self, prop_type=ConfigProperty.FILE_TYPE),
                # ConfigProperty('string_with_convert_function_good_for_converting_old_config_values_to_new_version', self, convert=convert_function),
                ## ...
            ]

        ## Plugin updates should keep configuration backward compatibility!

        # def legacy_convert(self):
        ## Legacy exceptional backward handling for converting one property to another property under different name
        ## and the ones that misc.ConfigProperty.convert could not handle.
        ## Check https://github.com/MikeGawi/ePiframe/blob/master/modules/configmanager.py
        ## Get global configuration value here with self.get('<entry name>') - check https://github.com/MikeGawi/ePiframe/blob/master/config.cfg

    ## End of PluginConfigManager class.

    ## Adding all basic modules that can be used later:
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/pidmanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/misc/logs.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/base/configbase.py and https://github.com/MikeGawi/ePiframe/blob/master/modules/configmanager.py
    ## Super method will save variables to self scope, i.e. self.path, self.pid_manager, self.logging, etc., load configuration and validate it.
    ## path is the real base path of the plugin.
    ## Plugin local configuration will be loaded as well.
    def __init__(
        self,
        path: str,
        pid_manager: PIDManager,
        logging: Logs,
        global_config: ConfigBase,
    ):
        super().__init__(path, pid_manager, logging, global_config)
        ## ...

    ## Hints:
    ## Use global constants with Constants.<variable name> - check https://github.com/MikeGawi/ePiframe/blob/master/misc/constants.py
    ## Put something to logs with self.logging.log('<text>')
    ## Get global configuration value with self.global_config.get('<entry name>') - check https://github.com/MikeGawi/ePiframe/blob/master/config.cfg
    ## Get the plugin local configuration value with self.config.get('<entry name>')

    ## All methods below can be used together within the same plugin:

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override when new photo source is added by the plugin, e.g. add DeviantArt photo source, sync photos from remote location, etc.
    ## Basic photo collector modules are passed here:
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/photomanager.py
    ## This method should collect the data of new photos and return Pandas DataFrame that will be processed (i.e. filtered, sorted, combined with other sources and used to pick up photo).
    ## The ID (unique and can be filename or some id from image hosting site), creation time and source columns are crucial - with them the sorting and filtering will work out of the box.
    ## If the source is in the Web, check connection first with https://github.com/MikeGawi/ePiframe/blob/master/misc/connection.py
    # def add_photo_source(
    #         self,
    #         id_label: str,
    #         creation_label: str,
    #         source_label: str,
    #         photo_manager: PhotoManager,
    # ):
    ## example (add files from local path):
    # from modules.localsourcemanager import LocalSourceManager
    # location = LocalSourceManager ('path_to_photos', False, Constants.EXTENSIONS)
    # self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
    # return location.get_local_photos(id_label, creation_label, source_label, self.SOURCE)

    ## example 2 (add files with dates to DataFrame, set source and return):
    # import pandas as pd
    # photos = pd.DataFrame()
    # photos = pd.DataFrame(list(zip(files, dates)), columns=[id_label, creation_label])
    # self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
    # photos[source_label] = self.SOURCE
    # return photos
    ## Creation time must be in YYYY-mm-ddTHH:MM:SSZ, i.e. 2021-01-27T22:59:37Z format!
    ## Remember to save source name to self.SOURCE variable as it will indicate the source plugin.
    ## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py

    ## This method is used to retrieve the file (that has been picked up from the new source specified above) according to the ID value, e.g. download, sync, etc.
    ## The filename holds only name, no extension. path is the target path of the photo.
    ## photo is a Pandas element photo representation with all possible columns and id_label as identifier.
    ## If not overriden the standard copy from photo id (as a source location) to filename method will be used, extension will be added automatically.
    ## Returns final filename, best if it would contain an extension.
    # def add_photo_source_get_file(
    #         self,
    #         photo,
    #         path: str,
    #         filename: str,
    #         id_label: str,
    #         creation_label: str,
    #         source_label: str,
    #         photo_manager: PhotoManager,
    # ):
    ## example (add extension from MIME type and copy from source to target location with extension added):
    # import shutil
    # from modules.convertmanager import ConvertManager
    # convert_manager = ConvertManager()
    # returned_filename = ''
    # error, image_type = convert_manager.get_image_format(self.global_config.get('convert_bin_path'), photo[id_label], Constants.FIRST_FRAME_GIF) #if this is a GIF then just check the first frame
    # if not error and image_type:
    # 	returned_filename = filename + "." + Constants.TYPE_TO_EXTENSION[Constants.MIME_START + image_type.lower()]
    # returned_filename = os.path.join(path, returned_filename)
    # shutil.copy(photo[id_label], returned_filename)
    # return returned_filename

    ## example 2 (this source gets photo MIME type /can be converted to extension name with constants/ and download URL so create a filename and download the file):
    # returned_filename = filename + "." + Constants.TYPE_TO_EXTENSION[photo['MIMETYPE_HEADER']]
    # download_url = photo['URL']
    # connection.download_file(download_url, path, returned_filename, Constants.OK_STATUS_ERRORCODE, Constants.CHECK_CONNECTION_TIMEOUT)
    # return returned_filename

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override when final photos list that will be used for picking a photo needs to be changed, e.g. sorted, filtered, turned upside-down, etc.
    ## Returns modified photo_list (Pandas DataFrame). Basic list modification modules are passed here.
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/photomanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/indexmanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/filteringmanager.py
    # def change_photos_list(
    #         self,
    #         id_label: str,
    #         creation_label: str,
    #         source_label: str,
    #         photo_list,
    #         photo_manager: PhotoManager,
    #         index_manager: IndexManager,
    #         filtering_manager: FilteringManager,
    # ):
    ## example (sort photo_list descendingly by creation time):
    # return photo_list.sort_values(by = creation_label, ascending = False)
    ## Creation time must be in YYYY-mm-ddTHH:MM:SSZ, i.e. 2021-01-27T22:59:37Z format!
    ## It's good to reset the records indexing after sorting with photo_manager.reset_index(photo_list)
    ## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/filteringmanager.py

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override when the photo needs to be processed before the basic conversion, and it is currently in the original version (high quality photo), e.g. oil paint effect, frame, stamps, etc.
    ## The source photo path is in original_photo and this method should save modified photo as original_photo too. Basic photo conversion modules are passed here:
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py
    ## photo is a Pandas element photo representation with all possible columns and id_label as identifier.
    ## is_horizontal boolean indicates whether frame is in horizontal position.
    # def preprocess_photo(
    #         self,
    #         original_photo: str,
    #         is_horizontal: bool,
    #         convert_manager: ConvertManager,
    #         photo,
    #         id_label: str,
    #         creation_label: str,
    #         source_label: str,
    # ):
    ## example (add graphic element from file to the photo):
    # from PIL import Image
    # image = Image.open(original_photo)
    ## get image size if needed
    # width, height = image.size
    # element = Image.open(element_path)
    # image.paste(element, (1, 100))
    # image.save(original_photo)
    ## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/weathermanager.py

    ## Hint: it is possible to get image size directly from file with error, width, height = ConvertManager().get_image_size(self.global_config.get('convert_bin_path'), original_photo, Constants.FIRST_FRAME_GIF)

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override when the photo needs to be processed before sending to display (and it's already converted to the display), e.g. add text, re-convert, etc.
    ## The source photo path is in final_photo and this method should save modified photo as final_photo too. Basic photo conversion modules are passed here:
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py
    ## width and height are photo sizes in pixels.
    ## is_horizontal boolean indicates whether frame is in horizontal position.
    ## photo is a Pandas element photo representation with all possible columns and id_label as identifier.
    # def postprocess_photo(
    #     self,
    #     final_photo: str,
    #     width: int,
    #     height: int,
    #     is_horizontal: bool,
    #     convert_manager: ConvertManager,
    #     photo,
    #     id_label: str,
    #     creation_label: str,
    #     source_label: str,
    # ):
    ## example (add text to converted photo):
    # from PIL import Image, ImageDraw, ImageFont, ImageColor
    # image = Image.open(final_photo)
    ## rotating image if frame not in horizontal position
    # if not is_horizontal: image = image.transpose(Image.ROTATE_90 if self.global_config.getint('rotation') == 90 else Image.ROTATE_270)
    # draw = ImageDraw.Draw(image)
    # font = ImageFont.truetype(os.path.join(self.path, 'static/fonts/NotoSans-SemiCondensed.ttf'), 20) #path holds the absolute path to the plugin folder
    # stroke = ImageColor.getcolor('Black', image.mode) #mind the color mode of the image
    # fill = ImageColor.getcolor('White', image.mode)
    # draw.text((1, 100), 'text', font = font, stroke_width = 2, stroke_fill = stroke, fill = fill)
    ## rotating back if in vertical position
    # if not is_horizontal: image = image.transpose(Image.ROTATE_270 if self.global_config.getint('rotation') == 90 else Image.ROTATE_90)
    # image.save(final_photo)
    ## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/weathermanager.py

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override extend_api method when need to extend API functions, e.g. new data returned by query/website like get hardware statistics, expose API for smart home server, etc.
    ## Basic web related modules are passed:
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
    ## Returns list of WebUIManager.SiteBind objects that have typical Flask binding syntax and point to a function to trigger.
    ## Possible fields: url, func, methods = ['GET'], defaults = None
    ## Functions should return jsonify version of data.
    ## For more complicated API features plugin add_website method (with Flask Blueprints) can be used (without adding menu entry)

    ## example (add two new API functions):

    ## called with /api/get_text/<text>
    ## user login is not needed to get the data
    # def get_text_func(self, text=str()):
    # from flask import jsonify
    # return jsonify(text_label=text)

    # from flask_login import login_required
    ## called with /api/get_data?query=<query>
    ## user login is needed to get the data
    # @login_required
    # def get_data_func(self):
    # from flask import jsonify, request
    # data = db_connection.get_data_from_query(request.args.get('query'))
    # return jsonify(data_label=data)

    ## This is the plugin method that is fired:
    # def extend_api(
    #         self,
    #         web_manager: WebUIManager,
    #         users_manager: UsersManager,
    #         backend: BackendManager,
    # ):
    # new_apis = [
    # 	WebUIManager.SiteBind('/api/get_text/<text>', self.get_text_func),
    # 	WebUIManager.SiteBind('/api/get_data', self.get_data_func)
    # ]
    # return new_apis

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override when need to add new website to WebUI, with the optional link on the main menu.
    ## Basic web related modules are passed here:
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
    ## Flask Blueprints are used for additional website code: https://flask.palletsprojects.com/en/2.0.x/blueprints/
    ## For new menu entries (optional) list of WebUIManager.MenuEntry objects are used, possible fields: name, url, id, icon
    ## name is the name of the menu entry to appear (e.g. "Show graph"), url is the link path e.g. "/test",
    ## id is the element id to find it with javascript and for example change styling when active.
    ## icon should be taken from Boostrap Icons https://icons.getbootstrap.com/, e.g. "bi bi-alarm"
    # def add_website(
    #         self,
    #         web_manager: WebUIManager,
    #         users_manager: UsersManager,
    #         backend: BackendManager,
    # ):
    ## example (add new website 'Test' with link to '<IP>/test'in WebUI menu):
    # from plugins.<plugin_name>.<website_name> import <website_name>_bp
    # menus = [ WebUIManager.MenuEntry ('Test', '/test', 'test-menu', 'bi bi-apple') ] #can be more than one
    # web_manager.add_menu_entries(menus) #optional
    # websites = [ <website_name>_bp ] #can be more than one
    # return websites

    ## Inside plugin path create folders: templates (for website templates) and static (for static content, scripts, styles, etc.)
    ## Inside plugin path create file <website_name>.py with:
    # from flask import Blueprint, render_template
    # from flask_login import login_required
    # <website_name>_bp = Blueprint('<website_name>_bp', __name__,  template_folder='templates', static_folder='static' )
    # @<website_name>_bp.route('/test') #this is the URL of the site
    # @login_required #user login is needed to visit. The order matters so this decorator should be the last one before method.
    # def view():
    # return render_template('test.html', text='This text will be passed!')

    ## Inside plugin templates folder create file test.html with:
    # {% extends "layout.html" %} <!-- This will load ePiframe template, jQuery and Bootstrap -->
    # {% block title %}Test{% endblock %}
    # {% block head %}
    #  {{ super() }}
    #  <!-- Load static resources -->
    # {% endblock %}
    # {% block content %}
    #   <!-- Content -->
    # 	<p>{{ text }}</p>
    #   <script>
    #   	//Scripts
    # 		$(".test-menu").addClass("link-light"); //Light up website link in menu
    #   </script>
    # {% endblock %}
    ## https://github.com/MikeGawi/ePiframe/blob/master/templates/index.html

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override add_action method when need to extend action buttons in WebUI Tools section, e.g. control device, trigger system action, etc.
    ## Basic web related modules are passed:
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
    ## Returns dictionary of action key : WebUIManager.ActionEntry value objects with possible fields: name, func, icon, action
    ## name is the name of the button to appear (e.g. "Ping machine"), action is the action name e.g. "send_ping"
    ## func is the function to trigger and icon should be taken from Boostrap Icons https://icons.getbootstrap.com/, e.g. "bi bi-alarm"

    ## example (add two new action buttons to turn light on/off with configured IP):

    # def light_on(self):
    # import requests
    # requests.get(url = self.config(light_ip), params = 'ON')

    # def light_off(self):
    # import requests
    # requests.get(url = self.config(light_ip), params = 'OFF')

    # def add_action(
    #         self,
    #         web_manager: WebUIManager,
    #         users_manager: UsersManager,
    #         backend: BackendManager,
    # ):
    # new_actions = {
    # 	'lighton' : WebUIManager.ActionEntry('Turn Light On', self.light_on, 'bi bi-lightbulb-fill', 'lighton'),
    # 	'lightoff' : WebUIManager.ActionEntry('Turn Light Off', self.light_off, 'bi bi-lightbulb', 'lightoff'),
    # }
    # return new_actions

    ## ---------------------------------------------------------------------------------------------------------------------------

    ## Uncomment and override when need to add new thread to ePiframe service: frequently gathering data, scheduled triggers, etc.
    ## Basic web/service related modules are passed here:
    ## https://github.com/MikeGawi/ePiframe/blob/master/ePiframe_service.py
    ## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
    # def add_service_thread(self, service: Service, backend: BackendManager):
    ## example (gather statistics every 60 seconds - persistent thread, enabled by configuration):
    # from modules.statsmanager import StatsManager
    # import time
    # stats_manager = StatsManager(backend)
    # while True:
    # 	backend.refresh() #check if frame configuration changed and reload it
    # 	if backend.is_web_enabled() and backend.stats_enabled():
    # 		try:
    # 			stats_manager.feed_stats()
    # 		except Exception as exception:
    # 			self.logging.log(exception)
    # 			pass
    # 	time.sleep(60) #sleep 60 seconds between feeds
    ## Check: https://github.com/MikeGawi/ePiframe/blob/master/ePiframe_service.py
