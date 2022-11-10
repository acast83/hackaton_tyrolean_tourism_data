pip install --upgrade pip

PYCURL_SSL_LIBRARY=openssl \
    LDFLAGS="-L$(brew --prefix openssl)/lib" \
    CPPFLAGS="-I$(brew --prefix openssl)/include" \
    pip install pycurl --no-cache-dir

cat requirements.txt  | awk '{print "pip install " $0}' | bash
