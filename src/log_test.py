import logger

l = logger.logger()
l.do_log = True
l.log_message("hello", "info")
l.log_message("bad behavior", "error")
