
brew install libmemcached

pip uninstall pycurl
pip install pycurl --global-option="--with-openssl"



pip install plotly
pip install cufflinks



------------------
https://github.com/algoo/preview-generator

apt-get install zlib1g-dev libjpeg-dev python3-pythonmagick inkscape xvfb
poppler-utils libfile-mimeinfo-perl
qpdf libimage-exiftool-perl ufraw-batch ffmpeg

pip install preview-generator

mac os :  brew install freetype imagemagick


----------------------
imgkit

sudo apt-get install wkhtmltopdf
brew install wkhtmltopdf

------
No module named ipykernel_launcher
ipykernel_launcher


# DOCKER 
 docker build -t netcadlabs/nbviewer .
 
 docker run --rm -p 5000:5000 netcadlabs/nbviewer
 
 docker run -v ./data/:/srv/nbviewer/data/ -p 5000:5000 netcadlabs/nbviewer
 