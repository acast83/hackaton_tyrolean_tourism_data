pip install --upgrade pip

pip install pycurl --global-option="--with-openssl"

cat requirements.txt  | awk '{print "pip install " $0}' | bash

