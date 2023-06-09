# Copyright (c) 2020, DontManage and contributors
# For license information, please see license.txt


import re
from urllib.parse import urlencode

import dontmanage
from dontmanage import _
from dontmanage.core.doctype.file.file import get_random_filename
from dontmanage.utils.data import sbool
from dontmanage.website.doctype.website_settings.website_settings import modify_header_footer_items
from dontmanage.website.utils import cleanup_page_name
from dontmanage.website.website_generator import WebsiteGenerator


class WikiPage(WebsiteGenerator):
	def before_save(self):

		details = dontmanage.db.get_values(
			"Wiki Page", filters={"name": self.name}, fieldname=["route", "title"]
		)

		if not details:
			return

		old_route, old_title = (details[0][0], details[0][1])

		if old_route != self.route or old_title != self.title:
			self.clear_sidebar_cache()

	def after_insert(self):
		dontmanage.cache().hdel("website_page", self.name)

		# set via the clone method
		if hasattr(dontmanage.local, "in_clone") and dontmanage.local.in_clone:
			return

		revision = dontmanage.new_doc("Wiki Page Revision")
		revision.append("wiki_pages", {"wiki_page": self.name})
		revision.content = self.content
		revision.message = "Create Wiki Page"
		revision.raised_by = dontmanage.session.user
		revision.insert()

	def clear_sidebar_cache(self):
		for key in dontmanage.cache().hgetall("wiki_sidebar").keys():
			dontmanage.cache().hdel("wiki_sidebar", key)

	def on_trash(self):

		dontmanage.db.sql("DELETE FROM `tabWiki Page Revision Item` WHERE wiki_page = %s", self.name)

		dontmanage.db.sql(
			"""DELETE FROM `tabWiki Page Revision` WHERE name in
			(
				SELECT name FROM `tabWiki Page Revision`
				EXCEPT
				SELECT DISTINCT parent from `tabWiki Page Revision Item`
			)"""
		)

		for name in dontmanage.get_all("Wiki Page Patch", {"wiki_page": self.name, "new": 0}, pluck="name"):
			patch = dontmanage.get_doc("Wiki Page Patch", name)
			try:
				patch.cancel()
			except dontmanage.exceptions.DocstatusTransitionError:
				pass
			patch.delete()

		for name in dontmanage.get_all("Wiki Page Patch", {"wiki_page": self.name, "new": 1}, pluck="name"):
			dontmanage.db.set_value("Wiki Page Patch", name, "wiki_page", "")

		wiki_sidebar_name = dontmanage.get_value("Wiki Group Item", {"wiki_page": self.name})
		dontmanage.delete_doc("Wiki Group Item", wiki_sidebar_name)

		self.clear_sidebar_cache()

	def set_route(self):
		if not self.route:
			self.route = "wiki/" + cleanup_page_name(self.title)

	def update_page(self, title, content, edit_message, raised_by=None):
		"""
		Update Wiki Page and create a Wiki Page Revision
		"""
		self.title = title

		# only update the tail end of route
		self.route = self.route.replace(self.route.split("/")[-1], cleanup_page_name(self.title))

		if content != self.content:
			self.content = content
			revision = dontmanage.new_doc("Wiki Page Revision")
			revision.append("wiki_pages", {"wiki_page": self.name})
			revision.content = content
			revision.message = edit_message
			revision.raised_by = raised_by
			revision.insert()

		self.save()

	def verify_permission(self, permtype):
		if permtype == "read" and self.allow_guest:
			return True
		permitted = dontmanage.has_permission(self.doctype, permtype, self)
		if not permitted:
			action = permtype
			if action == "write":
				action = "edit"
			dontmanage.local.response["type"] = "redirect"
			dontmanage.local.response["location"] = "/login?" + urlencode({"redirect-to": dontmanage.request.url})
			raise dontmanage.Redirect

	def redirect_to_login(self, action):
		dontmanage.local.response["type"] = "redirect"
		dontmanage.local.response["location"] = "/login?" + urlencode({"redirect-to": dontmanage.request.url})
		raise dontmanage.Redirect

	def set_breadcrumbs(self, context):
		context.add_breadcrumbs = True
		if dontmanage.form_dict:
			context.parents = [{"route": "/" + self.route, "label": self.title}]
		else:
			parents = []
			splits = self.route.split("/")
			if splits:
				for index, _route in enumerate(splits[:-1], start=1):
					full_route = "/".join(splits[:index])
					wiki_page = dontmanage.get_all(
						"Wiki Page", filters=[["route", "=", full_route]], fields=["title"]
					)
					if wiki_page:
						parents.append({"route": "/" + full_route, "label": wiki_page[0].title})

				context.parents = parents

	def get_context(self, context):
		self.verify_permission("read")
		self.set_breadcrumbs(context)
		wiki_settings = dontmanage.get_single("Wiki Settings")
		context.navbar_search = wiki_settings.add_search_bar
		context.add_dark_mode = wiki_settings.add_dark_mode
		context.script = wiki_settings.javascript
		context.wiki_search_scope = wiki_settings.wiki_search_scope
		context.metatags = {
			"title": self.title,
			"description": self.meta_description,
			"keywords": self.meta_keywords,
			"image": self.meta_image,
			"og:image:width": "1200",
			"og:image:height": "630",
		}
		context.edit_wiki_page = dontmanage.form_dict.get("editWiki")
		context.new_wiki_page = dontmanage.form_dict.get("newWiki")
		context.last_revision = self.get_last_revision()
		context.number_of_revisions = dontmanage.db.count(
			"Wiki Page Revision Item", {"wiki_page": self.name}
		)
		html = dontmanage.utils.md_to_html(self.content)
		context.content = html
		context.has_wiki_page_edit_permission = dontmanage.has_permission(
			doctype="Wiki Page", ptype="write", throw=False
		)
		context.show_sidebar = True
		context.hide_login = True
		context.name = self.name
		if (dontmanage.form_dict.editWiki or dontmanage.form_dict.newWiki) and dontmanage.form_dict.wikiPagePatch:
			(
				context.patch_new_code,
				context.patch_new_title,
				context.new_sidebar_group,
			) = dontmanage.db.get_value(
				"Wiki Page Patch",
				dontmanage.form_dict.wikiPagePatch,
				["new_code", "new_title", "new_sidebar_group"],
			)
		context = context.update(
			{
				"navbar_items": modify_header_footer_items(wiki_settings.navbar),
				"post_login": [
					{"label": _("My Account"), "url": "/me"},
					{"label": _("Logout"), "url": "/?cmd=web_logout"},
					{
						"label": _("Contributions ") + get_open_contributions(),
						"url": "/contributions",
					},
					{
						"label": _("My Drafts ") + get_open_drafts(),
						"url": "/drafts",
					},
				],
			}
		)

	def get_items(self, sidebar_items):
		topmost = "wiki"

		sidebar_html = dontmanage.cache().hget("wiki_sidebar", topmost)
		if not sidebar_html or dontmanage.conf.disable_website_cache or dontmanage.conf.developer_mode:
			context = dontmanage._dict({})
			context.sidebar_items = sidebar_items
			wiki_settings = dontmanage.get_single("Wiki Settings")
			context.wiki_search_scope = wiki_settings.wiki_search_scope
			context.light_mode_logo = wiki_settings.logo
			context.dark_mode_logo = wiki_settings.dark_mode_logo
			sidebar_html = dontmanage.render_template(
				"wiki/wiki/doctype/wiki_page/templates/web_sidebar.html", context
			)
			dontmanage.cache().hset("wiki_sidebar", topmost, sidebar_html)

		return sidebar_html

	def get_sidebar_items(self):
		wiki_sidebar = dontmanage.get_single("Wiki Settings").wiki_sidebar
		sidebar = {}

		for sidebar_item in wiki_sidebar:
			wiki_page = dontmanage.get_doc("Wiki Page", sidebar_item.wiki_page)
			if sidebar_item.parent_label not in sidebar:
				sidebar[sidebar_item.parent_label] = [
					{
						"name": wiki_page.name,
						"type": "Wiki Page",
						"title": wiki_page.title,
						"route": wiki_page.route,
						"group_name": sidebar_item.parent_label,
					}
				]
			else:
				sidebar[sidebar_item.parent_label] += [
					{
						"name": wiki_page.name,
						"type": "Wiki Page",
						"title": wiki_page.title,
						"route": wiki_page.route,
						"group_name": sidebar_item.parent_label,
					}
				]

		return self.get_items(sidebar)

	def get_last_revision(self):
		last_revision = dontmanage.db.get_value(
			"Wiki Page Revision Item", filters={"wiki_page": self.name}, fieldname="parent"
		)
		return dontmanage.get_doc("Wiki Page Revision", last_revision)

	def clone(self, original, new):

		# used in after_insert of Wiki Page to resist create of Wiki Page Revision
		dontmanage.local.in_clone = True

		cloned_wiki_page = dontmanage.copy_doc(self, ignore_no_copy=True)
		cloned_wiki_page.route = cloned_wiki_page.route.replace(original, new)

		cloned_wiki_page.flags.ignore_mandatory = True
		cloned_wiki_page.save()

		items = dontmanage.get_all(
			"Wiki Page Revision",
			filters={
				"wiki_page": self.name,
			},
			fields=["name"],
			pluck="name",
			order_by="`tabWiki Page Revision`.creation",
		)

		for item in items:
			revision = dontmanage.get_doc("Wiki Page Revision", item)
			revision.append("wiki_pages", {"wiki_page": cloned_wiki_page.name})
			revision.save()

		self.update_time_and_user("Wiki Page", cloned_wiki_page.name, self)

		return cloned_wiki_page

	def update_time_and_user(self, dt, dn, new_doc):
		for field in ("modified", "modified_by", "creation", "owner"):
			dontmanage.db.set_value(dt, dn, field, new_doc.get(field))


