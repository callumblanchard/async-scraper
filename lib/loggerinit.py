import logging
import os.path


def logger_init(name):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(name)s: %(message)s",
        level=logging.DEBUG,
        datefmt="%H:%M:%S",
        filename=os.path.join("log", "logfile.log"),
    )

    logging.getLogger("chardet.charsetprober").disabled = True

    return logging.getLogger(name)
