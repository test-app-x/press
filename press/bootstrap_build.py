# Copyright (c) 2021, Frappe Technologies Pvt. Ltd. and Contributors
# For license information, please see license.txt

import frappe
import os
import time
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete


def prepare():
	complete_setup_wizard()

	settings = frappe.get_single("Press Settings")
	setup_certbot(settings)
	setup_root_domain(settings)

	setup_github(settings)

	setup_ssh_key()
	setup_cluster()

	setup_proxy_server()
	setup_database_server()
	setup_server()

	setup_registry(settings)

	setup_logging(settings)
	setup_monitoring(settings)

	setup_apps()
	setup_plans()


def complete_setup_wizard():
	setup_complete(
		{
			"language": "English",
			"country": "India",
			"timezone": "Asia/Kolkata",
			"currency": "INR",
		}
	)


def setup_certbot(settings):
	settings.eff_registration_email = frappe.conf.press_bootstrap_eff_registration_email
	settings.certbot_directory = os.path.join(
		frappe.conf.press_bootstrap_home_directory, ".certbot"
	)
	settings.webroot_directory = os.path.join(
		frappe.conf.press_bootstrap_home_directory, ".certbot", "webroot"
	)
	settings.save()
	settings.reload()


def setup_root_domain(settings):
	root_domain = frappe.conf.press_bootstrap_root_domain
	if frappe.db.get_value("Root Domain", root_domain):
		domain = frappe.get_doc("Root Domain", root_domain)
	else:
		domain = frappe.get_doc(
			{
				"doctype": "Root Domain",
				"name": root_domain,
				"default_cluster": "Default",
				"aws_access_key_id": frappe.conf.press_bootstrap_aws_access_key_id,
				"aws_secret_access_key": frappe.conf.press_bootstrap_aws_secret_access_key,
			}
		).insert()
	frappe.db.commit()
	while not frappe.db.exists(
		"TLS Certificate", {"wildcard": True, "domain": root_domain, "status": "Active"}
	):
		print("Waiting for TLS certificate")
		time.sleep(1)
		frappe.db.commit()

	settings.domain = domain.name
	settings.cluster = domain.default_cluster
	settings.save()
	settings.reload()


def setup_github(settings):
	settings.github_access_token = frappe.conf.press_bootstrap_github_access_token
	settings.save()
	settings.reload()


def setup_ssh_key():
	cluster = frappe._dict(frappe.conf.press_bootstrap_cluster)
	if frappe.db.get_value("SSH Key", cluster.name):
		return
	frappe.get_doc(
		{
			"doctype": "SSH Key",
			"name": cluster.name,
			"public_key": open(os.path.expanduser("~/.ssh/id_rsa.pub")).read(),
			"enabled": True,
			"default": True,
		}
	).insert()
	frappe.db.commit()


def setup_cluster():
	cluster = frappe._dict(frappe.conf.press_bootstrap_cluster)
	if frappe.db.get_value("Cluster", cluster.name):
		return
	frappe.get_doc(
		{
			"doctype": "Cluster",
			"name": cluster.name,
			"public": True,
			"provider": "AWS EC2",
			"region": cluster.region,
			"availability_zone": cluster.availability_zone,
			"aws_access_key_id": frappe.conf.press_bootstrap_aws_access_key_id,
			"aws_secret_access_key": frappe.conf.press_bootstrap_aws_secret_access_key,
			"ssh_key": cluster.name,
		}
	).insert()
	frappe.db.commit()


def setup_registry(settings):
	if frappe.db.exists("Registry Server", {"hostname": "registry"}):
		registry = frappe.get_doc("Registry Server", {"hostname": "registry"})
	else:
		registry = frappe.get_doc(
			{
				"doctype": "Registry Server",
				"hostname": "registry",
				"ip": "10.0.4.101",
				"private_ip": "10.1.4.101",
			}
		).insert()

	settings.clone_directory = os.path.join(
		frappe.conf.press_bootstrap_home_directory, ".clones"
	)
	settings.build_directory = os.path.join(
		frappe.conf.press_bootstrap_home_directory, ".builds"
	)

	settings.docker_registry_url = registry.name
	settings.docker_registry_username = registry.registry_username
	settings.docker_registry_password = registry.get_password("registry_password")

	settings.save()
	settings.reload()


def setup_logging(settings):
	if frappe.db.exists("Log Server", {"hostname": "log"}):
		log = frappe.get_doc("Log Server", {"hostname": "log"})
	else:
		log = frappe.get_doc(
			{
				"doctype": "Log Server",
				"hostname": "log",
				"ip": "10.0.4.102",
				"private_ip": "10.1.4.102",
			}
		).insert()

	settings.log_server = log.name

	settings.save()
	settings.reload()


