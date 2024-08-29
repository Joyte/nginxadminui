import os
import re
import codecs
from extensions.apimodels import Log, LogType, LogErrorLevel


class LogException(Exception):
    pass


class LogManager:
    def __init__(self):
        self.log_dir = os.getenv("LOG_DIR", "/etc/nginxadminui/logs")
        self.access_log_pattern = re.compile(
            r"(?P<remote_addr>\S+) "  # IP address
            r"- (?P<remote_user>\S+) "  # Remote user
            r"\[(?P<time_local>.*?)\] "  # Time
            r'"(?P<request>.*?)" '  # Request
            r"(?P<status>\d{3}) "  # Status code
            r"(?P<body_bytes_sent>\d+) "  # Body bytes sent
            r'"(?P<http_referer>.*?)" '  # HTTP referer
            r'"(?P<http_user_agent>.*?)"'  # User agent
        )
        self.error_log_pattern = re.compile(
            r"(?P<date>\d{4}/\d{2}/\d{2}) "  # Date
            r"(?P<time>\d{2}:\d{2}:\d{2}) "  # Time
            r"\[(?P<log_level>\w+)\] "  # Log level (error, warn, etc.)
            r"(?P<pid>\d+)#(?P<tid>\d+): "  # PID and TID
            r"\*(?P<cid>\d+) "  # Connection ID
            r"(?P<message>.*)"  # Error message
        )

    def get_logs(self):
        return {
            name: [type[:-4] for type in os.listdir(f"{self.log_dir}/{name}")]
            for name in os.listdir(self.log_dir)
        }

    def get_log(self, log: Log, limit: int = 100, offset: int = 0):
        if not os.path.exists(f"{self.log_dir}/{log.name}"):
            raise LogException("Log not found.")

        logs = []
        # Read log lines without reading the whole file
        with open(f"{self.log_dir}/{log.name}/{log.type.name}.log", "r") as f:
            for i, line in enumerate(f):
                if i < offset:
                    continue
                logs.append(line)
                if i >= limit - 1 + offset:
                    break

        parsed_logs = []
        for i, log_line in enumerate(logs):
            if log.type == LogType.error:
                match = self.error_log_pattern.match(log_line)
                parsed_line = match.groupdict()
                parsed_line["importance"] = LogErrorLevel[
                    parsed_line["log_level"]
                ].value

            else:
                match = self.access_log_pattern.match(log_line)
                parsed_line = match.groupdict()
            if not match:
                continue

            parsed_logs.append(parsed_line)
        return parsed_logs

    def create_log(self, log: Log):
        if not os.path.exists(f"{self.log_dir}/{log.name}"):
            os.makedirs(f"{self.log_dir}/{log.name}")
            for logtype in LogType:
                with open(f"{self.log_dir}/{log.name}/{logtype.value}.log", "w") as f:
                    pass
        else:
            raise LogException("Log type already exists.")

    def delete_log(self, log: Log):
        if not os.path.exists(f"{self.log_dir}/{log.name}"):
            raise LogException("Log not found.")

        for logtype in LogType:
            os.remove(f"{self.log_dir}/{log.name}/{logtype.value}.log")

        os.rmdir(f"{self.log_dir}/{log.name}")
