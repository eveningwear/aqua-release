
import sys, os, re, time, os.path


import codex

if __name__ == "__main__":
    
    #print codex.queryProducts()
    myCodex = codex.CodexService()
    results = myCodex.getBuilds("Bridge", "4.0", platform="win32", language="mul", certlevel="Integration Ready")
    
    if len(results)>0:
        product = results[0]
        print product._location