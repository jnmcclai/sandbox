#!/usr/bin/python
# coding: utf-8

import paramiko
import time
import re

#could do some prompt regex play
prompt = ""

class ParamikoPlay():

  def __init__(self, ip, user, pwd, port=23):
    self.user = user
    self.ip = ip
    self.pwd = pwd
    self.port = port
    self._sshClient = None

  def _createSshClient(self):
    """
    Creates a ssh client, invokes a shell and returns a channel to this shell.
    """
    try:
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(self.ip, username=self.user, password=self.pwd )
      channel = client.invoke_shell(width=256)
      self._sshClient = client
      self._sshChannel = channel
    except:
      raise AssertionError('could not open ssh connection.')
    return client, channel

  def _reconnectSshClient(self):
    """
    Checks if a ssh client is already open and, if so, checks if it is still active.
    Otherwise a new client is started. Returns the current ssh client.
    """
    try:
      if self._sshClient.get_transport().is_active() is True:
        pass
    except:
      self._sshClient, self._sshChannel = self._createSshClient()
      self._enableDefaultCliOptions()
    finally:
      return self._sshClient, self._sshChannel

  def _execSshCommand(self, command):
    client, channel = self._reconnectSshClient()
    output = ''

    try:
      # clear leftovers
      while channel.recv_ready():
        channel.recv(1)
      # send the command
      channel.send(command + '\n')
      # wait until channel has data
      while not channel.recv_ready():
        time.sleep(0.1)
      # read until end of prompt
      while not output.endswith('$ '):
        while channel.recv_ready():
          output += channel.recv(1)
      # check for errors
      if 'cli>ERROR:' in output:
        assert False, output

    except AssertionError as e:
      raise AssertionError('ssh command "%s" failed with error "%s"' % (command, e))

    # return output without command and prompt
    return '\n'.join(output.splitlines()[1:-1])


if __name__ == '__main__':

  #create an instance
  instance = ParamikoPlay("10.13.225.19", "cli", "diversifEye")

  #create ssh session
  instance._createSshClient()

  #run some cmds
  print instance._execSshCommand("cli help")
  print instance._execSshCommand("cli configure cliDefaultPartition=3")
  print instance._execSshCommand("cli configure cliDefaultDiversifEyeUser=ERPS")
  print instance._execSshCommand("cli listApplications")
