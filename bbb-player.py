import argparse
from urllib.parse import urlparse
import os
import urllib.request
import json
from distutils.dir_util import copy_tree
import traceback
import re
from datetime import timedelta
import logging
import time
from shutil import copytree
import webbrowser
from moviepy.editor import VideoFileClip, clips_array
from fastapi import FastAPI
from starlette.responses import StreamingResponse
import requests
from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import xml.etree.ElementTree as ET
import shutil
import zipfile
from dotenv import load_dotenv
from fastapi import Depends,HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

load_dotenv()
LOGGING_LEVEL = logging.INFO
# LOGGING_LEVEL = logging.DEBUG
DOWNLOADED_FULLY_FILENAME = "rec_fully_downloaded.txt"
DOWNLOADED_MEETINGS_FOLDER = "downloadedMeetings"
DEFAULT_COMBINED_VIDEO_NAME = "combine-output"
COMBINED_VIDEO_FORMAT = "mkv"
BBB_METADATA_FILENAME = "bbb-player-metadata.json"
CURRENT_BBB_PLAYBACK_VERSION = "3.1.1"
CURRENT_BBBINFO_VERSION = "1"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
#env variables
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SUBJECT = os.getenv("SUBJECT")
DOWNLOAD_SERVER =  os.getenv("DOWNLOAD_SERVER")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
BBB_SERVER = os.getenv("BBB_SERVER")
#Security_api_keys
SECRET_KEY = os.getenv("SECRET_KEY")  # Replace with your actual secret key
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
###############################

#setFastAPI
app = FastAPI()
# Define a custom logging formatter class that inherits from logging.Formatter
class CustomFormatter(logging.Formatter):
    # ANSI color codes for text formatting
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    # Log format template
    format = "[%(asctime)s -%(levelname)8s]: %(message)s"

    # Mapping of log levels to formatted log messages with colors
    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }
    # Override the format method to apply the custom formatting based on log level
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, "%H:%M:%S")
        return formatter.format(record)

#sets up a logging configuration with a custom formatter and a stream handler. 
ch = logging.StreamHandler()
ch.setLevel(LOGGING_LEVEL)
ch.setFormatter(CustomFormatter())
logging.basicConfig(format="[%(asctime)s -%(levelname)8s]: %(message)s",
                    datefmt="%H:%M:%S",
                    level=LOGGING_LEVEL,
                    handlers=[ch])

# Get a logger instance with the name 'bbb-player'
logger = logging.getLogger('bbb-player')

# Check if pySmartDL library is available, otherwise use urllib
try:
    from pySmartDL import SmartDL

    smartDlEnabled = True
except ImportError:
    logger.warning("pySmartDL not imported, using urllib instead")
    smartDlEnabled = False
    
    # Try to import progressist for displaying a progress bar
    try:
        from progressist import ProgressBar
        # Configure a progress bar with a specific template
        bar = ProgressBar(throttle=timedelta(seconds=1),
                          template="Download |{animation}|{tta}| {done:B}/{total:B} at {speed:B}/s")
    except:
        # If progressist is not available, log a warning
        logger.warning("progressist not imported. Progress bar will not be shown. Try running: \
                            pip3 install progressist")
        bar = None

def moviepyCombine(video_path1,video_path2,output_path):
    
    clip1 = VideoFileClip(video_path1)
    clip2 = VideoFileClip(video_path2)

    final_clip = clips_array([[clip1, clip2]])

    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    clip1.close()
    clip2.close()



    
def downloadFiles(baseURL, basePath, bbbInfo):
    # List of files to download
    filesForDL = ["metadata.xml","video/webcams.mp4", "deskshare/deskshare.mp4"]
     # Flag to determine whether to combine video files
    combine_boolean = True
     # Initialize the downloadedFiles dictionary in bbbInfo
    bbbInfo["downloadedFiles"] = {}
    # Iterate through each file to download
    for i, file in enumerate(filesForDL):
        logger.info(f'[{i + 1}/{len(filesForDL)}] Downloading {file}')
        # Construct the download URL for the current file
        downloadURL = baseURL + file
        logger.debug(downloadURL)
        # Specify the save path for the downloaded file
        savePath = os.path.join(basePath, file)
        logger.debug(savePath)
        # Mark the file as not downloaded in the downloadedFiles dictionary
        bbbInfo["downloadedFiles"][file] = False
        saveBBBmetadata(basePath, bbbInfo)
        
        try:
            # Download the file using pySmartDL if available, else use urllib
            if smartDlEnabled:
                smartDl = SmartDL(downloadURL, savePath)
                smartDl.start()
            else:
                urllib.request.urlretrieve(
                    downloadURL, savePath, reporthook=bar.on_urlretrieve if bar else None)
             # Mark the file as downloaded in the downloadedFiles dictionary
            bbbInfo["downloadedFiles"][file] = True
            saveBBBmetadata(basePath, bbbInfo)

        except urllib.error.HTTPError as e:
            # Handle HTTP errors, log a warning for 404 errors
            if e.code == 404:
                if file == "deskshare/deskshare.mp4":
                    combine_boolean = False
                logger.warning(f"Did not download {file} because of 404 error")
        except Exception as e:
            # Log exceptions and continue with the next file
            logger.exception(e)
    # Return updated bbbInfo and combine_boolean
    return bbbInfo,combine_boolean


