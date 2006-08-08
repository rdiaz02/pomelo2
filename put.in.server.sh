#!/bin/bash
## Execute from prot03 in /http/pomelo2

rsync -av bzrs@ameiva:/Disk2/bzr-repositories/pomelo2/ /http/pomelo2
chgrp -R www-data *

