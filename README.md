# ePiframe_plugin

This code is a template to create new plugins for [ePiframe](https://github.com/MikeGawi/ePiframe) photo frame.

Check [the list](#plugins-list) of available plugins!

# What is it?

The base plugin class exposes methods to add new functions to photo frame or even to the Raspberry Pi itself as ePiframe runs its own auto recovering service, Flask based website with jQuery and Bootstrap 5 and can trigger system functions. The plugin provides basic frame helper modules, access to backend and customizable configuration class that has validation, conversion, dependencies, value/type verification and more.

With these methods plugin can extend ALL ePiframe photo functions:
* Adds new photos source and photos retrieving methods, e.g. new image hosting site source, adding methods to sync with cloud, etc.
* Manipulates collected photos list before selecting the photo, e.g. sorting, filtering, turning upside-down, adding AI recognition etc.
* Preprocesses a high quality photo before conversion for the display, e.g. oil paint effect, photo filters, frame, stamps, etc.
* Postprocesses converted (for the display size and type) photo before sending to frame, e.g. add text, re-convert, etc.

But also methods to extend not strictly photo related functions:
* Extends API functions, e.g. adding REST API, returns data by query/website such as getting hardware statistics, exposes API for smart home server, etc.
* Adds WebUI new website, e.g. adds a server controlling site, with optional link in the WebUI menu and ePiframe templating.
* Adds new action buttons in WebUI Tools section of ePiframe, e.g. controls device, triggers system action, controls smart devices, etc.
* Adds new thread to ePiframe service, e.g. frequently gathering data, scheduled triggers, etc.

# How to start?

Check the detailed [documentation](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/SETUP.md) with examples and [tutorial](https://github.com/MikeGawi/ePiframe_plugin/blob/master/docs/TUTORIAL.md) and have fun!

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
