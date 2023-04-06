# Copyright (c) 2021, DontManage and Contributors
# MIT License. See license.txt


import dontmanage


def execute():
	try:
		dontmanage.db.sql("alter table `tabWiki Page Patch` drop column is_new;")
		dontmanage.db.commit()
	except BaseException:
		pass