def createFolder(path):
    # Create meeting folders, based on https://stackabuse.com/creating-and-deleting-directories-with-python/
    try:
        os.makedirs(path)
    except OSError:
        logger.debug("Creation of the directory %s failed" % path)
    else:
        logger.debug("Successfully created the directory %s " % path)


def copyFolderContents(src, dst):
    # This function copies files and folders from the src folder to the dst folder. If files already exist, it overwrites them.
    try:
        logger.debug("Using copytree")
        copytree(src, dst)
    except:
        logger.debug("Using copy_tree")
        copy_tree(src, dst)



def combine(fileIdOrName,combine_boolean):
    try:
        # Attempt to list items in the directory for the specified meeting
        items = os.listdir(os.path.join(SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER, fileIdOrName))
         # Change the current working directory to the meeting folder
        os.chdir(os.path.join(
            SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER, fileIdOrName))
    except:
        # Handle the case where the meeting with the specified ID or name is not downloaded
        logger.error(f"Meeting with ID {fileIdOrName} is not downloaded. \
                    Download it first using the --download command")
        exit(1)
    # Check if the fileIdOrName looks like a BBB meeting ID
    matchesName = re.match(
        r"([0-9a-f]{40}-\d{13})", fileIdOrName, re.IGNORECASE)
    if matchesName:
        # if file id/name looks like bbb 54 char string use a simple predefined name
        meetingId = matchesName.group(0)
        logger.info(
            f"Extracted meeting id: {meetingId} from provided name")
        logger.info(
            f"Setting output file name to {DEFAULT_COMBINED_VIDEO_NAME}")
        fileName = DEFAULT_COMBINED_VIDEO_NAME
    else:
        # Otherwise, use the provided fileIdOrName as the file name
        fileName = fileIdOrName
    # Check if combining video files is enabled
    if combine_boolean == True:
        # Check if the combined video file already exists
        if (os.path.isfile(f'./{fileName}.{COMBINED_VIDEO_FORMAT}')):
            logger.warning(
                f'./{DEFAULT_COMBINED_VIDEO_NAME}.{COMBINED_VIDEO_FORMAT} already found. Aborting.')
            exit(1)
        elif (os.path.isfile('./deskshare/deskshare.mp4') and os.path.isfile('./video/webcams.mp4')):
            # If both video files exist, combine them using the moviepyCombine function
            logger.info("The files exits")
            fileName = fileName+".mp4"
            moviepyCombine('./deskshare/deskshare.mp4','./video/webcams.mp4',fileName)
            # Create a zip file containing the combined video file
            zip_file_name = fileIdOrName + ".zip"
            with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(fileName)

        else:
            # Handle the case where video files are not found
            logger.error(
                'Video files not found, this meeting might not be supported.')
            exit(1)
    else:
        # If combining is not enabled, move the webcams.mp4 file to the specified file name
        fileName = fileName+".mp4"
        zip_file_name = fileIdOrName + ".zip"
        shutil.move('./video/webcams.mp4',fileName)
        # Create a zip file containing the moved video file
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(fileName)


def get_metadata_components(elem,path_to_metadata_file):
    tree = ET.parse(path_to_metadata_file)
    root = tree.getroot()

    for elem in root.iter(elem):
        return elem.text

