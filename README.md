# BBB-Recording

This is a repo that allows you to download and combine a meeting recorded using Big Blue Button, and it sends you an email containing a download link for your meeting. This repo is heavily inspired by the repo [andrazznidar/bbb-player](https://github.com/andrazznidar/bbb-player).This repo retains some blocks of code originating from the repo [andrazznidar/bbb-player](https://github.com/andrazznidar/bbb-player)

## Download necessary files

Using pySmartDL, the script downloads the necessary files (deskshare and webcam) for then combining them into one.

## Combine

Using ffmpeg under the hood of moviepy, the script combines the downloaded files.

## Send Email

The file is then compressed into a zip and is sent as an email to the user with the download link in it.

## How to use


To use this repo, you need to have git and docker installed on your machine. Then, follow these steps:

- Clone this repo using `git clone https://github.com/DalinarGarofalo4/BBB-Recording.git`
- Change directory to the repo using `cd BBB-Recording`
- Build a docker image using `docker build -t bbb-recording .`
 Run a docker container using `docker run -p 5000:5000 -v /path/to/your/folder/myBBBmeetings:/app/ downloadedMeetings DalinarGarofalo4/BBB-Recording`
- Enter the meeting ID and your email address when prompted
- Wait for the script to finish and check your email for the download link
- Stop the container using `docker stop bbb-recording`

## Get JWT

To get the JWT check out the file JWT.txt