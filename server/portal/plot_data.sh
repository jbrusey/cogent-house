#!/bin/bash

DIR=/home/ross/pulp/
FILES=`ls ${DIR}/*gnu*.csv`
NGINX=/var/www/pulp/
LINES=8064 # 1 month of data
PLOTDIR=/home/ross/pulp/portal

# for each node_x_gnu.csv: 
for FN in ${FILES}; do
    Rscript ${PLOTDIR}/plot.R ${FN}
    mv *.png ${NGINX}
done
