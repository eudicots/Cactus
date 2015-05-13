Internationalization
====================

Using internationalization with Cactus
--------------------------------------

To enable internationalization for your project:

  1. Add a `locale` key to (one of your) configuration file(s)
  2. Mark strings for translation in your site (using `{% trans %}`)
  3. Run `cactus messages:make`
  4. Edit the .po file that was created with translations.


Multiple languages with Cactus
------------------------------

To make the best of translations, you'll need multiple configuration files: one per language you'd like to support.

This lets you transparently deploy multiple versions of your website to multiple buckets (one per language).