def get_open_contributions():
	count = len(
		dontmanage.get_list(
			"Wiki Page Patch",
			filters=[["status", "=", "Under Review"], ["raised_by", "=", dontmanage.session.user]],
		)
	)
	return f'<span class="count">{count}</span>'


def get_open_drafts():
	count = len(
		dontmanage.get_list(
			"Wiki Page Patch",
			filters=[["status", "=", "Draft"], ["owner", "=", dontmanage.session.user]],
		)
	)
	return f'<span class="count">{count}</span>'


@dontmanage.whitelist()
def preview(content, name, new, type, diff_css=False):
	html = dontmanage.utils.md_to_html(content)
	if new:
		return {"html": html}
	from ghdiff import diff

	old_content = dontmanage.db.get_value("Wiki Page", name, "content")
	diff = diff(old_content, content, css=diff_css)
	return {
		"html": html,
		"diff": diff,
		"orignal_preview": dontmanage.utils.md_to_html(old_content),
	}


@dontmanage.whitelist()
def extract_images_from_html(content):
	dontmanage.flags.has_dataurl = False
	file_ids = {"name": []}

	def _save_file(match):
		data = match.group(1)
		data = data.split("data:")[1]
		headers, content = data.split(",")

		if "filename=" in headers:
			filename = headers.split("filename=")[-1]

			# decode filename
			if not isinstance(filename, str):
				filename = str(filename, "utf-8")
		else:
			mtype = headers.split(";")[0]
			filename = get_random_filename(content_type=mtype)

		_file = dontmanage.get_doc(
			{"doctype": "File", "file_name": filename, "content": content, "decode": True}
		)
		_file.save(ignore_permissions=True)
		file_url = _file.file_url
		file_ids["name"] += [_file.name]
		if not dontmanage.flags.has_dataurl:
			dontmanage.flags.has_dataurl = True

		return f'<img src="{file_url}"'

	if content and isinstance(content, str):
		content = re.sub(r'<img[^>]*src\s*=\s*["\'](?=data:)(.*?)["\']', _save_file, content)
	return content, file_ids["name"]


