# Cactus

Cactus is a simple but poweful static website generator using the [Django template system][1].

It is based on the idea that most dynamicness on websites these days can be done using Javascript and external services while the actual site can stay static. Still, it's nice to use a well known system like Django to generate your site so you can use the template system and other goodies. The static output allows for very fast and easy hosting, especially combined with a cdn like [Amazon Cloudfront][2]. More discussion about this at [hacker news][3]

Alternatives to Cactus are [Hyde][4] and [Jekyll][5] but I wanted to build something simpler our in-house designers at [Sofa][6] could use more easily.

[1]: http://docs.djangoproject.com/en/dev/topics/templates/
[2]: http://aws.amazon.com/cloudfront/
[3]: http://news.ycombinator.com/item?id=2233620
[4]: http://ringce.com/hyde
[5]: https://github.com/mojombo/jekyll
[6]: http://www.madebysofa.com

## Basic Installation

Get the Cactus source by downloading/cloning this repository.

The very basic installation of Cactus only needs Django and Baker. More python goodies are needed based on the features you may use. You can install them easily like this:

    easy_install baker django simplejson boto keyring pyfsevents

If you get an error building pyfsevents, you need to install [Apple's Developer Tools][http://developer.apple.com/technologies/tools]. You can do without, but the serve command won't work.

## For the impatient: Quickstart

The fastest way to start developing right away. If you need a little more context please skip this and keep on reading.

	cd <cactus location>
	python cactus.py init ~/my-cactus-test-site
	python cactus.py serve ~/my-cactus-test-site

This should open your browser with a fresh generated site. You can now start editing it.


## Basic Usage

### Creating a new project

You can create a new project by generating a new project stucture like this. Make sure the destination folder does not exist yet.

	python cactus.py init [path]

If you did not see any errors, the path you pointed to should now look like this.
	
	- build					Generated site (upload this to your host)
	- pages					Your actual site pages
		- index.html
	- templates				Holds your django templates
		- base.html
	- static				Directory with static assets
		- images
		- css
		- js
	- extras
		- contexts.py		Allows for custom page contexts
		- templatetags.py	Hold custom django template tags

### Making your site

After generating your site you can start building by adding pages to contents, which can rely on templates. So for example if you want a page `/articles/2010/my-article.html` you would create the file with directories in your pages folder. Then you can edit the file and use django's template features.

### Building your site

When you build your site it will generate a static version in the build folder that you can upload to any host. Basically it will render each page from your pages folder, copy it over to the build folder and add all the static assets to it so it becomes a self contained website. You can build your site like this:

	python cactus.py build [path]

#### Linking and contexts

Cactus makes it easy to relatively link to pages and static assets inside your project by using the standard context variables MEDIA\_PATH and ROOT\_PATH. For example if you are at page `/blog/2011/Jan/my-article.html` and would like to link to `/contact.html` you would write the following: 

	<a href={{ ROOT_PATH }}/contact.html>Contact</a>

Optionally you can add variables to the context per page, by modifying the context function in contexts.py

#### Custom Django template tags

TODO

### Serving, testing and developing your site

Cactus can run a small webserver to preview your site and update it when you make any changes. This is really handy when developing. You can run it like this:

	python cactus.py serve [path]

## Deploying

Sofa uses Cactus in combination with [Amazon S3 website features][7] and CloudFront to build maintainable and very fast websites. But beacuse Cactus generates static sites, you could host them pretty much anywhere, from Akamai to DropBox.

[7]: http://aws.amazon.com/about-aws/whats-new/2011/02/17/Amazon-S3-Website-Features/

Before deploying (we like [Fabric][8]) you could compress your Javascript and CSS using for example [Google Closure][9] and [CSSMin][10] for even more performant sites. Also make sure you host your content gzipped to clients, which requires [a bit extra work][11] when using Amazon S3.

[8]: http://www.fabfile.org
[9]: http://code.google.com/closure/compiler/docs/gettingstarted_ui.html
[10]: http://code.google.com/p/cssmin/
[11]: http://devblog.famundo.com/articles/2007/03/02/serving-compressed-content-from-amazons-s3

