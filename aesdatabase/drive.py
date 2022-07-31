from .header import *


class DriveSetup:
    def __init__(self, add_attachment: bool = False, add_backup: bool = False):
        self.isAttachment = add_attachment
        self.isBackup = add_backup
        self.isCreated = False

        # Database directory
        self.__databaseFolderName = None
        self.__databaseFileName = None
        self.__databaseExtension = None
        self.databaseSignature = None
        self.databaseDir = None
        self.databasePath = None
        self.database_update(
            main='', folder='database', file='database', extension='db', signature=b'AESDatabase'
        )

        # Temp directory
        self.__tempFolderName = None
        self.tempDir = None
        self.temp_update(
            main='', folder='temp'
        )

        # Attachments directory
        self.__attachmentFolderName = None
        self.attachmentDir = None
        self.attachment_update(
            main=self.databaseDir, folder='attachments'
        )

        # Backup directory
        self.__backupFolderName = None
        self.__backupFileName = None
        self.__backupExtension = None
        self.backupSignature = None
        self.backupDir = None
        self.backupPath = None
        self.backup_update(
            main='', folder='backup', file='database', extension='backup', signature=b'AESDatabase'
        )

    def database_update(
            self, main: str = None, folder: str = None, file: str = None,
            extension: str = None, signature: bytes = None
    ):
        if main is None and self.databaseDir:
            main = os.path.dirname(self.databaseDir)
        if folder:
            self.__databaseFolderName = folder
        if file:
            self.__databaseFileName = file
        if extension:
            self.__databaseExtension = extension
        if signature:
            self.databaseSignature = signature

        previous_dir = self.databaseDir
        self.databaseDir = os.path.join(main, self.__databaseFolderName)
        self.databasePath = os.path.join(
            self.databaseDir, '%s.%s' % (self.__databaseFileName, self.__databaseExtension)
        )

        try:
            if previous_dir == os.path.dirname(self.attachmentDir):
                self.attachment_update(main=self.databaseDir)
        except AttributeError:
            return

    def temp_update(self, main: str = None, folder: str = None):
        if main is None and self.tempDir:
            main = os.path.dirname(self.tempDir)
        if folder:
            self.__tempFolderName = folder

        self.tempDir = os.path.join(main, self.__tempFolderName)

    def attachment_update(self, main: str = None, folder: str = None):
        if main is None and self.attachmentDir:
            main = os.path.dirname(self.attachmentDir)
        if folder:
            self.__attachmentFolderName = folder

        self.attachmentDir = os.path.join(main, self.__attachmentFolderName)

    def backup_update(
            self, main: str = None, folder: str = None, file: str = None,
            extension: str = None, signature: bytes = None
    ):
        if main is None and self.backupDir:
            main = os.path.dirname(self.backupDir)
        if folder:
            self.__backupFolderName = folder
        if file:
            self.__backupFileName = file
        if extension:
            self.__backupExtension = extension
        if signature:
            self.backupSignature = signature

        self.backupDir = os.path.join(main, self.__backupFolderName)
        self.backupPath = os.path.join(
            self.backupDir, '%s.%s' % (self.__backupFileName, self.__backupExtension)
        )

    def create(self) -> list:
        """
        Create all directories are configured
        :exception PermissionError
        """

        result = []

        os.makedirs(self.databaseDir, exist_ok=True)
        result.append(self.databaseDir)

        os.makedirs(self.tempDir, exist_ok=True)
        result.append(self.tempDir)

        if self.isAttachment:
            os.makedirs(self.attachmentDir, exist_ok=True)
            result.append(self.attachmentDir)

        if self.isBackup:
            os.makedirs(self.backupDir, exist_ok=True)
            result.append(self.backupDir)

        self.isCreated = True
        return result

    def delete(
            self, database: bool = True, temp: bool = True, attachment: bool = True, backup: bool = True
    ) -> list:
        """
        Delete all directories are configured
        :exception PermissionError
        """

        result = []

        if database and os.path.exists(self.databaseDir):
            self.__remove_dir(self.databaseDir)
            result.append(self.databaseDir)

        if temp and os.path.exists(self.tempDir):
            self.__remove_dir(self.tempDir)
            result.append(self.tempDir)

        if attachment and self.isAttachment and os.path.exists(self.attachmentDir):
            self.__remove_dir(self.attachmentDir)
            result.append(self.attachmentDir)

        if backup and self.isBackup and os.path.exists(self.backupDir):
            self.__remove_dir(self.backupDir)
            result.append(self.backupDir)

        self.isCreated = False
        return result

    @staticmethod
    def __remove_dir(path: str):
        try:
            shutil.rmtree(path)
        except PermissionError:
            raise
        except OSError:
            pass
