#!/usr/bin/python
import os
from logging import StreamHandler, FileHandler, Formatter, getLogger, INFO, DEBUG
logPath = '../.'
logPath = logPath + os.sep


class ServiceLog(object):
    def __init__(self, log_name):
        self.log_name = log_name

    def _logger_die(self, logger, msg):
        logger.error(msg)
        raise AssertionError(msg)

    def ret_log_file_path(self):
        return logPath + self.log_name

    def logger_writer(self, date):
        formatter = Formatter('[%(asctime)s][%(filename)s:%(lineno)s][%(levelname)s][%(thread)d] %(message)s')
        DataLog = getLogger(self.log_name)
        DataLog.handlers = []
        DataLog.setLevel(DEBUG)
        DataLog.propagate = False

        console = StreamHandler()
        console.setFormatter(formatter)
        console.setLevel(INFO)
        DataLog.addHandler(console)

        logfiledebug = FileHandler(filename=logPath + self.log_name + '.' + date + '.debug.log', mode='a')
        logfiledebug.setFormatter(formatter)
        logfiledebug.setLevel(DEBUG)
        DataLog.addHandler(logfiledebug)

        logfileinfo = FileHandler(filename=logPath + self.log_name + '.' + date + '.info.log', mode='a')
        logfileinfo.setFormatter(formatter)
        logfileinfo.setLevel(INFO)
        DataLog.addHandler(logfileinfo)
        DataLog.die = lambda msg: self._logger_die(DataLog, msg)
        return DataLog
