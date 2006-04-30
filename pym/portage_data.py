# portage_data.py -- Calculated/Discovered Data Values
# Copyright 1998-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Id: /var/cvsroot/gentoo-src/portage/pym/portage_data.py,v 1.5.2.2 2005/02/26 11:22:38 carpaski Exp $


import os,pwd,grp
from portage_util import writemsg
from output import green,red

ostype=os.uname()[0]

lchown = None
if ostype=="Linux" or ostype.lower().endswith("gnu"):
	userland="GNU"
	os.environ["XARGS"]="xargs -r"
elif ostype == "Darwin":
	userland="Darwin"
	os.environ["XARGS"]="xargs"
	def lchown(*pos_args, **key_args):
		pass
elif ostype.endswith("BSD") or ostype =="DragonFly":
	userland="BSD"
	os.environ["XARGS"]="xargs"
else:
	writemsg(red("Operating system")+" \""+ostype+"\" "+red("currently unsupported. Exiting.")+"\n")
	sys.exit(1)

if not lchown:
	if "lchown" in dir(os):
		# Included in python-2.3
		lchown = os.lchown
	else:
		import missingos
		lchown = missingos.lchown


	
os.environ["USERLAND"]=userland

# Portage has 3 security levels that depend on the uid and gid of the main
# process and are assigned according to the following table:
#
# Privileges  secpass  uid    gid
# normal      0        any    any
# group       1        any    portage_gid
# super       2        0      any
#
# If the "wheel" group does not exist then wheelgid falls back to 0.
# If the "portage" group does not exist then portage_uid falls back to wheelgid.

secpass=0

uid=os.getuid()
wheelgid=0

if uid==0:
	secpass=2
try:
	wheelgid=grp.getgrnam("wheel")[2]
	if (not secpass) and (wheelgid in os.getgroups()):
		secpass=1
except KeyError:
	writemsg("portage initialization: your system doesn't have a 'wheel' group.\n")
	writemsg("Please fix this as it is a normal system requirement. 'wheel' is GID 10\n")
	writemsg("`emerge baselayout` and a config update with dispatch-conf, etc-update\n")
	writemsg("or cfg-update should remedy this problem.\n")
	pass

#Discover the uid and gid of the portage user/group
try:
	portage_uid=pwd.getpwnam("portage")[2]
	portage_gid=grp.getgrnam("portage")[2]
	if secpass < 1 and portage_gid in os.getgroups():
		secpass=1
except KeyError:
	portage_uid=0
	portage_gid=wheelgid
	writemsg("\n")
	writemsg(  red("portage: 'portage' user or group missing. Please update baselayout\n"))
	writemsg(  red("         and merge portage user(250) and group(250) into your passwd\n"))
	writemsg(  red("         and group files. Non-root compilation is disabled until then.\n"))
	writemsg(      "         Also note that non-root/wheel users will need to be added to\n")
	writemsg(      "         the portage group to do portage commands.\n")
	writemsg("\n")
	writemsg(      "         For the defaults, line 1 goes into passwd, and 2 into group.\n")
	writemsg(green("         portage:x:250:250:portage:/var/tmp/portage:/bin/false\n"))
	writemsg(green("         portage::250:portage\n"))
	writemsg("\n")

if (uid!=0) and (portage_gid not in os.getgroups()):
	writemsg("\n")
	writemsg(red("*** You are not in the portage group. You may experience cache problems\n"))
	writemsg(red("*** due to permissions preventing the creation of the on-disk cache.\n"))
	writemsg(red("*** Please add this user to the portage group if you wish to use portage.\n"))
	writemsg("\n")

