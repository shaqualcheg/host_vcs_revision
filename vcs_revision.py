#!/usr/bin/python
import re, json, paramiko, sys
f = open(sys.argv(1), "r")
connections = []
results = []
conn_params = re.sub(r'\[|\]', '', f.read().replace('},', '};').strip()).split(';')
for host in conn_params:
    connections.append(json.loads(host))
for connection in connections:
  client = paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  client.connect(connection["hostname"], username=connection["user"], password=connection["user"])
  ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && git branch")
  if (ssh_stderr is None):
     vcs_type = "git"
     vcs_branch = ssh_stdout
     ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && git log | head -1 | awk '{print $0}'")
     vcs_revision = ssh_stdout
  else:
    vcs_type = "svn"
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && svn info | grep '^URL:' | egrep -o '(tags|branches)/[^/]+|trunk' | egrep -o '[^/]+$'")
    vcs_branch = ssh_stdout
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && svn info | grep Revision | awk '{print $1}'")
    vcs_revision = ssh_stdout
  if (client.key_filename is None):
    auth_method = "password"
  else:
    auth_method = "certificate"
  results.append({connection["user"]:{"vcs_type":vcs_type, "branch":vcs_branch, "revision":vcs_revision, "auth_type":auth_method}})
print(json.dumps(results, sort_keys=True))