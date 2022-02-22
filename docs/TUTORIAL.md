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

Of course you already have a working ePiframe and all dependencies installed so the most important thing now to start with is... the name for your project. It is really nice to have it before starting anything as it will help with the flow and all the thoughs will have a name under them. At some point ePiframe had a working name *GoopheePi* (Google Photos ePaper Pi) but later, after adding new functions I thought that with e-Paper display it looks *epic* so it was changed to *ePiframe*. The only limitation for the name is to not use dots and dashes as that will disturb ePiframe plugin recognition mechanism.

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

If there are more prerequisites needed for your plugin, i.e. external API's, sites, modules, projects - mention in the documentation how to install/configure them and if they have limitations or price.

Let's install rsync:
```
	sudo apt update
	sudo apt install rsync
```

## Implementation

Plugin will be installed in <*ePiframe root path*>*/plugins/*<*plugin_name*> path and you can just put it there to make tests easier but remember to [stop the service](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#service-control) to not interfere working frame.

ePiframe [can be installed](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#manual) also on non-Pi architectures and to avoid Pi system check just run ePiframe with ```--test``` flag from CLI, i.e. ```./ePiframe.py --test```. Running WebUI and other services is possible with [other commands](https://github.com/MikeGawi/ePiframe/blob/master/INSTALL.md#command-line).

Plugins base class is embedded in the ePiframe code and the plugin class inherits exposed methods that can be overriden. The plugin manager inside ePiframe will run these methods in different phases of ePiframe runtime and will do that only if the method is used. 

The scope starts in the root folder of ePiframe so if some module needs to be used it should import from ```modules.<module_name>```, e.g. ```from modules.databasemanager import databasemanager```. If the plugin needs additional files/modules these can be imported with the same module hierarchy, i.e. ```plugins.<plugin_name>.<module_name>```.

Most of the basic ePiframe modules that can be useful for particular plugins methods are passed during the run but all needed ePiframe ingredients can be imported if needed.

If exception occurs during the run of overridden method (that stops the next steps of the plugin) an exception should be raised to be catched by the main script to be properly reported in logs.

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

Let's copy this key to clipboard, login to destination server (with the *USER* account that will be used for synchronization) and place this SSH key into *~/.ssh/authorized_keys* file. If the file doesn't exists, create it manually:
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

to put the configuration entries to. This structure allows validation, type check, value check and lot more (WebUI rendering for example) of plugin settings. Let's put or new variables:
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

```local_path``` (DEST = destination of photos) is a file type property that existance will be checked during configuration loading. Here's a small trick: ```convert``` method used for converting value property to another value (it just passes the value to the method and returns new value) is used to create the directory if it's missing. It doesn't change the value as method is not returning new one. That's a trick to do something with the value before validation. The method ```create_dir``` is a part of [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) module.

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

Problematic, right? Especially when ePiframe works on Raspberry Pi Zero, so ePiframe just gathers the data (i.e. ID, creationtime, etc.) from this source, gets all needed parameters and works on the list. If it randomly picks the photo from this source *only then* downloads it and process. 

It works for Google Photos where there is a huge number of photos to download and we get only the one we want. For local storage source it's different because we already have photos on the storage and we just want to pick/copy the one we want to process and display on frame.

This step should be number 3. as it's executed after [Step 3: Photo list](#step-3-photo-list) but let's keep it here to stay in the source context.

The plugin base class method to overwrite is [```add_photo_source_get_file```](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#adding-new-photo-source-file-retrieving-method) and it should return photo final filename, best if it would contain an extension. 

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

So we have now a final photo path with full destination filename. The last thing we need to do is copy the source file synced from remote location to ```filename_ret``` with *shutil*. The final code looks like this:
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
* ```localsourcemanager.create_dir``` is a method of [localsourcemanager](https://github.com/MikeGawi/ePiframe/blob/master/modules/localsourcemanager.py) module to create a directory if it doesn't exists - thumbnail folder in that case
* ```self.__THUMB_NAME``` is a prefix for thumbnail file and it is also used as a thumbnail folder name
* ```for index, row in rows.iterrows():``` allows iteriting through Pandas rows and returns ```index, row``` in every loop cycle
* ```thumb_file``` is generated from photo ID (source filename in this case) its path, filename and thumbnail idetifier prefix. It will be created in thumbnail folder
* the thumbnail will be generated ONLY if it doesn't exists for the photo
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
* preprocessing done by ```preprocess_photo```(https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#photo-preprocessing) method that processes the photo before the basic conversion when it is currently in the original version (high quality photo)
* postprocessing done by ```postprocess_photo```(https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#photo-postprocessing) method that processes the photo before sending to display (and it's already converted to the display)

Watermark adding procedure can be done on both but postprocessing is more demanding as photo can already be rotated to vertical frame and have reduced colors for the display, so we will use this for tutorial purposes.

Both methods are not returning any output as they should overwrite passed photo filename.

For adding watermark, so pasting other image atop of the photo, we will use [Pillow](https://pillow.readthedocs.io/en/stable/) that is a dependency of ePiframe. Pillow - The Python Imaging Library adds image processing capabilities to Python interpreter.

The code is pretty straightforward as Pillow is easy to use but:




### Step 5: Extending API

*Plugin will extend the ePiframe API with methods to show thumbnail and original photo*

### Step 6: Adding website

*Plugin will add the website to ePiframe WebUI to present the gathered photos (with use of API function stated above)*

### Step 7: Adding configuration

*Plugin will have configuration file that can be configured in CLI or WebUI, that validates entries and allows to customize its functionality*

## Finishing touches

### Documentation and licensing

### Sharing the plugin

## Final code and summary