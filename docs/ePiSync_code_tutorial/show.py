"""The ePiSync WebUI page (Step 6 of the tutorial, ePiframe 1.x WebUI hook form)."""

from flask import Blueprint, render_template
from flask_login import login_required

from plugins.ePiSync_code_tutorial._plugin import Plugin


class Show:
    """Builds the page blueprint with access to the plugin (its settings, files)."""

    def __init__(self, plugin: Plugin):
        self.plugin = plugin

    def get_show_bp(self) -> Blueprint:
        show_bp = Blueprint(
            "show_bp", __name__, template_folder="templates", static_folder="static"
        )

        @show_bp.route("/episync")  # the URL of the page
        @login_required  # only logged-in users; keep it the last decorator
        def show() -> str:
            return render_template(
                "show.html",
                number=len(self.plugin.synced_files()),
                width=self.plugin.config.get("thumb_width"),
                height=self.plugin.config.get("thumb_height"),
            )

        return show_bp
