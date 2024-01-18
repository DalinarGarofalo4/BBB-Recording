from datetime import timedelta, datetime
from distutils.dir_util import copy_tree
from http.client import responses
import json
import logging
from moviepy.editor import VideoFileClip, clips_array
import os
import re
from shutil import copytree, move
import time
from urllib import error, parse, request
import xml.etree.ElementTree as ElementTree
import zipfile

from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT
)

from app.exceptions import ApiException, raise_exception
from app.error_codes import FOLDER_CREATION_FAILED, FILE_NOT_FOUND
from app.config import current

logger = logging.getLogger(__name__)


# TODO: *** IMPORTANT ***
# TODO: Refactor this util...

# Check if pySmartDL library is available, otherwise use urllib
try:
    bar = None
    from pySmartDL import SmartDL
    smart_dl_enabled = True
except ImportError:
    SmartDL = None
    logger.warning("pySmartDL not imported, using urllib instead")
    smart_dl_enabled = False

    # Try to import progressist for displaying a progress bar
    try:
        from progressist import ProgressBar

        # Configure a progress bar with a specific template
        bar = ProgressBar(
            throttle=timedelta(seconds=1),
            template="Download |{animation}|{tta}| {done:B}/{total:B} at {speed:B}/s"
        )
    except Exception:
        # If progressist is not available, log a warning
        logger.warning(
            'progressist not imported. Progress bar will not be shown. Try running: pip3 install progressist'
        )


# TODO: Missing unit tests...
async def combine(file_id_or_name, combine_boolean):
    try:
        # Attempt to list items in the directory for the specified meeting
        os.listdir(os.path.join(current.BASE_DIR, current.BBB.DOWNLOADED_MEETINGS_FOLDER, file_id_or_name))

        # Change the current working directory to the meeting folder
        os.chdir(os.path.join(current.BASE_DIR, current.BBB.DOWNLOADED_MEETINGS_FOLDER, file_id_or_name))
    except Exception as ex:
        # Handle the case where the meeting with the specified ID or name is not downloaded
        msg = f'{responses[HTTP_404_NOT_FOUND]}. ' \
              f'Meeting with ID {file_id_or_name} is not downloaded. Download it first using the --download command'
        logger.error(msg)
        raise_exception(ApiException(), HTTP_404_NOT_FOUND, msg, FILE_NOT_FOUND, ex)

    # Check if the fileIdOrName looks like a BBB meeting ID
    matches_name = re.match(r"([0-9a-f]{40}-\d{13})", file_id_or_name, re.IGNORECASE)
    if matches_name:
        # if file id/name looks like bbb 54 char string use a simple predefined name
        meeting_id = matches_name.group(0)
        logger.info(f"Extracted meeting id: {meeting_id} from provided name")
        logger.info(f"Setting output file name to {current.BBB.DEFAULT_COMBINED_VIDEO_NAME}")
        file_name = current.BBB.DEFAULT_COMBINED_VIDEO_NAME
    else:
        # Otherwise, use the provided fileIdOrName as the file name
        file_name = file_id_or_name

    # Check if combining video files is enabled
    if combine_boolean:
        # Check if the combined video file already exists
        combine_video_name = current.BBB.DEFAULT_COMBINED_VIDEO_NAME
        combine_video_format = current.BBB.COMBINED_VIDEO_FORMAT

        if os.path.isfile(f'./{file_name}.{combine_video_format}'):
            logger.warning(f'./{combine_video_name}.{combine_video_name} already found. Aborting.')
            exit(1)
        elif os.path.isfile('./deskshare/deskshare.mp4') and os.path.isfile('./video/webcams.mp4'):
            # If both video files exist, combine them using the moviepyCombine function
            logger.info("The files exits")
            file_name = file_name + ".mp4"
            await moviepy_combine('./deskshare/deskshare.mp4', './video/webcams.mp4', file_name)

            # Create a zip file containing the combined video file
            zip_file_name = file_id_or_name + ".zip"
            with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_name)

        else:
            # Handle the case where video files are not found
            msg = f'{responses[HTTP_404_NOT_FOUND]}. Video files not found, this meeting might not be supported.'
            logger.error(msg)
            raise_exception(ApiException(), HTTP_404_NOT_FOUND, msg, FILE_NOT_FOUND)

    else:
        # If combining is not enabled, move the webcams.mp4 file to the specified file name
        file_name = file_name + ".mp4"
        zip_file_name = file_id_or_name + ".zip"
        move('./video/webcams.mp4', file_name)

        # Create a zip file containing the moved video file
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(file_name)


