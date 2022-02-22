from modules.base.pluginbase import pluginbase
from modules.base.configbase import configbase
from misc.configprop import configprop
from misc.constants import constants
from modules.convertmanager import convertmanager
from modules.localsourcemanager import localsourcemanager
from PIL import Image, ImageColor
from flask import request, send_file
from flask_login import login_required
import os, shutil, subprocess

class plugin(pluginbase):
	
	name = 'ePiSync'
	author = 'ePiframe-plugin tutorial'
	description = 'Sync photos with rsync from remote location, generate thumbnails, then add watermark, API method and a website to view new photos'
	site = 'https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md'
	info = 'All steps gathered here to create a multi-functional ePiframe plugin'
	
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
	
	__THUMB_NAME = "thumb_"
	
	def __init__ (self, path, pidmgr, logging, globalconfig):
		super().__init__(path, pidmgr, logging, globalconfig)		
	
	## ---------------------------------------------------------------------------------------------------------------------------
	
	#method that adds new photo source
	def add_photo_source (self, idlabel, creationlabel, sourcelabel, photomgr):
		cmd = 'rsync --timeout={} --ignore-existing {}@{}:{}* {} 2>&1 > /dev/null' #command string
		source = self.config.get('remote_path') if self.config.get('remote_path').endswith('/') else self.config.get('remote_path') + '/' #adding / at the end if not exists
		os.system(cmd.format(self.config.get('sync_timeout'), self.config.get('remote_user'), self.config.get('remote_host'), source, self.config.get('local_path'))) #starting command with args
				
		loc = localsourcemanager (self.config.get('local_path'), False, constants.EXTENSIONS) #getting synced files with localsourcemanager
		self.SOURCE = "'{}' plugin source".format(self.name) #it is required to set the source name
		return loc.get_local_photos(idlabel, creationlabel, sourcelabel, self.SOURCE) #returning dataframe of photos with needed labels
	
	#method that retrieves the file from new photo source
	def add_photo_source_get_file (self, photo, path, filename, idlabel, creationlabel, sourcelabel, photomgr):
		filename_ret = filename	
		#getting image MIME type with ImageMagick
		err, imagetype = convertmanager().get_image_format(self.globalconfig.get('convert_bin_path'), photo[idlabel], constants.FIRST_FRAME_GIF) #if this is a GIF then just check the first frame
		if not err and imagetype:
			filename_ret = filename + "." + constants.TYPE_TO_EXTENSION[constants.MIME_START + imagetype.lower()] #converting MIME type to extension
		filename_ret = os.path.join(path, filename_ret) #combining filename
		shutil.copy(photo[idlabel], filename_ret) #copying to target path
		return filename_ret
	
	## ---------------------------------------------------------------------------------------------------------------------------
	
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
				
		return photo_list #returning initial photo_list as nothing has changed
	
	## ---------------------------------------------------------------------------------------------------------------------------
	
	#method that postprocesses the photo
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
	
	## ---------------------------------------------------------------------------------------------------------------------------
	
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
		
	## ---------------------------------------------------------------------------------------------------------------------------
	
	#method that adds new website and menu entry
	def add_website (self, webmgr, usersmgr, backend):
		from plugins.ePiSync_tutorial_code.show import show #import site
		webmgr.add_menu_entries([ webmgr.menu_entry ('ePiSync', '/episync', 'episync-menu', 'bi bi-image') ]) #create menu entry with name, URL, menu id and icon
		site = show(self) #create site class and pass plugin
		return [ site.get_show_bp() ] #return list of websites to add