##Add Headers V1.5
##darin.hensley@rackspace.com

import os 
import sys
import json
import multiprocessing
import requests
import pyrax

def auth():
    url = "https://identity.api.rackspacecloud.com/v2.0/tokens"
    username =  raw_input("Please enter your username: ")
    password = raw_input("Please enter your password: ")
    link_url = raw_input("\nPlease enter your Cloud Files url\n"
			  "Be sure to include a slash '/' at the end of the url!\n"
			  "(Example- https://storage101.ord1.clouddrive.com/v1/MossoCloudFS_2ced834d-7055-24f0-14a5-e23fb032806b/)\n> ")
    region = raw_input("Please ether ORD, DFW, IAD, or SYD for region: ")

    region = region.upper()

    jsonreq = ( {"auth": {"passwordCredentials": {
		  "username": username,
		  "password": password }}})
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
 
    cf = pyrax.connect_to_cloudfiles(region=region)    
    return token, cf, link_url

def container(cf, link):
    new_list = [] 
    url_list = [] 
    
    value = raw_input("Please enter container name: ")
    try:    
        value = cf.get_container(value)
    except:
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
    header = raw_input("\nEnter header only(exclude colon)>  ")
    value = raw_input("Please enter value of the header>  ")

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
    print "Add Header To Your Cloud Files! Ver. 1.5\n"
    
    #link="https://storage101.ord1.clouddrive.com/v1/MossoCloudFS_2cea874d-6a69-44f0-84a5-f27fb040806b/"
    results = []
    error_list = []
    token, cf, link = auth()
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


