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

2. run `./run.sh records/101` to do image recognition, make and
   publish website, and update catalog on discogs.

### Notes

discogs username: `tomstringer`

This will not necessarily get the correct release in discogs for every
album. After everything is there, we could look at how variable the
value is for different releases for each album, and then use that to
make a short list of albums to check more thoroughly to see if it's
worth $$$.

With label and catalog # info:

First try searching for releases including all fields, take "best" match.
If no matches, then remove the catalog number, take the "best" match.
If no matches, then remove the label, take "best" match.

"Best" match can start as first match. But it would probably be better
to define a similarity metric based on matching to the different
fields (and then give ties to US releases).

Also good to keep in mind that the Discogs value estimate is [probably
high](https://www.reddit.com/r/vinyl/comments/bfxbmc/how_accurate_is_discogs_estimated_collection_value/). Seems
like the "median" value is probably a decent estimate of what a record
in VG+ quality would sell for. Probably a little bit high, because
Discogs only looks at the past sales, not how recent they are (so the
median might be based on sales from many years ago and nobody has
bought one in a long time).
