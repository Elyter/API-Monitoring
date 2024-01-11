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
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
        with open(CONFIG_FILE_PATH, "w") as config_file:
            json.dump({"ports": []}, config_file, indent=2)

    with open(CONFIG_FILE_PATH, "r") as config_file:
        return json.load(config_file)


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
    recent_reports = [
        report_id for report_id in reports if is_within_last_x_hours(report_id, last_x_hours)
    ]

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
        logging.warning("No reports available in the specified time range.")
        return None

def is_within_last_x_hours(report_id, last_x_hours):
    report_file = os.path.join(REPORTS_DIR, report_id)
    with open(report_file, "r") as report_file:
        report_data = json.load(report_file)

    report_time = datetime.datetime.strptime(report_data["timestamp"], "%Y-%m-%d %H:%M:%S")
    time_difference = datetime.datetime.now() - report_time

    return time_difference.total_seconds() / 3600 <= last_x_hours



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
        report = check_resources()
        print("Report generated:\n")
        print(f"id : {report["id"]}")
        print(f"timestamp : {report["timestamp"]}")
        print(f"cpu_percent : {str(report["cpu_percent"])}%")
        print(f"ram_percent : {str(report["ram_percent"])}%")
        print(f"disk_percent : {str(report["disk_percent"])}%")
        print(f"ports_status : {str(report["ports_status"])}")

    elif "list" in os.sys.argv:
        listReports = list_reports()
        print("Lists of available reports:\n")
        for report in listReports:
            print(report)

    elif "get" in os.sys.argv and "last" in os.sys.argv:
        report = get_last_report()
        print("Last report: \n")
        print(f"id : {report["id"]}")
        print(f"timestamp : {report["timestamp"]}")
        print(f"cpu_percent : {str(report["cpu_percent"])}%")
        print(f"ram_percent : {str(report["ram_percent"])}%")
        print(f"disk_percent : {str(report["disk_percent"])}%")
        print(f"ports_status : {str(report["ports_status"])}")

    elif "get" in os.sys.argv and "avg" in os.sys.argv and len(os.sys.argv) == 4:
        last_x_hours = int(os.sys.argv[3])
        report = get_average_report(last_x_hours)
        print(f"Average report for the last {last_x_hours} hours: \n")
        print(f"cpu_percent : {str(report["cpu_percent"])}%")
        print(f"ram_percent : {str(report["ram_percent"])}%")
        print(f"disk_percent : {str(report["disk_percent"])}%")

    else:
        print("Usage: python monit.py [check | list | get last | get avg X]")