def downloadScript(inputURL, meetingNameWanted):
    # Initialize bbbInfo dictionary with metadata
    bbbInfo = {}
    bbbInfo["BBBINFO_VERSION"] = CURRENT_BBBINFO_VERSION
    bbbInfo["allDone"] = False
    bbbInfo["inputURL"] = inputURL
    bbbInfo["meetingNameWanted"] = meetingNameWanted
    # Append the last 5 characters of the inputURL to meetingNameWanted
    meetingNameWanted = meetingNameWanted + "-"+ inputURL[-5:]
    # get meeting id from url https://regex101.com/r/UjqGeo/3
    matchesURL = re.search(r"/?(\d+\.\d+)/.*?([0-9a-f]{40}-\d{13})/?",
                           inputURL,
                           re.IGNORECASE)
    if matchesURL and len(matchesURL.groups()) == 2:
        bbbVersion = matchesURL.group(1)
        meetingId = matchesURL.group(2)
        logger.info(f"Detected bbb version:\t{bbbVersion}")
        logger.info(f"Detected meeting id:\t{meetingId}")

        bbbInfo["detectedBBBversion"] = bbbVersion
        bbbInfo["meetingId"] = meetingId
    else:
        logger.error("Meeting ID could not be found in the url.")
        exit(1)
    # Construct the base URL for downloading files
    baseURL = "{}://{}/presentation/{}/".format(urlparse(inputURL).scheme,
                                                BBB_SERVER,
                                                meetingId)
    logger.debug("Base url: {}".format(baseURL))

    bbbInfo["baseURL"] = baseURL
    # Construct the folder path for the downloaded meeting files
    if meetingNameWanted:
        folderPath = os.path.join(
            SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER, meetingNameWanted)
    else:
        folderPath = os.path.join(
            SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER, meetingId)
    logger.debug("Folder path: {}".format(folderPath))
    # Check if the download is complete based on the existence of the DOWNLOADED_FULLY_FILENAME file
    if os.path.isfile(os.path.join(folderPath, DOWNLOADED_FULLY_FILENAME)):
        folder_exist = True
        combine_boolean = None
    else:
        folder_exist = False
         # Initialize downloadCompleted flag and start download time in bbbInfo
        bbbInfo["downloadCompleted"] = False

        foldersToCreate = [os.path.join(folderPath, x) for x in [
            "", "video", "deskshare", "presentation"]]
        # Create necessary folders for the downloaded files
        for i in foldersToCreate:
            createFolder(i)

        bbbInfo["downloadStartTime"] = time.time()
        saveBBBmetadata(folderPath, bbbInfo)

        # Download files and update bbbInfo and combine_boolean
        bbbInfo,combine_boolean = downloadFiles(baseURL, folderPath, bbbInfo)

        # Update download end time and set downloadCompleted flag to True    
        bbbInfo["downloadEndTime"] = time.time()
        bbbInfo["downloadCompleted"] = True
        saveBBBmetadata(folderPath, bbbInfo)

        # Copy contents of the "player3" folder to the downloaded meeting folder
        copyFolderContents(os.path.join(SCRIPT_DIR, "player3"), folderPath)
        bbbInfo["copiedBBBplaybackVersion"] = CURRENT_BBB_PLAYBACK_VERSION
        saveBBBmetadata(folderPath, bbbInfo)
        # Create a DOWNLOADED_FULLY_FILENAME file to mark a successful download
        with open(os.path.join(folderPath, DOWNLOADED_FULLY_FILENAME), 'w') as fp:
            pass

        bbbInfo["allDone"] = True
        saveBBBmetadata(folderPath, bbbInfo)


    return combine_boolean,os.path.basename(folderPath),folder_exist

def saveBBBmetadata(folderPath, bbbInfo):
    with open(os.path.join(folderPath, BBB_METADATA_FILENAME), 'w') as bjf:
        json.dump(bbbInfo, bjf)

def format_time(start_time):
    timestamp_ms = start_time

    # Convert milliseconds to seconds
    timestamp_sec = timestamp_ms / 1000

    # Convert timestamp to datetime object
    datetime_obj = datetime.utcfromtimestamp(timestamp_sec)

    # Format the datetime as a string
    formatted_datetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime

def send_email(to_email,room_name,download_link,smtp_server = SMTP_SERVER, smtp_port= SMTP_PORT):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = "Dirección de descarga de la grabación " + room_name
    time = str(format_time(int(get_metadata_components('start_time',"metadata.xml"))))
    message = f"Your meeting {room_name} of the {time} is ready for download in the following link {download_link}"
    msg.attach(MIMEText(message, 'plain'))
    # Establish a connection to the SMTP server
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.connect(smtp_server, smtp_port)
        # Use TLS for secure connection
        server.starttls()

        # Log in to the email account
        server.login(SENDER_EMAIL,SENDER_PASSWORD)

        # Send the email
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    print(f"Email sent successfully to {to_email}")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def verify_token(token: str = Depends(oauth2_scheme)):
    # Define an HTTPException to handle authentication failure
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the JWT using the provided token, secret key, and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Return the decoded payload if successful
        return payload
    except JWTError:
        # Raise the credentials_exception if JWT decoding fails
        raise credentials_exception

@app.get("/")
async def hello(current_user:dict = Depends(verify_token)):
    return "Hello"
@app.get("/video/{url:path}:{meeting_name}/{correo}")
async def main(url,meeting_name,correo,current_user:dict = Depends(verify_token)):
    combine_boolean,folder_name,folder_exists = downloadScript(url,meeting_name)
    # Check if the folder for the downloaded meeting exists
    if folder_exists == True:
        pass
    else:
        try:   
            combine(folder_name,combine_boolean)
        except:
            # If an exception occurs, remove the downloaded meeting folder and try combining again
            shutil.rmtree(os.path.join(SCRIPT_DIR, DOWNLOADED_MEETINGS_FOLDER,meeting_name+"-"+ url[-5:]))
            combine(folder_name,combine_boolean)
    download_link = DOWNLOAD_SERVER +"/" + meeting_name +"-"+ url[-5:] + "/" + meeting_name +"-"+url[-5:] +".zip"
    send_email(correo,meeting_name,download_link,SMTP_SERVER,SMTP_PORT)
