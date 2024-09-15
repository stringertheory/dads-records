#!/bin/sh
python get_album_image_info.py "$@" &&
rsync -cvzr records/ norbert:/var/www/files/records/ &&
python add_to_discogs.py "$@"
