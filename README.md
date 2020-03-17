# Delete files in Home Assistant
Delete file service for home Assistant. For example delete snapshots.


## Integration installation
In `/config` folder create `custom_components` folder and load source files folder `delete` in it. In 'configuration.yaml' include:
```
delete:
```

## Services
### Service: delete.file
`delete.file` is used to delete a file.

#### attributes:
- `file` is used to indicate file path. it is a mandatory attribute.

#### Example
```
service: delete.file
data:
  file: '/config/image_snapshot/photo.png'
```

### Service: delete.files_in_folder
`delete.files_in_folder` is used to delete a files within the folder, where files are older than specified period of time in seconds (default is 1 hour).

#### attributes:
- `folder` is used to indicate folder path. it is a mandatory attribute.
- `time` is used to indicate how old files must be to be deleted in seconds. Default is 1 hour (3600 seconds). It is an optional attribute.

#### Example
```
service: delete.files_in_folder
data:
  folder: '/config/image_snapshot/'
  time: 86400
```
