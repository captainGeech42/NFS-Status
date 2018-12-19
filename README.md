# NFS Health Check

## About

This script validates the following items for a NFS share
 - Reachable by ping?
 - Server available? (checked via RPC)
 - Share available? (checked via RPC)
 - Share mounted?
 - Share readable by current user?
 - Share writeable by current user?

If any test fails, the following actions are taken
 - An email alert is sent
 - The NFS share is forcibly unmounted
 - The specified local device will be mounted to the same mount point

This script only works on Linux. If you want to make a Windows version, please submit a pull request.

## Setup

The following changes must be made to the `nfs_status.py` script (they all have a TODO comment next to them)
 - Configure your email settings
   - To/From
   - SMTP Server/Port
   - SMTP Authentication if necessary
 - Configure your NFS settings
   - NFS Host
   - NFS Share
   - Local Mount Point
   - Test file path
   - Local device to mount if NFS is unavailable
 - Configure your log settings
   - Filepath to write logs to
     - If you don't want logs written to disk, don't set the `log_fp` global variable. The `log()` function will skip writing to disk if `log_fp` is set to `None` (which is the value it's initialized to)

For the `rotate.py` script, just change the filepath to the persistent log you set in `nfs_status.py`.

You'll want to put this in your crontab most likely. Edit your crontab with `crontab -e`, and add the following (adjust timing for `nfs_status.py` as you wish):
```
0 0 * * * /path/to/rotate.py # midnight everyday
* * * * * ( sleep 30; /path/to/nfs_status.py ) # halfway through every minute
```

You also have to create the test file with some contents before running the script for the first time. Each time it runs it will put the current timestamp in the test file, but it needs that file to exist initially so that the `share_readable()` test passes.

Each test that gets ran will be written to the log with a timestamp, so you can keep track of what's being run when.

## Disclaimer

This script is still being tested so there may be some issues. If something breaks related to the script, please submit an issue.

Also, in an ideal world the `Test`/`TestRunner` classes wouldn't be in the same file, but everything in one file makes it easier to push out to remote servers, which is how I'm using this script. It should be pretty easy to move those classes to their own file(s) if you want to do that (a PR for that would be cool).