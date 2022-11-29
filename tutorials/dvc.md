## DVC
### Initialize DVC
Throughout this tutorial, it is assumed you are already inside a repository that you want to use DVC to track, log and son on.

Structure of this repo:
```bash
.
├── dataset
│   └── dvc-storage  # our `remote storage` where tracked data is hosted and versioned
├── docs
├── mlruns
├── niklib
├── niklib.egg-info
├── ...
└── raw-dataset     # our original place of the data that need to be tracked
```

About the `raw-dataset`: It could *also* host files that you need to have but not tracked such as csv or original dataset that is not pickled yet. For instance, let's say you have 500 images and never plan to add anything it. But you want to try different preprocessing steps that each would take loads of time. Here, you can have all the images, but only track the pickled images of original dataset and all other preprocessed instances of it.

Here is an example:
1. You have a directory of 100 directories of multiple files hosted in `raw-dataset/raw`, e.g.
```
raw-dataset/raw/0/0.jpg
raw-dataset/raw/0/0.pdf
raw-dataset/raw/1/1.jpg
raw-dataset/raw/1/1.pdf
...
raw-dataset/raw/99/99.jpg
raw-dataset/raw/99/99.pdf
```
2. You now pickle all these data into a single file again hosted in `raw-dataset`, e.g. `raw-dataset/all.pkl`
3. You track the `raw-dataset/all.pkl` file
4. DVC does the versioning and you will the copy of file from step 2 (or 3) in `dataset/dvc-storage/ID/ANOTHER_ID`. `ANOTHER_ID` is your file for that particular version.

#### Initialize DVC Repo
If you are not importing an already defined DVC project, i.e. if you are initializing this current project as a DVC, you need to only run the following once per project:

```bash
dvc init
```

#### Commit Initialized DVC Meta Files
After running previous command, DVC creates new meta files for ignoring some data and defining the project structure. These files need to be tracked via your version control as they are required for importing a DVC project. (otherwise DVC won't figure out what to track and where the remote storage is)

```bash
git add .
git commit -m 'dvc init'
```

#### Configure the Remote Storage (S3, Gdrive, local, etc)
Here, you need to configure a remote storage where the actual data of files you want to track will be hosted. For instance, let's say you have a one big `pickle` file as your data. Of course the whole point of DVC is that so you no longer track these huge files via git (or manually!). By defining a *remote storage*, every time you track a data file, it will be copied to remote storage you defined with some versioning. Simply put, give a path that your copies of data will be hosted.

*Remark1: You can use cloud storages such as S3, also local file system as a remote storage too.*
*Remark2: Since the plan here is for demonstration, I use a local file system for remote storage.*

```bash
dvc remote add -d dvc-remote dataset/remote-storage
```

#### Commit Remote Storage Configuring
After running the previous command, a config file will be generated which has info about the configured remote storage. You must commit these file too so when you are importing the project, you can retrieve any particular version of data you desire.

```bash
git commit .dvc/config -m 'configure remote storage'
```

### Start Tracking

#### Create the Source Directory For Data Tracking
Create a directory that you want to track data from (where you pickled):
```bash
mkdir raw-dataset
```

#### Track Files via DVC
For the sake of demonstration, let's assume we have `data.pkl` located in `raw-dataset`.

Now, we can add files to DVC, just like adding files to git. By doing this for file `[file_name.extension]`, DVC generates `[file_name.extension].dvc` which contains info about the `md5`, size, and the path where we wanted to track.

For instance, if we run `dvc add raw-dataset/data.pkl` for `raw-dataset/data.pkl`, DVC generates `raw-dataset/data.pkl.dvc` file which contains the following info:
```
outs:
- md5: f86263278a04b25ec5fbec8cfec04423
  size: 370226
  path: data.pkl
```

Furthermore, it updates `raw-dataset/.gitignore` file to ignore `data.pkl` which makes sense as we don't want to commit into git for data change directly, and only DVC change for a data should be tracked.

#### Track DVC Generated Meta Files via Git
After each time we add a file to DVC, a new `[your_file].dvc` will be generated and `.gitignore` will be updated with the path of `[your_file]`. For example mentioned above following changes will happen:
1. Creates `raw-dataset/data.pkl.dvc`
2. Updates `raw-dataset/.gitignore`


Now, add both files to git:

```bash
git add raw-dataset/.gitignore raw-dataset/data.pkl.dvc
git commit -m 'data: track'
```

#### Easy Retrieval via Git Tags
Although you can load these data via different methods, but I think the best way is to just tag particular commits of data (or all commits of data) and version them so you have better understanding of data changes. Most of the time, we want the latest data, so instead of naming, use semantic versioning.

```bash
git tag -a 'v0.0.0.1' -m 'sample data'
```

#### Push to Remote Storage
So far, data only exists on our local folder i.e. `raw-dataset`. So to push it to remote storage we defined previously, we `push` it with DVC:

```bash
dvc push
```

By doing this, now we can see a copy of `raw-dataset/data.pkl` in the remote storage (e.g. our local remote storage; `dataset/remote-storage`) with a different name that DVC decided. You can see the tracked data in remote storage:
```bash
ls -lR dataset/remote-storage
```

#### Cleaning Local Instance of Tracked Data
We might have multiple tracked files that we no longer need them in our local directory. For instance, multiple huge files that we tracked, now only want the largest/latest file. For that, we can simply delete the file from our local directory, since we can retrieve it from remote storage whenever we want. For example, now that `data.pkl` is in the remote storage, we no longer need it and we can remove it.

```bash
rm -rf raw-dataset/data.pkl
```

*WARNING: don not remove `*.dvc` files or you will lose the link*


#### Cleaning the Cache
When we load a tracked data via DVC, DVC will cache it to prevent large file downloads. So, if you no longer want cached data for any reason, you can clean the cache:
```bash
rm -rf .dvc/cache
```

### Retrieving Data
We can retrieve data based on the revision, tag, latest and other methods. Simply, we can pull this via DVC:
```bash
dvc pull
```

### Remarks
In case you need to delete a tag (i.e. update an already existing tag by first deleting it):
```
git tag -d your_tag_name 
git push --delete origin tag your_tag_name
```
