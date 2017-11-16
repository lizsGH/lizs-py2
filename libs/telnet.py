#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:   lizs
# Site:     http://alizs.cc
# Time:     10/30/17 2:39 PM

import telnetlib
import socket


class BdTelnet(object):

    def __init__(self, username, password, host, port=0, system='linux',
                 connect_timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 read_timeout=10):
        # system: linux, windows
        self.system = system.lower()
        self.username = username
        self.password = password
        self.read_timeout = read_timeout
        # self.linefeed = self._linefeed
        self.is_login = False
        self.tn = telnetlib.Telnet(host=host, port=port, timeout=connect_timeout)
        username and password and self.login()

    @property
    def linefeed(self):
        """Get the linefeed of the system. e.g. windows -> \r\n, linux -> \n"""
        linefeed = "\n"
        if self.system == 'windows':
            linefeed = "\r\n"
        return linefeed

    @property
    def success_flag(self):
        """The identification when login successful."""
        flag = ':~$'
        if self.system == 'windows':
            flag = 'Microsoft Telnet Server'
        return flag

    def cmd(self, cmd):
        return '%s%s' % (cmd, self.linefeed)

    def _read_until(self, match, timeout=None):
        timeout = timeout if timeout else self.read_timeout
        return self.tn.read_until(match=match, timeout=timeout)

    def _write(self, cmd, result=False):
        self.tn.write(self.cmd(cmd))
        return self._result(cmd) if result else None

    def _result(self, cmd):
        match = ['%s%s' % (i, cmd) for i in ['>', '# ', '$ ']]
        # the first line, e.g. ~$ cmd, C:\Users\Administrator>cmd
        cmd_line = self.tn.expect(match)[-1].splitlines()[-1]
        # print('cmd: %s' % cmd_line)
        delimiter = cmd_line[: -len(cmd)]
        # print('delimiter: %s' % delimiter)
        result = self._read_until(delimiter)
        # remove the last line, e.g. ~$, C:\Users\Administrator>
        result = self.linefeed.join(result.splitlines()[:-1])
        # add a new start, otherwise, the first line of next command will be cmd
        # and not the prefix, e.g. "ls -l". What we need like "$ ls -l".
        self._write('')
        return result

    def login(self, username=None, password=None):
        username = username if username else self.username
        password = password if password else self.password
        'login:' in self._read_until('login:', 15) and self._write(username)
        'assword:' in self._read_until('assword:') and self._write(password)
        # login = self._read_until('login:', 15)
        # print('login'.center(100, '-'))
        # print(login)
        # if 'login:' in login:
        #     print('Write login username')
        #     self._write(username)
        # pwd = self._read_until('assword:')
        # print('password'.center(100, '-'))
        # print(pwd)
        # if 'assword:' in pwd:
        #     print('Write password')
        #     self._write(password)
        if self.success_flag in self._read_until(self.success_flag):
            print('Login Successful!')
            self.is_login = True
            return True
        return False

    def execute(self, command):
        """Execute a command and return the result."""
        if self.is_login:
            return self._write(command, result=True)

    def batch_execute(self, commands):
        return {cmd: self.execute(cmd) for cmd in commands}

    def close(self):
        self.tn.close()


if __name__ == '__main__':
    host = '172.16.3.222'
    username = 'administrator'
    password = '123456'
    system = 'windows'
    cmd = 'whoami'
    tn = BdTelnet(username=username, password=password, host=host, system=system)
    result = tn.execute(cmd)
    print('-' * 100)
    print(result)
    print('-' * 100)
    cmds = ['whoami', 'echo %cd%', 'whoami']
    print(tn.batch_execute(cmds))
    print('-' * 100)
    tn.close()
