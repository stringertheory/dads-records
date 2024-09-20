#!/bin/sh
python get_album_image_info.py "$@" &&
python make_index.py &&
python make_batch_pages.py &&
rsync -cvzr records/ norbert:/var/www/files/records/
# python add_to_discogs.py "$@"
