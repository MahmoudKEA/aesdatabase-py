from aesdatabase import *
import unittest


drive = DriveSetup(add_attachment=True, add_backup=True)
drive.create()

password = '123456789'  # Set None for test without encryption
db = DatabaseEngine(drive, password=password)

# Create table and data insert
db.create_table(['id', 'username', 'password'])
for i in range(10):
    db.insert(id=i, username='user%s' % i, password='123')

debugging = True


def function_name(text: str):
    print(f"[ + ] Start for: {text}")


class MyTestCase(unittest.TestCase):
    outputPath = None

    def test1_dump_backup(self):
        function_name('dump_backup')

        # Task
        result = db.dump_backup()
        MyTestCase.outputPath = result

        # Debugging
        if debugging:
            print(f"""
            result: {result}
            """)

        # Test
        self.assertTrue(os.path.exists(result))

    def test2_load_backup(self):
        function_name('load_backup')

        # Task
        count_before = db.count_row()
        db.load_backup(MyTestCase.outputPath)
        count_after = db.count_row()

        # Debugging
        if debugging:
            print(f"""
            count_before: {count_before}
            count_after: {count_after}
            """)

        # Test
        self.assertAlmostEqual(count_before, 10)
        self.assertAlmostEqual(count_after, 10)

    @staticmethod
    def test3_select():
        function_name('select')

        # Task
        for index, row in db.select():

            # Debugging
            if debugging:
                print(f"""
                index: {index}
                row: {row}
                """)


if __name__ == '__main__':
    unittest.main()
