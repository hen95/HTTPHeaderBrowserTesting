import requests
import json
import re


capabilitiesList = []

print('[+] Getting browser versions')
auth=('USERNAME', 'PASSWORD')
r = requests.get('https://api.browserstack.com/automate/browsers.json', auth=auth)
json_data = r.json()


# mobile

# android
capabilitiesList += [x for x in json_data if x['os'] == 'android' and 
        ('Samsung Galaxy S20' == x['device'] and x['os_version'] == '11.0') or
        ('Samsung Galaxy S20' == x['device'] and x['os_version'] == '10.0') or
        ('Samsung Galaxy S10' == x['device'] and x['os_version'] == '9.0')][-3:]
# iphone
capabilitiesList += [x for x in json_data if x['browser'] == 'iphone' and
        ('iPhone 11' == x['device'] and x['os_version'] == '14') or
        ('iPhone 11' == x['device'] and x['os_version'] == '13') or
        ('iPhone 8' == x['device'] and x['os_version'] == '12')][-3:]

# pc

# Chrome [-6:]
capabilitiesList += [x for x in json_data if x['os'] == 'Windows' and x['os_version'] == '10' and
        x['browser'] == 'chrome'][-3:]

# Firefox 81.0 - Firefox 86.0 beta Windows 10 [-6:]
capabilitiesList += [x for x in json_data if x['os'] == 'Windows' and x['os_version'] == '10' and
        x['browser'] == 'firefox'][-1:]

# Safari 11.1 High Sierra - Safari 14.0 Big Sur, Safari 13.1 click is bugged... [-3:]
capabilitiesList += [x for x in json_data if x['os'] == 'OS X' and x['browser'] == 'safari'][-1:]

# windows 10 IE 11
capabilitiesList += [x for x in json_data if x['os'] == 'Windows' and x['os_version'] == '10' and
        x['browser'] == 'ie'][-1:]

# windows 10 Edge 18 - beta [-11:]
capabilitiesList += [x for x in json_data if x['os'] == 'Windows' and x['os_version'] == '10' and
        x['browser'] == 'edge'][-1:]
capabilitiesList += [x for x in json_data if x['os'] == 'Windows' and x['os_version'] == '10' and
        x['browser'] == 'edge' and x['browser_version'] == '18.0']

print('[+] selected ', len(capabilitiesList), ' browsers.')

print(json.dumps(capabilitiesList, indent=2))

