import logging


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = record.levelname.ljust(8)
        return super().format(record)


logger = logging.getLogger(name='ImageDistributor')
logger.propagate = False

handler = logging.StreamHandler()
handler.setFormatter(
    CustomFormatter(
        fmt='%(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
)
logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)