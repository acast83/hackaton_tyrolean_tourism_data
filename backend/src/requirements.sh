pip install --upgrade pip

#LINUX
pip install pycurl --global-option="--with-openssl"

#MAC
#PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L$(brew --prefix openssl)/lib" CPPFLAGS="-I$(brew --prefix openssl)/include"  pip install pycurl --no-cache-dir


cat requirements.txt  | awk '{print "pip install " $0}' | bash

