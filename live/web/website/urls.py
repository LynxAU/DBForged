"""
This reroutes from an URL to a python view-function/class.

The main web/urls.py includes these routes for all urls (the root of the url)
so it can reroute to all website pages.

"""

from django.urls import path

from evennia.web.website.urls import urlpatterns as evennia_website_urlpatterns
from web.website.views import technique_ui

# add patterns here
urlpatterns = [
    path("db/techniques/", technique_ui, name="db_technique_ui"),
]

# read by Django
urlpatterns = urlpatterns + evennia_website_urlpatterns
