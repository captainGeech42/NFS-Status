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

The following changes must be made to the script (they all have a TODO comment next to them)
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

You also have to create the test file with some contents before running the script for the first time. Each time it runs it will put the current timestamp in the test file, but it needs that file to exist initially so that the `share_readable()` test passes.

## Disclaimer

This script is still being tested so there may be some issues. If something breaks related to the script, please submit an issue.