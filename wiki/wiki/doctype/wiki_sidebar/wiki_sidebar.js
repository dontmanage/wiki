// Copyright (c) 2021, DontManage and contributors
// For license information, please see license.txt

dontmanage.ui.form.on("Wiki Sidebar", {
  refresh: function (frm) {
    frm.set_query("type", "sidebar_items", function () {
      return {
        filters: {
          name: ["in", ["Wiki Page", "Wiki Sidebar"]],
        },
      };
    });
  },
});
