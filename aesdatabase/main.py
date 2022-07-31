from .header import *
from .drive import DriveSetup
from . import error


class DatabaseEngine(object):
    def __init__(self, drive: DriveSetup, password: str = None):
        self.__drive = drive
        self.__password = password
        self.__columns = []
        self.__rows = []

        self.isEncrypted = False
        if password:
            self.isEncrypted = True

    def create_table(self, column_titles: list):
        """
        Create a table, EX: column_titles=['username', 'password']
        :exception error.TableCreationError
        """

        if self.__columns:
            raise error.TableCreationError("This database already has table created")

        for title in column_titles:
            if column_titles.count(title) > 1:
                raise error.TableCreationError(f"{title} title is duplicated")
            elif not isinstance(title, str):
                raise error.TableCreationError(f"{title} type expected str, but got {type(title)}")

        self.__columns = column_titles

    def insert(self, row_index: int = 0, **kwargs):
        """
        Insert a new row in the table
        :exception error.TableCreationError
        :exception error.TableTitleError
        :exception error.RowItemError
        """

        self.__table_creation_validator()
        row = []

        for column_index, title in enumerate(self.__columns):
            try:
                item = kwargs[title]
                row.append(item)
                self.__item_type_validator(column_index, item)

            except KeyError:
                raise error.TableTitleError(f"Please define {title} value")

        self.__rows.insert(row_index, row)

    def select(self, column_titles: list = None, **kwargs) -> typing.Tuple[int, dict]:
        """
        Select all rows and able to filter them
        :exception error.TableCreationError
        """

        self.__table_creation_validator()

        if not column_titles:
            column_titles = self.__columns

        for row_index, row in enumerate(self.__rows):
            row = {
                title: row[i] for i, title in enumerate(self.__columns) if title in column_titles
            }

            if kwargs and any(row[title] != item for title, item in kwargs.items()):
                continue

            yield row_index, row

    def edit(self, row_index: int, **kwargs):
        """
        Edit a row already inserted
        :exception error.TableCreationError
        :exception error.RowNotFoundError
        :exception error.RowItemError
        """

        self.__table_creation_validator()
        self.__row_index_validator(row_index)
        row = []

        for column_index, title in enumerate(self.__columns):
            try:
                item = kwargs[title]
                row.append(item)
                self.__item_type_validator(column_index, item)

            except KeyError:
                row.append(self.__rows[row_index][column_index])
                continue

        self.__rows[row_index] = row

    def remove_column(self, title: str):
        """
        Remove a column already defined
        :exception error.TableCreationError
        :exception error.TitleUndefinedError
        """

        self.__table_creation_validator()

        try:
            column_index = self.__columns.index(title)
        except ValueError:
            raise error.TitleUndefinedError(f"Title {title} is not defined")

        del self.__columns[column_index]

        for row in self.__rows:
            del row[column_index]

    def remove_row(self, row_index: int):
        """
        Remove a row already inserted
        :exception error.TableCreationError
        :exception error.RowNotFoundError
        """

        self.__table_creation_validator()
        self.__row_index_validator(row_index)

        del self.__rows[row_index]

    def clear(self):
        """Clear all rows"""

        self.__rows.clear()

    def count_column(self) -> int:
        """Get count of columns"""

        return len(self.__columns)

    def count_row(self) -> int:
        """Get count of rows"""

        return len(self.__rows)

    def import_attachment(self, name: str, path: str, ignore_file_exists: bool = False) -> str:
        """
        Import a file from drive to database attachments
        :exception error.AttachmentStatusError
        :exception FileNotFoundError
        :exception FileExistsError
        """

        self.__attachment_validator()
        directory = os.path.join(self.__drive.attachmentDir, name)
        os.makedirs(directory, exist_ok=True)

        if self.__password:
            cipher = aescrypto.AESCrypto(self.__password)
            _, output_path = cipher.encrypt_file(
                path, directory=directory, ignore_file_exists=ignore_file_exists
            )
        else:
            output_path = os.path.join(directory, os.path.basename(path))
            if not ignore_file_exists and os.path.exists(output_path):
                raise FileExistsError("File already exists")

            shutil.copy2(path, directory)

        return output_path

    def export_attachment(
            self, name: str, file_name: str, output_dir: str = None, ignore_file_exists: bool = False
    ) -> str:
        """
        Export a file from database attachments to drive ( by default = temp )
        :exception error.AttachmentStatusError
        :exception aescrypto.error.SignatureNotFoundError
        :exception aescrypto.error.WrongKeyError
        :exception FileNotFoundError
        :exception FileExistsError
        """

        self.__attachment_validator()
        directory = os.path.join(self.__drive.attachmentDir, name)
        path = os.path.join(directory, file_name)

        if not output_dir:
            output_dir = self.__drive.tempDir

        if self.__password:
            path = aescrypto.utility.add_extension(path)
            cipher = aescrypto.AESCrypto(self.__password)
            _, output_path = cipher.decrypt_file(
                path, directory=output_dir, ignore_file_exists=ignore_file_exists
            )
        else:
            output_path = os.path.join(output_dir, file_name)
            if not ignore_file_exists and os.path.exists(os.path.join(output_dir, os.path.basename(path))):
                raise FileExistsError("File already exists")

            shutil.copy2(path, output_dir)

        return output_path

    def select_attachments(self, name: str = None, file_name: str = None) -> str:
        """
        Select all attachments and able to filter them
        :exception error.AttachmentStatusError
        """

        self.__attachment_validator()

        for root, _, files in os.walk(self.__drive.attachmentDir):
            if name and name != os.path.basename(root):
                continue

            for file in files:
                if file_name and file_name != file:
                    continue

                yield os.path.join(root, file)

    def remove_attachment(self, name: str, file_name: str) -> bool:
        """
        Remove a file already attached in database
        :exception error.AttachmentStatusError
        """

        self.__attachment_validator()
        directory = os.path.join(self.__drive.attachmentDir, name)
        path = os.path.join(directory, file_name)
        valid = False

        if self.__password:
            path = aescrypto.utility.add_extension(path)

        try:
            os.remove(path)
            valid = True
            os.rmdir(directory)
        except (OSError, FileNotFoundError):
            # Ignore if the directory contains other files & file not exists
            pass

        return valid

    def exists_attachment(self, name: str, file_name: str) -> bool:
        """
        Check for a file in the database attachments
        :exception error.AttachmentStatusError
        """

        self.__attachment_validator()
        directory = os.path.join(self.__drive.attachmentDir, name)
        path = os.path.join(directory, file_name)

        if self.__password:
            path = aescrypto.utility.add_extension(path)

        return os.path.exists(path)

    def load_backup(
            self, path: str, row_indexes: list = None, attachment_names: list = None, password: str = None
    ):
        """
        Load all data from a backup file into database
        :exception error.TableCreationError
        :exception error.SignatureNotFoundError
        :exception error.BackupStatusError
        :exception aescrypto.error.SignatureNotFoundError
        :exception aescrypto.error.WrongKeyError
        :exception FileNotFoundError
        """

        self.__table_creation_validator()
        self.__backup_validator()

        if not password:
            password = self.__password

        if password:
            cipher = aescrypto.AESCrypto(password)
            _, path = cipher.decrypt_file(path, directory=self.__drive.tempDir, ignore_file_exists=True)

        with open(path, 'rb') as src_file:
            # Read signature
            signature = src_file.read(len(self.__drive.backupSignature))
            if signature != self.__drive.backupSignature:
                raise error.SignatureNotFoundError("Signature not found")

            # Read rows
            size = struct.unpack('<Q', src_file.read(struct.calcsize('Q')))[0]
            data = src_file.read(size)
            rows = pickle.loads(data)

            for index, row in enumerate(rows):
                if (row in self.__rows) or (isinstance(row_indexes, list) and index not in row_indexes):
                    continue

                self.insert(**{
                    title: row[i] for i, title in enumerate(self.__columns)
                })

            # Read attachment info
            size = struct.unpack('<Q', src_file.read(struct.calcsize('Q')))[0]
            data = src_file.read(size)
            attachments_info = pickle.loads(data)

            # Read attachment files
            for file_path, size in attachments_info.items():
                name = os.path.dirname(file_path)
                directory = os.path.join(self.__drive.attachmentDir, name)
                file_path = os.path.join(self.__drive.attachmentDir, file_path)
                exists = os.path.exists(file_path)

                def __reader(file_size: int) -> typing.AnyStr:
                    while True:
                        chunk_size = min(chunkSize, file_size)
                        if chunk_size == 0:
                            break

                        file_size -= chunk_size
                        yield src_file.read(chunk_size)

                if isinstance(attachment_names, list) and name not in attachment_names or (
                        exists and os.path.getsize(file_path) == size
                ):
                    for _ in __reader(size):
                        continue
                    continue
                elif exists:
                    file_name = '%s %s' % (time.ctime().replace(':', '-'), os.path.basename(file_path))
                    file_path = os.path.join(directory, file_name)

                os.makedirs(directory, exist_ok=True)

                with open(file_path, 'wb') as output_file:
                    for chunk in __reader(size):
                        output_file.write(chunk)

        if password:
            os.remove(path)

    def dump_backup(
            self, row_indexes: list = None, attachment_names: list = None,
            output_dir: str = None, password: str = None
    ) -> str:
        """
        Dump all data to save on the drive as backup
        :exception error.TableCreationError
        :exception error.BackupStatusError
        """

        self.__table_creation_validator()
        self.__backup_validator()

        # Rows collection
        rows = self.__rows
        if isinstance(row_indexes, list):
            rows = [self.__rows[i] for i in row_indexes]

        # Attachments collection
        attachments_info = {}
        if self.__drive.isAttachment:
            for name in os.listdir(self.__drive.attachmentDir):
                if isinstance(attachment_names, list) and name not in attachment_names:
                    continue

                directory = os.path.join(self.__drive.attachmentDir, name)
                for file_name in os.listdir(directory):
                    size = os.path.getsize(os.path.join(directory, file_name))
                    attachments_info.update({os.path.join(name, file_name): size})

        file_name = '%s %s' % (time.ctime().replace(':', '-'), os.path.basename(self.__drive.backupPath))
        path = os.path.join(self.__drive.tempDir, file_name)

        with open(path, 'wb') as output_file:
            # Write signature
            output_file.write(self.__drive.backupSignature)

            # Write rows
            data = pickle.dumps(rows)
            size = len(data)
            output_file.write(struct.pack('<Q', size))
            output_file.write(data)

            # Write attachment info
            data = pickle.dumps(attachments_info)
            size = len(data)
            output_file.write(struct.pack('<Q', size))
            output_file.write(data)

            # Write attachment files
            for file_path in attachments_info:
                with open(os.path.join(self.__drive.attachmentDir, file_path), 'rb') as src_file:
                    while True:
                        chunk = src_file.read(chunkSize)
                        chunk_size = len(chunk)
                        if chunk_size == 0:
                            break

                        output_file.write(chunk)

        if not output_dir:
            output_dir = self.__drive.backupDir

        if not password:
            password = self.__password

        if password:
            cipher = aescrypto.AESCrypto(password)
            _, output_path = cipher.encrypt_file(path, directory=output_dir)

        else:
            output_path = os.path.join(output_dir, file_name)
            shutil.copy2(path, output_dir)

        os.remove(path)

        return output_path

    def load(self) -> bool:
        """
        Load all data into memory
        :exception error.TableCreationError
        :exception error.SignatureNotFoundError
        :exception aescrypto.error.SignatureNotFoundError
        :exception aescrypto.error.WrongKeyError
        """

        if not self.__drive.isCreated:
            self.__drive.create()

        try:
            if self.__password:
                path = aescrypto.utility.add_extension(self.__drive.databasePath)
                cipher = aescrypto.AESCrypto(self.__password)
                _, data = cipher.load(path)

            else:
                with open(self.__drive.databasePath, 'rb') as file:
                    data = file.read()

        except FileNotFoundError:
            return False

        signature_length = len(self.__drive.databaseSignature)
        signature = data[:signature_length]
        if signature != self.__drive.databaseSignature:
            raise error.SignatureNotFoundError("Signature not found")

        data = data[signature_length:]
        data = pickle.loads(data)

        self.create_table(data.pop(-1))
        self.__rows = data

        return True

    def dump(self):
        """
        Dump all data to save on the drive
        :exception error.TableCreationError
        """

        self.__table_creation_validator()

        if not self.__drive.isCreated:
            self.__drive.create()

        data = self.__drive.databaseSignature

        self.__rows.append(self.__columns)
        data += pickle.dumps(self.__rows)
        self.__rows.pop(-1)

        if self.__password:
            cipher = aescrypto.AESCrypto(self.__password)
            cipher.dump(data, path=self.__drive.databasePath, ignore_file_exists=True)

        else:
            with open(self.__drive.databasePath, 'wb') as file:
                file.write(data)

    def __table_creation_validator(self):
        if not self.__columns:
            raise error.TableCreationError("Table not created yet")

    def __row_index_validator(self, row_index: int):
        try:
            self.__rows[row_index]
        except IndexError:
            raise error.RowNotFoundError(f"Row index {row_index} does not exist")

    def __item_type_validator(self, column_index: int, item: typing.Any):
        try:
            first_row = self.__rows[0]
        except IndexError:
            # No previous row to check last item type
            return

        item_type = type(item)
        expected_type = type(first_row[column_index])

        if item_type is not expected_type:
            title = self.__columns[column_index]
            raise error.RowItemError(f"{title} type expected {expected_type}, but got {item_type}")

    def __attachment_validator(self):
        if not self.__drive.isAttachment:
            raise error.AttachmentStatusError("Attachment option is disabled")

    def __backup_validator(self):
        if not self.__drive.isBackup:
            raise error.BackupStatusError("Backup option is disabled")
