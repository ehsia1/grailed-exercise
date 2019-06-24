# Evan Hsia Coding Challenge Grailed

I wrote my solution in Python 2.7, in which I have about 2-3 years of full experience in classroom and internship settings.
My main solution is all in the file `solution.py`. In it is a main function in order to run the script, and the class `UsersTableFixes()` 
with functions:
  * `findAllDisallowedUsers()`: which finds all users with disallowed usernames
  * `resolveUsernameCollisions(dryRun=False)`: which resolves username collisions (taking the optional flag dryRun which if set prints to
  console rather than committing changes to db)
  * `resolveDisallowedUsernames(dryRun=False)`: which resolves disallowed usernames (taking the optional flag dryRun which if set prints to
  console rather than committing changes to db)
  * `getAllInvalidUsernames()`: a helper function used to get all invalid usernames in the `disallowed_usernames` table in order to avoid
  more conflicts during resolution. This was kept in the class because it requires the instance of the db connection in order to query.
  * `resolve(usersToResolve, collisionOrDisallowed, dryRun=False)`: the function that has the bulk of the resolution logic. In my design,
  resolving username collisions and disallowed usernames had a lot of overlap, with changes only to which users (usersToResolve) we were updating,
  and whether or not we added an integer suffix to the first username to resolve (we have to change all disallowed usernames, but we leave the first
  username the same when resolving collisions). Therefore resolve takes parameters:
    * `usersToResolve`, a list of user tuples to resolve,
    * `collisionOrDisallowed`, a bool that if True tells the function to behave like a collision, and if False then behave like disallowed resolution,
    * `dryRun`, an optional bool which if set will just print changes to console rather than committing them to the db.
    
In order to test, I wrote unit tests in the file `test.py`, testing each of the main functions of the challenge. `test.py` uses a copy of the
sample db given called `test.db`.

## Using `solution.py`
`solution.py` uses the argparse module in the main script. I created flags to run the script. Here is a breakdown of the flags and how to
run each function:
  * `-h, --help`: help breakdown
  * `--db DB` (required): path to the db that we want to query or make changes to
  * `--find-disallowed`:     if present, find all disallowed users
  * `--resolve-collisions`:  if present, resolve username collisions
  * `-d1`:                   if present, run dry run when resolving collisions. will not commit to db
  * `--resolve-disallowed`:  if present, resolve disallowed usernames
  * `-d2`:                   if present, run dry run when resolving disallowed. will not commit to db
#### Examples of usage:
  * `python solution.py --db test.db --resolve-collisions --resolve-disallowed` will resolve both collisions and disallowed usernames and commit both to db.
  * `python solution.py --db test.db --resolve-collisions -d1` will resolve collisions but output to console, not commit to db.
  * `python solution.py --db test.db --find-disallowed` will find users with disallowed usernames and output to console.  
  
  *Note that by default, the script will resolve collisions first then disallowed if both flags are present. This order was determined based on the order of the spec
  and can easily be changed. But as of now if we want to resolve disallowed first, we'd have to run with just the resolve-disallowed flag first, and then with just
  the resolve-collisions flag*
  
Please let me know if there are any questions about my code or approach! I did my best to comment and explain as much as possible in this README
