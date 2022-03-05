# ePiframe-plugin tutorial

In this tutorial we will gather all steps needed to create a multi-functional ePiframe plugin. Some functions may seem unecessary or exaggerated but this is only done for tutorial purposes and to show how much one plugin can do.

## The plugin

Let's consider a plugin with functions:
* [Step 1: Photo collecting](#step-1-photo-collection) - Collect the photos from remote host source with [rsync](https://en.wikipedia.org/wiki/Rsync)
* [Step 2: Retriving the photo](#step-2-retriving-the-photo) - When photo from this source (as more can be enabled) will be chosen, this plugin will have a method to retrieve the file from the source
* [Step 3: Photo list](#step-3-photo-list) - These photos will be collected, filtered, sorted, etc., will be randomly picked up by ePiframe and will have thumbnail generated
* [Step 4: Photo processing](#step-4-photo-processing) - Photo showed from the new source will have a watermark
* [Step 5: Extending API](#step-5-extending-api) - Plugin will extend the ePiframe API with methods to show thumbnail and original photo
* [Step 6: Adding website](#step-6-adding-website) - Plugin will add the website to ePiframe WebUI to present the gathered photos (with use of API function stated above)
* [Step 7: Adding configuration](#step-7-adding-configuration) - Plugin will have configuration file that can be configured in CLI or WebUI, that validates entries and allows to customize its functionality

## Prerequisites

Of course you already have a working ePiframe and all dependencies installed so the most important thing now to start with is... the name of your project. It is really nice to have it before starting anything as it will help with the flow and all the thoughs will have a name under them. At some point ePiframe had a working name *GoopheePi* (Google Photos ePaper Pi) but later, after adding new functions I thought that with e-Paper display it looks *epic* so it was changed to *ePiframe*. The only limitation for the name is not to use dots and dashes as that will disturb ePiframe plugin recognition mechanism.

Let's name this plugin *ePiSync* to stick to ePiframe name and emphasize sync function.

### Getting the code

* Start a new project with GitHub [*ePiframe_plugin*](https://github.com/MikeGawi/ePiframe_plugin) project template
* Clone the repository ```git clone <plugin URL>``` or download and unzip it
* Inside ```_plugin.py``` file fill in the basic data like name, description, author, etc.

Let's put our data:
```
name = 'ePiSync'
author = 'ePiframe_plugin tutorial'
description = 'Sync photos with rsync from remote location, generate thumbnails, then add watermark, API method and a website to view new photos'
site = 'https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md'
info = 'All steps gathered here to create a multi-functional ePiframe plugin'
```

### Installation of 3rd party components

Next thing is to gather all needed components. In case of our plugin we need to have *rsync* installed. It is a standard component of the Raspberry Pi OS *BUT* it's better to mention this in the plugin requirements and documentation. The rest is already embedded in ePiframe: Pillow for Python image processing, ImageMagick for command line image processing, Flask for API and website related things and Pandas for photo collection handling.

If there are more prerequisites needed for your plugin, i.e. external API's, sites, modules, projects - mention in the documentation how to install/configure them and whether they have limitations or price.

Let's install rsync:
```
sudo apt update
sudo apt install rsync
```

## Implementation

Plugin will be installed in <*ePiframe root path*>*/plugins/*<*plugin_name*> path and you can just put it there to make tests easier but remember to [stop the service](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#service-control) so you don't interfere a working frame.

ePiframe [can be installed](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#manual) also on non-Pi architectures and to avoid Pi system check, just run ePiframe with ```--test``` flag from CLI, i.e. ```./ePiframe.py --test```. Running WebUI and other services is possible with [other commands](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#command-line).

Plugins base class is embedded in the ePiframe code and the plugin class inherits exposed methods that can be overriden. The plugin manager inside ePiframe will run these methods in different phases of ePiframe runtime and will do that only if the method is used. 

The scope starts in the root folder of ePiframe so if some module needs to be used it should import from ```modules.<module_name>```, e.g. ```from modules.databasemanager import databasemanager```. If the plugin needs additional files/modules these can be imported with the same module hierarchy, i.e. ```plugins.<plugin_name>.<module_name>```.

Most of the basic ePiframe modules that can be useful for particular plugins methods are passed during the run but all needed ePiframe ingredients can be imported if needed.

If exception occurs during the run of overridden method (that stops the next steps of the plugin) an exception should be raised to be caught by the main script to be properly reported in logs.

Let's start with implementing steps needed by this plugin.

### Step 1: Photo collection

*Collect the photos from remote host source with [rsync](https://en.wikipedia.org/wiki/Rsync)*

rsync is an utility for efficiently transferring and synchronizing files between a computer and a storage drive and across networked computers by comparing the modification times and sizes of files. The benefit for using rsync is that it can omit already existing files and get only the new ones to a central Unix server using rsync/ssh and standard Unix accounts.

Generic syntax:
```
rsync [OPTION] … [USER@]HOST:SRC [DEST]
```

We need a *HOST* server that is providing photos under some *SRC* location and *USER* with access to this source. We don't want a situation that user needs to provide a password for synchronization to happen as ePiframe should be able to work headlessly. There are methods to pass the account password for the transfer ([sshpass](https://www.redhat.com/sysadmin/ssh-automation-sshpass)) but there are more elegant solutions to do that - SSH keys.

On our target server, so the one that will gather photos from the *HOST*, we will generate public SSH key with no password for the user that ePiframe works for (usually *pi*):
```
ssh-keygen -f ~/.ssh/id_rsa -q -P "" 
cat ~/.ssh/id_rsa.pub
```

This is our public SSH key that can be placed on other hosts to give us access:
```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDLVDBIpdpfePg/a6h8au1HTKPPrg8wuTrjdh0QFVPpTI4KHctf6/FGg1NOgM++hrDlbrDVStKn/b3Mu65//tuvY5SG9sR4vrINCSQF++a+YRTGU6Sn4ltKpyj3usHERvBndtFXoDxsYKRCtPfgm1BGTBpoSl2A7lrwnmVSg+u11FOa1xSZ393aaBFDSeX8GlJf1SojWYIAbE25Xe3z5L232vZ5acC2PJkvKctzvUttJCP91gbNe5FSwDolE44diYbNYqEtvq2Jt8x45YzgFSVKf6ffnPwnUDwhtvc2f317TKx9l2Eq4aWqXTOMiPFA5ZRM/CF0IJCqeXG6s+qVfRjB pi@ePiframe
```

Let's copy this key to clipboard, login to destination server (with the *USER* account that will be used for synchronization) and place this SSH key into *~/.ssh/authorized_keys* file. If the file doesn't exist, create it manually:
```
mkdir ~/.ssh
chmod 0700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 0644 ~/.ssh/authorized_keys
```

Now we can check if we're able to log in from target server to source with SSH (It should not ask for password):
```
ssh USER@HOST
```

So now we can combine an rsync command that is gathering the files, best if it would have timeout and flag to not overwrite already existing files. Few seconds in manual and:
```
rsync --timeout=TIME --ignore-existing USER@HOST:SRC DEST
```

According to the [contribution additional hints](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#additional-hints) of ePiframe_plugin: 

> Allow users to configure as much as possible options of the plugin, e.g. if plugin puts text somewhere, allow user to pick the position, color, font size, etc.

We should add these values to [configuration class and file](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#creating-configuration) to allow customization and validation of settings.

In *_plugin.py* file there's:
```
class configmgr (configbase):
		def load_settings(self):
			self.SETTINGS = [
				configprop('is_enabled', self, prop_type=configprop.BOOLEAN_TYPE), # this setting is required! 
				...
```

to put the configuration entries to. This structure allows validation, type check, value check and lot more (WebUI rendering for example) of plugin settings. Let's put our new variables:
```
## Config manager class.
class configmgr (configbase):
	def load_settings(self):
		self.SETTINGS = [
			configprop('is_enabled', self, prop_type=configprop.BOOLEAN_TYPE), # this setting is required! 
			#local path to sync to, notice that convert method is used to pass value to the create_dir method that creates the path if not exists
			#that's just a tricky way to use convert
			configprop('local_path', self, prop_type=configprop.FILE_TYPE, dependency='is_enabled', convert=localsourcemanager.create_dir),
			configprop('remote_path', self, dependency='is_enabled'), #this is string (by default)
			configprop('remote_host', self, dependency='is_enabled'), #all are dependent to is_enabled
			configprop('remote_user', self, dependency='is_enabled'), #and will be enabled only if is_enabled is true
			configprop('sync_timeout', self, minvalue=2, maxvalue=10, prop_type=configprop.INTEGER_TYPE, dependency='is_enabled'), #integer values with min and max thresholds
			...
```

```local_path``` (DEST = destination of photos) is a file type property whose existance will be checked during configuration loading. Here's a small trick: ```convert``` method used for converting value property to another value (it just passes the value to the method and returns new value) is used to create the directory if it's missing. It doesn't change the value as method is not returning new one. That's a trick to do something with the value before validation. The method ```create_dir``` is a part of [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) module.

Next properties: ```remote_path``` (SRC = remote host source path), ```remote_host``` (HOST = remote host IP or hostname) and ```remote_user``` (USER = remote host user used for sync) are string properties by default and will be checked if are not empty (by default).

Last property ```sync_timeout``` is an integer (type will be checked) and has value limits - minimum and maximum. If the value of this property is outside the range, it will produce an error. It is possible to specify only upper or only lower limit too. For more possibilities check: [configuration class](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#configuration-class).

All properties will be dependent on ```is_enabled``` boolean property (true or false) that determines if plugin is enabled or not. They will not be validated if disabled and will be blocked in WebUI for changes.

To get plugins config properties simply use ```self.config.get(NAME)``` for text properties and ```self.config.getint(NAME)``` for integer.

With that we can start implementing source collecting method for our plugin. The plugin base class method to overwrite is [```add_photo_source```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#adding-photo-source) and it returns Pandas DataFrame of collected photos with columns ```idlabel```, ```creationlabel```, ```sourcelabel``` (at least). So we need to sync the files in the destination path and gather them in a DataFrame (photos only, so extension-wisely), add creation time and source name (to indicate this new source).

For collecting the DataFrame we can use ePiframe built-in [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) module. That has all we need and is used for ePiframe collecting local photo source. Needed extensions are in ```constants.EXTENSIONS``` and the source is anything we wish as long it is unique, so name of the plugin for example.

Here's the code:

```
def add_photo_source (self, idlabel, creationlabel, sourcelabel, photomgr):
	cmd = 'rsync --timeout={} --ignore-existing {}@{}:{}* {} 2>&1 > /dev/null' #command string
	source = self.config.get('remote_path') if self.config.get('remote_path').endswith('/') else self.config.get('remote_path') + '/' #adding / at the end if not exists
	os.system(cmd.format(self.config.get('sync_timeout'), self.config.get('remote_user'), self.config.get('remote_host'), source, self.config.get('local_path'))) #starting command with args

	loc = localsourcemanager (self.config.get('local_path'), False, constants.EXTENSIONS) #getting synced files with localsourcemanager
	self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
	return loc.get_local_photos(idlabel, creationlabel, sourcelabel, self.SOURCE) #returning dataframe of photos with needed labels
```

* OS command - ``cmd`` was combined from config properties (check ```cmd.format...``` part)
* ```source``` remote host path is checked for containing '/' at the end and added if not (for files wildcard , i.e. '\*' in ```cmd```)
* ```os.system(...)``` is the method to run the OS command
* [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) module was used to create a DataFrame of files with specific extensions
* ```self.SOURCE``` - required source indicator value has been set
* method returns DataFrame with help of [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) module 

And that's it!

With this method ePiframe will sync all the photos with recognized extensions to a local destination location from remote source and will gather needed data to process the photos list. This list will be used for sorting, filtering and photo picking.

### Step 2: Retriving the photo

*When photo from this source (as more can be enabled) will be chosen, this plugin will have a method to retrieve the file from the source*

This step may be hard to understand but let's shine some light on the situation:
* Imagine a photo source in the Web that is slow and has thousands of terabytes of photos
* Downloading this data to RasPi would kill it
* Such amount of data needs a huge storage attached to Rasberry Pi
* There may be some limitations on hosting site that can timeout or just hang the process

Problematic, right? Especially when ePiframe works on Raspberry Pi Zero, so ePiframe just gathers the data (i.e. ID, creationtime, etc.) from this source, gets all needed parameters and works on the list. If it randomly picks the photo from this source *only then* downloads it and processes. 

It works for Google Photos where there is a huge number of photos to download and we get only the one we want. For local storage source it's different because we already have photos on the storage and we just want to pick/copy the one we want to process and display on frame.

This step should be number 3. as it's executed after [Step 3: Photo list](#step-3-photo-list) but let's keep it here to stay in the source context.

The plugin base class method to overwrite is [```add_photo_source_get_file```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#adding-new-photo-source-file-retrieving-method) and it should return photo final filename, best if it contains an extension. 

So this method should _retrieve the file_ and return the full path of the downloaded photo with extension. In the case of our plugin files are already in the local destination path so we need to recognize file type and copy it to target path for processing. As getting file extension is hard (some sources like Google Photos provide image [MIME type](https://en.wikipedia.org/wiki/MIME) that is indicating the right format) there are some ePiframe methods in [Convert Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py) module to do that. 

To use them just simply do:
```
def add_photo_source_get_file (self, photo, path, filename, idlabel, creationlabel, sourcelabel, photomgr):
	from modules.convertmanager import convertmanager
	convertman = convertmanager()
	filename_ret = ''		
	err, imagetype = convertman.get_image_format(self.globalconfig.get('convert_bin_path'), photo[idlabel], constants.FIRST_FRAME_GIF) #if this is a GIF then just check the first frame
	if not err and imagetype:
		filename_ret = filename + "." + constants.TYPE_TO_EXTENSION[constants.MIME_START + imagetype.lower()]
	filename_ret = os.path.join(path, filename_ret)
```

* ```filename``` is photo target name (only), no extension, ```path``` is the target path so the method should return "path + filename + . + extension"
* create [Convert Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py) module object and use ```convertman.get_image_format``` method to get the MIME type
* ```self.globalconfig``` is a global ePiframe configuration class that works like our plugin ```self.config``` object. Check [ePiframe config.cfg file](https://github.com/MikeGawi/ePiframe/blob/master/config.cfg) for more properties
* ```self.globalconfig.get('convert_bin_path')``` returns configured path to ImageMagick photo command line converter
* ```photo``` is the photos Pandas element that has been picked up by ePiframe to display. It contains all data collected in the [Step 1: Photo collecting](#step-1-photo-collection). ID (under ```photo[idlabel]```) in that case is a file path
* ```constants.FIRST_FRAME_GIF``` is a flag to process only the first frame of GIF format as method will return type for all frames by default
* ```constants.TYPE_TO_EXTENSION``` is the dictionary to convert MIME to image format extension. ePiframe allows also extension to MIME conversion, check more on [constants file](https://github.com/MikeGawi/ePiframe/blob/master/misc/constants.py)
* ```constants.MIME_START``` is the MIME type string identifier used to create proper MIME from the ```imagetype``` returned by [Convert Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/convertmanager.py) module
* ```filename_ret = os.path.join(path, filename_ret)``` joins path and final filename

So we have now a final photo path with full destination filename. The last thing we need to do is to copy the source file synced from remote location to ```filename_ret``` with *shutil*. The final code looks like this:
```	
def add_photo_source_get_file (self, photo, path, filename, idlabel, creationlabel, sourcelabel, photomgr):
	filename_ret = filename	
	#getting image MIME type with ImageMagick
	err, imagetype = convertmanager().get_image_format(self.globalconfig.get('convert_bin_path'), photo[idlabel], constants.FIRST_FRAME_GIF) #if this is a GIF then just check the first frame
	if not err and imagetype:
		filename_ret = filename + "." + constants.TYPE_TO_EXTENSION[constants.MIME_START + imagetype.lower()] #converting MIME type to extension
	filename_ret = os.path.join(path, filename_ret) #combining filename
	shutil.copy(photo[idlabel], filename_ret) #copying to target path
	return filename_ret
```

**_❗ IMPORTANT ❗_** This method will be executed ONLY when the ```sourcelabel``` pandas column value of chosen photo is the same as set in [Step 1: Photo collecting](#step-1-photo-collection).

**_❗ IMPORTANT ❗_** If not overwritten, this method will do exactly the same code as the one written here, by default if the ```self.Source``` has been set, so in case of this plugin it is redundant.

### Step 3: Photo list

*These photos will be collected, filtered, sorted, etc., will be randomly picked up by ePiframe and will have thumbnail generated*

Just to remind:

>ePiframe works only on the list of photos information not on files as it would be resources consuming. The only file that it works on is the one that is processed and displayed on frame.

So we collect a photos list from different sources and plugins and ePiframe will sort it (ascendingly, descendingly), filter by creation date, by number of photos automatically IF all crucial Pandas columns for this source are collected, that is ID, creation time and source name. We don't need to do anything here but we get a whole collection of photos passed to overwritten [```change_photos_list```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#changing-photos-list) method. So just to show one of the possibilities let's generate thumbnails for photos from this source. Of course that could be also done in [Step 1: Photo collecting](#step-1-photo-collection). 

More general purpose of [```change_photos_list```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#changing-photos-list) method is:
>changing final photos list, e.g. sorting, filtering, turning upside-down, adding AI recognition etc.

and it should return modified ```photo_list``` (Pandas DataFrame).

First, we need a method to generate photo thumbnail and as we have ImageMagick on board that will be easy. To generate same size, rectangular thumbnail from photo of any size we should use command:
```
convert <input_photo> -background white -gravity center -sample <thumbnail_width>x<thumbnail_height> -extent <thumbnail_width>x<thumbnail_height> <output_photo>
```

And again we should add width and height to configuration for user customization:
```
## Config manager class.
	class configmgr (configbase):
		def load_settings(self):
			self.SETTINGS = [
				...
				configprop('thumb_width', self, minvalue=100, maxvalue=400, prop_type=configprop.INTEGER_TYPE, dependency='is_enabled'),
				configprop('thumb_height', self, minvalue=100, maxvalue=300, prop_type=configprop.INTEGER_TYPE, dependency='is_enabled')
				...
```

* ```thumb_width``` and ```thumb_height``` are integer values with min and max thresholds dependent on ```is_enabled``` flag

So let's combine this into code:
```
__THUMB_NAME = "thumb_"

def __subproc (self, arg):
	#method to start process with arguments. 
	#it needs a list of arguments
	args = arg.split()
	process = subprocess.Popen(args, stdout=subprocess.PIPE)
	process.wait()
	out, err = process.communicate()
	return out, err 

#method that changes collected photo list
def change_photos_list (self, idlabel, creationlabel, sourcelabel, photo_list, photomgr, indexmgr, filteringmgr):		
	size = self.config.get('thumb_width') + 'x' + self.config.get('thumb_height')
	thumb_cmd = '{} {} -background white -gravity center -sample {} -extent {} {}' #thumbnail generation command
	rows = photo_list[photo_list[sourcelabel] == self.SOURCE] #getting rows only from the source of this plugin
	localsourcemanager.create_dir(os.path.join(self.config.get('local_path'), self.__THUMB_NAME + '/')) #creating thumbnails directory

	for index, row in rows.iterrows(): #iteriting through rows
		thumb_file = os.path.join(os.path.dirname(row[idlabel]), self.__THUMB_NAME + '/', self.__THUMB_NAME + os.path.basename(row[idlabel])) #getting thumb path
		if not os.path.exists(thumb_file): 
			out, err = self.__subproc(thumb_cmd.format(self.globalconfig.get('convert_bin_path'), row[idlabel], size, size, thumb_file)) #creating thumbnail
			if err:	raise Exception(err)

	return photo_list
```

* ```__subproc``` method is a helping method to start a process and get command ouput. This is just a different method of running OS command than ```os.system(...)``` used in [Step 1: Photo collecting](#step-1-photo-collection)
* ```size``` is a formatted string with width and height values taken from the plugin configuration
* ```thumb_cmd``` is a string representing ImageMagick thumbnail generating command
* ```rows``` are the Pandas rows from whole photos collection gathered from photos sources that will be filtered out by the source name, i.e. ```self.SOURCE``` set in [Step 1: Photo collecting](#step-1-photo-collection)
* ```localsourcemanager.create_dir``` is a method of [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) module to create a directory if it doesn't exist - thumbnail folder in that case
* ```self.__THUMB_NAME``` is a prefix for thumbnail file and it is also used as a thumbnail folder name
* ```for index, row in rows.iterrows():``` allows iteriting through Pandas rows and returns ```index, row``` in every loop cycle
* ```thumb_file``` is generated from photo ID (source filename in this case) its path, filename and thumbnail idetifier prefix. It will be created in thumbnail folder
* the thumbnail will be generated ONLY if it doesn't exist for the photo
* ```self.__subproc``` will execute ImageMagick command for every file and generate thumbnail, return output and error which will raise an exception if necessary
* ```return photo_list``` is returning initial ```photo_list``` as nothing has changed

After ```change_photos_list``` execution by ePiframe the thumbnails will be generated in additional folder for every synced photo like this:
```
photos
├── photo1.jpg
├── photo2.jpg
├── photo3.jpg
├── photo4.jpg
└── thumb_
    ├── thumb_photo1.jpg
    ├── thumb_photo2.jpg
    ├── thumb_photo3.jpg
    └── thumb_photo4.jpg
```

where *photos* is the local destination path of synchronized photos and *photo\[1-4\].jpg* are synced photos.

In the case of our plugin the photo list has not been changed but we could see how to use this method for different purposes.

### Step 4: Photo processing

*Photo showed from the new source will have a watermark*

Plugin base class allows two methods of the chosen (from collection) photo processing:
* preprocessing done by [```preprocess_photo```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#photo-preprocessing) method that processes the photo before the basic conversion when it is currently in the original version (high quality photo)
* postprocessing done by [```postprocess_photo```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#photo-postprocessing) method that processes the photo before sending to display (and it's already converted to the display)

Watermark adding procedure can be done on both but postprocessing is more demanding as photo can already be converted for the display, so we will use this for tutorial purposes.

Both methods are not returning any output as they should overwrite passed photo filename.

For adding watermark, so pasting other image atop of the photo, we will use [Pillow](https://pillow.readthedocs.io/en/stable/) that is a dependency of ePiframe. Pillow - The Python Imaging Library adds image processing capabilities to Python interpreter.

The code is pretty straightforward as Pillow is easy to use but the photo is already converted to fit the display and that's a bit problematic:
* the photo can be in vertical position, rotated clockwise or counterclockwise to fit vertically positioned frames
* have reduced palette of colors as can be converted to fit black and white e-Paper display

Easiest way to handle rotation is to read ePiframe global configuration and get rotation state, then rotate in the opposite direction, process the image and rotate back. To do that just simply:
```
from PIL import Image, ImageColor

def postprocess_photo (self, finalphoto, width, height, is_horizontal, convertmgr, photo, idlabel, creationlabel, sourcelabel):
	image = Image.open(finalphoto)
	if not is_horizontal: image = image.transpose(Image.ROTATE_90 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_270) #rotating image if frame not in horizontal position
	...
	<image processing>
	...
	
	if not is_horizontal: image = image.transpose(Image.ROTATE_270 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_90) #rotating back if in vertical position
	image.save(finalphoto) #saving as final photo
```

* ```Image.open``` opens an image from ```finalphoto``` path
* ```is_horizontal``` is passed to the method by ePiframe and it's indicating if the frame is in horizontal position
* ```image.transpose``` is a Pillow transposing method that is rotating to specified angle value, e.g. ```Image.ROTATE_90```
* ```self.globalconfig.getint('rotation')``` returns current photo rotation in degrees
* ```image.save``` saves processed image to provided ```finalphoto``` path - it's overwriting the input file

This code loads the photo to ```image``` object, resets the rotation if any exists, processes it and saves rotated image back.

The next problem is current photo colors mode we need to take care of as new pasted image, our watermark, can be in a different mode. To get current ```image``` mode use ```mode = image.mode``` and to convert ```watermark``` to this mode - ```watermark = watermark.convert(mode)```. It is also possible to set other modes, i.e. RGB, RGBA, CMYK [and more](https://pillow.readthedocs.io/en/stable/handbook/concepts.html).

We also need method to resize watermark - [```Image.resize```](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.resize) and to paste image to image - [```Image.paste```](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.paste). 

With all that knowledge we can summarize or code like this:
```
from PIL import Image, ImageColor

def postprocess_photo (self, finalphoto, width, height, is_horizontal, convertmgr, photo, idlabel, creationlabel, sourcelabel):
	if self.SOURCE and not photo.empty and photo[sourcelabel] == self.SOURCE:
		image = Image.open(finalphoto)
		mode = image.mode #get photo mode
		if not is_horizontal: image = image.transpose(Image.ROTATE_90 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_270) #rotating image if frame not in horizontal position
		newimage = image.convert('RGBA') #converting to RGB with alpha

		watermark = Image.open(os.path.join(self.path, 'static/images/watermark.png')).convert('RGBA') #self.path is a plugin path
		watermark = watermark.resize((width//10, height//10)) #resizing watermark to 1/10 of width and height
		newimage.paste(watermark, (width-10-width//10, height-10-height//10), watermark) #pasting watermark on the photo and with watermark mask
		newimage = newimage.convert(mode) #convert back to original photo mode

		if not is_horizontal: newimage = newimage.transpose(Image.ROTATE_270 if self.globalconfig.getint('rotation') == 90 else Image.ROTATE_90) #rotating back if in vertical position

		newimage.save(finalphoto) #saving as final photo
```

* this method is executed for every photo but with ```if self.SOURCE and not photo.empty and photo[sourcelabel] == self.SOURCE``` we determine that it will be done only for photos with the source like ```self.SOURCE```. Checking if ```photo``` is empty is because image pre/postprocessing may be also done manually from the [command line](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#command-line) and in that case there is no photos Pandas collection
* ```finalphoto``` is open, rotated to an normal position (if vertical) and converted to RGBA (Red Green Blue + Alpha) as ```newimage```, to not supress any transparent areas of watermark. Old color mode is saved to ```mode```
* watermark is open to ```watermark```, also converted to RGBA mode, resized to 1/10 of a width and height of target photo and pasted on right-bottom position minus 10 pixels margin from right and bottom
* image is converted back to original color mode, rotated back to initial rotation and saved as input image

The results look like this:
<p align="center">
	<img src ="https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/assets/watermark.bmp" width="400">
</p>

When taken care of image mode and rotation, plugin can make any photo processing as long as it's not hardware demanding or at least optimized for Raspberry Pi.

### Step 5: Extending API

*Plugin will extend the ePiframe API with methods to show thumbnail and original photo*

ePiframe comes with a built in [API](https://github.com/MikeGawi/ePiframe/blob/master/docs/API.md) that can perform simple actions by calling an URL (with [curl](https://curl.se/) for example), e.g. reboot frame, change photo, get logs, get current photo, etc. Plugins can extend this functionality and add new actions like adding REST API, return hardware statistics, expose API for smart home server, etc.

As ePiframe WebUI is based on Flask so are API methods and in simple words we create a method to perform action or return something and create a binding to this method that is triggered by URL.

Plugin base class method to overwrite is [```extend_api```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#extending-api) that returns list of ```webmgr.site_bind``` objects (possible fields: ```url```, ```func```, ```methods = ['GET']```, ```defaults = None```) that have typical [Flask binding](https://flask.palletsprojects.com/en/2.0.x/quickstart/#url-building) syntax and point to a function to trigger, where ```webmgr``` is a passed [WebUI Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py).

Example:
```
#method to call with /api/get_text/<text>
def get_text_func(self, text=str()):
	from flask import jsonify
	return jsonify(text_label=text)	

#This is the plugin method that is fired:
def extend_api (self, webmgr, usersmgr, backend):
	return [ webmgr.site_bind('/api/get_text/<text>', self.get_text_func) ]
```

* ```get_text_func``` method receives ```text``` value from ```<IP>/api/get_text/<text>``` URL and returns JSON version of it
* ```extend_api``` method returns Flask binding to ```get_text_func``` method to bind method and URL

More than one method can be added and ```extend_api``` method should just return a list of them.

So back to our plugin: *API method should return a thumbnail and original photo* and that will be used by new website to display photos synced by the plugin.

A good working reference would be ```get_image``` method in [WebUI Manager](https://github.com/MikeGawi/ePiframe/blob/eb3753684360848cc79278a45121879b5bd9ab0b/modules/webuimanager.py#L174) that is basically doing the same thing - it just uses Flask ```send_file``` method to expose file under URL.

As our new URL will return only one file at once we need to allow to pick any file and have option to display full-sized photo or just a thumbnail. Every Flask bounded method gets a request that is passed to URL and it contains arguments. To get request argument we need to use ```request.args.get(<NAME>)``` and get the passed value with ```http://<URL>?<NAME>=<VALUE>&<NAME2>=<VALUE2>&...```. In our case we need to get index of the file and thumbnail flag. To have the list of synced files we can use [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) and ```get.files()``` method as we did in [Step 1: Photo collecting](#step-1-photo-collection).

To get the files from configured path:
```
localsourcemanager(self.config.get('local_path'), False, constants.EXTENSIONS).get_files()
```

* this returns a list of gathered photos paths according to their extensions. ```False``` flag is not to check the location recursively

Flask [```send_file```](https://flask.palletsprojects.com/en/2.0.x/api/#flask.send_file) method that retuns file under URL needs to know the MIME type of the image, to get that we can use ePiframe dictionary in [constants file](https://github.com/MikeGawi/ePiframe/blob/master/misc/constants.py):
```
mimetype=constants.EXTENSION_TO_TYPE[str(filename).rsplit('.')[-1].lower()])
```

* ```mimetype``` will have MIME type value of the ```filename``` according to it's extracted extension

After gathering all information, we get code like this:
```
from flask import request, send_file
from flask_login import login_required

def get_files(self):
	return localsourcemanager(self.config.get('local_path'), False, constants.EXTENSIONS).get_files() #get all files with localsourcemanager

#login is required to use this API entry
@login_required
def get_sync_image(self):
	filename = str()
	filenum =  int(request.args.get('file')) if 'file' in request.args and request.args.get('file').isdigit() else 0 #if file=<value> in URL then read file number	
	files = self.get_files()

	try:
		#get filename or thumbnail filename if URL contains thumb argument
		filename = files[filenum] if not 'thumb' in request.args else os.path.join(os.path.dirname(files[filenum]), self.__THUMB_NAME + '/', self.__THUMB_NAME + os.path.basename(files[filenum]))
	except Exception:
		pass
	return send_file(filename, mimetype=constants.EXTENSION_TO_TYPE[str(filename).rsplit('.')[-1].lower()]) if filename else 'No Photo!' #send file if exists and message if doesn't

#method that adds new API method
def extend_api (self, webmgr, usersmgr, backend):
	return [ webmgr.site_bind('/api/get_sync_image', self.get_sync_image) ] #bind API method with URL
```

* ```get_files``` is a helper method that returns list of synced photo paths for the configured ```local_path``` property
* ```@login_required``` is a decorator that determines if this function needs user to be logged in to visit website. If not added then anyone, even non-authorized users can access it
* ```get_sync_image``` method retrieves ```filenum``` - index of desired photo from ```request.args``` passed to URL like ```http://<IP>/api/get_sync_image?file=1```
* ```filenum``` index is used to get the file from ```files``` - list of photos and if request contains ```thumb``` argument then it takes the file from thumbnail folder and filename with thumbnail prefix. Thumbnail request argument is passed like this: ```http://<IP>/api/get_sync_image?file=1&thumb=```
* method returns file with its MIME type or error text if any occurs

The results look like this:
<div align="center">

|<img src ="https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/assets/apiphoto.png" width="400"/>| 
|:--:| 
|*Photo returned by API by URL with photo index argument*|

|<img src ="https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/assets/apithumb.png" width="400"/>| 
|:--:| 
|*Photo thumbnail returned by API by URL with photo index argument and thumbnail flag*|

|<img src ="https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/assets/apierror.png" width="400"/>| 
|:--:| 
|*API error for retriving the photo index out of files list range*|
</div>

### Step 6: Adding website

*Plugin will add the website to ePiframe WebUI to present the gathered photos (with use of API function stated above)*

We have almost everything in place: photos synced to a local storage, generated photos thumbnails and API methods to simply display them. Now it's time to create a new ePiframe website that presents what we did by now. 

The sites are created with [Flask Blueprints](https://flask.palletsprojects.com/en/2.0.x/blueprints/) and it is possible to use ePiframe template with embedded jQuery and Bootstrap 5 that makes them very functional and beautiful. 

Plugin base class method to overwrite is [```add_website```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#adding-new-websites-and-menu-entries) and for new menu entries (optional) list of ```webmgr.menu_entry``` from passed [WebUI Manager](https://github.com/MikeGawi/ePiframe/blob/master/modules/webuimanager.py) objects is used, possible fields: ```name```, ```url```, ```id```, ```icon```. ```name``` is the name of the menu entry to appear (e.g. "Show graph"), ```url``` is the link path e.g. "/test", ```id``` is the element ID to find it with javascript and for example change styling when active. ```icon``` should be taken from [Boostrap Icons](https://icons.getbootstrap.com/), e.g. "bi bi-alarm".

This process is more complex than previous ones as it needs more files to create and more than Python knowledge.

Inside plugin path let's create folders: _templates_ (for website templates) and _static_ (for static content, scripts, styles, etc.). File *show.py* should be created along with plugin *_plugin.py* file and *show.html* in *templates* folder.

Files structure :
```
├── _plugin.py
├── show.py
├── static
│   └── images
│       └── watermark.png
└── templates
    └── show.html
```

Overwritten plugin base method will be very simple to implement:
```
def add_website (self, webmgr, usersmgr, backend):
	from plugins.ePiSync.show import show #import site
	webmgr.add_menu_entries([ webmgr.menu_entry ('ePiSync', '/episync', 'episync-menu', 'bi bi-image') ]) #create menu entry with name, URL, menu id and icon
	site = show(self) #create site class and pass plugin
	return [ site.get_show_bp() ] #return list of websites to add
```

* ```from plugins.ePiSync.show import show``` imports the *show.py* file Flask Blueprint of the website we're adding
* ```webmgr.add_menu_entries``` method add menu entries to ePiframe WebUI menu (more than one are allowed)
* ```webmgr.menu_entry ('ePiSync', '/episync', 'episync-menu', 'bi bi-image')``` is a menu entry that name is *ePisync*, takes to ```/episync``` URL, menu ID is ```episync-menu``` and icon is [```bi bi image```](https://icons.getbootstrap.com/icons/image/)
* ```site``` is a ```show``` object that is passing plugin class to constructor
* method returns list of added websites (more than one allowed)

Now let's create a Blueprint of our ePisync website. *show.py* file code:
```
from flask import Blueprint, render_template
from flask_login import login_required	

class show():
	
	#constructor to pass plugin class
	def __init__(self, plugin):
		self.plugin = plugin
	
	#returns generated blueprint website with injected plugin class
	def get_show_bp(self):	
		show_bp = Blueprint('show_bp', __name__,  template_folder='templates', static_folder='static' )

		@show_bp.route('/episync') #this is the URL of the site
		@login_required #user login is needed to visit.
		def show():    
			return render_template('show.html', number=len(self.plugin.get_files()), width=self.plugin.config.get('thumb_width'), height=self.plugin.config.get('thumb_height'))
		
		return show_bp
```

* class ```show``` is a helping class that generates Blueprint and injects plugin class
* plugin class is injected in the constructor
* ```get_show_bp``` returns dynamically created website Blueprint with rendering method and URL binding
* ```show_bp``` is a website Blueprint object that will be recognized for Flask under *show_bp* name, has templates and static folders configured to the ones we've created
* ```@show_bp.route('/episync')``` is the route to our website (notice the Blueprint object name decorator at the beginning). ```http://<IP>/episync``` will be an URL for our website
* ```@login_required``` decorator determines if website needs a user to be logged in to visit it. This decorator should be the last one just above the method name and can be removed so everyone can visit this site, even not authenticated users
* ```def show()``` is a website rendering method that is executed when bounded address is visited. 
* ```return render_template``` returns website template *show.html* that is in configured *templates* folder and passes values with names ```number```, ```width``` and ```height``` to the template. These names are arbitrary as are just the identifier inside the template
* ```number=len(self.plugin.get_files())``` will be a number of synced files with use of our helping method from [Step 5: Extending API](#step-5-extending-api)
* ```width=self.plugin.config.get('thumb_width')``` and ```height=self.plugin.config.get('thumb_height')``` will have plugin configuration passed values

You probably wonder why this website is created in such a tricky way, that's because we want to inject plugin class to use it inside the template and generating it inside a method that dynamically joins all elements is a good way to do that.

To summarize what we did so far:
* we've created a file structure to hold templates and Blueprint resources to generate a new webiste
* by overwriting plugin base class ```add_website``` method we've added new menu entry that will be visible on ePiframe website and pointed our new website Blueprint to be the target site for it
* we've created a generating class ```show``` in *show.py* file that is joining plugin class with website template and creates Blueprint object, binds website URL and injects values to template renderer so plugin variables can be used in template

The last step is to create the template itself. It needs some basic knowledge of Jinja, HTML, Javascript, Bootstrap 5 and jQuery but it's way more simple than it sounds. First, let's gather some elements that can help us.

Our site name will be *ePisync show*. It should have the template of ePiframe not to stand out as we want it to be a part of ePiframe. It will show the synced photos thumbnails in a dynamic table that is responsive for the display that it works on and should be adapting to mobile view. Photo should be enlarged when clicked on.

Let's check a ready template schema in Jinja for such site:
```
{% extends "layout.html" %} <!-- This will load ePiframe template, jQuery and Bootstrap -->
{% block title %}<SITE_NAME>{% endblock %}
{% block head %}
  {{ super() }} <!-- Load static resources -->
{% endblock %}
{% block content %}
   	<!-- Content -->
	...
	<script>
	//Scripts
		$(".<MENU_NAME>").addClass("link-light"); //Light up website link in menu
   </script>
{% endblock %}	
```

* ```extends "layout.html"``` is a code that will use ePiframe template for the site and will load jQuery, Bootstrap and more
* ```block title``` is a website name block
* ```block head``` is an HTML head block to load initial scripts and resources. ```super()``` will load ePiframe resources
* ```block content``` is a website content part to put HTML
* ```<script>``` is a place to put scripts in
* ```$(".<MENU_NAME>").addClass("link-light");``` will light up the website link in the ePiframe website menu. That's why we need menu entry id in the code that adds it

With that template and [Bootstrap 5 documentation](https://getbootstrap.com/docs/5.0/getting-started/introduction/) we can slowly create our view.

First let's create a container with photos - our elements. Quick look in the documentation and we find [grid](https://getbootstrap.com/docs/5.0/layout/grid/) that allows to have rows and columns that dynamically adjust to view size. 

Elements to close to each other? Look at [spacing](https://getbootstrap.com/docs/5.0/utilities/spacing/). [Borders](https://getbootstrap.com/docs/5.0/utilities/borders/), even with rounded corners? [Tooltips](https://getbootstrap.com/docs/5.0/components/tooltips/)? Predefined [colors](https://getbootstrap.com/docs/5.0/customize/color/) that suit with each other? Bootstrap have it all, well documented and with examples.

With that, some time, patience and many trials and errors we get this *show.html* code:
```
{% extends "layout.html" %} <!-- This will load ePiframe template, jQuery and Bootstrap -->
{% block title %}ePiSync show{% endblock %}  <!-- Site title -->
{% block head %}
  {{ super() }}  <!-- Load all parent scripts -->
{% endblock %}
{% block content %}
   <!-- Content -->
		<div class="container">
		  <h3 class="pt-2"> ePiSync Images: </h3>
		  <div class="row row-cols-auto p-4">
			{% for file in range(number) %}  <!-- Loop through file indices -->
			<div class="col-auto p-2">
				<div class="row px-0 col-auto mx-auto border border-4 rounded-3" >
					<a href="{{ url_for('get_sync_image') }}?file={{ file }}" target="_blank" data-bs-toggle="tooltip" title="Click to view image" class="px-0" data-bs-placement="top" style="height: {{ height }}px; width: {{ width }}px;">
						<img src="{{ url_for('get_sync_image') }}?thumb=&file={{ file }}" alt="No Photo!" width="{{ width }}" height="{{ height }}"/>
					</a>
				</div>					
			</div>
			{% endfor %}
		  </div>
		</div>
   <script>
		//Scripts
		//Show tooltips
		$('document').ready(function(){
			$('[data-bs-toggle=tooltip]').tooltip();
		});
		
		$(".episync-menu").addClass("link-light"); //Light up website link in menu
   </script>
{% endblock %}
```

* ```{% for file in range(number) %}...{% endfor %}``` is a Jinja loop that assings value from 0 to ```number``` range to a ```file``` variable in cycles. With that code inside this loop is generated ```number``` of times with different ```file``` input
* photo will be a hyperlink - ```<a href...``` that has an embedded image - ```<img...``` that is in a ```div``` with rounded corners as a border
* photo hyperlink will take us to a website - API method with different file index as URL request argument. Notice that URL is specified with method name (```<a href="{{ url_for('get_sync_image') }}?file={{ file }}"...```) inside Blueprint ```show``` class so even if binding is changed it will work as URL is not hardcoded. ```target="_blank"``` opens new web browser tab not closing the current one
* photo image source is again taken from our new API method with thumbnail request argument that dynamically puts thumbnail to our photo hyperlink
* notice that ```{{ height }}``` and ```{{ width }}``` values are passed here by template rendering method inside ```show``` class
* ```$('document').ready(function(){...``` is a script that is used by Bootstrap to trigger tooltips and was taken from the [tooltips documentation](https://getbootstrap.com/docs/5.0/components/tooltips/)
* ```$(".episync-menu").addClass("link-light");``` links up menu entry link with id ```episync-menu```

The results look like this:
<p align="center">
	<img src ="https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/assets/website.png" width="400">
</p>

### Step 7: Adding configuration

*Plugin will have configuration file that can be configured in CLI or WebUI, that validates entries and allows to customize its functionality*

We're done with the plugin implementation but we've gathered some properties of the configuration that needs to be documented and prepared. 

Configuration in ePiframe is very strict to validation, types, dependencies, etc. so the plugin should be the same. Settings are dynamically rendered in the WebUI according to the type thus some additional steps needs to be performed to get that right. There are two things to be done:
* [Configuration class](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#configuration-class)
* [Configuration file](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#configuration-file)

The plugin configuration can be checked the same way as ePiframe configuration:

```./ePiframe.py --check-config```

All plugins configurations will be checked as well.

We've already got configuration class that we've built during the implementation and that is:

```
## Config manager class.
class configmgr (configbase):
	def load_settings(self):
		self.SETTINGS = [
			configprop('is_enabled', self, prop_type=configprop.BOOLEAN_TYPE), # this setting is required! 
			#local path to sync to, notice that convert method is used to pass value to the create_dir method that creates the path if not exists
			#that's just a tricky way to use convert
			configprop('local_path', self, prop_type=configprop.FILE_TYPE, dependency='is_enabled', convert=localsourcemanager.create_dir),
			configprop('remote_path', self, dependency='is_enabled'), #this is string (by default)
			configprop('remote_host', self, dependency='is_enabled'), #all are dependent to is_enabled
			configprop('remote_user', self, dependency='is_enabled'), #and will be enabled only if is_enabled is true
			configprop('sync_timeout', self, minvalue=2, maxvalue=10, prop_type=configprop.INTEGER_TYPE, dependency='is_enabled'), #integer values with min and max thresholds
			configprop('thumb_width', self, minvalue=100, maxvalue=400, prop_type=configprop.INTEGER_TYPE, dependency='is_enabled'),
			configprop('thumb_height', self, minvalue=100, maxvalue=300, prop_type=configprop.INTEGER_TYPE, dependency='is_enabled')
		]
## End of configmgr class.
```

This list contains all customizable configuration properties with information on how to render it, validate, treat and process. Now we need to create conifguration file that can be set in CLI and ePiframe WebUI as well.

Let's create _<plugin_name>/default/config.default_ according to added settings and copy it to _<plugin_name>/config.cfg_ file (default file is used to restore default values the other one is used for the configuration).

Initially *config.cfg* and *config.default* should be the same. 

ePiframe *cfg* files have some syntax to make process easier:
* ```'; <text>'```- non processed comment that will be visible only in file and not in WebUI
* ```'# <text>'```- processed comment that will be visible in file and in WebUI. Every line above the property is concatenated into one text
* ```[<Section name>]``` - section used to divide entries into groups
* ```<entry name>=<value>``` - configuration property (unique within whole file) should not contain spaces or special characters and should be followed by = and a value (empty value is also possible)

Examples of entries:
```
my_ip=127.0.0.1
name=ePiframe
size=120
bool_value=0
empty_value=
list_value=2,3,2,1,2,3,4,3
path=logs/ePiframe.log
```

For more examples check [ePiframe config.cfg file](https://github.com/MikeGawi/ePiframe/blob/master/config.cfg)

So let's create _ePisync/default/config.default_ file for the plugin:
```
[General]

# Set 1 to enable plugin, 0 to disable.
# Default: 0 (disabled)
is_enabled=0

# Path to sync the photos to.
# Default: synced_photos
local_path=synced_photos

# Remote path to sync the photos from.
# Default: empty
remote_path=

# Remote host to sync the photos from.
# IP or hostname.
# Default: empty
remote_host=

# Remote user to sync the photos with.
# Default: empty
remote_user=

# Sync timeout.
# Value between 2 and 10.
# Default: 5
sync_timeout=5

# Thumbnail width in pixels.
# Value between 100 and 400.
# Default: 200
thumb_width=200

# Thumbnail height in pixels.
# Value between 100 and 300.
# Default: 120
thumb_height=120
```

* section name is *General*
* notice that boolean property *is_enabled* value is 0 or 1
* *local_path* is a string that represents a path
* *remote_path* has no value
* notice integer properties that have initial value

Now we should copy 1:1 the file to  _ePisync/config.cfg_, because _ePisync/default/config.default_ file is used to restore default properties values and should not change and the file _ePisync/config.cfg_ is used to be changed by the user for plugin customization.

The configuration class and the configuration file will be rendered in ePiframe *Plugins* menu like this:
<p align="center">
	<img src ="https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/assets/config.png" width="400">
</p>

## Finishing touches

As we've finished whole plugin implementation we should test it very deeply. During tests we should remember that:
* ePiframe works well with high quality HDMI displays and with e-Paper displays with limited color palette and size
* frame can be standing horizontally or vertically
* ePiframe works usually on Raspberry Pi Zero which needs a well optimized code and resources-wise code
* frame can be triggered from WebUI, Telegram Bot, CLI and ePiframe service
* keep in mind that WebUI has dark theme mode so if the plugin uses custom color outside the Bootstrap colors schema it can not work in this mode
* there may be other plugins working on this frame
* configuration after plugin update should be reverse compatible (use properties conversion, special handling and legacy convert - [Configuration class](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#configuration-class))

With these hints you can plan testing scenarios and make sure that plugin works fine in every situation.

ePiframe [command line](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#command-line) can be helpful to test every aspect of the implementation.

### Documentation and licensing

Taken from the [ePiframe_plugin Documentation](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#contribution):
>* Include screenshot of visual changes made by the plugin (if any)
>* Add a short, one sentence, clear description what it does and put this data in the plugin class as well
>* What external API's/sites/modules/projects it uses and if they have limitations or price
>* Include a detailed installation instruction, what needs to be installed and configured

There are some basic steps typical for the ePiframe infrastructure that are common for all plugins:
* Clone/download/extract the plugin to _<ePiframe_path>/plugins/<plugin_name_folder>_
* Configure plugin with _<ePiframe_path>/plugins/<plugin_name_folder>.config.cfg_ file or in ePiframe WebUI under _Plugins/<plugin_name>_
* Check configuration in WebUI or with ```./ePiframe.py --check-config``` command

Check [plugin examples](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#examples) for reference.

Plugin should be well documented and have very detailed instruction how to use it, install and configure. The configuration properties should have clear descriptions and examples. There is nothing as much annoying as a plugin you've dreamed of and that is hard to get working.

More on the plugin license can be found [here](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#license).

### Sharing the plugin

After the implementation, testing, documentation and having fun there is time to share the plugin. There's something thrilling and fun when sharing your creation with the world and ePiframe would like to help with that:
* Make your plugin repository public
* Add plugin details in [the table](https://github.com/MikeGawi/ePiframe_plugin#plugins-list) and create a pull request - it will appear on the main site

## Final code and summary

The final code created in this tutorial can be found [here](https://github.com/MikeGawi/ePiframe_plugin/tree/master/docs/ePiSync_code_tutorial). 

You could see all steps needed to create such complicated and crazy plugin. Creating plugins for ePiframe is not hard and could be a good start to have fun with Python by giving all posibilities, making hard things easier and give an opportunity. A good project idea can lead to a great scripting adventure, so have fun with it and all the best with reaching new goals! 