# TODO: Missing unit tests...
async def copy_folder_content(source_path: str, destination_path: str):
    try:
        copytree(src=source_path, dst=destination_path)
    except Exception:
        copy_tree(src=source_path, dst=destination_path)


async def create_folder(path: str) -> None:
    try:
        os.makedirs(path)
    except OSError as ex:
        msg = f'{responses[HTTP_409_CONFLICT]}. Folder creation failed'
        raise_exception(ApiException(), HTTP_409_CONFLICT, msg, FOLDER_CREATION_FAILED, ex)


# TODO: Missing unit tests...
def format_time(start_time):
    timestamp_ms = start_time

    # Convert milliseconds to seconds
    timestamp_sec = timestamp_ms / 1000

    # Convert timestamp to datetime object
    datetime_obj = datetime.utcfromtimestamp(timestamp_sec)

    # Format the datetime as a string
    formatted_datetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


# TODO: Missing unit tests...
def get_metadata_components(elem, path_to_metadata_file):
    tree = ElementTree.parse(path_to_metadata_file)
    root = tree.getroot()

    for elem in root.iter(elem):
        return elem.text


# TODO: Missing unit tests...
async def save_bbb_metadata(folder_path: str, bbb_info: dict):
    with open(os.path.join(folder_path, current.BBB.METADATA_FILENAME), 'w') as bjf:
        json.dump(bbb_info, bjf)


# TODO: Missing unit tests...
async def download_files(base_url: str, base_path: str, bbb_info: dict):
    # List of files to download
    files_for_dl = ["metadata.xml", "video/webcams.mp4", "deskshare/deskshare.mp4"]

    # Flag to determine whether to combine video files
    combine_boolean = True

    # Initialize the downloadedFiles dictionary in bbb_info
    bbb_info["downloadedFiles"] = {}

    # Iterate through each file to download
    for i, file in enumerate(files_for_dl):
        logger.info(f'[{i + 1}/{len(files_for_dl)}] Downloading {file}')

        # Construct the download URL for the current file
        download_url = base_url + file
        logger.debug(download_url)

        # Specify the save path for the downloaded file
        save_path = os.path.join(base_path, file)
        logger.debug(save_path)

        # Mark the file as not downloaded in the downloadedFiles dictionary
        bbb_info["downloadedFiles"][file] = False
        await save_bbb_metadata(base_path, bbb_info)

        try:
            # Download the file using pySmartDL if available, else use urllib
            if smart_dl_enabled:
                smart_dl = SmartDL(download_url, save_path, verify=False)
                smart_dl.start()
            else:
                request.urlretrieve(download_url, save_path, reporthook=bar.on_urlretrieve if bar else None)

            # Mark the file as downloaded in the downloadedFiles dictionary
            bbb_info["downloadedFiles"][file] = True
            await save_bbb_metadata(base_path, bbb_info)

        except error.HTTPError as e:
            # Handle HTTP errors, log a warning for 404 errors
            if e.code == 404:
                if file == "deskshare/deskshare.mp4":
                    combine_boolean = False
                logger.warning(f"Did not download {file} because of 404 error")

        except Exception as ex:
            # Log exceptions and continue with the next file
            logger.exception(ex)

    # Return updated bbb_info and combine_boolean
    return bbb_info, combine_boolean