@dontmanage.whitelist()
def update(
	name,
	content,
	title,
	attachments="{}",
	message="",
	wiki_page_patch=None,
	new=False,
	new_sidebar="",
	new_sidebar_items="",
	draft=False,
	new_sidebar_group="",
):

	context = {"route": name}
	context = dontmanage._dict(context)
	content, file_ids = extract_images_from_html(content)

	new = sbool(new)
	draft = sbool(draft)

	status = "Draft" if draft else "Under Review"
	if wiki_page_patch:
		patch = dontmanage.get_doc("Wiki Page Patch", wiki_page_patch)
		patch.new_title = title
		patch.new_code = content
		patch.status = status
		patch.message = message
		patch.new = new
		patch.new_sidebar = new_sidebar
		patch.new_sidebar_items = new_sidebar_items
		patch.new_sidebar_group = new_sidebar_group
		patch.save()

	else:
		patch = dontmanage.new_doc("Wiki Page Patch")

		patch_dict = {
			"wiki_page": name,
			"status": status,
			"raised_by": dontmanage.session.user,
			"new_code": content,
			"message": message,
			"new": new,
			"new_title": title,
			"new_sidebar_items": new_sidebar_items,
			"new_sidebar_group": new_sidebar_group,
		}

		patch.update(patch_dict)

		patch.save()

		if file_ids:
			update_file_links(file_ids, patch.name)

	out = dontmanage._dict()

	if dontmanage.has_permission(doctype="Wiki Page Patch", ptype="submit", throw=False) and not draft:
		patch.approved_by = dontmanage.session.user
		patch.status = "Approved"
		patch.submit()
		out.approved = True

	dontmanage.db.commit()
	if draft:
		out.route = "drafts"
	elif not dontmanage.has_permission(doctype="Wiki Page Patch", ptype="submit", throw=False):
		out.route = "contributions"
	elif hasattr(patch, "new_wiki_page"):
		out.route = patch.new_wiki_page.route
	else:
		out.route = patch.wiki_page_doc.route

	return out


