import aescrypto.utility
from aesdatabase import *
import unittest


drive = DriveSetup()
drive.create()

password = '123456789'  # Set None for test without encryption
db = DatabaseEngine(drive, password=password)
debugging = True


def function_name(text: str):
    print(f"[ + ] Start for: {text}")


class MyTestCase(unittest.TestCase):
    def test1_create_table(self):
        function_name('create_table')

        # Task
        case1 = {'column_titles': ['id', 'username', 'password', 'isActive', 'isActive']}   # Failed case
        case2 = {'column_titles': ['id', 'username', 'password', 'isActive', True]}   # Failed case
        case3 = {'column_titles': ['id', 'username', 'password', 'isActive']}
        case4 = {'column_titles': ['id', 'username', 'password', 'isActive']}   # Failed case

        for case in (case1, case2, case3, case4):
            issue = ''
            try:
                db.create_table(**case)
                success = True
            except error.TableCreationError as err:
                issue = err
                success = False

            # Debugging
            if debugging:
                print(f"""
                arguments: {case}
                success: {success}
                issue: {issue}
                """)

            # Test
            if case is case3:
                self.assertTrue(success)
            else:
                self.assertFalse(success)

    def test2_insert(self):
        function_name('insert')

        # Task
        case1 = {'id': 1, 'username': 'name'}   # Failed case
        case2 = {'id': 1, 'username': 'name', 'password': '123', 'isActive': True}
        case3 = {'id': 1, 'username': 'name', 'password': '123', 'isActive': 'True'}   # Failed case
        case4 = {'id': 2, 'username': 'name', 'password': '123', 'isActive': False}

        for case in (case1, case2, case3, case4):
            issue = ''

            try:
                db.insert(**case)
                success = True
            except (error.TableTitleError, error.RowItemError) as err:
                issue = err
                success = False

            # Debugging
            if debugging:
                print(f"""
                arguments: {case}
                success: {success}
                issue: {issue}
                """)

            # Test
            if case in (case2, case4):
                self.assertTrue(success)
            else:
                self.assertFalse(success)

    def test3_select(self):
        function_name('select')

        # Task
        case1 = {}
        case2 = {'column_titles': ['username']}
        case3 = {'column_titles': ['username', 'isActive'], 'username': 'name', 'isActive': True}
        case4 = {'username': 'name2'}

        for case in (case1, case2, case3, case4):
            rows = []

            for index, row in db.select(**case):
                rows.append(row)

            # Debugging
            if debugging:
                print(f"""
                arguments: {case}
                rows: {rows}
                """)

            # Test
            if case is case1:
                self.assertAlmostEqual(len(rows), db.count_row())
                self.assertAlmostEqual(len(rows[0]), db.count_column())
            elif case is case2:
                self.assertAlmostEqual(len(rows), db.count_row())
                self.assertAlmostEqual(len(rows[0]), len(case['column_titles']))
            elif case is case3:
                self.assertAlmostEqual(len(rows), 1)
                self.assertAlmostEqual(len(rows[0]), len(case['column_titles']))
                self.assertEqual(rows[0]['username'], case['username'])
                self.assertTrue(rows[0]['isActive'])
            elif case is case4:
                self.assertAlmostEqual(len(rows), 0)

    def test4_edit(self):
        function_name('edit')

        # Task
        case1 = {'username': 'name2', 'isActive': 'True'}   # Failed case
        case2 = {'username': 'name2', 'isActive': True}

        for case in (case1, case2):
            issue = ''
            row_before = None
            row_after = None

            for index, row_before in db.select(id=2):
                case['row_index'] = index

            try:
                db.edit(**case)
                success = True
                for index, row_after in db.select(id=2):
                    continue
            except error.RowItemError as err:
                issue = err
                success = False

            # Debugging
            if debugging:
                print(f"""
                arguments: {case}
                row_before: {row_before}
                row_after: {row_after}
                success: {success}
                issue: {issue}
                """)

            # Test
            self.assertEqual(row_before['username'], 'name')
            self.assertFalse(row_before['isActive'])
            if case is case2:
                self.assertTrue(success)
                self.assertEqual(row_after['username'], case['username'])
                self.assertTrue(row_after['isActive'])
            else:
                self.assertFalse(success)
                self.assertIsNone(row_after)

    def test5_remove_column(self):
        function_name('remove_column')

        # Task
        count_before = db.count_column()
        db.remove_column('isActive')
        count_after = db.count_column()

        count_row = 0
        for _, row in db.select():
            count_row += len(row)

        # Debugging
        if debugging:
            print(f"""
            count_before: {count_before}
            count_after: {count_after}
            count_row: {count_row / db.count_row()}
            """)

        # Test
        self.assertAlmostEqual(count_after, count_before - 1)
        self.assertAlmostEqual(count_row % count_after, 0)

    def test6_remove_row(self):
        function_name('remove_row')

        # Task
        index = None
        row_before = None
        row_after = None

        for index, row_before in db.select(id=2):
            break

        count_before = db.count_row()
        db.remove_row(index)
        count_after = db.count_row()

        for _, row_after in db.select(id=2):
            break

        # Debugging
        if debugging:
            print(f"""
            row_before: {row_before}
            count_before: {count_before}
            row_after: {row_after}
            count_after: {count_after}
            """)

        # Test
        self.assertAlmostEqual(count_after, count_before - 1)
        self.assertIsInstance(row_before, dict)
        self.assertIsNone(row_after)

    def test7_clear(self):
        function_name('clear')

        # Task
        count_before = db.count_row()
        db.clear()
        count_after = db.count_row()

        # Debugging
        if debugging:
            print(f"""
            count_before: {count_before}
            count_after: {count_after}
            """)

        # Test
        self.assertGreater(count_before, 0)
        self.assertAlmostEqual(count_after, 0)

    def test8_count_column(self):
        function_name('count_column')

        # Task
        result = db.count_column()

        # Debugging
        if debugging:
            print(f"""
            count: {result}
            """)

        # Test
        self.assertIsInstance(result, int)
        self.assertAlmostEqual(result, 3)

    def test9_count_row(self):
        function_name('count_row')

        # Task
        result = db.count_row()

        # Debugging
        if debugging:
            print(f"""
            count: {result}
            """)

        # Test
        self.assertIsInstance(result, int)
        self.assertAlmostEqual(result, 0)

    def test_10_dump(self):
        function_name('dump')

        # Task
        if db.isEncrypted:
            path = aescrypto.utility.add_extension(drive.databasePath)
        else:
            path = drive.databasePath

        try:
            checksum_before = aescrypto.utility.checksum(path)
        except FileNotFoundError:
            checksum_before = None

        db.dump()
        checksum_after = aescrypto.utility.checksum(path)

        # Debugging
        if debugging:
            print(f"""
            checksum_before: {checksum_before}
            checksum_after: {checksum_after}
            """)

        # Test
        if db.isEncrypted:
            self.assertNotEqual(checksum_before, checksum_after)
        else:
            self.assertEqual(checksum_before, checksum_after)


if __name__ == '__main__':
    unittest.main()
