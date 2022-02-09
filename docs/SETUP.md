<h1>ePiframe.plugin Documentation</h1>

# Table of Contents
<!--ts-->
   * [Contribution](#contribution)
      * [Additional hints](#additional-hints)
   * [Get started](#get-started)
   * [Structure](#structure)
      * [Files](#files)
      * [Built-in objects](#built-in-objects)
      * [Methods](#methods)
   * [Plugin methods](#plugin-methods)
      * [Adding photo source](#adding-photo-source)
	  	* [Adding new photo source file retrieving method](#adding-new-photo-source-file-retrieving-method)
      * [Changing photos list](#changing-photos-list)
      * [Photo preprocessing](#photo-preprocessing)
      * [Photo postprocessing](#photo-postprocessing)
      * [Extending API](#extending-api)
      * [Adding new websites and menu entries](#adding-new-websites-and-menu-entries)
      * [Adding new actions](#adding-new-actions)
      * [Adding service thread](#adding-service-thread)
   * [Creating configuration](#creating-configuration)
      * [Configuration class](#configuration-class)
      * [Configuration file](#configuration-file)
   * [Plugin installation](#plugin-installation)
   * [Examples](#examples)
   * [Tutorial](#tutorial)
<!--te-->

# Contribution

Please follow these rules if you want to create your own plugin:
* Include screenshot of visual changes made by the plugin (if any)
* Add a short, one sentence, clear description what it does and put this data in the plugin class as well
* What external API's/sites/modules/projects it uses and if they have limitations or price
* Include a detailed installation instruction, what needs to be installed and configured
* Add plugin details in this table and create a pull request- it will appear on this site

## Additional hints

* Keep in mind that most ePiframes work on Raspberry Pi Zero, so include information about what hardware is needed if this setup is not enough
* Allow users to configure as much as possible options of the plugin, e.g. if plugin puts text somewhere, allow user to pick the position, color, font size, etc.
* Keep backward compatibility of the plugin configuration files, like ePiframe does, or indicate what needs to be changed manually to adapt the configuration to the newest plugin version after update

# Get started

* Start a new project with GitHub [*ePiframe.plugin*](https://github.com/MikeGawi/ePiframe.plugin) project template and change the _<plugin_name>_ folder name to the name of the plugin - ePiframe will use this name to recognize the plugin module
* Inside ```_plugin.py``` file fill in the basic data like name, description, author, etc.
* Start overriding methods that the plugin will use, use built-in modules or create new ones and have fun with it!
* Create plugin configuration file
* Test the plugin with ePiframe and put everything to the new GitHub project if all good
* Add plugin details in the table and create a pull request - it will appear on the main site

# Structure

Plugins base class is embedded in the ePiframe code and the plugin class inherits exposed methods that can be overriden. The plugin manager inside ePiframe will run these methods in different phases of ePiframe runtime and will do that only if the method is used. 

The scope starts in the root folder of ePiframe so if some module needs to be used it should import from ```modules.<module_name>```, e.g. ```from modules.databasemanager import databasemanager```. If the plugin needs additional files/modules these can be imported with the same module hierarchy, i.e. ```plugins.<plugin_name>.<module_name>```.

Most of the basic ePiframe modules that can be useful for particular plugins methods are passed during the run but all needed ePiframe ingredients can be imported if needed.

## Files

```
└── plugin_name
    ├── config.cfg
    ├── default
    │   └── config.default
    └── _plugin.py
```

*plugin_name* is the main directory of the plugin and it should be changed to the actual plugin name.

|File|Description|
|----|-----------|
|*_plugin.py*|main plugin module to work with| 
|*config.cfg*|plugin configuration file| 
|*config.default*|used to restore default configuration values|

Initially *config.cfg* and *config.default* should be the same.

## Built-in objects

|Object|Description|
|------|-----------|
|```self.config```|plugin configuration class| 
|```constants.<variable name>```|[ePiframe global constants](https://github.com/MikeGawi/ePiframe/blob/master/misc/constants.py)|
|```self.globalconfig```|global [ePiframe configuration](https://github.com/MikeGawi/ePiframe/blob/master/config.cfg)| 
|```self.pidmgr```|[ePiframe pidmanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/pidmanager.py) that holds and controls ePiframe PID|
|```self.logging```|[ePiframe logger](https://github.com/MikeGawi/ePiframe/blob/master/misc/logs.py) that gathers runtime logs| 
	
Hints:
* Use global constants with ```constants.<variable name>```
* Put something to logs with ```self.logging.log('<text>')```
* Get global configuration value with ```self.globalconfig.get('<entry name>')```
* Get the plugin local configuration value with ```self.config.get('<entry name>')```

## Methods

```plugin``` class photos specific exposed methods to override:

|Method|Description|
|------|-----------|
|```add_photo_source```|adding new photos source|
|```add_photo_source_get_file```|retrieve the file (that has been picked up from the new source specified above)| 
|```change_photos_list```|changing collected photos list| 
|```preprocess_photo```|high quality source photo preprocessing before conversion for the display| 
|```postprocess_photo```|converted photo postprocessing when photo is ready to be put on the display|

Other ```plugin``` class exposed methods to override:

|Method|Description|
|------|-----------|
|```extend_api```|extending API functions|
|```add_website```|adding new websites to ePiframe WebUI| 
|```add_action```|adding new action buttons to ePiframe Tools section in WebUI| 
|```add_service_thread```|adding new thread to ePiframe service| 

# Plugin methods

## Adding photo source

* **Method to override:** ```add_photo_source```
* **Usage cases:** adding new image hosting site source, adding methods to sync with cloud, etc.
* **Passed modules:** 
	* [Photo Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/photomanager.py) - photos + Pandas manipulation methods
* **Passed variables:**
	|Variable|Description|
	|--------|-----------|
	|```idlabel```|photo ID label name|
	|```creationlabel```|photo creation time label name|
	|```sourcelabel```|photo source label name|
* **Returns:** _Pandas DataFrame_ of collected photos with columns _idlabel_, _creationlabel_, _sourcelabel_ (at least). Add more columns if needed
* **Current functionality of ePiframe:** gathering photos from specific albums of Google Photos and/or local storage

This method should collect the data of new photos and return Pandas DataFrame that will be processed (i.e. filtered, sorted, combined with other sources and used to pick up photo). The ID (unique and can be filename or some id from image hosting site), creation time and source columns are crucial - with them the sorting and filtering will work out of the box.

Examples:

```
def add_photo_source (self, idlabel, creationlabel, sourcelabel, photomgr):
	#add files from local path
	from modules.localsourcemanager import localsourcemanager
	loc = localsourcemanager ('path_to_photos', False, constants.EXTENSIONS)
	self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
	return loc.get_local_photos(idlabel, creationlabel, sourcelabel, self.SOURCE)
```

```
def add_photo_source (self, idlabel, creationlabel, sourcelabel, photomgr):
	#add files with dates to DataFrame, set source and return:
	import pandas as pd
	photos = pd.DataFrame()
	files = <get files...>
	dates = <get files dates ...>
	photos = pd.DataFrame(list(zip(files, dates)), columns=[idlabel, creationlabel])
	self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
	photos[sourcelabel] = self.SOURCE
	return photos
```

References: 
* [ePiframe Local Source Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py)

__*NOTE:*__ Creation time must be in _YYYY-mm-ddTHH:MM:SSZ_, i.e. 2021-01-27T22:59:37Z format!

### Adding new photo source file retrieving method

* **Method to override:** ```add_photo_source_get_file```
* **Usage cases:** retrieve the file (that has been picked up from the new source specified above) according to the ID value, e.g. download, sync, etc.
* **Passed modules:** 
	* [Photo Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/photomanager.py) - photos + Pandas manipulation methods
* **Passed variables:**
	|Variable|Description|
	|--------|-----------|
	|```photo```|a Pandas element photo representation with all possible columns and ```idlabel``` as identifier|
	|```path```|the target path of the photo|
	|```filename```|photo target name (only), no extension|
	|```idlabel```|photo ID label name|
	|```creationlabel```|photo creation time label name|
	|```sourcelabel```|photo source label name|
* **Returns:** photo final filename, best if it would contain an extension
* **Current functionality of ePiframe:** downloading selected photo from Google Photos and/or copying from local storage

This method is optional and if not overriden, the standard copy from photo id (as a source location) to filename method will be used, extension will be added automatically.

Examples:

```
def add_photo_source_get_file (self, photo, path, filename, idlabel, creationlabel, sourcelabel, photomgr):
	#add extension from MIME type and copy from source to target location with extension added:
	import shutil
	from modules.convertmanager import convertmanager
	convertman = convertmanager()
	filename_ret = ''		
	err, imagetype = convertman.get_image_format(self.globalconfig.get('convert_bin_path'), photo[idlabel], constants.FIRST_FRAME_GIF) #if this is a GIF then just check the first frame
	if not err and imagetype:
		filename_ret = filename + "." + constants.TYPE_TO_EXTENSION[constants.MIME_START + imagetype.lower()]
	filename_ret = os.path.join(path, filename_ret) 
	shutil.copy(photo[idlabel], filename_ret)
	return filename_ret
```

```
def add_photo_source_get_file (self, photo, path, filename, idlabel, creationlabel, sourcelabel, photomgr):
	#this source gets photo MIME type (can be converted to extension name with constants) and download URL so create a filename and download the file:
	#The MIME type and URL column should be populated in the previous source collecting method !
	#filename_ret = filename + "." + constants.TYPE_TO_EXTENSION[photo['MIMETYPE_HEADER']]
	#downloadUrl = photo['URL']
	#connection.download_file(downloadUrl, path, filename_ret, constants.OK_STATUS_ERRORCODE, constants.CHECK_CONNECTION_TIMEOUT)
	#... timeout, connection error handling, etc.
	#return filename_ret
```

References: 
* [ePiframe Local Source Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py)

__*NOTE:*__ Creation time must be in _YYYY-mm-ddTHH:MM:SSZ_, i.e. 2021-01-27T22:59:37Z format!

## Changing photos list

* **Method to override:** ```change_photos_list```
* **Usage cases:** changing final photos list, e.g. sorting, filtering, turning upside-down, adding AI recognition etc.
* **Passed modules:** 
	* [Photo Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/photomanager.py) - photos + Pandas manipulation methods
	* [Index Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/indexmanager.py) - photo indexing methods
	* [Filtering Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/filteringmanager.py) - photos list filtering and sorting methods
* **Passed variables:**
	|Variable|Description|
	|--------|-----------|
	|```photo_list```|a Pandas element photos list representation with all possible columns and idlabel as identifier|
	|```idlabel```|photo ID label name|
	|```creationlabel```|photo creation time label name|
	|```sourcelabel```|photo source label name|
* **Returns:**  modified ```photo_list``` (Pandas DataFrame)
* **Current functionality of ePiframe:** sorting (ascendingly, descendingly), filtering by creation date, by number of photos

Example:

```
def change_photos_list (self, idlabel, creationlabel, sourcelabel, photo_list, photomgr, indexmgr, filteringmgr):
	#sort photo_list descendingly by creation time:
	return photo_list.sort_values(by = creationlabel, ascending = False)
```

References: 
* [ePiframe Filtering Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/filteringmanager.py)

__*NOTE:*__ Creation time must be in _YYYY-mm-ddTHH:MM:SSZ_, i.e. 2021-01-27T22:59:37Z format!
__*NOTE:*__ It's good to reset the records indexing after sorting with ```photomgr.reset_index(photo_list)```
	
## Photo preprocessing

* **Method to override:** ```preprocess_photo```
* **Usage cases:** process photo before the basic conversion when it is currently in the original version (high quality photo), e.g. oil paint effect, frame, stamps, etc.
* **Passed modules:** 
	* [Convert Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py) - file conversion, getting image type and dimensions methods
* **Passed variables:**
	|Variable|Description|
	|--------|-----------|
	|```orgphoto```|the source/target photo path with name and extension|
	|```width```|photo width in pixels|
	|```height```|photo height in pixels|
	|```is_horizontal```|boolean, indicates wheter frame is in horizontal position|
* **Returns:**  _nothing_. This method should save modified photo as ```orgphoto``` name passed to it
* **Current functionality of ePiframe:** there is no photo preprocessing

Example:

```
def preprocess_photo (self, orgphoto, width, height, is_horizontal, convertmgr):
	#add graphic element from file to the photo:
	from PIL import Image
	image = Image.open(orgphoto)
	element = Image.open(element_path)
	image.paste(element, (1, 100))
	image.save(orgphoto)
```

References: 
* [ePiframe Weather Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/weathermanager.py)

## Photo postprocessing

* **Method to override:** ```postprocess_photo```
* **Usage cases:** process photo before sending to display (and it's already converted to the display), e.g. add text, re-convert, etc.
* **Passed modules:** 
	* [Convert Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py) - file conversion, getting image type and dimensions methods
* **Passed variables:**
	|Variable|Description|
	|--------|-----------|
	|```finalphoto```|the source/target photo path with name and extension|
	|```width```|photo width in pixels|
	|```height```|photo height in pixels|
	|```is_horizontal```|boolean, indicates wheter frame is in horizontal position|
* **Returns:**  _nothing_. This method should save modified photo as ```finalphoto``` name passed to it
* **Current functionality of ePiframe:** adding weather information

Example:

```
def postprocess_photo (self, finalphoto, width, height, is_horizontal, convertmgr):
	#add text to converted photo:
	from PIL import Image, ImageDraw, ImageFont, ImageColor
	image = Image.open(finalphoto)
	draw = ImageDraw.Draw(image)
	font = ImageFont.truetype(os.path.join(self.path, 'static/fonts/NotoSans-SemiCondensed.ttf'), 20) #path holds the absolute path to the plugin folder
	stroke = ImageColor.getcolor('Black', image.mode) #mind the color mode of the image
	fill = ImageColor.getcolor('White', image.mode)
	draw.text((1, 100), 'text', font = font, stroke_width = 2, stroke_fill = stroke, fill = fill)
	image.save(finalphoto)
```

References: 
* [ePiframe Weather Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/weathermanager.py)

__*NOTE:*__ Photo can be converted to some specific image mode at this point (e.g. black and white) and is in the size ready for the display (e.g. 800x480 pixels) so have that in mind during image manipulations.

## Extending API

* **Method to override:** ```extend_api```
* **Usage cases:** extend API functions, e.g. adding REST API,return data by query/website like get hardware statistics, expose API for smart home server, etc.
* **Passed modules:** 
	* [WebUI Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py) - Websites rendering, API functions, settings handling from WebUI, etc.
	* [Users Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py) - WebUI users handling, access to users database, etc.
	* [Backend Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py) - All WebUI/Telegram Bot backend functions, files handling, triggering functions, etc.
* **Passed variables:** _none_
* **Returns:** list of ```webmgr.site_bind``` objects (possible fields: ```url```, ```func```, ```methods = ['GET']```, ```defaults = None```) that have typical [Flask binding](https://flask.palletsprojects.com/en/2.0.x/quickstart/#url-building) syntax and point to a function to trigger
* **Current functionality of ePiframe:** [ePiframe API](https://github.com/MikeGawi/ePiframe/blob/master/docs/API.md)

Example:

```
#add two new API functions:
	
#called with /api/get_text/<text>
#user login is not needed to get the data
def get_text_func(self, text=str()):
	from flask import jsonify
	return jsonify(text_label=text)	

from flask_login import login_required
#called with /api/get_data?query=<query>
#user login is needed to get the data
@login_required
def get_data_func(self):
	from flask import jsonify, request
	data = dbconn.get_data_from_query(request.args.get('query')) #get data from database
	return jsonify(data_label=data)

#This is the plugin method that is fired:
def extend_api (self, webmgr, usersmgr, backend):
	newapis = [
		webmgr.site_bind('/api/get_text/<text>', self.get_text_func),
		webmgr.site_bind('/api/get_data', self.get_data_func)
	]		
	return newapis
```

__*NOTE:*__ For more complicated API features plugin ```add_website method``` below (with [Flask Blueprints](https://flask.palletsprojects.com/en/2.0.x/blueprints/)) can be used (without adding menu entry)

## Adding new websites and menu entries	

* **Method to override:** ```add_website```
* **Usage cases:** add new website to WebUI, with the optional link on the main menu
* **Passed modules:** 
	* [WebUI Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py) - Websites rendering, API functions, settings handling from WebUI, etc.
	* [Users Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py) - WebUI users handling, access to users database, etc.
	* [Backend Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py) - All WebUI/Telegram Bot backend functions, files handling, triggering functions, etc.
* **Passed variables:** _none_
* **Returns:** _optional_ - for new menu entries list of ```webmgr.menu_entry``` objects. Possible fields: ```name```, ```url```, ```id```, ```icon```
* **Current functionality of ePiframe:** serving Web User Interface to configure and control the frame

The sites are created with [Flask Blueprints](https://flask.palletsprojects.com/en/2.0.x/blueprints/) and it is possible to use ePiframe template with embedded jQuery and Bootstrap 5 (check example). 

For new menu entries (optional) list of ```webmgr.menu_entry``` objects is used, possible fields: ```name```, ```url```, ```id```, ```icon```. ```name``` is the name of the menu entry to appear (e.g. "Show graph"), ```url``` is the link path e.g. "/test", ```id``` is the element ID to find it with javascript and for example change styling when active. ```icon``` should be taken from [Boostrap Icons](https://icons.getbootstrap.com/), e.g. "bi bi-alarm"

Example:

```
#add new website 'Test' with link to '<IP>/test'in WebUI menu:

def add_website (self, webmgr, usersmgr, backend):
	from plugins.<plugin_name>.<website_name> import <website_name>_bp
	menus = [ webmgr.menu_entry ('Test', '/test', 'test-menu', 'bi bi-apple') ] #can be more than one
	webmgr.add_menu_entries(menus) #optional
	websites = [ <website_name>_bp ] #can be more than one
	return websites
```

Inside plugin path create folders: _templates_ (for website templates) and _static_ (for static content, scripts, styles, etc.)

Files structure :

```
└── plugin_name
    ├── config.cfg
    ├── default
    │   └── config.default
    ├── _plugin.py
    ├── static
    │   └── ...
    ├── templates
    │   └── test.html
    └── test.py
```

Inside plugin path create file _<website_name>.py_ with:

```
	from flask import Blueprint, render_template
	from flask_login import login_required	
	<website_name>_bp = Blueprint('<website_name>_bp', __name__,  template_folder='templates', static_folder='static' )
	@<website_name>_bp.route('/test') #this is the URL of the site
	@login_required #user login is needed to visit. The order matters so this decorator should be the last one before method.
	def view():    
		return render_template('test.html', text='This text will be passed!')
```
		
Inside plugin templates folder create file test.html with:

```
	{% extends "layout.html" %} <!-- This will load ePiframe template, jQuery and Bootstrap -->
	{% block title %}Test{% endblock %}
	{% block head %}
	  {{ super() }}
	  <!-- Load static resources -->
	{% endblock %}
	{% block content %}
	   <!-- Content -->
		<p>{{ text }}</p>
	   <script>
	   	<!-- Scripts -->
			$(".test-menu").addClass("link-light"); <!--Light up website link in menu -->
	   </script>
	{% endblock %}	
```

References:
* [ePiframe Templates](https://github.com/MikeGawi/ePiframe/blob/master/templates/)

__*NOTE:*__ It is possible to add just the menu entry (e.g. add a link on ePiframe for a server site) with:

```
def add_website (self, webmgr, usersmgr, backend):
	menus = [ webmgr.menu_entry ('Server', '<server_ip>', 'server-menu', 'bi bi-server') ] #can be more than one
	webmgr.add_menu_entries(menus)
	return []
```

## Adding new actions

* **Method to override:** ```add_action```
* **Usage cases:** add action buttons in WebUI Tools section, e.g. control device, trigger system action, etc.
* **Passed modules:** 
	* [WebUI Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py) - Websites rendering, API functions, settings handling from WebUI, etc.
	* [Users Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/usersmanager.py) - WebUI users handling, access to users database, etc.
	* [Backend Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py) - All WebUI/Telegram Bot backend functions, files handling, triggering functions, etc.
* **Passed variables:** _none_
* **Returns:** dictionary of ```action``` key and ```webmgr.action_entry``` value objects with possible fields: ```name```, ```func```, ```icon```, ```action```
* **Current functionality of ePiframe:** reset service, reboot, power off, next photo actions

Dictionary of ```action``` key and ```webmgr.action_entry``` value objects is used, possible fields: ```name```, ```func```, ```icon```. ```action``` is the name of the button to appear (e.g. "Ping machine"), ```action``` is the action name e.g. "send_ping", ```func``` is the function to trigger and ```icon``` should be taken from [Boostrap Icons](https://icons.getbootstrap.com/), e.g. "bi bi-alarm".

Example:

```
#add two new action buttons to turn light on/off with configured IP:
	
def lighton(self):
	import requests
	requests.get(url = self.config(light_ip), params = 'ON')

def lightoff(self):
	import requests
	requests.get(url = self.config(light_ip), params = 'OFF')

def add_action (self, webmgr, usersmgr, backend):
	newactions = {
		'lighton' : webmgr.action_entry('Turn Light On', self.lighton, 'bi bi-lightbulb-fill', 'lighton'),
		'lightoff' : webmgr.action_entry('Turn Light Off', self.lightoff, 'bi bi-lightbulb', 'lightoff'),
	}
	return newactions
```

__*NOTE:*__ The new actions buttons will appear in the Tools section of ePiframe WebUI.

## Adding service thread

* **Method to override:** ```add_service_thread```
* **Usage cases:** add new thread to ePiframe service (```ePiframe_service.py```): frequently gathering data, scheduled triggers, etc.
* **Passed modules:** 
	* [ePiframe Service](https://github.com/MikeGawi/ePiframe/blob/master/ePiframe_service.py) - Service daemon object.
	* [Backend Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/backendmanager.py) - All WebUI/Telegram Bot backend functions, files handling, triggering functions, etc.
* **Passed variables:** _none_
* **Returns:** _nothing_ but this method will be started as a separate thread
* **Current functionality of ePiframe:** WebUI, statistics, Telegram Bot threads and frequently updating photo frame

Example:

```
#def add_service_thread (self, service, backend):
	#gather statistics every 60 seconds - persistent thread, enabled by configuration:
	from modules.statsmanager import statsmanager
	import time
	statsman = statsmanager(backend)
	while True:
		backend.refresh() #check if frame configuration changed and reload it
		if backend.is_web_enabled() and backend.stats_enabled():
			try:
				statsman.feed_stats()
			except Exception as e:
				self.logging.log(e)
				pass		
		time.sleep(60) #sleep 60 seconds between feeds
```

References:
* [ePiframe Service](https://github.com/MikeGawi/ePiframe/blob/master/ePiframe_service.py)

# Creating configuration

Configuration in ePiframe is very strict to validation, types, dependencies, etc. so the plugin should be the same. Settings are dynamically rendered in the WebUI according to the type thus some additional steps needs to be performed to get that right. There are two things to be done:
* [Configuration class](#configuration__class)
* [Configuration file](#configuration__file)

The plugin configuration can be checked the same way as ePiframe configuration:

```./ePiframe.py --check-config```

All the plugins configurations will be checked as well.

__*NOTE:*__ Allow users to configure as much as possible options of the plugin, e.g. if plugin puts text somewhere, allow user to pick the position, color, font size, etc.
__*NOTE:*__ Keep backward compatibility of the plugin configuration files, like ePiframe does, or indicate what needs to be changed manually to adapt the configuration to the newest plugin version after update

## Configuration class

Add configuration entries ```misc.configprop``` to ```configmgr``` class ```SETTINGS``` list inside ```_plugin.py``` file to allow validation, conversion, option dependencies, etc. for the configuration of the plugin. This structure will also help rendering settings entries in ePiframe WebUI.

Check:
* [ePiframe Config Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/configmanager.py)
* [ePiframe Config Property](https://github.com/MikeGawi/ePiframe/blob/master/misc/configprop.py)

Possible ```misc.configprop``` properties and methods passed in constructor:

|Property|Default Value|Description|
|--------|-------------|-----------|
|```name```|_none_|Name of the configuration entry that is also in the _config.cfg_ file|
|```configmanager```|_none_|Reference to the Configuration Manager object used to parse configuration. Usually ```self```|
|```prop_type```|```STRING_TYPE```|Type of the configuration property (check types below), used to validation and rendering in the WebUI|
|```notempty```|```True```|Flag to disallow empty values for the entry. ```True``` - value is needed, ```False``` - value can be empty|
|```dependency```|```None```|Property dependency check. More on that below|
|```minvalue```|```None```|Used to validate minimal value of numerical properties|
|```maxvalue```|```None```|Used to validate maximum value of numerical properties|
|```checkfunction```|```None```|Functon used to validate value of the property. It should return ```True``` when property value is correct|
|```special```|```None```|Structure to check more complicated property dependencies. More on that below|
|```length```|```None```|Property length check, e.g. list should have this number of elements. Should be used together with ```delimiter```|
|```delimiter```|```None```|Delimiter for list type properties, used to split values. Should be used together with ```length```|
|```possible```|```None```|List of possible values that property should be in|
|```resetneeded```|```None```|Flag to display "Reset needed after changing this property" alert in WebUI. Used to service related properties|
|```convert```|```None```|Method to convert value property to another value. More on that below|

```dependency``` is a structure that can be defined in two ways: by the name of the property that should enable child property (e.g. ```"dependency='is_function_enabled'"``` - that will check if boolean of ```is_function_enabled``` value is ```True``` and enable dependent property) or a name of the parent entry and the check function for more complicated checks, e.g. ```dependency=['display_type', displaymanager.get_spi()]```, the value of property ```'display_type'``` will be passed to ```displaymanager.get_spi()``` method and should return ```True``` if the value is right, only then the children entries will be enabled as well.

```special``` is defined as a method that gets two variables: check function and the list of properties that are dependent with each other, e.g. ```special=configprop.special(filteringmanager.verify_times, ['photos_from', 'photos_to'])```. The check function gets the list of properties values and should return ```True``` if the dependencies are met, e.g. check the start time and end time, end time shouldn't be before start time, so check function checks both values for that.

```convert``` is used for backward compatibility. The new value will be saved in the configuration, for example the date format changed and the new version needs to convert old property to the new format.

Possible property types:

|Type|Description|
|----|-----------|
|```STRING_TYPE```|Default type, used to hold text values|
|```FILE_TYPE```|File type, used to hold paths that will be checked if exists|
|```INTEGER_TYPE```|Integer value type, used to hold numerical values, with range checking|
|```FLOAT_TYPE```|Floating value type, used to hold real number values, with range checking, e.g. -0.5, 120.8, etc.|
|```BOOLEAN_TYPE```|Boolean value type, used to hold true/false values|
|```STRINGLIST_TYPE```|List of strings type, used to hold text lists, for option selection, combos, etc.|
|```INTLIST_TYPE```|List of integers type, used to hold numbers lists, for option selection, combos, etc.|
|```PASSWORD_TYPE```|Password type, used to hold passwords and will be masked in the WebUI|

Examples:

```
## Config manager class.
	class configmgr (configbase):
		def load_settings(self):
			## List of settings, one-to-one accurate with config.cfg and default/config.default files.
			## This structure allows validation, conversion, dependencies, value and type verification and more.
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
			## Get global configuration value here with self.get('<entry name>')
			
	## End of configmgr class.
```

## Configuration file

Fill in _<plugin_name>/default/config.default_ according to added settings and copy it to _<plugin_name>/config.cfg_ file (default file is used to restore default values the other one is used for the configuration).

Initially *config.cfg* and *config.default* should be the same.

Examples:

```
; This is a non-processed comment and it will not be parsed. Mind the space after semicolon.
; This file is a configuration file for the plugin and it is separated into sections with plain text names of config entries. 
; The parser is based on ConfigParser and You can refer to the documentation: https://docs.python.org/3/library/configparser.html
; Names (unique within whole file) should not contain spaces or special characters and should be followed by = and a value (empty value is also possible):
; name=value
; e.g.: 
; my_ip=127.0.0.1
; name=ePiframe
; size=120
; bool_value=0
; empty_value=
; list_value=2,3,2,1,2,3,4,3
; path=logs/ePiframe.log

; Sections are indicated by section name (unique within whole file) in square brackets and are used to divide entries into groups:
; e.g.
; [Section With Space]
; [Section 1]

; Below there is an example of section and entry. The entry comment marked with '# ' will be parsed and used as a help tip in WebUI. 
; The lines will be concatenated into one and added as a help tip to the next entry below.
; Such comment should provide precise information about what entry does, possible values and a default value.

[General]

# Set 1 to enable plugin, 0 to disable.
; This line still won't be parsed.
# Default: 1 (enabled)
is_enabled=1
```

References:
* [ePiframe config.cfg file](https://github.com/MikeGawi/ePiframe/blob/master/config.cfg)

# Plugin installation

According to the [contribution statements](#contribution), plugin should precisely describe:
* What external API's/sites/modules/projects it uses and if they have limitations or price
* Include a detailed installation instruction, what needs to be installed and configured

But there are some basic steps typical for the ePiframe infrastructure that are common for all plugins:
* Clone/download/extract the plugin to _<ePiframe_path>/plugins/<plugin_name_folder>_
* Configure plugin with _<ePiframe_path>/plugins/<plugin_name_folder>.config.cfg_ file or in ePiframe WebUI under _Plugins/<plugin_name>_
* Check configuration in WebUI or with ```./ePiframe.py --check-config``` command

# Examples

* Stock Information
* Frames and Quotes
* Photo Filters

# Tutorial

Small tutorial that gathers all steps needed to implement a plugin with different functionalities.