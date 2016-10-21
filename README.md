# munkiroller
A script that creates Munki manifests. You must the script on your wsgi server.



    http://127.0.0.1:8000/test&apikey=secret_a&formfactor=desktop&hostname=bigblue
     
will result in the following Munki manifest:

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
    
    
## Installation

## Usage
You can use it in a script in your worklow, i.e:

    #!/bin/bash
	certshort=$(scutil --get ComputerName)
	modelshort=$(sysctl -n hw.model)

	if [[ $modelshort == MacBook* ]]; then
  	  curl -s -X GET "http://munkiroller.dn/test&apikey=secret_a&hostname=$certshort&formfactor=laptop" &> /dev/null
	else
      curl -s -X GET "http://munkiroller.dn/test&apikey=secret_a&hostname=$certshort&formfactor=desktop" &> /dev/null
	fi
