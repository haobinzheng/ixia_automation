#
# Easy access to SSH through paramiko
# (pip install python-paramiko)
#

import threading
import getpass
import os
import time
import socket
import copy
from pprint import pformat
from robot.api import logger

try:
    #from paramiko import SSHClient, WarningPolicy, AutoAddPolicy, RSAKey
    from paramiko import SSHClient, AutoAddPolicy, RSAKey
except ImportError as e:
    raise Exception(e)

class mySSHClient(object):
    ''' Encapsulates SSH access '''
    def __init__(self, hostname, username='admin', password='', checkHost=True):
        ''' Set up SSH object to hostname. '''
        if checkHost:
            socket.getaddrinfo(hostname, 23, socket.AF_UNSPEC, socket.SOCK_STREAM)
        self.hostname = hostname
        self.makeSSH()
        self.username = None
        self.password = None
        self.stderr = None
        self.stdout = None
        self.exit_status = -1
        self.raiseOnError = True
        self.setUser(username, password)
        self._returnAsString = None
        self._checkExitStatus = False
        self.caughtException = None
        self.sshConnect()
        self.SSHSEMA = threading.Semaphore(1)

    def __del__(self):
        print("Closing ssh connection...")
        self.ssh.close()

    def sshConnect(self):
        self.ssh.connect(hostname=self.hostname,username=self.username, password=self.password,timeout = 2)

    def makeSSH(self):
        ''' Creates a new SSHClient object. '''
        self.ssh = SSHClient()
        # https://github.com/paramiko/paramiko/blob/master/demos/demo_simple.py
        #self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
 
    def setUser(self, username, password):
        ''' Set the username and password. Also clears the privateKey. '''
        self.username = username
        self.password = password
        self.privateKey = None

    def setPrivateKey(self, keyFile="~/.ssh/id_rsa"):
        '''
        Set the Private SSH key to use for authentication. By default uses your private key and username. 
        Once set the username and password set during initialization are ignored.
        '''
        self.privateKey = RSAKey.from_private_key_file(os.path.expanduser(keyFile))
        self.pkusername = getpass.getuser()

    def checkExitStatus(self, ret=True):
        '''
        Set the flag for checking exit code upon finishing the command.
        The flag is off by default, and this will turn it on by default.
        Run this before running cmd() to get exit status.
        '''
        self._checkExitStatus = ret

    def cmd_proc(self, command, returnAsString=True, timeout=0,
            exceptionRetriesLeft=3, ignoreTimeout=False, interaction=[]):
        '''
        Meant for quick running commands that may occasionally fail because of network issues. It will retry in that case. 
        '''
        try:
            return self.cmdNoRetries_sync(command, returnAsString=returnAsString, timeout=timeout, ignoreTimeout=ignoreTimeout)
        except Exception as e:
            if exceptionRetriesLeft <= 0:
                raise e
            self.makeSSH()
            self.sshConnect()
            return self.cmd_proc(command=command, returnAsString=returnAsString, timeout=timeout, exceptionRetriesLeft=(exceptionRetriesLeft - 1), ignoreTimeout=ignoreTimeout, interaction=interaction)


    def cmd(self, command, returnAsString=True, timeout=0,
            exceptionRetriesLeft=2, ignoreTimeout=False, interaction=[]):
        '''
        Meant for quick running commands that may occasionally fail because of network issues. It will retry in that case. 
        '''
        try:
            return self.cmdNoRetries(command, returnAsString=returnAsString, timeout=timeout, ignoreTimeout=ignoreTimeout, interaction=interaction)
        except Exception as e:
            if exceptionRetriesLeft <= 0:
                raise e
            self.ssConnect()
            return self.cmd(command=command, returnAsString=returnAsString, timeout=timeout, exceptionRetriesLeft=(exceptionRetriesLeft - 1), ignoreTimeout=ignoreTimeout, interaction=interaction)

    def cmdNoRetries_sync(self, command, returnAsString=True, timeout=0, ignoreTimeout=False):
        '''
        Executes command on the remote host. Raises Exception if stderr isn't empty. 
        By default returns the result as a string. Set returnAsString to False if that's not desirable. 
        Default timeout is 0 seconds which means it will wait forever. Override with your own timeout values as needed.
        If ignoreTimeout=True the command still gets terminated but stdout and stderr are processed as before.
        '''
        self.stderr = None
        self.stdout = None
        self.exit_status = None
         
        o = self.syncCmd(command, returnAsString)
        while self.stderr != None:
            self.makeSSH()
            self.sshConnect()
            o = self.syncCmd(command, returnAsString)
        return o


    def cmdNoRetries(self, command, returnAsString=True, timeout=0, ignoreTimeout=False, interaction=[]):
        '''
        Executes command on the remote host. Raises Exception if stderr isn't empty. 
        By default returns the result as a string. Set returnAsString to False if that's not desirable. 
        Default timeout is 0 seconds which means it will wait forever. Override with your own timeout values as needed.
        If ignoreTimeout=True the command still gets terminated but stdout and stderr are processed as before.
        '''
        self.stderr = None
        self.stdout = None
        self.exit_status = None
        if not self._returnAsString is None:
            returnAsString = self._returnAsString
        o = self.asyncCmd(command, returnAsString, interaction=interaction)
        try:
            self.caughtException = None
            o.waitTillDone(timeout)
        except TimeoutException as e:
            self.caughtException = e
            if ignoreTimeout:
                logger.console("Ignoring timeout of command (ignoreTimeout = True)" % command)
            else:
                if self.raiseOnError:
                    raise e
                    logger.console("Ignoring timeout of command (raiseOnError = False), consider using ignoreTimeout" % command)
        except Exception as e:
            self.caughtException = e
            if self.raiseOnError:
                raise e
            else:
                logger.console("Ignoring exception:" % e)
        finally:
            self.stderr = o.stderr
            self.stdout = o.stdout
            self.exit_status = o.exit_status

        if not o.caught is None:
            logger.console("Re-raising caught exception during mySSHCommand.cmd() :" + pformat(vars(o)))
            raise o.caught
        return o.stdout

    def syncCmd(self,command,returnAsString):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        out = stdout.readlines()
        err = stderr.readlines()
        self._returnAsString = returnAsString
        if len(err) > 0:
            if self._returnAsString:
                self.stderr = ''.join(err)
            else:
                self.stderr = err
        else:
            self.stderr = None
        self.stdout = out
        return out


    def asyncCmd(self, cmd, returnAsString=True, interaction=[]):
        '''
        Starts an asynchronous command on the remote host.
        Returns an mySSHCommand object which can be polled for command completeness.
        By default returns the result as a string in the returned object. 
        Set returnAsString to False if that's not desirable.
        '''
        if not self._returnAsString is None:
            returnAsString = self._returnAsString
        o = mySSHCommand(self, self.ssh, cmd, returnAsString,interaction=interaction)
        o.start()
        return o

