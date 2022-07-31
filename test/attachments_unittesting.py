from aesdatabase import *
import unittest


drive = DriveSetup(add_attachment=True)
drive.create()

password = '123456789'  # Set None for test without encryption
db = DatabaseEngine(drive, password=password)

name = 'test'
file_name = 'test.txt'
file_name_output = 'test.txt'
if password:
    file_name_output = aescrypto.utility.add_extension(file_name_output)

debugging = True


def function_name(text: str):
    print(f"[ + ] Start for: {text}")


class MyTestCase(unittest.TestCase):
    def test1_import_attachment(self):
        function_name('import_attachment')

        # Task
        if not os.path.exists(file_name):
            with open(file_name, 'w') as file:
                file.write('hello world!')

        exist_before = db.exists_attachment(name, file_name)
        result = db.import_attachment(name, file_name)
        exist_after = db.exists_attachment(name, file_name)

        # Debugging
        if debugging:
            print(f"""
            exist_before: {exist_before}
            result: {result}
            exist_after: {exist_after}
            """)

        # Test
        self.assertFalse(exist_before)
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(exist_after)

    def test2_export_attachment(self):
        function_name('export_attachment')

        # Task
        exist_before = db.exists_attachment(name, file_name)
        result = db.export_attachment(name, file_name, ignore_file_exists=True)
        exist_after = os.path.exists(file_name)

        # Debugging
        if debugging:
            print(f"""
            exist_before: {exist_before}
            result: {result}
            exist_after: {exist_after}
            """)

        # Test
        self.assertTrue(exist_before)
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))
        self.assertTrue(exist_after)

    def test3_select_attachments(self):
        function_name('select_attachments')

        # Task
        case1 = {}
        case2 = {'name': name}
        case3 = {'name': name, 'file_name': file_name_output}
        case4 = {'file_name': file_name_output}
        case5 = {'name': 'other'}
        case6 = {'file_name': 'other'}

        for case in (case1, case2, case3, case4, case5, case6):
            files = []

            for file in db.select_attachments(**case):
                files.append(file)

            # Debugging
            if debugging:
                print(f"""
                arguments: {case}
                files: {files}
                """)

            # Test
            if case in (case5, case6):
                self.assertAlmostEqual(len(files), 0)
            else:
                self.assertGreater(len(files), 0)

    def test4_remove_attachment(self):
        function_name('remove_attachment')

        # Task
        exist_before = db.exists_attachment(name, file_name)
        result = db.remove_attachment(name, file_name)
        exist_after = db.exists_attachment(name, file_name)

        # Debugging
        if debugging:
            print(f"""
            exist_before: {exist_before}
            result: {result}
            exist_after: {exist_after}
            """)

        # Test
        self.assertTrue(exist_before)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)
        self.assertFalse(exist_after)

    def test5_exists_attachment(self):
        function_name('exists_attachment')

        # Task
        result = db.exists_attachment(name, file_name)

        # Debugging
        if debugging:
            print(f"""
            result: {result}
            """)

        # Test
        self.assertIsInstance(result, bool)
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
