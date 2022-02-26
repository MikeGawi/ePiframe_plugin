from modules.base.pluginbase import pluginbase
from modules.base.configbase import configbase
from misc.configprop import configprop
from misc.constants import constants
from misc.connection import connection
import os

## Main ePiframe plugin template class
## For more detailed documentation, examples and tutorial visit: https://github.com/MikeGawi/ePiframe.plugin/blob/master/docs/SETUP.md
## All commented methods are optional!
class plugin(pluginbase):
	
	name = 'Plugin Name'
	author = 'Author Name'
	description = 'One sentence about what this plugin does'
	site = 'Plugin site URL and documentation'
	info = 'Additional info, license, etc.'
	
	## Config manager class.
	class configmgr (configbase):
		## Use self.main_class to get to the main plugin class here
		
		def load_settings(self):
			
			## List of settings, one-to-one accurate with config.cfg and default/config.default files.
			## This structure allows validation, conversion, dependencies, value and type verification and more.
			## Check https://github.com/MikeGawi/ePiframe/blob/master/modules/configmanager.py
			## and https://github.com/MikeGawi/ePiframe/blob/master/misc/configprop.py
			self.SETTINGS = [
				## this setting is required! 			
				configprop('is_enabled', self, prop_type=configprop.BOOLEAN_TYPE)
				#configprop('some_integer_value', self, minvalue=1, maxvalue=1080, prop_type=configprop.INTEGER_TYPE),
				#configprop('some_string_value_that_can_be_empty_with_bool_dependency', self, notempty=False, dependency='is_enabled'),
				#configprop('verified_integer_type_with_possible_options', self, prop_type=configprop.INTEGER_TYPE, possible=get_positions() or [1, 2, 3, 4], checkfunction=verify_position),
				#configprop('ip_with_check_and_bool_dependency', self, dependency='use_web', checkfunction=connection.is_ip),
				#configprop('delimited_list_of_integers', self, delimiter=',', prop_type=configprop.INTLIST_TYPE),
				#configprop('delimited_list_of_strings_with_mult_values_special_check_and_length', self, delimiter=',', prop_type=configprop.STRINGLIST_TYPE, length=7, special=check(verifyfunc, ['1st_entry', '2nd_entry'])),
				#configprop('value_based_dependency', self, minvalue=0, prop_type=configprop.INTEGER_TYPE, dependency=['config_entry_value_to_check', value_or_function_that_returns_value_to_get_true]),			
				#configprop('path', self, prop_type=configprop.FILE_TYPE),
				#configprop('string_with_convert_function_good_for_converting_old_config_values_to_new_version', self, convert=convert_function),
				## ...
			]
			
		## Plugin updates should keep configuration backward compatibilty!
		
		#def legacy_convert(self):
			## Legacy exceptional backward handling for converting one property to another property under different name
			## and the ones that misc.configprop.convert could not handle.
			## Check https://github.com/MikeGawi/ePiframe/blob/master/modules/configmanager.py
			## Get global configuration value here with self.get('<entry name>') - check https://github.com/MikeGawi/ePiframe/blob/master/config.cfg
			
	## End of configmgr class.
	
	
	## Adding all basic modules that can be used later: 
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/pidmanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/misc/logs.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/base/configbase.py and https://github.com/MikeGawi/ePiframe/blob/master/modules/configmanager.py
	## Super method will save variables to self scope, i.e self.path, self.pidmgr, self.logging, etc., load configuration and validate it.
	## path is the real base path of the plugin.
	## Plugin local configuration will be loaded as well.
	def __init__ (self, path, pidmgr, logging, globalconfig):
		super().__init__(path, pidmgr, logging, globalconfig)		
		## ...
	
	
	## Hints:
	## Use global constants with constants.<variable name> - check https://github.com/MikeGawi/ePiframe/blob/master/misc/constants.py
	## Put something to logs with self.logging.log('<text>')
	## Get global configuration value with self.globalconfig.get('<entry name>') - check https://github.com/MikeGawi/ePiframe/blob/master/config.cfg
	## Get the plugin local configuration value with self.config.get('<entry name>')
	
	
	## All methods below can be used together within the same plugin:
	
	## ---------------------------------------------------------------------------------------------------------------------------
		
	## Uncomment and override when new photo source is added by the plugin, e.g. add DeviantArt photo source, sync photos from remote location, etc.
	## Basic photo collector modules are passed here:
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/photomanager.py
	## This method should collect the data of new photos and return Pandas DataFrame that will be processed (i.e. filtered, sorted, combined with other sources and used to pick up photo).
	## The ID (unique and can be filename or some id from image hosting site), creation time and source columns are crucial - with them the sorting and filtering will work out of the box.
	## If the source is in the Web, check connection first with https://github.com/MikeGawi/ePiframe/blob/master/misc/connection.py
	#def add_photo_source (self, idlabel, creationlabel, sourcelabel, photomgr):
		## example (add files from local path):
		#from modules.localsourcemanager import localsourcemanager
		#loc = localsourcemanager ('path_to_photos', False, constants.EXTENSIONS)
		#self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
		#return loc.get_local_photos(idlabel, creationlabel, sourcelabel, self.SOURCE)
		
		## example 2 (add files with dates to DataFrame, set source and return):
		#import pandas as pd
		#photos = pd.DataFrame()		
		#photos = pd.DataFrame(list(zip(files, dates)), columns=[idlabel, creationlabel])
		#self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
		#photos[sourcelabel] = self.SOURCE
		#return photos
		## Creation time must be in YYYY-mm-ddTHH:MM:SSZ, i.e. 2021-01-27T22:59:37Z format!
		## Remember to save source name to self.SOURCE variable as it will indicate the source plugin.
		## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py
	
	## This method is used to retrieve the file (that has been picked up from the new source specified above) according to the ID value, e.g. download, sync, etc.
	## The filename holds only name, no extension. path is the target path of the photo.
	## photo is a Pandas element photo representation with all possible columns and idlabel as identifier.
	## If not overriden the standard copy from photo id (as a source location) to filename method will be used, extension will be added automatically.
	## Returns final filename, best if it would contain an extension.
	#def add_photo_source_get_file (self, photo, path, filename, idlabel, creationlabel, sourcelabel, photomgr):
		## example (add extension from MIME type and copy from source to target location with extension added):
		#import shutil
		#from modules.convertmanager import convertmanager
		#convertman = convertmanager()
		#filename_ret = ''		
		#err, imagetype = convertman.get_image_format(self.globalconfig.get('convert_bin_path'), photo[idlabel], constants.FIRST_FRAME_GIF) #if this is a GIF then just check the first frame
		#if not err and imagetype:
		#	filename_ret = filename + "." + constants.TYPE_TO_EXTENSION[constants.MIME_START + imagetype.lower()]
		#filename_ret = os.path.join(path, filename_ret) 
		#shutil.copy(photo[idlabel], filename_ret)
		#return filename_ret
		
		## example 2 (this source gets photo MIME type /can be converted to extension name with constants/ and download URL so create a filename and download the file):
		#filename_ret = filename + "." + constants.TYPE_TO_EXTENSION[photo['MIMETYPE_HEADER']]
		#downloadUrl = photo['URL']
		#connection.download_file(downloadUrl, path, filename_ret, constants.OK_STATUS_ERRORCODE, constants.CHECK_CONNECTION_TIMEOUT)
		#return filename_ret
	
	## ---------------------------------------------------------------------------------------------------------------------------
	
	## Uncomment and override when final photos list that will be used for picking a photo needs to be changed, e.g. sorted, filtered, turned upside-down, etc.
	## Returns modified photo_list (Pandas DataFrame). Basic list modification modules are passed here.
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/photomanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/indexmanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/filteringmanager.py
	#def change_photos_list (self, idlabel, creationlabel, sourcelabel, photo_list, photomgr, indexmgr, filteringmgr):
		## example (sort photo_list descendingly by creation time):
		#return photo_list.sort_values(by = creationlabel, ascending = False)
		## Creation time must be in YYYY-mm-ddTHH:MM:SSZ, i.e. 2021-01-27T22:59:37Z format!
		## It's good to reset the records indexing after sorting with photomgr.reset_index(photo_list)
		## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/filteringmanager.py
	
	## ---------------------------------------------------------------------------------------------------------------------------
		
	## Uncomment and override when the photo needs to be processed before the basic conversion and it is currently in the original version (high quality photo), e.g. oil paint effect, frame, stamps, etc.
	## The source photo path is in orgphoto and this method should save modified photo as orgphoto too. Basic photo conversion modules are passed here:
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py
	## photo is a Pandas element photo representation with all possible columns and idlabel as identifier.
	## is_horizontal boolean indicates wheter frame is in horizontal position.
	#def preprocess_photo (self, orgphoto, is_horizontal, convertmgr, photo, idlabel, creationlabel, sourcelabel):
		## example (add graphic element from file to the photo):
		#from PIL import Image
		#image = Image.open(orgphoto)
		## get image size if needed
		#width, height = image.size
		#element = Image.open(element_path)
		#image.paste(element, (1, 100))
		#image.save(orgphoto)
		## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/weathermanager.py
		
	## Hint: it is possible to get image size directly from file with err, width, height = convertmanager().get_image_size(self.globalconfig.get('convert_bin_path'), orgphoto, constants.FIRST_FRAME_GIF)

	## ---------------------------------------------------------------------------------------------------------------------------
			
	## Uncomment and override when the photo needs to be processed before sending to display (and it's already converted to the display), e.g. add text, re-convert, etc.
	## The source photo path is in finalphoto and this method should save modified photo as finalphoto too. Basic photo conversion modules are passed here:
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py
	## width and height are photo sizes in pixels.
	## is_horizontal boolean indicates wheter frame is in horizontal position.
	## photo is a Pandas element photo representation with all possible columns and idlabel as identifier.	
	#def postprocess_photo (self, finalphoto, width, height, is_horizontal, convertmgr, photo, idlabel, creationlabel, sourcelabel):
		## example (add text to converted photo):
		#from PIL import Image, ImageDraw, ImageFont, ImageColor
		#image = Image.open(finalphoto)
		## rotating image if frame not in horizontal position
		#if not is_horizontal: image = image.transpose(Image.ROTATE_90 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_270)
		#draw = ImageDraw.Draw(image)
		#font = ImageFont.truetype(os.path.join(self.path, 'static/fonts/NotoSans-SemiCondensed.ttf'), 20) #path holds the absolute path to the plugin folder
		#stroke = ImageColor.getcolor('Black', image.mode) #mind the color mode of the image
		#fill = ImageColor.getcolor('White', image.mode)
		#draw.text((1, 100), 'text', font = font, stroke_width = 2, stroke_fill = stroke, fill = fill)
		## rotating back if in vertical position
		#if not is_horizontal: image = image.transpose(Image.ROTATE_270 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_90)
		#image.save(finalphoto)
		## Reference: https://github.com/MikeGawi/ePiframe/blob/master/modules/weathermanager.py
	
	## ---------------------------------------------------------------------------------------------------------------------------
	
	## Uncomment and override extend_api method when need to extend API functions, e.g. new data returned by query/website like get hardware statistics, expose API for smart home server, etc.
	## Basic web related modules are passed:	
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
	## Returns list of webmgr.site_bind objects that have typical Flask binding syntax and point to a function to trigger.
	## Possible fields: url, func, methods = ['GET'], defaults = None
	## Functions should return jsonify version of data.
	## For more complicated API features plugin add_website method (with Flask Blueprints) can be used (without adding menu entry)
	
	## example (add two new API functions):
	
	## called with /api/get_text/<text>
	## user login is not needed to get the data
	#def get_text_func(self, text=str()):
		#from flask import jsonify
		#return jsonify(text_label=text)	
	
	#from flask_login import login_required
	## called with /api/get_data?query=<query>
	## user login is needed to get the data
	#@login_required
	#def get_data_func(self):
		#from flask import jsonify, request
		#data = dbconn.get_data_from_query(request.args.get('query'))
		#return jsonify(data_label=data)
	
	## This is the plugin method that is fired:
	#def extend_api (self, webmgr, usersmgr, backend):
		#newapis = [
		#	webmgr.site_bind('/api/get_text/<text>', self.get_text_func),
		#	webmgr.site_bind('/api/get_data', self.get_data_func)
		#]		
		#return newapis
		
	## ---------------------------------------------------------------------------------------------------------------------------
	
	## Uncomment and override when need to add new website to WebUI, with the optional link on the main menu.
	## Basic web related modules are passed here:	
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
	## Flask Blueprints are used for additional website code: https://flask.palletsprojects.com/en/2.0.x/blueprints/
	## For new menu entries (optional) list of webmgr.menu_entry objects are used, possible fields: name, url, id, icon
	## name is the name of the menu entry to appear (e.g. "Show graph"), url is the link path e.g. "/test",
	## id is the element id to find it with javascript and for example change styling when active. 
	## icon should be taken from Boostrap Icons https://icons.getbootstrap.com/, e.g. "bi bi-alarm"
	#def add_website (self, webmgr, usersmgr, backend):
		## example (add new website 'Test' with link to '<IP>/test'in WebUI menu):
		#from plugins.<plugin_name>.<website_name> import <website_name>_bp
		#menus = [ webmgr.menu_entry ('Test', '/test', 'test-menu', 'bi bi-apple') ] #can be more than one
		#webmgr.add_menu_entries(menus) #optional
		#websites = [ <website_name>_bp ] #can be more than one
		#return websites
		
	## Inside plugin path create folders: templates (for website templates) and static (for static content, scripts, styles, etc.)
	## Inside plugin path create file <website_name>.py with:
	#from flask import Blueprint, render_template
	#from flask_login import login_required	
	#<website_name>_bp = Blueprint('<website_name>_bp', __name__,  template_folder='templates', static_folder='static' )
	#@<website_name>_bp.route('/test') #this is the URL of the site
	#@login_required #user login is needed to visit. The order matters so this decorator should be the last one before method.
	#def view():    
		#return render_template('test.html', text='This text will be passed!')
		
	## Inside plugin templates folder create file test.html with:
	#{% extends "layout.html" %} <!-- This will load ePiframe template, jQuery and Bootstrap -->
	#{% block title %}Test{% endblock %}
	#{% block head %}
	#  {{ super() }}
	#  <!-- Load static resources -->
	#{% endblock %}
	#{% block content %}
	#   <!-- Content -->
	#	<p>{{ text }}</p>
	#   <script>
	#   	//Scripts
	#		$(".test-menu").addClass("link-light"); //Light up website link in menu
	#   </script>
	#{% endblock %}
	## https://github.com/MikeGawi/ePiframe/blob/master/templates/index.html
		
	## ---------------------------------------------------------------------------------------------------------------------------
	
	## Uncomment and override add_action method when need to extend action buttons in WebUI Tools section, e.g. control device, trigger system action, etc.
	## Basic web related modules are passed:	
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
	## Returns dictionary of action key : webmgr.action_entry value objects with possible fields: name, func, icon, action
	## name is the name of the button to appear (e.g. "Ping machine"), action is the action name e.g. "send_ping"
	## func is the function to trigger and icon should be taken from Boostrap Icons https://icons.getbootstrap.com/, e.g. "bi bi-alarm"
	
	## example (add two new action buttons to turn light on/off with configured IP):
	
	#def lighton(self):
		#import requests
		#requests.get(url = self.config(light_ip), params = 'ON')

	#def lightoff(self):
		#import requests
		#requests.get(url = self.config(light_ip), params = 'OFF')
	
	#def add_action (self, webmgr, usersmgr, backend):
		#newactions = {
		#	'lighton' : webmgr.action_entry('Turn Light On', self.lighton, 'bi bi-lightbulb-fill', 'lighton'),
		#	'lightoff' : webmgr.action_entry('Turn Light Off', self.lightoff, 'bi bi-lightbulb', 'lightoff'),
		#}
		#return newactions
		
	## ---------------------------------------------------------------------------------------------------------------------------
	
	## Uncomment and override when need to add new thread to ePiframe service: frequently gathering data, scheduled triggers, etc.
	## Basic web/service related modules are passed here:	
	## https://github.com/MikeGawi/ePiframe/blob/master/ePiframe_service.py
	## https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py
	#def add_service_thread (self, service, backend):
		## example (gather statistics every 60 seconds - persistent thread, enabled by configuration):
		#from modules.statsmanager import statsmanager
		#import time
		#statsman = statsmanager(backend)
		#while True:
		#	backend.refresh() #check if frame configuration changed and reload it
		#	if backend.is_web_enabled() and backend.stats_enabled():
		#		try:
		#			statsman.feed_stats()
		#		except Exception as e:
		#			self.logging.log(e)
		#			pass		
		#	time.sleep(60) #sleep 60 seconds between feeds
		## Check: https://github.com/MikeGawi/ePiframe/blob/master/ePiframe_service.py