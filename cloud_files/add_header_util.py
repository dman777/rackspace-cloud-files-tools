##Add Headers V1
##darin.hensley@rackspace.com

import os 
import sys
import multiprocessing
import requests
import pyrax

def auth():
    username =  raw_input("Please enter your username: ")
    api = raw_input("Please enter your API key: ")
    token = raw_input("Please paste your token: ")

    pyrax.set_setting("identity_type", "rackspace")
    try:
        pyrax.set_credentials(username, api) 
    except:
        print "Bad name or password!"
        sys.exit()
 
    cf = pyrax.connect_to_cloudfiles(region="ORD")    
    return token, cf

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
    print "The header and value to be added is> " + header + ":" + value

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
    #any(x is not None for x in list)
    if any(results):
	print "\nThese URLS failed: "
	for i in results:
	    print i
    else:
	print "No failures!"

def verify_headers(url):
    element = []
        results = requests.head(url, headers=header_token)
	if results.status_code == 200:
	    compare = set(headers.items()) & set(results.headers.items())
	    if len(compare) == 0:
		element.append(url)
		for key, value in results.headers.items():
		     line = key + ": " + value
		     element.append(line)
	        return element
	else:
	    print "Error! Could not verify the url: " + url
    
if __name__ == '__main__':
    link="https://storage101.ord1.clouddrive.com/v1/MossoCloudFS_2cea874d-6a69-44f0-84a5-f27fb040806b/"
    results = []
    error_list = []
    token, cf = auth()
    url_list = container(cf, link)
    get_headers(token)

    value = raw_input("Proceed? Enter [Y] for yes: ")
    if value == "Y":
        pool = multiprocessing.Pool(processes=8)
        results = pool.map(do_it, url_list)
        pool.close()
        pool.join()

	print "\nChecking for URL's that were unsuccessfull..."
	#error_check(results)

	value = raw_input("\nSafety Check - Verify all objects have the header? [Y] ")
	if value == "Y":
	    pool = multiprocessing.Pool(processes=8)
            results = pool.map(verify_headers, url_list)
	    pool.close()
	    pool.join()


    else:
        print "Operation Failed!"

   # value = raw_input("\nWould you like to list all objects and headers? Enter [Y] for yes: ")
   # if value =="Y":
    #    print_headers(url_list)

