# dropboxignore
Python implementation of Dropbox equivalent of .gitignore: .dropboxignore.
At the beginning tool will exclude using Selective Sync in Dropbox all directories matching rules stored in .dropboxignore. Later it will monitor the Dropbox's directory using inotify and exclude them before Dropbox sync them.

![Azure DevOps builds](https://img.shields.io/azure-devops/build/michalpkarol/dropboxignore/1.svg?style=flat-square)
![Azure DevOps tests (compact)](https://img.shields.io/azure-devops/tests/michalpkarol/dropboxignore/1.svg?compact_message&style=flat-square)
![Azure DevOps coverage](https://img.shields.io/azure-devops/coverage/michalpkarol/dropboxignore/1.svg?style=flat-square)

## Usage
`$PATH_TO_DROPBOX_DIRECTORY` is Dropbox root directory
1) Create .dropboxignore file in `$PATH_TO_DROPBOX_DIRECTORY`
2) Run `dropboxignore $PATH_TO_DROPBOX_DIRECTORY` and do not close your termial (needed for directory monitoring)

## Example .dropboxignore
Example .dropboxignore for Dropbox directory inside which JS/TS and Python projects are developed.
```
node_modules
__pycache__
.mypy_cache
.pytest_cache
.history
htmlcov
```
---
.dropboxignore works for whole Dropbox root directory, but it could be used for more selective exclusion eg.
```
some_project/node_modules
```
where only in `some_project` directory `node_modules` is excluded and for the rest of the projects `node_modules` are synced.
