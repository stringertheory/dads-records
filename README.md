# Dad's Records

### Setup

TODO, Add steps for:

- setting up python environment

- adding open AI API Key

- adding Discogs API Key


TODO: make sure that the Open API isn't called too much it gets
expensive (right now need to manually move images out of the `vinyls`
folder)

### Steps

0. make a numbered batch directory to store images for the batch

1. run `mogrify -path records/101/ -resize 1024 ~/Downloads/101./*` to
 move batch of images and into the correct directory and resize (with
 correct batch number and download folder, this is for 101)

2. run `get_album_image_info.py records/101` to make spreadsheet with
   artist/album names

3. run `add_to_discogs.py records/101` to add to "BeepBopBoop" folder
   in discogs and label with the batch number

### Notes

discogs username: `tomstringer`

This will not necessarily get the correct release in discogs for every
album. After everything is there, we could look at how variable the
value is for different releases for each album, and then use that to
make a short list of albums to check more thoroughly to see if it's
worth $$$.

