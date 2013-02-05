"""
   updatecert.py

   Written by: Eric Robinson

   Update the cert status of a build

   The various status levels are represented as:

   Not Tested
   Product Team Only
   Integration Ready (formerly "Suites Installer Ready")
   Milestone
   Pre Release
   Release Candidate
   Golden Master

   Example:

   python updatecert.py "Suites Installer Ready" Bridge 2.0 Application 582

"""

import sys, os, os.path
import codex


if __name__ == "__main__":

   if len(sys.argv) < 5:
      print "Must provide <Status> <Product> <Version> <Subproduct> <BuildNumber> [<Platform>]"
      print __doc__

   status = sys.argv[1]
   if status == "Suites Installer Ready":
      status = "Integration Ready"
   product = sys.argv[2]
   version = sys.argv[3]
   subproduct = sys.argv[4]
   build = sys.argv[5]
   if len(sys.argv) > 6:
      platform = sys.argv[6]
   else:
      platform = ""

   codexobj = codex.CodexService()

   user = "errobins"
   passwd = ""

   results = codexobj.getBuilds(product, version, subproduct, build, platform)
   i = 0
   for res in results:
      result = codexobj.setCertLevel(res._id, status, user, passwd)
      i += 1
   print "Updated %d builds" % (i)