# TODO: Missing unit tests...
async def download_script(input_url: str, meeting_name_wanted: str):
    # Initialize bbbInfo dictionary with metadata
    bbb_info = {
        'bbb_info_version': current.BBB.INFO_VERSION,
        'all_done': False,
        'input_url': input_url,
        'meeting_name_wanted': meeting_name_wanted
    }

    # Append the last 5 characters of the inputURL to meeting_name_wanted
    meeting_name_wanted = meeting_name_wanted + "-" + input_url[-5:]

    # get meeting id from url https://regex101.com/r/UjqGeo/3
    matches_url = re.search(r"/?(\d+\.\d+)/.*?([0-9a-f]{40}-\d{13})/?", input_url, re.IGNORECASE)
    meeting_id = ''

    if matches_url and len(matches_url.groups()) == 2:
        bbb_version = matches_url.group(1)
        meeting_id = matches_url.group(2)
        logger.info(f"Detected bbb version:\t{bbb_version}")
        logger.info(f"Detected meeting id:\t{meeting_id}")

        bbb_info["detected_bbb_version"] = bbb_version
        bbb_info["meeting_id"] = meeting_id
    else:
        logger.error("Meeting ID could not be found in the url.")
        # TODO:  throw 404 here, meeting_id not found...
        exit(1)

    # Construct the base URL for downloading files
    base_url = f'{parse.urlparse(input_url).scheme}://{current.BBB.SERVER}/presentation/{meeting_id}/'
    logger.debug(f'Base url: {base_url}')

    bbb_info["base_url"] = base_url

    # Construct the folder path for the downloaded meeting files
    meeting_name = meeting_name_wanted if meeting_name_wanted else meeting_id
    folder_path = os.path.join(current.BASE_DIR, current.BBB.DOWNLOADED_MEETINGS_FOLDER, meeting_name)

    logger.debug("Folder path: {}".format(folder_path))

    # Check if the download is complete based on the existence of the DOWNLOADED_FULLY_FILENAME file
    if os.path.isfile(os.path.join(folder_path, current.BBB.DOWNLOADED_FULLY_FILENAME)):
        folder_exist = True
        combine_boolean = None
    else:
        folder_exist = False

        # Initialize downloadCompleted flag and start download time in bbbInfo
        bbb_info["download_completed"] = False

        folders_to_create = [os.path.join(folder_path, x) for x in ["", "video", "deskshare", "presentation"]]

        # Create necessary folders for the downloaded files
        for i in folders_to_create:
            if not os.path.exists(i):
                await create_folder(i)

        bbb_info["download_start_time"] = time.time()
        await save_bbb_metadata(folder_path, bbb_info)

        # Download files and update bbb_info and combine_boolean
        bbb_info, combine_boolean = await download_files(base_url, folder_path, bbb_info)

        # Update download end time and set downloadCompleted flag to True
        bbb_info["download_end_time"] = time.time()
        bbb_info["download_completed"] = True
        await save_bbb_metadata(folder_path, bbb_info)

        # Copy contents of the "player3" folder to the downloaded meeting folder
        await copy_folder_content(os.path.join(current.BASE_DIR, "player3"), folder_path)
        bbb_info["copied_bbb_playback_version"] = current.BBB.PLAYBACK_VERSION
        await save_bbb_metadata(folder_path, bbb_info)

        # Create a DOWNLOADED_FULLY_FILENAME file to mark a successful download
        with open(os.path.join(folder_path, current.BBB.DOWNLOADED_FULLY_FILENAME), 'w'):
            pass

        bbb_info["all_done"] = True
        await save_bbb_metadata(folder_path, bbb_info)

    return combine_boolean, os.path.basename(folder_path), folder_exist


# TODO: Missing unit tests...
async def moviepy_combine(video_path1, video_path2, output_path):
    clip1 = VideoFileClip(video_path1)
    clip2 = VideoFileClip(video_path2)

    final_clip = clips_array([[clip1, clip2]])

    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    clip1.close()
    clip2.close()
