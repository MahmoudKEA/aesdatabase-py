# AESDatabase Library
#### This library is designed to store database as encrypted with AES-256 algorithm
- The ability to add attachment files to the database
- The ability to import and export a backup of all data and attachments in one file
- Designed by: Mahmoud Khalid

## Requirements for Python 3
    pip install pycryptodome
    aescrypto: https://github.com/MahmoudKhalid/aescrypto

## Usage
### Build a driver that defines all paths and directories
```python
import aesdatabase

# Build the driver
drive = aesdatabase.DriveSetup(
    add_attachment=True,        # Enable attachments feature
    add_backup=True             # Enable backup feature
)

# Create directories
drive.create()

# Delete all directories or some dirs
drive.delete(database=True, temp=True, attachment=True, backup=True)

# Check test/drive_unittesting.py for more examples
# ...
```

### How to connect a driver with database engine and use it
```python
import aesdatabase

# Build the driver
drive = aesdatabase.DriveSetup()
drive.create()

# Connect with database engine, by default password=None for unencrypted
db = aesdatabase.DatabaseEngine(drive, password='123456789')

# Load database if it's already created before
db.load()

# Or create a table if this is the first time
db.create_table(['id', 'username', 'password'])

# Insert new row
db.insert(id=1001, username='user', password='123456')

# Save changes
db.dump()

# Check test/main_unittesting.py for more examples
# ...
```

### How to add attachment files
```python
import aesdatabase

# Build the driver
drive = aesdatabase.DriveSetup()
drive.create()

# Connect with database engine, set a password to encrypt the files attached
db = aesdatabase.DatabaseEngine(drive, password='123456789')


# Add a file into attachments database
attachment_path = db.import_attachment(name='attachmentName', path='file/path/image.jpg')
print(attachment_path)
# >>> database/attachments/attachmentName/image.jpg

# Export a file from attachments to your drive
output_path = db.export_attachment(name='attachmentName', file_name='image.jpg', output_dir='Desktop')
print(output_path)
# >>> Desktop/image.jpg

# Check test/attachments_unittesting.py for more examples
# ...
```

### How to make backup file
```python
import aesdatabase

# Build the driver
drive = aesdatabase.DriveSetup()
drive.create()

# Connect with database engine, set a password to encrypt the backup file
db = aesdatabase.DatabaseEngine(drive, password='123456789')


# Add a file into attachments database
backup_path = db.dump_backup(
    row_indexes=None,           # Backup some rows or set None for all
    attachment_names=None,      # Backup some attachments or set None for all
    output_dir='Desktop',       # By default export into temp folder
    password=None               # By default, it uses a master password or set a specific one
)
print(backup_path)
# >>> Desktop/database.backup.aes

# Export a file from attachments to your drive
db.load_backup(
    path='Desktop/database.backup.aes', # Select the backup file path
    row_indexes=None,                   # Import some rows or set None for all
    attachment_names=None,              # Import some attachments or set None for all
    password=None                       # By default, it uses a master password or set a specific one
)


# Check test/backup_unittesting.py for more examples
# ...
```

### Go to the test folder to check all examples
    python test/drive_unittesting.py
    python test/main_unittesting.py
    python test/attachments_unittesting.py
    python test/backup_unittesting.py
- If you haven't a virtual environment, please copy "aesdatabase" folder into test folder to run