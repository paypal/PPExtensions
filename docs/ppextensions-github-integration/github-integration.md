# Github Integration

# About
A Jupyter extension to integrate notebooks with Github. This extension simplifies version controlling, sharing and resolving merge conflicts of notebooks.

### (Method 1) Local Environment Setup

#### Local Setup

**Register private Github token:** Go to Github website, click `Settings` --> `Developer settings` --> `Personal access tokens` --> `Generate new token`, copy the new token and export that as an environment variable.
~~~
export githubtoken=<Your token here>
~~~

Notice if the token is replaced, all local repo will be "unlinked" to remote. 

**Enable git merge driver:**
To show conflict in notebook, a nbmerge driver from nbdime module should be enabled as well.
~~~
git-nbmergedriver config --enable --global
~~~

#### Install Github Extension

~~~
pip install ppextensions
jupyter nbextension install github --user --py
jupyter nbextension enable github --user --py
jupyter serverextension enable github --py --user
~~~

Alternatively, if you want to install all extensions from [ppextensions](https://ppextensions.io)
~~~
cd PPExtensions
bash build/extension_init.sh
~~~

This command will automatically install all github and scheduler extensions.

**(Optional) Initialize a Github repo for notebooks**

If you want to create a separate repo for sharing the notebooks, go to github website and create a new repo, be sure to create a README as well in order to initialize the master branch, otherwise when you pull the repo, there will be a "master branch not found" error. 

**(Optional) Use an existing Github repo for sharing the notebooks**
Either push to or pull from that repo will create a local workspace in Private Sharing folder in the notebook startup folder.

### (Method 2) Use Docker
~~~
docker run --name=demo --link=mysql:db -i -t -e githubtoken=<your github token here> -e githubname=<github user> -e githubemail=<github email> -p 8080:8080 -p 8888:8888 qwjlegend/ppextensions

~~~

Then go to localhost:8888/?token=<jupyter notebook token printed in the command line> to start using notebook with ppextensions.

### Push to Github

**Push a single notebook to Github:** Select the notebook to be pushed, click `Sharing` --> `Push to Github`, select the repo, branch and type commit messages in the popup, and click on `Push`.

When you push a notebook outside the `Sharing` folder, the notebook will be moved under `Sharing/<Repo Name>/<Notebook Name>` path, and the be pushed to Github.
When you push a notebook inside the `Sharing` folder, only the "Linked" repo in the dropdown will display in the dropdown.

In the following situation, the push command will fail: 

***There is a conflict:*** Updates were rejected because the remote contains work that you do not have locally. Please do git pull and fix the possible conflicts before pushing again!

**Push a folder to Github:** Select the folder, click on `Sharing` --> `Push to Github`, select the repo, branch and type commit messages in the popup, and click on `Push`. 

When you push a folder outside the `Sharing` folder, that entire folder will be moved under "Sharing/<Repo Name>" path, and then be pushed to Github.


### Pull from Github

Click on `Sharing` --> `Pull from Github`, copy the Github repo url and paste that in the input area, then click on `Pull`. 

In the following situations, the pull command will fail:

***During a merge:*** You have not conclued your merge(MERGE_HEAD exists). Please, commit your changes before you can merge.

***There is a conflict:*** Auto-mergeing **.ipynb. CONFLICT(content): Merge conflict in **.ipynb. Automatic merge failed; fix conflicts and then commit the result.

***Untracked notebook in local:*** Your local changes to the following files would be overwritten by merge: xx.ipynb. Please, commit your changes or stash them before you can merge. Aborting.

### Commit

Open up a notebook, click on the Github icon in the tool bar. There are two types of commit:

**Commit one notebook:** This option will be used in most cases. 

In the following situations, this command will fail:

***Worktree clean, nothing to commit***

***There are other untracked/uncommitted notebooks:*** Nothing committed but untracked files presented. 

**Commit all notebooks in the same folder:** Only use this option when you want to commit the deleted notebooks.


### Conflict Fix

When you pull from Github and you local commit is different from remote commit, a conflict will be generated, if the conflict cannot be automatically resolved, you can fix the conflicts by opening the notebook.

In the error message, the conflicting files will be displayed. 

Notice: The merge-driver is depending on nbdime module,  while it is working well in identifying "cell level" conflicts, it does not fully support "notebook level" merging. Therefore, it is not guaranteed that a "notebook level" conflict (such as a deleted cell/added cell) will be identified in 100 percent correctness. Before the improved nbdime module is released, we would recommend the user to keep the number of cells unchanged in a collaborative circumstance. 

To commit, first click on the Github icon in the notebook toolbar, choose either `Commit this notebook only` or `Commit all notebooks in this folder`, then click on `Commit`. 
