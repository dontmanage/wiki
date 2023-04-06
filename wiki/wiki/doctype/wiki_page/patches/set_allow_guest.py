# Copyright (c) 2021, DontManage and Contributors
# MIT License. See license.txt


import dontmanage


def execute():
	dontmanage.reload_doctype("Wiki Page")
	# set allow_guest to 1 for all records
	dontmanage.db.set_value("Wiki Page", {"name": ("!=", ".")}, "allow_guest", 1)