class mySSHCommand(threading.Thread):
    '''
    Returned by mySSHClient.asyncStart. Use this object to retrieve IO and monitor progress.
    '''
    def __init__(self, parent, ssh, cmd, returnAsString, interaction=[]):
        self._returnAsString = returnAsString
        self.parent = parent
        self.ssh = copy.deepcopy(ssh)
        self.asyncCmd = cmd
        self.caught = None
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.stopped = threading.Event()
        self.interaction = interaction
        threading.Thread.__init__(self)
        self.name = '"%s"' % str(cmd)

    def __str__(self):
        return ("Stdout: %s\nStderr: %s" % (str(self.stdout), str(self.stderr)))

    def __del__(self):
        if self.is_alive():
            logger.console("mySSHCommand object being deleted while still running" % self)
            self.ssh.close()
            self.join()

    def run(self):
        '''
        Threading start point.
        '''
        try:
            self._cmd(self.asyncCmd)
        except Exception as e:
            self.caught = e

    def done(self):
        '''
        Returns True if the asynchronous command completed. Now access the .stdout and .stderr properties.
        '''
        return not self.is_alive()

    def stop(self):
        '''
        Stops the asynchronous command. Most likely no output will be preserved. 
        '''
        self.stopped.set()
        try:
            if self.stdin is None:
                pass
                logger.console("No stdin when stopping thread")
            else:
                pass
                logger.console("Sending Ctrl-C")
                self.stdin.write(chr(3))
        except Exception as e:
            logger.console("Stop exception ", e)
            pass
        self.ssh.close()
        self.join(0.1)

    def waitTillDone(self, timeout=0):
        '''
        Wait for the async process to be done, up to timeout seconds. Raises if timeout is exceeded.
        By default waits forever (timeout=0).
        '''
        start = time.time()
        while timeout == 0 or int(time.time() - start) <= timeout:
            if self.done():
                return
            time.sleep(0.01)
        logger.console("Stopping thread that timed out")
        self.stop()
        raise TimeoutException("Timeout %d seconds exceeded" % timeout)

    def _cmd(self, command):
        '''
        Executes command on the remote host. Raises Exception if stderr isn't empty.
        '''
        self.stderr = None
        self.stdout = None
        self.exit_status = -1
        out = ''
        with self.parent.SSHSEMA:
            if self.stopped.isSet():
                logger.console("Stopped while waiting in SSHSEMA")
                return
            if self.parent.privateKey is None:
                self.ssh.connect(self.parent.hostname, username=self.parent.username, password=self.parent.password, timeout=2)
            else:
                self.ssh.connect(self.parent.hostname, username=self.parent.pkusername, pkey=self.parent.privateKey, timeout=2)
            if self.stopped.isSet():
                logger.console("Stopped while waiting to connect")
                return

        if self.interaction == []:
            self.stdin, stdout, stderr = self.ssh.exec_command(command)
            out = stdout.readlines()
            err = stderr.readlines()
            if len(err) > 0:
                if self._returnAsString:
                    self.stderr = ''.join(err)
                else:
                    self.stderr = err
            else:
                self.stderr = None
        else:
            logger.console("Interaction", self.interaction)
            chan = self.ssh.invoke_shell()
            try:
                for x in self.interaction:
                    exp, cmd = x
                    logger.console('expecting__|:(%s)' % exp)
                    buff = ''
                    while not buff.endswith(exp) and not chan.exit_status_ready():
                        resp = chan.recv(1024)
                        buff += resp
                    logger.console('receiving__|:<%s>' % buff)
                    time.sleep(1)
                    logger.console('sending cmd:(%s)' % cmd)
                    chan.send(cmd + '\n')
                    out = buff
            except Exception as e:
                logger.console(e)

        if len(out) > 0 and self.parent._checkExitStatus:
            try:
                self.exit_status = int(out[-1])
            except ValueError:
                # In case attempted cast from str to int
                pass  # leave exit status as -1

        if self._returnAsString:
            self.stdout = ''.join(out)
        else:
            self.stdout = out
        self.ssh.close()


if __name__ == "__main__":
    ssh_client = mySSHClient("10.105.241.19",password='Fortinet123!')
    output = ssh_client.cmd_proc("get system status")
    print(f"Using process based ssh cmd: {output}")
    output = ssh_client.cmd_proc("get system status")
    print(f"Using thread based ssh cmd: {output}")
    del ssh_client

    