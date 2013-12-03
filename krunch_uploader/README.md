Krunch-Uploader
===============
Python 2.7.*

Module required: requests, dateutil

Version 1.5 - Cloud Files Bulk Uploader with luxury and concurrency. Enter name, api key, mount point and it will do the rest.

#Directions:
Have a single mount point with all the containers and files you would like to upload. 
For each directory under that mount point, a container will be created in your cloud account.
If the container already exists in your cloud account, no problem. Container will not be over written.
Krunch Uploader will upload all your files per each directory/container to the relative container in the cloud account.

#Features:
 * menu driven for ease.
 * md5 sum check sum verification for each upload to ensure data integrity. 
 * custom value for concurrent uploads
 * debug, info, and error logging
 * each upload will try 5 times before giving up
 * automatic token renewal
 * utf-8 check in filenames
 * 5GB file limit size check
 * Python multi-threading is used instead of multiprocessing. This allows for full optimization of this I/O bound utlity. In addition, a smaller memory foot print. 
