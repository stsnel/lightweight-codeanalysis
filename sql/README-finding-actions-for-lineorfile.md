This file contains examples of how to query the SQLite database
of an instrumented SUT to find actions that executed a particular
line of code (or any line of code in a particular file).

This example is based on the CKAN dev environment. In order to spin
it up, you will need to install a recent version of [Vagrant](https://vagrantup.com)
and [VirtualBox](https://virtualbox.org). 

# Starting the VM

Start the VM by running `vagrant up` in the /suts/ckan-dev/source directory. This
will spin up an instrumented data catalog application named [CKAN](https://ckan.org)
in a VM. 

After the command completes, you should be able to see the web interface
running at http://localhost:8080/.

# Performing actions

The TESTAR protocol will call an instrumentation endpoint before each endpoint to
label the action, so that instrumentation data can be linked to each action. Such
labels are called "log contexts" in the instrumentation.

* First navigate to http://localhost:8080 in your browser. You should see the CKAN main page.
* In a second tab, navigate to http://localhost:8080/testar-logcontext/aboutaction
* In the first tab, click on the "About" menu button
* In the second tab, navigate to http://localhost:8080/testar-logcontext/loginaction
* In the first tab, click on "Log in", and log in with username "tester" / password "tester".
* In the second tab, navigate to http://localhost:8080/testar-logcontext/otherdata

# Querying the instrumentation database

The instrumentation database has now stored lines of code executed for two actions: "aboutaction"
and "loginaction". This section contains some examples about how run queries on the collected
instrumention data.

During automated tests, this would likely be done by adding an endpoint to the instrumented SUT
to extract query data. However, it's also possible to explore the data by querying the instrumentation
database directly.

First start SQLite in the VM in the following way:

```bash
$ vagrant ssh
vagrant@vagrant:~$ sqlite3 /coverage/coverage.dat 
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite> 
```

## Printing a list of lines for an action

This query prints the first five lines of code in the application
itself that were executed when we clicked on the about button. If you
are also interested in lines of code in underlying libraries, remove
the `file.path` WHERE clause from the query.

```sql
sqlite> SELECT
         log_line.id as log_id,
          file.path as file,
          log_context.context as log_context,
          log_line.line_number as line_number
        FROM
          log_line
          LEFT JOIN log_context ON log_context.id = log_line.log_context_id
          LEFT JOIN file ON log_line.file_id = file.id
        WHERE
          log_context.context = "aboutaction" AND
          file.path LIKE '/usr/lib/ckan/default/%'
        LIMIT 5
        ;
239377|/usr/lib/ckan/default/src/ckan/ckan/config/middleware/flask_app.py|aboutaction|428
239378|/usr/lib/ckan/default/src/ckan/ckan/config/middleware/flask_app.py|aboutaction|397
239412|/usr/lib/ckan/default/src/ckan/ckan/config/middleware/flask_app.py|aboutaction|400
239413|/usr/lib/ckan/default/src/ckan/ckan/views/__init__.py|aboutaction|48
239414|/usr/lib/ckan/default/src/ckan/ckan/common.py|aboutaction|156
```

## Finding actions that executed lines in a file

This query counts the number of times a line of code in a particular file was executed
for each action. Note that lines can be executed multiple times, for example in loops,
so the number of executed lines can be higher than the number of lines of code in the file.

```sql
sqlite> SELECT
          log_context.context,
          COUNT(log_line.id)
        FROM
          log_line
          LEFT JOIN log_context ON log_context.id = log_line.log_context_id
          LEFT JOIN file ON log_line.file_id = file.id
        WHERE
          file.path = '/usr/lib/ckan/default/src/ckan/ckan/authz.py' AND
          log_context.context like "%action"
        GROUP BY log_context.context;
aboutaction|68
loginaction|282
```

## Finding action that executed a particular line in a file

This query finds actions that executed a particular line in a file (line 64
in user.py):

```sql
sqlite> SELECT
          COUNT(log_line.id),
          log_context.context as log_context
        FROM
          log_line
          LEFT JOIN log_context ON log_context.id = log_line.log_context_id
          LEFT JOIN file ON log_line.file_id = file.id
        WHERE 
          file.path = '/usr/lib/ckan/default/src/ckan/ckan/model/user.py' AND
          log_line.line_number = 64
        GROUP BY log_context.context;
8|loginaction
```

## Calculating distance metrics to a particular line in a file

If we don't get any exact matches for a line of code, we can calculate
a simple distance metric, e.g. the minimum number of lines between a line
executed by the action and a target line:

```sql
sqlite> SELECT
          MIN(ABS(61 - log_line.line_number)),
          log_context.context as log_context
        FROM
          log_line
          LEFT JOIN log_context ON log_context.id = log_line.log_context_id
          LEFT JOIN file ON log_line.file_id = file.id
        WHERE 
          file.path = '/usr/lib/ckan/default/src/ckan/ckan/model/user.py'
        GROUP BY log_context.context;
2|loginaction
```
