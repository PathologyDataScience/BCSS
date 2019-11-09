import os
import sys
import logging
from io import BytesIO
from PIL import Image

CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, CWD)
Image.MAX_IMAGE_PIXELS = 1000000000
logger = logging.getLogger()

import configs as cf


def create_directory_structure(folderList):
    """create folders if non-existent"""
    savepaths = {'base': cf.SAVEPATH}
    for folder in folderList:
        folderpath = os.path.join(cf.SAVEPATH, folder)
        savepaths[folder] = folderpath
        try:
            os.mkdir(folderpath)
        except FileExistsError:
            pass
    return savepaths


def printNlog(msg, level='info'):
    print(msg)
    if level == 'info':
        logger.info(msg)
    elif level == 'error':
        logger.error(msg)
    else:
        pass


def get_image_from_htk_response(resp):
    """Given a girder response, get np array image"""
    image_content = BytesIO(resp.content)
    image_content.seek(0)
    Image.open(image_content)
    image = Image.open(image_content)
    return image
