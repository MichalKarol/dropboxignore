# dropboxignore
Python implementation of Dropbox equivalent of .gitignore: .dropboxignore.
At the beginning tool will exclude using Selective Sync in Dropbox all directories matching rules stored in .dropboxignore. Later it will monitor the Dropbox's directory using inotify and exclude them before Dropbox sync them.

![Azure DevOps builds](https://img.shields.io/azure-devops/build/michalpkarol/dropboxignore/1.svg?style=flat-square)
![Azure DevOps tests (compact)](https://img.shields.io/azure-devops/tests/michalpkarol/dropboxignore/1.svg?compact_message&style=flat-square)
![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/michalpkarol/dropboxignore/1.svg?style=flat-square)

## Usage
1) Create .dropboxignore file
2) Run `dropboxignore $PATH_TO_DROPBOX_DIRECTORY`
