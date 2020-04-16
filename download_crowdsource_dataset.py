#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
import girder_client
import datetime
import csv
import requests
import numpy as np
from skimage.transform import resize
from imageio import imwrite

CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, CWD)

from utils import (
    create_directory_structure, printNlog, get_image_from_htk_response, cf)

# =============================================================================


def run_prepwork():
    """Ground work"""
    # create directories
    savepaths = create_directory_structure(
        ['wsis', 'annotations', 'masks', 'images', 'logs'])

    # configure logger
    now = str(datetime.datetime.now()).replace(' ', '_').replace(':', '_')
    logging.basicConfig(
        filename=os.path.join(savepaths['logs'], now + '.log'),
        format='%(asctime)s %(levelname)-3s %(message)s', level=logging.INFO)
    printNlog("STARTED.")

    # Connect to API
    gc = girder_client.GirderClient(apiUrl=cf.APIURL)
    if cf.apiKey is not None:
        gc.authenticate(apiKey=cf.apiKey)
    else:
        printNlog("""Enter login information below.
        If you don't have an account, register for free at:
        http://demo.kitware.com/histomicstk/histomicstk
        It only takes a minute.
        """)
        gc.authenticate(interactive=True)

    # Get list of slides to download
    resp = gc.get("item?folderId=%s&limit=1000000" % cf.source_folder_id)
    slides = dict()
    for s in resp:
        short_name = s['name'][:12]
        slides[short_name] = {'name': s['name'], '_id': s['_id']}
    del resp

    # Do not re-download slides
    existing_slides = set([
        j for j in os.listdir(savepaths['wsis']) if j.endswith('.svs')])
    slide_list = list(set(slides.keys()) - existing_slides)

    # restrict slide list if needed
    if cf.SLIDES_TO_KEEP is not None:
        slide_list = [j for j in slide_list if j in cf.SLIDES_TO_KEEP]

    # Assign as configurations
    cf.gc = gc
    cf.savepaths = savepaths
    cf.slide_list = slide_list
    cf.slides = slides

# =============================================================================


def download_rgbs_and_masks():
    """Download RGB images and corresponding masks"""
    n_slides = len(cf.slide_list)

    sldid = 0
    with open(cf.ROIBOUNDSPATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:

            slide_name = row[''][:12]
            if slide_name not in cf.slide_list:
                continue

            sldid += 1
            xmin = int(float(row['xmin']))
            ymin = int(float(row['ymin']))
            
            if 'images' in cf.PIPELINE:
                printNlog("Downloading RGB image: Slide %d of %d (%s)" % (
                    sldid, n_slides, slide_name))

                # Default is to get things at base magnification
                getStr = \
                    "/item/%s/tiles/region?left=%d&right=%d&top=%d&bottom=%d" \
                    % (
                        cf.slides[slide_name]['_id'],
                        xmin, int(float(row['xmax'])),
                        ymin, int(float(row['ymax'])),)

                if cf.MPP is not None:  # Specific microns-per-pixel
                    mm = 0.001 * cf.MPP
                    getStr += "&mm_x=%.4f&mm_y=%.4f" % (mm, mm)
                    append_str = "MPP-%.4f" % cf.MPP

                elif cf.MAG is not None:  # Specific magnification
                    getStr += "&magnification=%.2f" % cf.MAG
                    append_str = "MAG-%.2f" % cf.MAG

                else:
                    append_str = "MAG-0"

                resp = cf.gc.get(getStr, jsonResp=False)
                rgb = get_image_from_htk_response(resp)
                rgb.save(
                    os.path.join(
                        cf.savepaths['images'], "%s_xmin%d_ymin%d_%s.png"
                        % (row[''], xmin, ymin, append_str)))

            if 'masks' in cf.PIPELINE:
                printNlog("Downloading mask: Slide %d of %d (%s)" % (
                    sldid, n_slides, slide_name))

                mask = np.uint8(get_image_from_htk_response(
                    requests.get(row['mask_link'])))

                # resize to match RGB magnification
                if 'images' in cf.PIPELINE:
                    mask = np.uint8(resize(
                        mask, output_shape=np.array(rgb).shape[:2],
                        order=0, preserve_range=True, anti_aliasing=False))
                else:
                    append_str = "MAG-0"

                imwrite(im=mask, uri=os.path.join(
                    cf.savepaths['masks'], "%s_xmin%d_ymin%d_%s.png"
                    % (row[''], xmin, ymin, append_str)))

# =============================================================================


def download_jsons():
    """Download JSON annotations -- at base magnification."""
    for sldid, slide_name in enumerate(cf.slide_list):
        printNlog("Downloading annotations (base mag): Slide %d of %d (%s)" % (
            sldid + 1, len(cf.slide_list), slide_name))
        annotations = cf.gc.get(
            "/annotation/item/" + cf.slides[slide_name]['_id'])
        savename = os.path.join(
            cf.savepaths['annotations'], cf.slides[slide_name]['name'])
        savename = savename.replace('.svs', '.json')
        with open(savename, 'w') as f:
            json.dump(annotations, f)

# =============================================================================


def create_wsi_download_script():
    """Create WSI download shell script"""
    # bat script if windows, else bash script
    ext = '.bat' if os.name == 'nt' else '.sh'
    cf.savepaths['wsi_script'] = os.path.join(
        cf.savepaths['wsis'], 'download_wsis' + ext)

    # Add commands to batch or bash script
    printNlog("Adding download commands to %s" % cf.savepaths['wsi_script'])
    if cf.apiKey is not None:
        apikey = cf.apiKey
    else:
        resp = cf.gc.post('api_key')
        apikey = resp['key']
    for slide_name in cf.slide_list:
        command_base = \
            "girder-client --api-url %s --api-key %s download %s %s" % (
            cf.APIURL, apikey, cf.slides[slide_name]['_id'],
            cf.savepaths['wsis'])
        with open(cf.savepaths['wsi_script'], 'a') as f:
            f.write(command_base + "\n")

# =============================================================================


def main():
    """main pipeline."""
    # add configs
    run_prepwork()

    # run pipeline
    if ('images' in cf.PIPELINE) or ('masks' in cf.PIPELINE):
        download_rgbs_and_masks()

    if 'annotations' in cf.PIPELINE:
        download_jsons()

    if 'wsis' in cf.PIPELINE:
        create_wsi_download_script()

    printNlog("DONE.")
    if 'wsis' in cf.PIPELINE:
        printNlog("""
            Now please run the batch or shell script from the command line
            using the following command:
            Windows:
                %s
            Mac or Linux:
                bash %s
            to download the full whole-slide images.
            """ % (cf.savepaths['wsi_script'], cf.savepaths['wsi_script']))


# =============================================================================

if __name__ == '__main__':
    main()
