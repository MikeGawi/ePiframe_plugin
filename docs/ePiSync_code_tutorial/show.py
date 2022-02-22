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