# Copyright (c) 2020, DontManage and contributors
# For license information, please see license.txt

import json

import dontmanage
from dontmanage.model.document import Document


class WikiSettings(Document):
	def on_update(self):
		# change the route of wiki page for search scope
		for wiki_page in dontmanage.get_all("Wiki Page", fields=["name", "route"]):
			if self.wiki_search_scope == wiki_page.route.split("/", 1)[0]:
				break
			dontmanage.db.set_value(
				"Wiki Page",
				wiki_page["name"],
				{"route": f"{self.wiki_search_scope}/{wiki_page['route'].split('/', 1)[-1]}"},
			)


@dontmanage.whitelist()
def update_sidebar(sidebar_items):
	sidebars = json.loads(sidebar_items)

	sidebar_items = sidebars.items()
	if sidebar_items:
		idx = 0
		for sidebar, items in sidebar_items:
			for item in items:
				idx += 1
				dontmanage.db.set_value(
					"Wiki Group Item", {"wiki_page": item["name"]}, {"parent_label": sidebar, "idx": idx}
				)

	for key in dontmanage.cache().hgetall("wiki_sidebar").keys():
		dontmanage.cache().hdel("wiki_sidebar", key)
