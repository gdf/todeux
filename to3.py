#!/usr/bin/env python
from __future__ import generators, with_statement
import sys,time,re
import os,os.path,shutil
from datetime import datetime

DB=os.path.join(os.path.curdir, ".todeux")
in_homedir = os.path.abspath(os.path.curdir)==os.path.abspath(os.path.expanduser("~"))
if os.path.exists(DB) and (not in_homedir):
  print "[Using project list]"
else:
  DB=os.path.join(os.path.expanduser("~"), ".todeux")

todofile=re.compile(r"^(\d+)--([^~]+)$")

def red(s):
  print "%s[0;31m%s%s[0m" % (chr(27),s,chr(27)),

def light_red(s):
  print "%s[1;31m%s%s[0m" % (chr(27),s,chr(27)),

def yellow(s):
  print "%s[1;33m%s%s[0m" % (chr(27),s,chr(27)),

def brown(s):
  print "%s[0;33m%s%s[0m" % (chr(27),s,chr(27)),

def cyan(s):
  print "%s[0;36m%s%s[0m" % (chr(27),s,chr(27)),

def light_blue(s):
  print "%s[1;34m%s%s[0m" % (chr(27),s,chr(27)),

def blue(s):
  print "%s[0;34m%s%s[0m" % (chr(27),s,chr(27)),

def green(s):
  print "%s[0;32m%s%s[0m" % (chr(27),s,chr(27)),

def light_green(s):
  print "%s[1;32m%s%s[0m" % (chr(27),s,chr(27)),

def pri_color(fn):
  m = todofile.match(fn)
  pri = int(m.groups()[0])
  if pri==1:
    light_red(fn)
  elif pri==2:
    brown(fn)
  elif pri==3:
    cyan(fn)
  elif pri==4:
    green(fn)
  else:
    blue(fn)

def t_list(opts):
  """list
     Show all open tasks.
     """
  for fn in sorted(os.listdir(os.path.join(DB, "open"))):
    if todofile.match(fn):
      pri_color(fn)
      # count lines !~ /^\S+:/, ~= /^\s*$/, don't count first
      with open(os.path.join(DB, "open", fn), 'r') as f:
        comments = len([l for l in f.readlines() if not re.search(r'^(\s*$|[\w\s]+:)', l)])
        if comments > 1: print "+",
      print ""

def t_add(opts):
  """add [-P] <short description>
     Add a new task.
     """
  pri = 3
  if opts[0].startswith("-"):
    pri = -1 * int(opts[0])
    opts = opts[1:]
  textdesc = " ".join(opts)
  filedesc = re.sub(r"[^\w+-]", "_", textdesc)
  newfile=os.path.join(DB, "open", "%02d--%s" % (pri, filedesc))
  if os.path.exists(newfile):
    print "%s already exists!" % newfile
    return
  with open(newfile, 'w') as f:
    f.writelines([textdesc+"\n","created: %s\n" % datetime.now().isoformat()])
  print "added: %s" % newfile

def t_do(opts):
  """do <task>
     Close an open task.
     """
  fn = taskfn_for_arg(opts[0])
  with open(os.path.join(DB, "open", fn), 'a') as f:
    f.write("done: %s\n" % datetime.now().isoformat())
    if len(opts) > 1:
      f.write("close comment: %s\n" % " ".join(opts[1:]))
  donefn = fn
  while os.path.exists(os.path.join(DB, "done", donefn)):
    donefn = "%s_" % donefn
  openfn=os.path.join(DB, "open", fn)
  donefn=os.path.join(DB, "done", donefn)
  shutil.move(openfn, donefn)
  print "Closed: %s" % fn

def t_show(opts):
  """show <task>
     Show task details.
  """
  fn = taskfn_for_arg(opts[0])
  print fn
  with open(os.path.join(DB, "open", fn), 'r') as f:
    for line in f:
      print line,

def t_pri(opts):
  """pri <task> <newpriority>
     Change task priority.
  """
  fn = taskfn_for_arg(opts[0])
  newprio = int(opts[1])
  with open(os.path.join(DB, "open", fn), 'a') as f:
    f.write("new prio: %d; %s\n" % (newprio, datetime.now().isoformat()))
  m = todofile.match(fn)
  newfn = "%02d--%s" % (newprio, m.groups()[1])
  oldpath=os.path.join(DB, "open", fn)
  newpath=os.path.join(DB, "open", newfn)
  shutil.move(oldpath, newpath)
  print newfn

def t_edit(opts):
  """edit <task>
     Edit task details.
     """
  fn = os.path.abspath(os.path.join(DB, "open", taskfn_for_arg(opts[0])))
  os.system("vi +3 \"%s\"" % fn)

def t_init(opts):
  """init [--home]
     Create new .todeux "database" in current directory.
     With --home, creates non-project ~/.todeux directory. 
     """
  db=os.path.join(os.path.curdir, ".todeux")
  if len(opts) > 0:
    if opts[0] == '--home':
      db=os.path.join(os.path.expanduser("~"), ".todeux")
    else:
      print "Unknown option for init: %s" % opts[0]
      sys.exit()
  if os.path.exists(db):
    print "%s already exists, doing nothing" % db
  else:
    os.makedirs(os.path.join(db, "open"))
    os.makedirs(os.path.join(db, "done"))
    print "Created: %s" % db

def taskfn_for_arg(a):
  hits = []
  for fn in os.listdir(os.path.join(DB, "open")):
    if todofile.match(fn) and re.search(a, fn):
      hits.append(fn)
  if len(hits)==0:
    print "No tasks match %s" %a
    sys.exit()
  if len(hits) > 1:
    print "Multiple tasks match %s" % a
    for x in hits: print x
    sys.exit()
  return hits[0]

if __name__ == '__main__':
  cmds = {
      None: t_list,
      'list': t_list,
      'add' : t_add,
      'pri' : t_pri,
      'do'  : t_do,
      'show': t_show,
      'edit': t_edit,
      'init': t_init,
      }
  c = None
  if len(sys.argv)>1:
    c=sys.argv[1]
    for long in cmds:
      if long==None: continue
      if long.startswith(c): c = long
  opts = sys.argv[2:]
  if cmds.has_key(c):
    cmds[c](opts)
  else:
    print "Usage: to3.py <command> [...options...]"
    print "Commands:"
    for k in cmds:
      if k==None: continue
      cmddoc = cmds[k].__doc__
      print "  %s:\t %s" % (k, cmddoc)

