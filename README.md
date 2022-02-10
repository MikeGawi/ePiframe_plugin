# ePiframe.plugin

This code is a template to create new plugins for [ePiframe](https://github.com/MikeGawi/ePiframe) photo frame.

Check [the list](#plugins-list) of available plugins!

# What is it?

The base plugin class exposes methods to add new functions to photo frame or even to the Raspberry Pi itself as ePiframe runs it's own auto recovering service, Flask based website with jQuery and Bootstrap 5 and can trigger system functions. The plugin provides basic frame helper modules, access to backend and customizable configuration class that has validation, conversion, dependencies, value/type verification and more.

With these methods plugin can extend ALL ePiframe photo functions:
* Add new photos source and photos retriving methods, e.g. new image hosting site source, adding methods to sync with cloud, etc.
* Manipulate collected photos list before selecting the photo, e.g. sorting, filtering, turning upside-down, adding AI recognition etc.
* Preprocess a high quality photo before conversion for the display, e.g. oil paint effect, photo filters, frame, stamps, etc.
* Postprocess converted (for the display size and type) photo before sending to frame, e.g. add text, re-convert, etc.

But also methods to extend not-strictly photo related functions:
* Extend API functions, e.g. adding REST API,return data by query/website like get hardware statistics, expose API for smart home server, etc.
* Add WebUI new website, e.g. add a server controlling site, with optional link in the WebUI menu and ePiframe templating.
* Add new action buttons in WebUI Tools section of ePiframe, e.g. control device, trigger system action, control smart devices, etc.
* Add new thread to ePiframe service, e.g. frequently gathering data, scheduled triggers, etc.

# How to start?

Check the detailed [documentation](https://github.com/MikeGawi/ePiframe-plugin/blob/master/docs/SETUP.md) with examples and tutorial and have fun!

# Contribution

Please follow these rules if you want to create your own plugin:
* Include screenshot of visual changes made by the plugin (if any)
* Add a short, one sentence, clear description what it does and put this data in the plugin class as well
* What external API's/sites/modules/projects it uses and if they have limitations or price
* Include a detailed installation instruction, what needs to be installed and configured
* Add plugin details in the table below and create a pull request - it will appear on this site

# Plugins list

|Plugin name and URL|Author|Desription|
|-------------------|------|----------|
| | | |
