#!/usr/bin/python
import re, json, paramiko, sys, time
file = sys.argv[1]
f = open(file, "r")
connections = []
results = []
conn_params = re.sub(r'\[|\]', '', f.read().replace('},', '};').strip()).split(';')
for host in conn_params:
    connections.append(json.loads(host))
for connection in connections:
  auth_method = "certificate"
  client = paramiko.SSHClient()
  client.load_system_host_keys()
  client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
  try:
        client.connect(connection["hostname"], username=connection["user"])
  except paramiko.ssh_exception.AuthenticationException:
        client.connect(connection["hostname"], username=connection["user"], password=connection["user"])
        auth_method = "password"
  ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && git branch")
  if (ssh_stderr.readline().strip()==''):
     vcs_type = "git"
     vcs_branch = ssh_stdout.readline().strip()
     ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && git log | head -1 | awk '{print $0}'")
     vcs_revision = ssh_stdout.readline().strip()
  else:
    vcs_type = "svn"
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && svn info | grep '^URL:' | egrep -o '(tags|branches)/[^/]+|trunk' | egrep -o '[^/]+$'")
    vcs_branch = ssh_stdout.readline().strip()
    ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command("cd bw/ && svn info | grep Revision | awk '{print $2}'")
    vcs_revision = ssh_stdout.readline().strip()
#  if (client.get_host_keys() is None):
#    auth_method = "password"
#  else:
#    auth_method = "certificate"
  results.append({connection["user"]:{"vcs_type":vcs_type, "branch":vcs_branch, "revision":vcs_revision, "auth_type":auth_method}})
  client.close()
f.close()
time.sleep(5)
print(json.dumps(results, indent=4, sort_keys=False))
