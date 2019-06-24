import sqlite3
import argparse

class UsersTableFixes():
    def __init__(self, dbName):
        self.conn = sqlite3.connect(dbName)
        self.cursor = self.conn.cursor()

    """
        this function returns the list of user objects that have disallowed usernames.
    """
    def findAllDisallowedUsers(self):
        out = []
        self.cursor.execute("SELECT * FROM users WHERE username IN (SELECT invalid_username FROM disallowed_usernames);")
        out = self.cursor.fetchall()
        return out

    """
        this function resolves username collisions.
        parameters: dryRun (bool) - default False. if true, we print instead of committing to db.
    """
    def resolveUsernameCollisions(self, dryRun=False):
        self.cursor.execute("SELECT * FROM users WHERE username IN (SELECT username FROM users GROUP BY username HAVING COUNT(username) > 1);")
        duplicateUsers = self.cursor.fetchall()
        self.resolve(duplicateUsers, True, dryRun)

    """
        this function resolves disallowed usernames.
        parameters: dryRun (bool) - default False. if true, we print instead of committing to db.
    """
    def resolveDisallowedUsernames(self, dryRun=False):
        self.resolve(self.findAllDisallowedUsers(), False, dryRun)

    """
        this function gets all invalid usernames of db. this is in the class because it needs the instance variable of cursor
        in order to query to the db.
    """
    def getAllInvalidUsernames(self):
        self.cursor.execute("SELECT invalid_username FROM disallowed_usernames")
        return [x[0] for x in self.cursor.fetchall()]

    """
        this function is the general resolve logic for both disallowed and collisions.
        parameters: usersToResolve (list) - list of user tuples (id, username) to resolve
                    collisionOrDisallowed (bool) - if true, we're resolving collisions, else
                                                    we're resolving disallowed
                    dryRun (bool) - default False, but if true, we print and do not commit to db
    """
    def resolve(self, usersToResolve, collisionOrDisallowed, dryRun=False):
        usernameIds = {}
        # get invalid usernames to make sure we do not cause conflicts later
        disallowedNames = self.getAllInvalidUsernames()
        # map usernames to list of ids that we have to change the usernames of
        for id, name in usersToResolve:
            if name not in usernameIds:
                usernameIds[name] = [id]
            else:
                usernameIds[name] += [id]
        # iterate through map to resolve conflicts one by one
        for name, ids in usernameIds.iteritems():
            suffix = 0
            if not collisionOrDisallowed:
                suffix += 1
            for i in range(len(ids)):
                if (collisionOrDisallowed and i > 0) or not collisionOrDisallowed:
                    # check if the new name causes more conflicts (collisions or disallowed) and keep incrementing
                    # suffix until we hit a valid username (it doesn't exist in users table already or disallowed)
                    self.cursor.execute("SELECT * FROM users WHERE username ='" + name + str(suffix) + "';")
                    while len(self.cursor.fetchall()) > 0 or name + str(suffix) in disallowedNames:
                        suffix += 1
                        self.cursor.execute("SELECT * FROM users WHERE username ='" + name + str(suffix) + "';")
                    if dryRun:
                        print "%s" % ((ids[i], name + str(suffix)),)
                    else:
                        self.cursor.execute("UPDATE users SET username = '" + name + str(suffix) + "' WHERE id = " + str(ids[i]) + ";")
                # this elif is just to print the first user in the case of collision on dry run since that one stays the same
                elif collisionOrDisallowed and i == 0 and dryRun:
                    print "%s" % ((ids[i], name),)
                suffix += 1
        self.conn.commit()

    # close db connection when class is finished being used
    def __del__(self):
        self.conn.close()
        print 'DB CONNECTION CLOSED'

def main():
    # main uses argument flags to run each class function, right now it defaults to resolving collisions
    # before disallowed, but the order can be easily switched
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, help='path to db', required=True)
    parser.add_argument('--find-disallowed', action='store_true', help='if present, find all disallowed users')
    parser.add_argument('--resolve-collisions', action='store_true', help='if present, resolve username collisions')
    parser.add_argument('-d1', action='store_true', help='if present, run dry run when resolving collisions - will not commit to db')
    parser.add_argument('--resolve-disallowed', action='store_true', help='if present, resolve disallowed usernames')
    parser.add_argument('-d2', action='store_true', help='if present, run dry run when resolving disallowed - will not commit to db')
    args = parser.parse_args()

    usersFixes = UsersTableFixes(args.db)

    if args.find_disallowed:
        print usersFixes.findAllDisallowedUsers()
    if args.resolve_collisions:
        if args.d1:
            print "PRINTING AFFECTED ROWS TO CONSOLE: NO CHANGES BEING COMMITTED TO DB"
            usersFixes.resolveUsernameCollisions(True)
        else:
            usersFixes.resolveUsernameCollisions()
            print "CHANGES COMMITTED TO DB"
    if args.resolve_disallowed:
        if args.d2:
            print "PRINTING AFFECTED ROWS TO CONSOLE: NO CHANGES BEING COMMITTED TO DB"
            usersFixes.resolveDisallowedUsernames(True)
        else:
            usersFixes.resolveDisallowedUsernames()
            print "CHANGES COMMITTED TO DB"


if __name__ == "__main__":
    main()
