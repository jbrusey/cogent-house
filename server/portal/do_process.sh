#!/bin/bash

# process data with the portal
PORTAL_PATH=/home/ross/pulp/

/usr/bin/python ${PORTAL_PATH}/portal/process-data.py -i ${PORTAL_PATH} -o ${PORTAL_PATH}
FILES=`ls ${PORTAL_PATH}/*gnu*.csv`
for FN in ${FILES}; do 
    /usr/bin/sort ${FN} > ${PORTAL_PATH}/.tmp
    /bin/mv ${PORTAL_PATH}/.tmp ${FN}
done
