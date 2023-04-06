# Copyright (c) 2020, DontManage and Contributors
# MIT License. See license.txt


import dontmanage


def get_context(context):
	topmost_wiki_name = dontmanage.get_single("Wiki Settings").wiki_sidebar[0].wiki_page
	topmost_wiki_route = dontmanage.get_value("Wiki Page", topmost_wiki_name, "route")

	# find and route to the first wiki page
	if topmost_wiki_route:
		dontmanage.response.location = topmost_wiki_route
		dontmanage.response.type = "redirect"
		raise dontmanage.Redirect
