#!/usr/bin/env python3

# Helpful SE post
# https://unix.stackexchange.com/questions/176673/how-can-i-determine-if-an-nfs-remote-is-exporting-a-directory

# Disclaimer: only works on Linux

from datetime import datetime
from email.message import EmailMessage
import os
import smtplib
import subprocess
import sys
import textwrap

debug = False

# To add a new test, do the following:
# 1. Make a function that does the test (return a bool)
# 2. Make a Test object with that function
#    i.e. t = Test("Sample test", func, [arg1, arg2])
# 3. Add fail actions/success actions as needed
#    i.e. t.add_fail_action(func, [])
# 4. Add the test to the TestRunner object
#    i.e. tr.add_test(t)

# To run the tests, call run_tests() on a TestRunner object

class Test:
    def __init__(self, name, func, args):
        self.name = name
        self.func = func
        self.args = args

        self.email = True

        self.fail = {}
        self.success = {}

        self.add_fail_action(email_alert, ["{} test failed".format(self.name)])


    def add_fail_action(self, func, args):
        self.fail[func] = args


    def add_success_action(self, func, args):
        self.success[func] = args


    def run(self):
        ret = self.func(*self.args)
        if debug:
            print("test \"{}\" returned {}".format(self.name, ret))
        if not ret:
            for f in self.fail.keys():
                if debug:
                    print("executing {}({})".format(repr(f), self.fail[f]))
                f(*self.fail[f])
        else:
            for f in self.success.keys():
                if debug:
                    print("executing {}({})".format(repr(f), self.success[f]))
                f(*self.success[f])
        return ret


class TestRunner:
    def __init__(self):
        self.tests = []


    def add_test(self, test):
        self.tests.append(test)


    def run_tests(self):
        for t in self.tests:
            ret = t.run()
            if not ret:
                exit(1)


# Returns the stdout of a command (as a str)
def get_stdout(cmd):
    result = subprocess.run(cmd.split(" "), stdout=subprocess.PIPE)
    return result.stdout.decode("utf-8")


# Returns datetime str
def get_ts():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Ping test
# Returns true if ping succeeds
def ping_test(host):
    ping_ret = os.system("ping -c 1 -w2 {host} > /dev/null 2>&1".format(host=host))
    return ping_ret == 0


# Checks if NFS server is running
# Returns true if server is running
def server_available(host):
    rpc_output = get_stdout("rpcinfo -t {host} nfs 4".format(host=host))
    return "version 4 ready and waiting" in rpc_output


# Check if specified share is available
# Returns true if available
def share_available(host, share):
    showmount_output = get_stdout("showmount -e {host}".format(host=host))
    return "/logs" in showmount_output


# Checks is specified share is mounted
# Returns true if mounted
def share_mounted(host, share, mount_point):
    df_output = get_stdout("df -h")
    return "{host}:/{share}".format(host=host, share=share) in df_output and mount_point in df_output


# Check if share is readable by the current user
# Returns true if readable
def share_readable(test_fp):
    try:
        with open(test_fp, "r"):
            None
    except:
        return False
    return True


# Check if share is writeable by the current user
# Returns true if writeable
def share_writeable(test_fp):
    try:
        with open(test_fp, "w") as f:
            f.write("{ts}\n".format(ts=get_ts()))
    except:
        return False
    return True


# Send email alert
def email_alert(failure):
    body = '''\
            An error has occurred with the NFS share on bro-master:

            {failure}

            Please contact Zach or Zander ASAP

            Thank you,
            root@bro-master\
            '''.format(failure=failure)

    msg = EmailMessage()

    # TODO Set these fields accordingly
    msg['From'] = "root@host.local"
    msg['To'] = "something@somewhere.gtld"
    msg['Subject'] = "[URGENT] NFS Error"

    msg.set_content(textwrap.dedent(body))

    # TODO Set your SMTP server accordingly
    with smtplib.SMTP("smtp.somewhere.gltd", 587) as smtp:
        smtp.starttls()
        # TODO You may need to authenticate with your SMTP server here
        smtp.send_message(msg)


# Mount RAID array
def mount_raid(device, mount_point, umount=True):
    os.system("umount -fl {mount_point}".format(mount_point=mount_point))
    os.system("mount {device} {mount_point}".format(device=device, mount_point=mount_point))


# Run tests
def main(argv):
    if "debug" in argv:
        global debug
        debug = True

    # TODO Set these values according to your configuration
    # TODO You must put something in the test file before running for the first time
    host = "172.16.1.1" # IP/DNS for your NFS server
    share = "logs" # Name of the NFS share
    mount_point = "/mnt/logs" # Local mount point for the NFS share
    test_fp = os.path.join(mount_point, "status.test") # Absolute path to test file (script will read/write it)
    raid = "/dev/sda1" # Block device to mount if NFS is unavailable

    runner = TestRunner()

    test1 = Test("Ping", ping_test, [host])
    test1.add_fail_action(mount_raid, [raid, mount_point])
    runner.add_test(test1)

    test2 = Test("Server available", server_available, [host])
    test2.add_fail_action(mount_raid, [raid, mount_point])
    runner.add_test(test2)

    test3 = Test("Share available", share_available, [host, share])
    test3.add_fail_action(mount_raid, [raid, mount_point])
    runner.add_test(test3)

    test4 = Test("Share mounted", share_mounted, [host, share, mount_point])
    test4.add_fail_action(mount_raid, [raid, mount_point])
    runner.add_test(test4)

    test5 = Test("Share readable", share_readable, [test_fp])
    test5.add_fail_action(mount_raid, [raid, mount_point])
    runner.add_test(test5)

    test6 = Test("Share writeable", share_writeable, [test_fp])
    test6.add_fail_action(mount_raid, [raid, mount_point])
    runner.add_test(test6)

    runner.run_tests()


# entry point
if __name__ == "__main__":
    sys.exit(main(sys.argv))