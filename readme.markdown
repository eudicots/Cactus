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

Get the Cactus source by cloning this repository.

The very basic installation of hyde only needs Django and Baker. More python goodies are needed based on the features you may use. For example Markdown for the markdown template tags.

    pip install -r requirements.txt

Make the cactus.py script executable (if it not is already) and place it in a location where you can run it easily.

    chmod 755 cactus.py

## Basic Usage

### Creating a new project: cactus.py init <path>

Generates a new project at given path with a basic project layout. After adding some custom content it could look something like this.
	
	- build					Generated site
	- contents				Your actual site pages
		- index.html
		- blog
			my-post.html
	- templates				Holds your django templates
		- base.html
		- footer.html
	- static				Directory with static assets
		- images
		- css
		- js
	- contexts.py			Allows for custom page contexts
	- templatetags.py		Hold custom django template tags

### Making your site

After generating your site you can start building by adding pages to contents, which can rely on templates. 

### Building your site: cactus.py build <path>

Building basically renders each page in the contents folder using the django templates to the same location in the build folder, and copies all static assets.

Cactus makes it easy to relatively link to pages and static assets inside your project by using the standard context variables MEDIA\_PATH and ROOT\_PATH. For example if you are at page /blog/2011/Jan/my-article.html and would like to link to /contact.html you would write the following: `<a href={{ ROOT_PATH }}/contact.html>Contact</a>`.

### Serving your site: cactus.py serve <path>

TODO. Serve your site using a small internal webserver rebuilding content each time you change a page.

## Deploying

Sofa uses Cactus in combination with [Amazon S3 website features][1] and CloudFront to build maintainable and very fast websites. But beacuse Cactus generates static sites, you could host them pretty much anywhere, from Akamai to DropBox.

[1]: http://aws.amazon.com/about-aws/whats-new/2011/02/17/Amazon-S3-Website-Features/

Before deploying (we like [Fabric][1]) you could compress your Javascript and CSS using for example [Google Closure][2] and [CSSMin][3] for even more performant sites. Also make sure you host your content gzipped to clients, which requires [a bit extra work][4] when using Amazon S3.

[1]: http://www.fabfile.org
[2]: http://code.google.com/closure/compiler/docs/gettingstarted_ui.html
[3]: http://code.google.com/p/cssmin/
[4]: http://devblog.famundo.com/articles/2007/03/02/serving-compressed-content-from-amazons-s3

