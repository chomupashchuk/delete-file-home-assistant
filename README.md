# Delete files in Home Assistant
Delete file service for Home Assistant. For example delete snapshots.

## WARNINGS
- **All files are case sensitive.**
- **Custom component is run from Home Assistant and has access from same python runtime environment. It means no access outside of Home Assistant visibility (for example Hassio paths or folders).**
- **Home Assistant runs custom components not as `root` and thus permissions towards files and folders must be checked manually as component cannot change to the user with higher privilidges.**
- **Integration should delete data only within specified parameters so removal of unwanted files is users responsibility (correct specification of names).**

## Integration installation
In `/config` folder create `custom_components` folder and load source files folder `delete` in it. In 'configuration.yaml' include:
```
delete:
```
Order of actions:
- Copy data to `custom_components`;
- Restart Home Assistant to find the component;
- Include data in `configuration.yaml`;
- Restart Home Asistant to see new services.

## Services
### Service: delete.file
`delete.file` is used to delete a file.

#### attributes:
- `file` is used to indicate file path. it is a mandatory attribute.
- `no_warn` indicates if warnings are generated (default is `false` meaning warnings are included in the log).

#### Example
Delete file `photo.png` in folder `/config/image_snapshot`:
```
service: delete.file
data:
  file: '/config/image_snapshot/photo.png'
```

### Service: delete.files_in_folder
`delete.files_in_folder` is used to delete files within the folder, where files shall be deleted if they are older than specified period of time in seconds (default is 24 hours).

#### attributes:
- `folder` is used to indicate folder path. it is a mandatory attribute.
- `time` is used to indicate how old files must be  in seconds in order to be deleted. Default is 24 hours (86400 seconds). It is an optional attribute.
- `only_extensions` is list of extensions of files that are allowed to be deleted. Cannot be used together with `except_extensions`. Note: extension names must match exactly. It is an optional attribute.
- `except_extensions` is list of extensions of files that are not allowed to be deleted. Cannot be used together with `only_extensions`. Note: extension names must match exactly. It is an optional attribute.
- `except_files` is list of files that are not allowed to be deleted. Note: file names and extensions must match exactly, they are case sensitive. It is an optional attribute.
- `scan_subfolders` Indicates if subfolders to be scanned (default is `false`). It is an optional attribute.
- `remove_subfolders` Indicates if empty subfolders to be deleted (default is `false`). It is an optional attribute.
- `size` Indicates maximum folder size to be kept in Megabytes (value 0 disables this functionality). After checking last modification time additional check is made towards folder size. If it exceeds the specified value, then files are deleted even if specified time has not been exceeded. Files are deleted starting from the oldest file until the condition is met. It is an optional attribute.
- `no_warn` indicates if warnings are generated (default is `false` meaning warnings are included in the log).

#### Example 1
Delete files older than a week in folder `/config/image_snapshot/`:
```
service: delete.files_in_folder
data:
  folder: '/config/image_snapshot/'
  time: 604800
```

#### Example 2
Delete files older than 24 hours with only extensions `png` and `jpg` (note that they must match exactly) in folder `/config/image_snapshot/`:
```
service: delete.files_in_folder
data:
  folder: '/config/image_snapshot/'
  only_extensions:
    - '.png'
    - '.jpg'
```

#### Example 3
Delete files older than 1 hour except extensions `zip` and `yaml` (note that they must match exactly) in folder `/config/image_snapshot/`:
```
service: delete.files_in_folder
data:
  folder: '/config/image_snapshot/'
  time: 3600
  except_extensions:
    - '.zip'
    - '.yaml'
```

#### Example 4
Delete files (even if creates less than a second ago) including files in subfolders (empty subfolders shall also be removed) except `important.txt` and `important.db` files (nothe that names must match exactly and it is case sensitive) when scanning folder `/config/test`:
```
service: delete.files_in_folder
data:
  folder: "/config/test"
  time: 0
  scan_subfolders: true
  remove_subfolders: true
  except_files:
    - 'important.txt'
    - 'important.db'
```

#### Example 5
Delete files (even if creates less than a second ago) including files in subfolders (empty subfolders shall also be removed) except `important.txt` and `important.db` files (nothe that names must match exactly and it is case sensitive) when scanning folder `/config/test`, folder size must be kept not higher than 100Mb:
```
service: delete.files_in_folder
data:
  folder: "/config/test"
  time: 0
  scan_subfolders: true
  remove_subfolders: true
  except_files:
    - 'important.txt'
    - 'important.db'
  size: 100
```

#### Example 6
Delete files (even if creates less than a second ago) including files in subfolders (empty subfolders shall also be removed) except `important.txt` and `important.db` files (nothe that names must match exactly and it is case sensitive) when scanning folder `/config/test`, folder size must be kept not higher than 100Mb, no warnings generated in the log for removed files:
```
service: delete.files_in_folder
data:
  folder: "/config/test"
  time: 0
  scan_subfolders: true
  remove_subfolders: true
  except_files:
    - 'important.txt'
    - 'important.db'
  size: 100
  no_warn: true
```