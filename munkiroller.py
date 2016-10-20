# -*- coding: utf-8 -*-
"""This is the docstring for the munkiroller.py module.

Call this script with the correct parameters to get a Munki manifest created.

You can give `manifestname` and `formfactor` [laptop|desktop] in the calling string. Authentication is done by a
API value that is passed as `apikey`.

i.e http://127.0.0.1:8000/sub&apikey=secret_a&formfactor=desktop&hostname=bigblue

- Remember to set the APIkeys in the script before using the script outside your test environment.
- Remember to adjust the content of local_manifest_desktop / local_manifest_laptop to suit your environment.
"""

from urlparse import parse_qs
import plistlib
import os
import sys

def write_manifest(manifestname, formfactor):
    """This function writes a Munki manifest. Does not overwrite if the manifest already exists!

    Takes a manifestname and a formfactor.

    `manifestname`can be any string, `formfactor` needs to be 'desktop' or 'laptop'.

    The code below is an example of the result of writeManifest when `formfactor` is 'desktop'.

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>catalogs</key>
        <array>
            <string>production</string>
        </array>
        <key>included_manifests</key>
        <array>
            <string>prod_osx_desktop_uib</string>
        </array>
        <key>managed_installs</key>
        <array>
        </array>
        <key>managed_uninstalls</key>
        <array>
        </array>
        <key>managed_updates</key>
        <array>
        </array>
        <key>optional_installs</key>
        <array>
        </array>
        <key>user</key>
        <string>imagr</string>
    </dict>
    </plist>

    Parameters
    ----------
    manifestname : str
        Indicating the name of the manifest. This will be the name of the file when its written to disk.
    formfactor : str
        Indicating if the machine that the manifest belongs to is 'laptop' or 'desktop'. Other values are ignored.

    Returns
    -------
    None

    """
    manifest_path = '/usr/local/munkiroller_env/manifests/'
    manifest_path = 'manifests/'
    write_plist = False
    plist_exist = False

    if not os.access('manifests', os.W_OK):
        try:
            os.mkdir('manifests', 0700)
        except OSError as e:
            pass

    local_manifest_desktop = {
        'catalogs': ['production'],
        'included_manifests': ['prod_osx_desktop_uib'],
        'managed_installs': [],
        'managed_uninstalls': [],
        'optional_installs': [],
        'user': 'imagr',
    }

    local_manifest_laptop = {
        'catalogs': ['production'],
        'included_manifests': ['prod_osx_laptop_uib'],
        'managed_installs': [],
        'managed_uninstalls': [],
        'optional_installs': [],
        'user': 'imagr',
    }

    if formfactor == 'desktop':
        local_manifest = local_manifest_desktop
        write_plist = True
    elif formfactor == 'laptop':
        local_manifest = local_manifest_laptop
        write_plist = True

    if os.path.exists(str(manifest_path) + str(manifestname)):
        plist_exist = True
    else:
        plist_exist = False

    if write_plist and not plist_exist:
        plistlib.writePlist(local_manifest, str(manifest_path) + str(manifestname))


def application(environ, start_response):
    """ This is the entrypoint of this wsgi application.

    Params
    ------
    environ : list of key/value pairs
        Information about the caller environment. https://www.python.org/dev/peps/pep-3333/#environ-variables
    start_response : callable
        Unknown. https://www.python.org/dev/peps/pep-3333/#the-start-response-callable

    Return
    ------


    """
    http_data = "Intentionally left blank"
    http_status = "200 OK"

    manifest_name = "no_manifest_name"
    formfactor_name = "no_formfactor_name"

    keys = { 'key_a': 'secret_a', 'key_b': 'secret_b', 'key_c': 'secret_c', 'key_d': 'secret_d', }

    authenticated_by_apikey = False

    provided_hostname = False
    provided_formfactor = False

    try:
        if environ['PATH_INFO'] == "/":
            http_data = "Intentionally left blank."
        else:
            params = parse_qs(environ['PATH_INFO'])

            if 'apikey' in params:
                apikey_value = params['apikey'][0]
                if apikey_value in keys.values():
                    authenticated_by_apikey = True
                else:
                    authenticated_by_apikey = False
            if 'hostname' in params:
                manifest_name = params['hostname'][0]
                provided_hostname = True
            if 'formfactor' in params:
                formfactor_name = params['formfactor'][0]
                provided_formfactor = True

            if authenticated_by_apikey:
                http_data = "Authenticated by APIkey"
                http_status = "200 OK"
                if provided_hostname and provided_formfactor:
                    write_manifest(manifest_name, formfactor_name)
                    http_data = http_data + ", hostname and formfactor provided."
                elif not provided_hostname and not provided_formfactor:
                    http_data = http_data + ", but missing hostname and formfactor.\nNothing written to disk!"
                elif provided_hostname:
                    http_data = http_data + ", but missing formfactor.\nNothing written to disk!"
                elif provided_formfactor:
                    http_data = http_data + ", but missing hostname.\nNothing written to disk!"
                else:
                    http_data = http_data + ", but something went wrong.\nNothing written to disk!"

            else:
                http_data = "Not authenticated by APIkey\nNothing written to disk!"
                http_status = "403 Forbidden"

        start_response(http_status, [
            ("Content-Type", "text/plain"),
            ("Content-Length", str(len(http_data)))
        ])
        return iter([http_data])


    except Exception:
        http_status = "500 Internal Server Error"
        response_headers = [("content-type", "text/plain")]
        start_response(http_status, response_headers, sys.exc_info())
        return ["Exception: something wrong in munkiroller::application"]


# To test with Gunicorn
# $ cd /Users/username/development/github/munkiroller
# $ source activate munkiroller
# $ conda install gunicorn
# $ gunicorn --workers=1 munkiroller:application
# optionally, which will bind to all interfaces, and --max-requests will make your code "automatically reload on change"
# $ gunicorn munkiroller:app --bind 0.0.0.0:8000 --max-requests 1