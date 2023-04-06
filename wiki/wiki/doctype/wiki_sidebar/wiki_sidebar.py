# Copyright (c) 2021, DontManage and contributors
# For license information, please see license.txt


import dontmanage
from dontmanage.model.document import Document


class WikiSidebar(Document):
	def validate(self):
		self.clear_cache()

	def on_update(self):
		self.clear_cache()

	def clear_cache(self):
		topmost = "wiki"
		dontmanage.cache().hdel("wiki_sidebar", topmost)
