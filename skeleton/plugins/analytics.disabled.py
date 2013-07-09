# Universal Analytics plug-in

# How-To:
# 1. Register for Google Universal Analytics and get a
#       property ID.
# 2. Replace GA_ID below with your Google Analytics property ID.
# 3. Ensure that the {{ tracking }} block appears on your pages
#       just before the end of the <head> section (it should
#       hopefully be in base.html)

GA_ID = 'UA-XXXXXXXX-X'

# Tracking code template: DO NOT CHANGE unless you
# know what you are doing
GA_CODE = """
        <script>
          (function(i,s,o,g,r,a,m){{i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){{
          (i[r].q=i[r].q||[]).push(arguments)}},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
          }})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

          ga('create', '{0}');
          ga('send', 'pageview');

        </script>
    """

SNIPPET = ''

def preBuild(site):

    global SNIPPET

    SNIPPET = GA_CODE.format(GA_ID)

def preBuildPage(site, page, context, data):

    context['universalAnalytics'] = SNIPPET

    return context, data
