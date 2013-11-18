import time
import requests
import logging

logger = logging.getLogger("krunch")

def create_containers(cloud_container_list, file_container_list, 
        authenticate, cloud_url):
    auth_header = { "X-Auth-Token" : authenticate.token }
    
    combined_containerlist = cloud_container_list + file_container_list
    temp_containerlist = list(set(combined_containerlist))
    count = len(temp_containerlist) - len(cloud_container_list)
    if (count >=1):
        msg = "Found " + str(count) + " container(s) to add!"
        logger.info("%s", msg)
        for file_container in file_container_list:
            if file_container in cloud_container_list:
                pass
            else:
                url = cloud_url + file_container
                for i in range(5):
                    try:
                        r = requests.put(url, headers=auth_header)
                        if r.status_code == 201:
                            msg =  ('Container \"'+ file_container + '"'
                                   + " created and added successfully!")
                            logger.info("%s", msg)
                            break
                        elif r.status_code == 401:
                            msg =  ('Token invalid for Container \"'+ file_container + '"'
                                   + " creation. Renewing Token...")
                            logger.error("%s", msg)
                            authenticate.getToken()
                            auth_header = { "X-Auth-Token" : authenticate.token }
                            time.sleep(2)
                            continue
                        else: 
                            if i == 4:
                                msg =  ('Failure for Container \"'+ file_container + '"'
                                       + " creation. This was the 5th and final try.")
                                logger.error("%s", msg)
                            continue
                    except requests.exceptions.RequestException:
                         if i == 4: 
                            msg =  ('Failure for Container \"'+ file_container + '"'
                                   + " creation. This was the 5th and final try.")
                            logger.error("%s", msg)
                         time.sleep(2)
                         return
    else:
        msg = "All containers exist, none need to be added."
        logger.info(msg)




