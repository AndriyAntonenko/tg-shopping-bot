import logging
import sys

def setup_logging(level=logging.INFO):
  fmt = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
  logging.basicConfig(stream=sys.stdout, level=level, format=fmt)