def update_file_links(file_ids, patch_name):
	for file_id in file_ids:
		file = dontmanage.get_doc("File", file_id)
		file.attached_to_doctype = "Wiki Page Patch"
		file.attached_to_name = patch_name
		file.save()


def get_source_generator(resolved_route, jenv):
	path = resolved_route.controller.split(".")
	path[-1] = "templates"
	path.append(path[-2] + ".html")
	path = "/".join(path)
	return jenv.loader.get_source(jenv, path)[0]


def get_source(resolved_route, jenv):
	if resolved_route.page_or_generator == "Generator":
		return get_source_generator(resolved_route, jenv)

	elif resolved_route.page_or_generator == "Page":
		return jenv.loader.get_source(jenv, resolved_route.template)[0]


@dontmanage.whitelist(allow_guest=True)
def get_sidebar_for_page(wiki_page):
	sidebar = dontmanage.get_doc("Wiki Page", wiki_page).get_sidebar_items()
	return sidebar


@dontmanage.whitelist()
def approve(wiki_page_patch):
	if not dontmanage.has_permission(doctype="Wiki Page Patch", ptype="submit", throw=False):
		dontmanage.throw(
			_("You are not permitted to approve, Please wait for a moderator to respond"),
			dontmanage.PermissionError,
		)

	patch = dontmanage.get_doc("Wiki Page Patch", wiki_page_patch)
	patch.approved_by = dontmanage.session.user
	patch.status = "Approved"
	patch.submit()


@dontmanage.whitelist()
def delete_wiki_page(wiki_page_route):
	if not dontmanage.has_permission(doctype="Wiki Page", ptype="delete", throw=False):
		dontmanage.throw(
			_("You are not permitted to delete a Wiki Page"),
			dontmanage.PermissionError,
		)
	wiki_page_name = dontmanage.get_value("Wiki Page", {"route": wiki_page_route})
	if wiki_page_name:
		dontmanage.delete_doc("Wiki Page", wiki_page_name)
		return True

	dontmanage.throw(_("The Wiki Page you are trying to delete doesn't exist"))
