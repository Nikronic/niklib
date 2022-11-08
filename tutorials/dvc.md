## DVC
### DVC Usage

```bash

# init the DVC
dvc init # only first time

# commit DVC changes so git tracks them
git commit -m "dvc init"

# configure a remote storage (S3, Gdrive, local, etc)
# i put processed pickled dataframes here, since decoded files, csv, etc are not important and only having the pickled dataframe is enough
dvc remote add -d dvc-remote dataset/remote-storage

# commit configuring remote storage to git
git commit .dvc/config -m "configure remote storage"

### now we are ready to start track our data

# create a directory that you want to track data from (where you pickle)
mkdir raw-dataset
# move something to it, pickle, etc. Let's call it data.pkl

# add file you want to track to dvc. By doing this, it generates data.pkl.dvc file which contains links to data.pkl. Also, it updated raw-dataset/.gitignore file to ignore data.pkl
dvc add raw-dataset/data.pkl

# add both files to git: raw-dataset/.gitignore and raw-dataset/data.pkl.dvc
git add raw-dataset/.gitignore raw-dataset/data.pkl.dvc
git commit -m "data: track"

# to ease the access to the data, we create a tag
git tag -a "v0.0.0.1" -m "sample data"

# data so far only exists on our local folder i.e. raw-dataset. So to push it to remote storage, we push with DVC
dvc push

# now we can see a copy of raw-dataset/data.pkl in dataset/remote-storage with different name
ls -lR dataset/remote-storage

# now that data.pkl is in remote storage, we no longer need it, so remove it
# WARNING: dont remove *.dvc files or you will lose the link
rm -rf raw-dataset/data.pkl

# we can clean the cache of data too
rm -rf .dvc/cache

# now if want to work with this data again, we pull via DVC
dvc pull

```

In case you need to delete a tag (i.e. update an already existing tag by first deleting it):
```bash
git tag -d your_tag_name 
git push --delete origin tag your_tag_name
```
