## Bootstrapping project for the development

### requirements:
 - linux or macOS
 - python 3.10+
 - postgresql 14
 - npm / nodejs 


### steps:

 - checkout complete code from repo
 - follow steps for each part of project (backend / webapp / mobile) written in this file

#### Backend

 - using python 3.10 create virtual environment

```
cd backend
python3.10 -m venv .venv
    source .venv/bin/activate
```

 - update pip, install wheel and depend on platform install pycurl library with support for openssl

```
pip install --upgrade pip
pip install wheel
```
 - on LINUX:
```
pip install pycurl --global-option="--with-openssl"
```
 - on mac OS (ONLY)
```
PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L$(brew --prefix openssl)/lib" CPPFLAGS="-I$(brew --prefix openssl)/include"  pip install pycurl --no-cache-dir
```
and then install all from requirement.txt 

```
cd src
pip install -r requirements.txt
```

### Running integration tests

```commandline
cd tests_integration        # (backend/src/tests_integration)
PYTHONPATH=.. pytest .
```