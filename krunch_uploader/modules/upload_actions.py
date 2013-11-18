import Queue
import os
import hashlib
import requests
import time
import sys
import logging
from threading import Thread

logger = logging.getLogger("krunch")

def do_the_uploads(file_list, file_quantity, retry_list):
    """The uploading engine"""
    value = raw_input(
	    "\nPlease enter how many conncurent "
            "uploads you want at one time(example: 200)> ")
    value = int(value)
    logger.info('{} conncurent uploads will be used.'.format(value))

    confirm = raw_input(
	    "\nProceed to upload files? Enter [Y/y] for yes: ").upper()
    if confirm == "Y":
	sys.stdout.write("\x1b[2J\x1b[H")
	q = Queue.Queue()
	def worker():
	    while True:
		item = q.get()	
		upload_file(item, file_quantity, retry_list)
		q.task_done()

	for i in range(value):
	    t = Thread(target=worker)
	    t.setDaemon(True)
	    t.start()

	for item in file_list:
	    q.put(item)

	q.join()
	print "Finishing cleaning up process..",
	time.sleep(2) #Allowing the threads to cleanup
	print "done."

def retry(file_list, file_quantity, retry_list, error):
    copy_retry_list = []
    copy_retry_list = list(retry_list)
    #must delete elements of orignial retry_list
    #if retry_list=[] was used, the script would still
    #use the memory location of the old list. 
    del retry_list[:]

    while True:
	copy_retry_list_count = len(copy_retry_list)
	if copy_retry_list_count:
	    print (
		   "\nFile upload is complete. However, there"
		   "\nare {} files that failed and can be retried."
		   "\nThese can be verified in {}".format(copy_retry_list_count, error))

	    confirm = raw_input(
		    "Would you like to retry?"
		    "\nEnter [N/n] to exit or [Y/y] for retry: ").upper()

	    if confirm == "Y":
		msg = ("\nRetrying failed upload files..")
		logger.info(msg)
		do_the_uploads(copy_retry_list, file_quantity, retry_list)
		return True
	else:
	    msg = ("\nCongratulations! No failed uploads were found!!!")
	    logger.info(msg)
	    return False

def md5sum(absolute_path_filename):
    """Calculates the checksum before uploading. When given to cloud files, Cloud will calculate
       the checksum and do a compare also. Krunch uploader will do a extra compare afterwards
       as a double check since it takes very little overhead to do this."""
    blocksize = 4000
    f = open(absolute_path_filename, 'rb')
    buf = f.read(blocksize)
    md5sum = hashlib.md5()
    while len(buf) > 0:
        md5sum.update(buf)
	buf = f.read(blocksize)
    return md5sum.hexdigest()

def upload_file(file_obj, file_quantity, retry_list):
    """Uploads a file. One file per it's own thread. No batch style. This way if one upload
       fails no others are effected."""
    absolute_path_filename, filename, dir_name, token, url = file_obj
    url = url + dir_name + '/' + filename

    src_md5 = md5sum(absolute_path_filename)

    if src_md5:
	pass
    else:
	msg = (
		'Filename \"{}\" is missing md5 checksum!'
		' This will not stop upload, but md5 check will not be checked!'.format(filename))
	logger.error(msg)

    header_collection = {
	    "X-Auth-Token": token,
	    "ETag": src_md5 }

    print "\nUploading " + absolute_path_filename
    for i in range(5):
	try:
	    with open(absolute_path_filename) as f:
		r = requests.put(url, data=f, headers=header_collection, timeout=1)
            if r.status_code == 201:
		if src_md5 == r.headers['etag']:
		    file_quantity.deduct()
		    msg = (
			'File \"{}\" successfully'
		        ' loaded with verified md5 \"{}\"'.format(filename, src_md5))
		    logger.info(msg)
		    msg = (
			'{} out of {} files left'.format(file_quantity.quantity, file_quantity.total))
		    logger.info(msg)
		    break
		else:
		    msg = (
			'File \"{}\" checksum verification failed with'
		        ' \"{}\". Retrying upload'.format(filename, src_md5))
		    logger.error(msg)
		    if i is not 4:
		        continue
		    else:
			msg = (
			    'File \"{}\" checksum verification failed with'
			    ' \"{}\". \nThis was the 5th and final try.'
			    ' File will be placed on the retry list'.format(filename, src_md5))
			logger.error(msg)
			retry_list.append(file_obj)

	    if r.status_code == 401:
		msg = ('Token has expired for upload \"{}\"'
			' Renewing token...'.format(filename))
		logger.error(msg)
		authenticate.getToken()
		auth_header = { "X-Auth-Token" : authenticate.token }
		continue
	    else: 
		msg = ('Http status code {} for file \"[]\". Retrying...'.format(filename, r.status_code))
		if i is not 4:
		    continue
		else:
		    msg = (
			'File \"{}\" failed with HTTP code'
			' \"{}\". \nThis was the 5th and final try.'
			' File will be placed on the retry list.'.format(filename, r.status_code))
		    logger.error(msg)
		    retry_list.append(file_obj)

        except requests.exceptions.RequestException:
	     if i == 4:
		 msg = ('Error! Could not do API call to \"{}\"'
			 ' This was the 5th and final try.'
			 ' File will be placed on the retry list.'.format(filename))
		 logger.error(msg)
		 retry_list.append(file_obj)
		 return
	     else:
		 msg = ('Error! Could not do API call to upload \"{}\". '
		        'This was the #{} attempt. Trying again...'.format(filename, i+1))
		 logger.error(msg)
	     time.sleep(1)

