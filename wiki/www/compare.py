import dontmanage
from dontmanage import _
from dontmanage.query_builder import DocType

from wiki.wiki.doctype.wiki_page.wiki_page import update


def get_context(context):
	context.no_cache = 1

	wiki_settings = dontmanage.get_single("Wiki Settings")
	context.banner_image = wiki_settings.logo
	context.script = wiki_settings.javascript
	context.docs_search_scope = ""
	can_edit = dontmanage.session.user != "Guest"
	context.can_edit = can_edit
	context.show_my_account = False

	context.doc = dontmanage.get_doc("Wiki Page", dontmanage.form_dict.wiki_page)
	context.doc.set_breadcrumbs(context)

	from ghdiff import diff

	revision = dontmanage.form_dict.compare
	context.title = "Revision: " + revision
	context.parents = [
		{"route": "/" + context.doc.route, "label": context.doc.title},
		{"route": "/" + context.doc.route + "/revisions", "label": "Revisions"},
	]

	revision = dontmanage.get_doc("Wiki Page Revision", revision)

	context.revision = revision

	WikiPageRevision = DocType("Wiki Page Revision")
	WikiPageRevisionItem = DocType("Wiki Page Revision Item")

	previous_revisions = (
		dontmanage.qb.from_(WikiPageRevision)
		.join(WikiPageRevisionItem)
		.on(WikiPageRevision.name == WikiPageRevisionItem.parent)
		.where(WikiPageRevisionItem.creation < revision.creation)
		.where(WikiPageRevisionItem.wiki_page == context.doc.name)
		.select(WikiPageRevision.content)
		.orderby(WikiPageRevision.creation)
		.run()
	)

	if not previous_revisions or not previous_revisions[-1]:
		context.diff = diff("", revision.content, css=False)
	else:
		context.diff = diff(previous_revisions[-1][0], revision.content, css=False)

	return context


@dontmanage.whitelist()
def restore_wiki_revision(wiki_revision_name, wiki_page_name, wiki_revision_message):
	if not dontmanage.has_permission(doctype="Wiki Page", ptype="update", throw=False):
		dontmanage.throw(
			_("You are not permitted to revert the Wiki Page"),
			dontmanage.PermissionError,
		)

	wiki_revision_content = dontmanage.get_value("Wiki Page Revision", wiki_revision_name, ["content"])
	wiki_patch_title = dontmanage.get_value(
		"Wiki Page Patch", {"wiki_page": wiki_page_name}, ["new_title"]
	)

	update_vals = update(
		name=wiki_page_name,
		content=wiki_revision_content,
		title=wiki_patch_title,
		message=wiki_revision_message,
	)

	return update_vals.route
