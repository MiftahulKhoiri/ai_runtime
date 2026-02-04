import logging

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        h = logging.StreamHandler()
        f = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
        h.setFormatter(f)
        logger.addHandler(h)

    return logger