# coding=utf-8

import os
import shutil

from safe.common.custom_logging import setup_logger as setup_logger_safe


def realtime_logger_name():
    """Get logger name for Realtime."""
    logger_name = 'InaSAFE Realtime'
    return logger_name


def setup_logger():
    """Run once when the module is loaded and enable logging.

    Borrowed heavily from this:
    http://docs.python.org/howto/logging-cookbook.html
    """
    sentry_url = (
        'http://7674f55697ba4c0d81d12ac0efa82e7a'
        ':b197c79de15045509f5f9a1bf97e09da@sentry.kartoza.com/2')
    setup_logger_safe(realtime_logger_name(), sentry_url=sentry_url)


def split_layer_ext(layer_path):
    """Split layer file by basename and extension.

    We need this to accommodate parsing base_layer.aux.xml into
    base_layer with ext .aux.xml, which is not provided os.path.splitext

    :param layer_path: The path to the base file of the layer
    :type layer_path: str

    :return: A tuple of basename and extension: (basename, ext)
    :rtype: (str, str)
    """
    split = layer_path.split('.')
    # take the first as basename and the rest as ext
    banana = split[0]
    return banana, '.'.join([''] + split[1:])


def copy_layers(source, destination):
    """Copy InaSAFE Layer with all it's possible accompanying files.

    :param source: Source base layer file
    :param destination: Destination base layer file
    """
    # Retrieve basename
    source_basename, ext = os.path.splitext(os.path.basename(source))
    destination_basename, ext = os.path.splitext(
        os.path.basename(destination))

    # Retrieve dirname
    source_dirname = os.path.dirname(source)
    destination_dirname = os.path.dirname(destination)

    for root, dirs, files in os.walk(source_dirname):
        for f in files:
            s_basename, s_ext = split_layer_ext(f)
            if s_basename == source_basename:
                src = os.path.join(root, f)
                d_filename = destination_basename + s_ext
                dst = os.path.join(destination_dirname, d_filename)
                shutil.copy(src, dst)


class BaseHazardTaskResult(object):

    def __init__(self, success, hazard_path=None):
        super(BaseHazardTaskResult, self).__init__()
        self.success = success
        self.hazard_path = hazard_path
