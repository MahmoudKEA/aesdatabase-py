from aesdatabase import *
import unittest


drive = DriveSetup(add_attachment=True, add_backup=True)
debugging = True


def function_name(text: str):
    print(f"[ + ] Start for: {text}")


class MyTestCase(unittest.TestCase):
    def test_create(self):
        function_name('create')

        # Task
        result: list = drive.create()

        # Debugging
        if debugging:
            print(f"""
            result: {result}
            isAttachment: {drive.isAttachment}
            isBackup: {drive.isBackup}
            databaseSignature: {drive.databaseSignature}
            databaseDir: {drive.databaseDir}
            databasePath: {drive.databasePath}
            tempDir: {drive.tempDir}
            attachmentDir: {drive.attachmentDir}
            backupSignature: {drive.backupSignature}
            backupDir: {drive.backupDir}
            backupPath: {drive.backupPath}
            """)

        # Test
        self.assertIsInstance(result, list)
        self.assertIsInstance(drive.databaseSignature, bytes)
        self.assertTrue(os.path.exists(drive.databaseDir))
        self.assertEqual(os.path.dirname(drive.databasePath), drive.databaseDir)
        self.assertTrue(os.path.exists(drive.tempDir))
        if drive.isAttachment:
            self.assertTrue(os.path.exists(drive.attachmentDir))
        if drive.isBackup:
            self.assertIsInstance(drive.backupSignature, bytes)
            self.assertTrue(os.path.exists(drive.backupDir))
            self.assertEqual(os.path.dirname(drive.backupPath), drive.backupDir)

    def test_delete(self):
        function_name('delete')

        # Task
        result: list = drive.delete()

        # Debugging
        if debugging:
            print(f"""
            result: {result}
            """)

        # Test
        self.assertIsInstance(result, list)
        self.assertFalse(os.path.exists(drive.databaseDir))
        self.assertFalse(os.path.exists(drive.tempDir))
        if drive.isAttachment:
            self.assertFalse(os.path.exists(drive.attachmentDir))
        if drive.isBackup:
            self.assertFalse(os.path.exists(drive.backupDir))


if __name__ == '__main__':
    unittest.main()
