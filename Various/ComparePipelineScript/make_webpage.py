import glob
import shutil
import os

outputdir = "webpage"

os.makedirs(outputdir, exist_ok=True)

webpage = """<!DOCTYPE html>
<head>
<title>COLIBRE Birth Pressure Distribution</title>
</head>
<body>
<h1>Birth Pressure Distribution for various COLIBRE runs</h1>"""

img_template = """<div style="float: left; width: 600px;">
<p>{name}</p>
<p><img width="500px" src="{img_url}" /></p>
</div>"""

files = sorted(glob.glob("*.png"))

for file in files:
    name = file.rstrip(".png")
    webpage += img_template.format(name=name, img_url=file)
    shutil.copyfile(file, f"{outputdir}/{file}")

webpage += "</body>"
with open(f"{outputdir}/index.html", "w") as handle:
    handle.write(webpage)
