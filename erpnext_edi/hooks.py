from . import __version__ as app_version

app_name = "erpnext_edi"
app_title = "Erpnext Edi"
app_publisher = "ketan"
app_description = "UN/EDIFACT"
app_email = "ketantada@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/erpnext_edi/css/erpnext_edi.css"
# app_include_js = "/assets/erpnext_edi/js/erpnext_edi.js"

# include js, css files in header of web template
# web_include_css = "/assets/erpnext_edi/css/erpnext_edi.css"
# web_include_js = "/assets/erpnext_edi/js/erpnext_edi.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "erpnext_edi/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "erpnext_edi.utils.jinja_methods",
# 	"filters": "erpnext_edi.utils.jinja_filters"
# }

jinja = {
    "methods": [
        "india_compliance.gst_india.utils.get_state",
        "india_compliance.gst_india.utils.jinja.add_spacing",
        "india_compliance.gst_india.utils.jinja.get_supply_type",
        "india_compliance.gst_india.utils.jinja.get_sub_supply_type",
        "india_compliance.gst_india.utils.jinja.get_e_waybill_qr_code",
        "india_compliance.gst_india.utils.jinja.get_qr_code",
        "india_compliance.gst_india.utils.jinja.get_transport_type",
        "india_compliance.gst_india.utils.jinja.get_transport_mode",
        "india_compliance.gst_india.utils.jinja.get_ewaybill_barcode",
        "india_compliance.gst_india.utils.jinja.get_e_invoice_item_fields",
        "india_compliance.gst_india.utils.jinja.get_e_invoice_amount_fields",
    ],
}

# Installation
# ------------

# before_install = "erpnext_edi.install.before_install"
# after_install = "erpnext_edi.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "erpnext_edi.uninstall.before_uninstall"
# after_uninstall = "erpnext_edi.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "erpnext_edi.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
    # 	"all": [
    # 		"erpnext_edi.tasks.all"
    # 	],
    # 	"daily": [
    # 		"erpnext_edi.tasks.daily"
    # 	],
    # "all": ["erpnext_edi.erpnext_edi.cron.get_edi_messages.fetch_messages"],
    # 	"weekly": [
    # 		"erpnext_edi.tasks.weekly"
    # 	],
    # 	"monthly": [
    # 		"erpnext_edi.tasks.monthly"
    # 	],
    "cron": {
        "*/5 * * * *": ["erpnext_edi.erpnext_edi.cron.get_edi_messages.fetch_messages"],
        "*/7 * * * *": ["erpnext_edi.erpnext_edi.cron.process_edi_log.exec"],
    }
}

# Testing
# -------

# before_tests = "erpnext_edi.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "erpnext_edi.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "erpnext_edi.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"erpnext_edi.auth.validate"
# ]