def setup_monitoring(settings):
	if frappe.db.exists("Monitor Server", {"hostname": "monitor"}):
		monitor = frappe.get_doc("Monitor Server", {"hostname": "monitor"})
	else:
		monitor = frappe.get_doc(
			{
				"doctype": "Monitor Server",
				"hostname": "monitor",
				"ip": "10.0.4.103",
				"private_ip": "10.1.4.103",
			}
		).insert()

	settings.monitor_server = monitor.name
	settings.monitor_token = frappe.generate_hash()
	settings.press_monitoring_password = frappe.generate_hash()

	if not frappe.db.exists("Telegram Group", "Alerts"):
		frappe.get_doc(
			{
				"doctype": "Telegram Group",
				"name": "Alerts",
				"chat_id": frappe.conf.press_bootstrap_telegram_chat_id,
				"token": frappe.conf.press_bootstrap_telegram_bot_token,
			}
		).insert()

	settings.telegram_alerts_chat_group = "Alerts"

	settings.save()
	settings.reload()


def setup_proxy_server():
	if frappe.db.exists("Proxy Server", {"hostname": "n1"}):
		return
	frappe.get_doc(
		{
			"doctype": "Proxy Server",
			"hostname": "n1",
			"ip": "10.0.1.101",
			"private_ip": "10.1.1.101",
		}
	).insert()


def setup_database_server():
	if frappe.db.exists("Database Server", {"hostname": "m1"}):
		return
	frappe.get_doc(
		{
			"doctype": "Database Server",
			"title": "First - Database",
			"hostname": "m1",
			"ip": "10.0.3.101",
			"private_ip": "10.1.3.101",
		}
	).insert()


def setup_server():
	if frappe.db.exists("Server", {"hostname": "f1"}):
		return
	frappe.get_doc(
		{
			"doctype": "Server",
			"title": "First - Application",
			"hostname": "f1",
			"ip": "10.0.2.101",
			"private_ip": "10.1.2.101",
			"proxy_server": f"n1.{frappe.conf.press_bootstrap_root_domain}",
			"database_server": f"m1.{frappe.conf.press_bootstrap_root_domain}",
		}
	).insert()


def setup():
	servers = [
		("Proxy Server", f"n1.{frappe.conf.press_bootstrap_root_domain}"),
		("Database Server", f"m1.{frappe.conf.press_bootstrap_root_domain}"),
		("Server", f"f1.{frappe.conf.press_bootstrap_root_domain}"),
		("Registry Server", f"registry.{frappe.conf.press_bootstrap_root_domain}"),
		("Log Server", f"log.{frappe.conf.press_bootstrap_root_domain}"),
		("Monitor Server", f"monitor.{frappe.conf.press_bootstrap_root_domain}"),
	]
	for server_type, server in servers:
		frappe.get_doc(server_type, server).setup_server()


def setup_plans():
	plans = [("Free", 0), ("USD 10", 10), ("USD 25", 25)]
	for index, plan in enumerate(plans, 1):
		if frappe.db.exists("Site Plan", plan[0]):
			continue
		frappe.get_doc(
			{
				"doctype": "Site Plan",
				"name": plan[0],
				"document_type": "Site",
				"plan_title": plan[0],
				"price_usd": plan[1],
				"price_inr": plan[1] * 80,
				"cpu_time_per_day": index,
				"max_database_usage": 1024 * index,
				"max_storage_usage": 10240 * index,
				"roles": [
					{"role": "System Manager"},
					{"role": "Press Admin"},
					{"role": "Press Member"},
				],
			}
		).insert()


def setup_apps():
	if frappe.db.exists("App", "frappe"):
		app = frappe.get_doc("App", "frappe")
	else:
		app = frappe.get_doc(
			{"doctype": "App", "name": "frappe", "title": "Frappe Framework", "frappe": True}
		).insert()
	if frappe.db.exists("App Source", {"app": app.name}):
		source = frappe.get_doc("App Source", {"app": app.name})
	else:
		source = frappe.get_doc(
			{
				"doctype": "App Source",
				"app": app.name,
				"branch": "develop",
				"repository_url": "https://github.com/frappe/frappe",
				"public": True,
				"team": "Administrator",
				"versions": [{"version": "Nightly"}],
			}
		).insert()
	if frappe.db.exists("Release Group", {"title": "Frappe"}):
		return
	frappe.get_doc(
		{
			"doctype": "Release Group",
			"title": "Frappe",
			"version": "Nightly",
			"team": "Administrator",
			"apps": [{"app": app.name, "source": source.name}],
			"server": [
				{"server": f"f1.{frappe.conf.press_bootstrap_root_domain}", "default": True}
			],
		}
	).insert()
