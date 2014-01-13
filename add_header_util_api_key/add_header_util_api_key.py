##Add Headers V1.5
##darin.hensley@rackspace.com

import os 
import sys
import getpass
import json
import multiprocessing
import requests
import pyrax

def auth():
    url = "https://identity.api.rackspacecloud.com/v2.0/tokens"
    username =  raw_input("Please enter your username: ")
    apikey = raw_input("Please enter your API Key: ")

    jsonreq =  {"auth": {"RAX-KSKEY:apiKeyCredentials": {
		  "username": username,
		  "apiKey": apikey }}}

    auth_headers = {'content-type': 'application/json'}
    pyrax.set_setting("identity_type", "rackspace")
    try:
	r = requests.post(url, data=json.dumps(jsonreq), headers=auth_headers)
	jsonresp = json.loads(r.text)
	token = str(jsonresp['access']['token']['id'])
	tenant = str(jsonresp['access']['token']['tenant']['id'])
	pyrax.auth_with_token(token, tenant)

    except:
        print "Bad name or password!"
        sys.exit()
 
    return token, jsonresp

def get_link(jsonresp):
    foo = jsonresp["access"]["serviceCatalog"]
    for i in foo:
	for value in i.values():
	    if value == "cloudFiles":
	        bar = i
    
    regions = [ 
	{ str(bar["endpoints"][0]["region"]) : str(bar["endpoints"][0]["publicURL"]) },
	{ str(bar["endpoints"][1]["region"]) : str(bar["endpoints"][1]["publicURL"]) },
	{ str(bar["endpoints"][2]["region"]) : str(bar["endpoints"][2]["publicURL"]) },
	{ str(bar["endpoints"][3]["region"]) : str(bar["endpoints"][3]["publicURL"])}]

    sys.stdout.write("\x1b[2J\x1b[H")
    print "Regions/URLs:"
    for i, item in enumerate(regions):
        for value in item.values():
	    j=str(i+1)
	    print "%s) %s" % (j, value)

    value = raw_input("Please enter choice: ")
    value = int(value)-1
    while True:
	try:
	    link = regions[value].values()[0]+"/"
	    region = regions[value].keys()[0]
	    break
	except IndexError:
	    "Wrong value!"
    cf = pyrax.connect_to_cloudfiles(region=region)    
    return cf, link

def container(cf, link):
    new_list = [] 
    url_list = [] 
    
    #sys.stdout.write("\x1b[2J\x1b[H")
    value = raw_input("\nPlease enter container name: ")
    try:    
        value = cf.get_container(value)
    except:
	print link
	print cf.list_containers()
        print "No Container Found!"
        sys.exit()
    
    print "Getting objects!..."
    objects = value.get_objects(full_listing=True)
    print "Got objects...Processing objects..."
    for i in objects:
        go = link + value.name + "/" + i.name 
        url_list.append(go)
    
    print "These are the objects that will get the header: "
    for i in url_list:
        print "-----------------------------------"
        print i
   
    return url_list


def get_headers(token):
    header = raw_input("\nEnter header only(exclude colon)>")
    value = raw_input("Please enter value of the header>")

    header = header.lower()
    value = value.lower()

    global headers
    global header_token

    headers = {
         "X-Auth-Token": token,
         header: value }

    header_token = { "X-Auth-Token": token }

    print "-------------------------------------------"
    print "The header and value to be added is> " + header + ": " + value

def do_it(url):
    print "Adding header to: \n" + url
    n = requests.post(url, headers=headers)
    if  not n.status_code == 202:
	return url

def print_headers(url_list):
    for i in url_list:
        print "*****************************************"
        print i
        n = requests.head(i, headers=header_token)
	print n.status_code
	if n.status_code == 200:
	    for key, value in n.headers.items():
		print key + ": " + value
	else:
	    print "TOKEN DID NOT AUTHENTICATE!"
	    sys.exit()

def error_check(results):
    if any(results):
	print "\nThese URLS failed: "
	for i in results:
	    print i
    else:
	print "No failures!"

def verify_headers(url):
        results = requests.head(url, headers=header_token)
	if results.status_code == 200:
	    compare = set(headers.items()) & set(results.headers.items())
	    if len(compare) == 0:
		print "\nERROR! Missing header in:"
		print url
		for key, value in results.headers.items():
		     print key + ": " + value
	else:
	    print "Error! Could not verify the url: " + url
    
if __name__ == '__main__':
    sys.stdout.write("\x1b[2J\x1b[H")
    print ("Add Header To ALL Your Cloud Files\n"
           "     In A Container! Ver. 1.5\n")
    
    #link="https://storage101.ord1.clouddrive.com/v1/MossoCloudFS_2cea874d-6a69-44f0-84a5-f27fb040806b/"
    results = []
    error_list = []
    token, jsonrep = auth()
    cf, link = get_link(jsonrep)
    url_list = container(cf, link)
    get_headers(token)

    value = raw_input("Proceed? Enter [Y/y] for yes: ").upper()
    if value == "Y":
        pool = multiprocessing.Pool(processes=8)
        results = pool.map(do_it, url_list)
        pool.close()
        pool.join()

	#print "\nChecking for URL's that were unsuccessfull..."
	#error_check(results)

	value = raw_input("\nSafety Check - Verify all objects have the header? [Y/y] ")
	value = value.upper()
	if value == "Y":
	    pool = multiprocessing.Pool(processes=8)
            pool.map(verify_headers, url_list)
	    pool.close()
	    pool.join()
	    print "Done..."


    else:
        print "Operation Failed!"

   # value = raw_input("\nWould you like to list all objects and headers? Enter [Y] for yes: ")
   # if value =="Y":
    #    print_headers(url_list)


