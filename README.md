# Delete files in Home Assistant
Delete file service for home Assistant. For example delete snapshots.


## Integration installation
In `/config` folder create `custom_components` folder and load source files folder `delete` in it. In 'configuration.yaml' include:
```
delete:
```

## Service
`delete.file` is used to delete a file

attribute `file` is used to indicate file and its location.
