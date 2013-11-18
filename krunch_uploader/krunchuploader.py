##Krunch Uploader Ver. #1.0
##darin.hensley@rackspace.com

import logging 
import os 
import sys
sys.path.insert(0, './modules')
import json
import time
import signal
from os.path import expanduser
from auth import Authenticate
from getinfo import get_containers, get_files, get_link
from container_util import create_containers
from filter import MyFilter
from upload_actions import do_the_uploads, retry

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    sys.exit(0)


home = expanduser("~") + '/'

directory = home + "krunchuploader_logs"

if not os.path.exists(directory):
    os.makedirs(directory)

debug = directory + "/krunchuploader__debug_" + str(os.getpid()) + ".txt"
error = directory + "/krunchuploader__error_" + str(os.getpid()) + ".txt"
info = directory + "/krunchuploader__info_" + str(os.getpid()) + ".txt"

os.open(debug, os.O_CREAT | os.O_EXCL)
os.open(error, os.O_CREAT | os.O_EXCL)
os.open(info, os.O_CREAT | os.O_EXCL)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


logging.basicConfig(level=logging.DEBUG,
	format='%(asctime)s - %(levelname)s - %(message)s',
	filename=debug,
	filemode='w')

logger = logging.getLogger("krunch")

fh_error = logging.FileHandler(error)
fh_error.setLevel(logging.ERROR)
fh_error.setFormatter(formatter)
fh_error.addFilter(MyFilter(logging.ERROR))

fh_info = logging.FileHandler(info)
fh_info.setLevel(logging.INFO)
fh_info.setFormatter(formatter)
fh_info.addFilter(MyFilter(logging.INFO))

std_out_error = logging.StreamHandler()
std_out_error.setLevel(logging.ERROR)
std_out_error.addFilter(MyFilter(logging.ERROR))
std_out_info = logging.StreamHandler()
std_out_info.addFilter(MyFilter(logging.INFO))
std_out_info.setLevel(logging.INFO)

logger.addHandler(fh_error)
logger.addHandler(fh_info)
logger.addHandler(std_out_error)
logger.addHandler(std_out_info)



def main():
    title = """\
	 _   __                      _             
	| | / /                     | |            
	| |/ / _ __ _   _ _ __   ___| |__          
	|    \| '__| | | | '_ \ / __| '_ \         
	| |\  \ |  | |_| | | | | (__| | | |        
	\_| \_/_|   \__,_|_| |_|\___|_|_|_|        
	| | | |     | |               | |          
	| | | |_ __ | | ___   __ _  __| | ___ _ __ 
	| | | | '_ \| |/ _ \ / _` |/ _` |/ _ \ '__|
	| |_| | |_) | | (_) | (_| | (_| |  __/ |   
	 \___/| .__/|_|\___/ \__,_|\__,_|\___|_|   
	      | |                                  
	      |_|  
               Version 1.0 TronTeam
"""
    sys.stdout.write("\x1b[2J\x1b[H")
    print title
 
    username = raw_input("Please enter your username: ")
    apikey = raw_input("Please enter your apikey: ")

    authenticate = Authenticate(username, apikey)
    cloud_url = get_link(authenticate.jsonresp)
    #per 1 million files the list will take
    #approx 300MB of memory.

    file_container_list, file_list = get_files(authenticate, cloud_url)
    cloud_container_list = get_containers(authenticate, cloud_url)
    create_containers(cloud_container_list,
	    file_container_list, authenticate, cloud_url)

    return file_list


class FileQuantity(object):
    """Keeps track of files that have been uploaded and how many are left"""
    def __init__(self, file_quantity):
	self.quantity = file_quantity
	self.total = file_quantity

    def deduct(self):
	self.quantity = self.quantity - 1

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    retry_list = []
    file_list = main()
    file_quantity = FileQuantity(len(file_list))
    do_the_uploads(file_list, file_quantity, retry_list)
    while True:
	cont = retry(file_list, file_quantity, retry_list, error)
	if not cont:
	    break


    print "\nLogs and their locations are:"
    print error
    print info
    print debug



