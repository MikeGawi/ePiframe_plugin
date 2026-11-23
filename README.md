# ePiframe_plugin

This code is a template to create new plugins for the [ePiframe](https://github.com/MikeGawi/ePiframe) photo frame.

Check [the list](#plugins-list) of available plugins!

**This version is for ePiframe 2.0 (Plugin API v2).** Plugins written for ePiframe 1.x need to be updated - see
[Migrating a 1.x plugin](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md#migrating-a-1x-plugin).

# What is it?

The plugin base class (part of ePiframe) exposes methods to add new functions to the photo frame, or even to the
Raspberry Pi itself, as ePiframe runs its own auto recovering service and a Flask based website and can trigger
system functions. A plugin gets typed access to ePiframe (configuration, logger, photo index entries, ImageMagick)
and its own configuration with validation, conversion, dependencies, value/type checks and WebUI rendering.

With these methods a plugin can extend ePiframe photo functions:
* Adds new photo sources and photo retrieving methods, e.g. a new image hosting site, a folder synced from a cloud
* Preprocesses the high quality photo before the conversion for the display, e.g. oil paint effect, photo filters
* Postprocesses the converted (to the display size and colors) photo before it is shown, e.g. text, frames, stamps

But also not strictly photo related functions (these methods will be redesigned with the new WebUI of ePiframe 2.0):
* Extends API functions, e.g. a REST API returning hardware statistics, an API for a smart home server
* Adds new WebUI pages, e.g. a server control page, with an optional link in the WebUI menu and ePiframe styling
* Adds new action buttons in the WebUI Tools section, e.g. controlling devices, triggering system actions
* Adds new threads to the ePiframe service, e.g. frequently gathering data, scheduled triggers

# How to start?

Check the detailed [documentation](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md) with
examples and the [tutorial](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md) and have fun!

# Contribution

Please follow these rules if you want to create your own plugin:
* Include screenshot of visual changes made by the plugin (if any)
* Add a short, one sentence, clear description what it does and put this data in the plugin class as well
* Add what external APIs/sites/modules/projects it uses and if they have limitations or price
* Include a detailed installation instruction, what needs to be installed and configured
* Add plugin details in the table below and create a pull request - it will appear on this site

# Plugins list

| Plugin name and URL                                                            | Author                                  | Description                                                  |
|--------------------------------------------------------------------------------|-----------------------------------------|--------------------------------------------------------------|
| [cryptocurrency_ePiframe](https://github.com/MikeGawi/cryptocurrency_ePiframe) | [MikeGawi](https://github.com/MikeGawi) | Displays cryptocurrency price and percentage change on frame |
| [cartoon_ePiframe](https://github.com/MikeGawi/cartoon_ePiframe)               | [MikeGawi](https://github.com/MikeGawi) | Photo cartoon-like style preprocessing                       |
| [decor_ePiframe](https://github.com/MikeGawi/decor_ePiframe)                   | [MikeGawi](https://github.com/MikeGawi) | Display decorative frames and quotes on frame                |
||||
