import dontmanage


def get_context(context):

	dontmanage.form_dict.revisions = True
	wiki_settings = dontmanage.get_single("Wiki Settings")
	context.banner_image = wiki_settings.logo
	context.script = wiki_settings.javascript
	context.docs_search_scope = ""
	can_edit = dontmanage.session.user != "Guest"
	context.can_edit = can_edit
	context.show_my_account = False
	wiki_page_name = dontmanage.db.get_value(
		"Wiki Page", filters={"route": dontmanage.form_dict.wiki_page}, fieldname="name"
	)

	revisions = dontmanage.db.get_all(
		"Wiki Page Revision",
		filters=[["Wiki Page Revision Item", "wiki_page", "=", wiki_page_name]],
		fields=["message", "creation", "owner", "name", "raised_by", "raised_by_username"],
	)
	context.revisions = revisions
	context.no_cache = 1
	context.doc = dontmanage.get_doc("Wiki Page", wiki_page_name)
	context.title = "Revisions: " + context.doc.title

	context.doc.set_breadcrumbs(context)
	return context
