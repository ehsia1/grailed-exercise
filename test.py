import unittest
import sqlite3
import shutil
from solution import UsersTableFixes

class TestUsersTableFixes(unittest.TestCase):
    def setUp(self):
        shutil.copy("grailed-exercise.sqlite3", "test.db")
        self.conn = sqlite3.connect("test.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("INSERT INTO users (id, username) VALUES(10001, 'about1')")
        self.cursor.execute("INSERT INTO disallowed_usernames (id, invalid_username, created_at, updated_at) VALUES(8, 'about2', '2018-06-15 15:35:15.379899', '2018-06-15 15:35:15.379899')")
        self.conn.commit()
        self.usersFixes = UsersTableFixes("test.db")

    def testFindDisallowedUsers(self):
        expected = [
            (1957, 'about'),
            (3487, 'about'),
            (5580, 'about'),
            (9441, 'about'),
            (2400, 'grailed'),
            (2873, 'grailed'),
            (4737, 'grailed'),
            (6491, 'grailed'),
            (2448, 'heroine'),
            (3035, 'heroine'),
            (8141, 'heroine'),
            (6935, 'privacy'),
            (9491, 'privacy'),
            (9921, 'privacy'),
            (4302, 'profile'),
            (9478, 'profile'),
            (9537, 'profile'),
            (786, 'settings'),
            (3206, 'settings'),
            (7011, 'settings'),
            (7088, 'settings'),
            (7599, 'settings'),
            (9807, 'settings'),
            (4512, 'terms'),
            (9479, 'terms')]
        self.assertEquals(self.usersFixes.findAllDisallowedUsers(), expected)

    def testResolveCollisions(self):
        self.usersFixes.resolveUsernameCollisions()
        self.cursor.execute("SELECT * FROM users WHERE username IN (SELECT username FROM users GROUP BY username HAVING COUNT(username) > 1);")
        self.assertEquals(self.cursor.fetchall(), [])
        self.cursor.execute("SELECT COUNT(username) FROM users GROUP BY username;")
        counts = [x[0] for x in self.cursor.fetchall()]
        self.assertEquals(counts, [1] * len(counts))
        # test to make sure 'about2' wasn't used as a collision resolve because it was added to disallowed table
        self.cursor.execute("SELECT * FROM users WHERE username = 'about2';")
        self.assertEquals(self.cursor.fetchall(), [])

    def testResolveDisallowedUsernames(self):
        self.cursor.execute("SELECT username, COUNT(username) FROM users GROUP BY username;")
        oldCounts = self.cursor.fetchall()
        oldCountMap = {}
        for username, count in oldCounts:
            if username not in oldCountMap:
                oldCountMap[username] = count
            else:
                oldCountMap[username] += count
        self.usersFixes.resolveDisallowedUsernames()
        self.assertEquals(self.usersFixes.findAllDisallowedUsers(), [])
        self.cursor.execute("SELECT username, COUNT(username) FROM users GROUP BY username;")
        # make sure that we didn't add to any duplicates already there - therefore
        # we the new list of unique usernames should be longer than the old
        # and for every username in the new db, the count should equal 1 if it
        # wasn't in the original db, or it should be <= to the count from the original db
        newCounts = self.cursor.fetchall()
        self.assertTrue(len(newCounts) >= len(oldCounts))
        newCountMap = {}
        for username, count in newCounts:
            if username not in newCountMap:
                newCountMap[username] = count
            else:
                newCountMap[username] += count
        for username in newCountMap.keys():
            if username not in oldCountMap:
                self.assertEquals(newCountMap[username], 1)
            else:
                self.assertTrue(newCountMap[username] <= oldCountMap[username])


    def tearDown(self):
        self.conn.close()

if __name__ == "__main__":
    unittest.main()
