# monit.py

import psutil
import json
import os
import datetime
import socket
import logging
from logging.handlers import RotatingFileHandler

# Configurations
LOG_DIR = "/var/monit"
CONFIG_FILE_PATH = "/etc/monit/monit_config.json"
REPORTS_DIR = "/var/monit/reports"


def setup_logging():
    log_file = os.path.join(LOG_DIR, "monit.log")

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logging.basicConfig(
        handlers=[RotatingFileHandler(log_file, maxBytes=102400, backupCount=5)],
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO,
    )


def load_config():
    if not os.path.exists(CONFIG_FILE_PATH):
        return {}

    with open(CONFIG_FILE_PATH, "r") as config_file:
        return json.load(config_file)


def save_config(config):
    with open(CONFIG_FILE_PATH, "w") as config_file:
        json.dump(config, config_file, indent=2)


def check_resources():
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage("/").percent

    config = load_config()
    ports_status = {}
    for port in config.get("ports", []):
        ports_status[port] = is_port_open("127.0.0.1", port)

    report = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "id": str(hash(datetime.datetime.now())),
        "cpu_percent": cpu_percent,
        "ram_percent": ram_percent,
        "disk_percent": disk_percent,
        "ports_status": ports_status,
    }

    report_file = os.path.join(REPORTS_DIR, f"report_{report['id']}.json")
    with open(report_file, "w") as report_file:
        json.dump(report, report_file, indent=2)

    logging.info("Check completed and report generated.")
    return report


def list_reports():
    reports = [f for f in os.listdir(REPORTS_DIR) if f.startswith("report_")]
    logging.info("List of available reports: %s", reports)
    print(reports)
    return reports


def get_last_report():
    reports = list_reports()
    if reports:
        latest_report = max(reports)
        report_file = os.path.join(REPORTS_DIR, latest_report)
        with open(report_file, "r") as report_file:
            last_report = json.load(report_file)
        logging.info("Retrieved the last report.")
        return last_report
    else:
        logging.warning("No reports available.")
        return None


def get_average_report(last_x_hours):
    reports = list_reports()
    recent_reports = sorted(reports, reverse=True)[:last_x_hours]

    if recent_reports:
        average_report = {"cpu_percent": 0, "ram_percent": 0, "disk_percent": 0}

        for report_id in recent_reports:
            report_file = os.path.join(REPORTS_DIR, report_id)
            with open(report_file, "r") as report_file:
                report_data = json.load(report_file)

            average_report["cpu_percent"] += report_data["cpu_percent"]
            average_report["ram_percent"] += report_data["ram_percent"]
            average_report["disk_percent"] += report_data["disk_percent"]

        total_reports = len(recent_reports)
        average_report["cpu_percent"] /= total_reports
        average_report["ram_percent"] /= total_reports
        average_report["disk_percent"] /= total_reports

        logging.info("Calculated the average report for the last %d hours.", last_x_hours)
        return average_report
    else:
        logging.warning("No reports available.")
        return None


def is_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False


if __name__ == "__main__":
    setup_logging()

    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    # Commands
    if "check" in os.sys.argv:
        check_resources()

    elif "list" in os.sys.argv:
        list_reports()

    elif "get" in os.sys.argv and "last" in os.sys.argv:
        get_last_report()

    elif "get" in os.sys.argv and "avg" in os.sys.argv and len(os.sys.argv) == 4:
        last_x_hours = int(os.sys.argv[3])
        get_average_report(last_x_hours)

    else:
        print("Usage: python monit.py [check | list | get last | get avg X]")
