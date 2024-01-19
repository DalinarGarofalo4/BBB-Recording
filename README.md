# BBB Recording API

## Description
This is a repo that allows you to download and combine a meeting recorded using Big Blue Button 
and it sends you an email containing a download link for your meeting and a link with the option 
for upload recording into user drive.

Using pySmartDL, the script downloads the necessary files (deskshare and webcam) for then combining them into one.
Using ffmpeg under the hood of moviepy, the script combines the downloaded files.
The file is then compressed into a zip and is sent as an email to the user with the download link in it.
To get the JWT check out the file JWT.txt

This repo is inspired by the repo [andrazznidar/bbb-player](https://github.com/andrazznidar/bbb-player). 
This repo retains some blocks of code originating from the repo [andrazznidar/bbb-player](https://github.com/andrazznidar/bbb-player)

```
Python 3.10.5
pip 23.3.2
GNU Make 3.81
```

## Deploy
1. Clone repository:
    ```
    git clone https://github.com/DalinarGarofalo4/BBB-Recording.git
    ```

2. Install dependencies:
    ```
    cd BBB-Recording
    make .PHONY
    make install
    make generate-keys
    python JWT_generator.py
    ```

## Tests
* For run lint:
  ```
  make lint
  ```

* For run tox:
  ```
  make tox
  ```
