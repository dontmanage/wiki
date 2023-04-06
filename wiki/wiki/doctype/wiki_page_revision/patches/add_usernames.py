import dontmanage


def execute():

	dontmanage.reload_doctype("Wiki Page Revision")

	revision = dontmanage.qb.DocType("Wiki Page Revision")
	user = dontmanage.qb.DocType("User")

	(
		dontmanage.qb.update(revision)
		.join(user)
		.on(user.name == revision.raised_by)
		.set(revision.raised_by_username, user.username)
	).run()
