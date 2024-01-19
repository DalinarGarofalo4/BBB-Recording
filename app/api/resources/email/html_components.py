def _get_fist_part():
    return """
            <!DOCTYPE html>
<html>

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Example</title>
</head>
<body style="font-family: 'Roboto', sans-serif; margin: 0; padding: 0; background-color: #FFFFFF; max-width: 640px;">
"""


def _get_end_part():
    return """
        <div></div>
    </div>
</body>

</html>
"""


def _get_header(title: str):
    title = title.replace("//", "<br>")
    return f"""
            <div style="height: 196px; background: linear-gradient(106.85deg, #009FA3 3.96%, #005B7F 96.25%);">
        <div style="text-align: center; position: relative; padding: 46px; margin: 0 auto;">
            <h2 class="title" style="font-weight: 500; font-size: 30px; color: #FFFFFF;">{title}</h2>
        </div>
    </div>
    <div style="height: auto; padding: 24px; Continued: 0;">"""


def record_ready_email(date_time, download_link, upload_link):
    body = _get_fist_part() + _get_header("Record ready for download // Grabación lista") + f"""
    <div style="height: auto; padding: 24px; Continued: 0;">
        <div style="height: auto; margin: 0 auto; padding: 32px 0;">
            <div style="height: auto; margin: 0 auto; text-align: center;">
                <p style="width: 100%; font-weight: 400; font-size: 14px; line-height: 150%; color: #000000;">
                    Su grabación está <a href = {download_link}>aquí</a>. <br>
                    Tambien tiene la opción de subirlo directo al drive de su usuario haciendo click
                    <a href = {upload_link}> aquí</a>. <br>
                </p> <br>
            </div>
        </div>""" + _get_end_part()
    return body
