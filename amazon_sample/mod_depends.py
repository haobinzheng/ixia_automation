#!/usr/bin/python
##################################################################
## mod_depends.py 
## Parse Builder modules to determine dependent policies
##################################################################
## 2012-12-27 rafaelo
## First draft - needs some clean up and error-checking added
##################################################################

import os
import sys
import re
import md5
import pickle
from optparse import OptionParser


parser = OptionParser()
modpath = os.getcwd() + "/out"
polpath = os.getcwd() + "/module/border/junos"
modules = {}
devices = {}


def output(msg, context=""):
    if (not options.verbose):
        if (not context in ["STATUS"]):
            return
    print "%s" % (msg)


def get_policy_list(path):
    try:
        os.chdir(path)
    except OSError:
        # just raise the error for now
        raise
        
    for modfile in os.listdir(path):
        if (not re.match("policy-.*", modfile)):
            continue
        output("Found Policy: %s" % (modfile))
        parse_module(path + "/" + modfile)
    


def get_mod_list(path,search_device=None):
    global devices
    br_dev_match = re.compile("([a-z]{3}[0-9]{1,3})-(br|en)-(tra|agg|dcr|cor|lbe|edg)-((r|sw)[0-9]{1,3})")
    
    if (search_device):
        re_search_device = re.compile("^" + search_device + "$")
    
    ## Don't parse these for dependencies
    ignore_modules = [ "all", "_modinfo", "custom_1"]
    
    try:
        os.chdir(path)
    except OSError:
        # just raise the error for now
        raise
    
    ## walk through every device's out folder
    ## and create a unique list of modules seen
    for device in os.listdir(path):            
        if not os.path.isdir(device):
            continue

        if (search_device):
            if (not re_search_device.match(device)):
                continue

        output("Device: %s" %(device))

        devtype = ""
        ## determine device type
        match = br_dev_match.search(device)
        if (match):
            devtype = match.group(2) + "-" + match.group(3)
            if devtype not in devices:
                devices[devtype] = []    
            
        for modfile in os.listdir(device):
            #print "Potential Module: %s" % (modfile)
            if not os.path.isfile(path + "/" + device + "/" + modfile):
                continue
            if modfile in ignore_modules:
                continue
            
            output("Found module: %s" % (modfile))
            
            
            if (devtype):
                devices[devtype].append(modfile)
                
            
            parse_module(path + "/" + device + "/" + modfile)


def add_module(modfile):
    global modules
    module = os.path.basename(modfile)
    modparts = module.split("_")
    modversion = modparts.pop()
    modname = "_".join(modparts)
    #m = md5.new(module)
    #modhash = m.hexdigest()
    modhash = ""
    
    modules[module] = { 'name':modname,'version':modversion, 'hash':modhash, 'depends':[]}


## Pull the module name from a file\path
def get_mod_name(modfile):
    module = os.path.basename(modfile)
    modparts = module.split("_")
    modparts.pop()
    return "_".join(modparts)

## Pull the module version from a file\path    
def get_mod_version(modfile):    
    module = os.path.basename(modfile)
    modparts = module.split("_")
    return modparts.pop()


def parse_module(modfile):
    global modules
    policies = []
    module = os.path.basename(modfile)
    re_import = re.compile("(vrf-)?(import|export)\s([A-Za-z0-9_-]+);$")
    re_import_chain = re.compile("(vrf-)?(import|export)\s\[([\sA-Za-z0-9_-]+)\]")
    re_policy = re.compile("(^|\s+)policy ([A-Za-z0-9_-]+);")
    re_policy_statement = re.compile("(policy-statement)\s+([a-zA-Z0-9_-]+)\s+{")
    
    try:
        lines = [line.strip() for line in open(modfile, 'r')]
    except:
        raise

    for line in lines:
        match = re_import.search(line)
        if (match):
            policies.append("policy-%s_1" % (match.group(3)))
            continue
        match = re_import_chain.search(line)
        if (match):
            modchain = match.group(3).strip()
            for policy in modchain.split():
                policies.append("policy-%s_1" % (policy))
            continue
        match = re_policy.search(line)
        if (match):
            policies.append("policy-%s_1" % (match.group(2)))
        
        ## check for policy-statements, unless we're already looking at a policy-* file
        if (not re.match("policy-", module)):
            match = re_policy_statement.search(line)
            if (match):
                output("\tEmbedded policy: %s" % (match.group(2)))
                policies.append("policy-%s_1" % (match.group(2)))
                
            
        
    
    ## Uniq the list of policies we've found
    policies = list(set(policies))
    #print policies
    
    if not modules.has_key(module):
        add_module(module)
    
    modules[module]['depends'] = list(set(modules[module]['depends'] + policies))
    
    if (len(policies)):
        pass
        #print "Module: %s" % (module)
        output("\t%s\n" % (module) + "\t" + "\n\t".join(modules[module]['depends']) )
        
def check_depends(modname):
    global modules
    matched = []
    
    re_module = re.compile("^" + modname + "$")
    
    for module in modules.keys():
        match = re_module.search(module)
        if (match):
            matched.append(module)
            print "Module dependencies for %s:" % (module)
            for dep in modules[module]['depends']:
                print "\t%s" % (dep)
    
    if (len(matched) == 0):
        print "No modules found for \"%s\"" % (modname)
        
    print ""
    return
                
    
    
def audit_depends():
    global modules
    
    for modfile in modules.keys():
        module = modules[modfile]
        for dep in module['depends']:
            if not dep in modules.keys():
                print "WARN: module %s required for %s but no module file found" % (dep, modfile)
    
    return
            


def ascript_new_shape(module, caption, origin_x, origin_y):
    ascript =  "set %s to make new shape at end of graphics with properties {corner radius: 9, size: {245.000000, 36.000000}, text: {text: \"%s\", alignment: center, text: \"%s\"}, origin: {%d, %d}, magnets: {{0, 1}, {0, -1}}}\n" % (module, caption, caption, origin_x,origin_y)
    return ascript

def ascript_new_connect(shape_A, shape_B):
    ascript = "set my_line to make new line at end of graphics with properties {point list: {{366.504, 213.516}, {366.504, 362.516}}, notes: {}, stroke cap: square, stroke join: miter}\n"
    
    ascript = ascript + "tell my_line\n\tset source to %s\n\tset tail magnet to 1\n\tset destination to %s\n\tset head magnet to 2\nend tell" % (shape_A, shape_B)

    return ascript
    
def pickle_module(file):
    global modules
    
    output("Saving dependency tree to %s" % (file))
        
    try:
        pf = open(file, 'wb')
        pickle.dump(modules, pf, -1)
    except IOError:
        raise
    
    finally:
    #    if (pf):
    #        pf.close()
        pass

    return 
    
    
    
    
def unpickle_module(file):
    pickled_mod = None
    pf = None
    
    try:
        pf = open(file, 'rb')
        pickled_mod = pickle.load(pf)
    except IOError:
        raise
    
    finally:
        if (pf):
            pf.close()
        
    
    return pickled_mod


def gen_module_ascript(script_file):
    global modules
    
    output("Generating AppleScript", "STATUS")
    
    try:
        f = open(script_file, "w")

        script = "tell application \"OmniGraffle Professional 5\"\n\ttell canvas of front window\n"
        
        ## Create shapes for all modules
        for module in modules.keys():
            mod = modules[module]
            hash = mod['hash']
            caption = "%s\nVersion %s" % (mod['name'], mod['version'])
            script = script + "\t" + ascript_new_shape(module.replace("-","_"), caption, 0, 0) + "\n"
        
        ## Create shapes for all device types
    #    for dev in devices.keys():
    #        script = script + "\t" + ascript_new_shape(dev.replace("-","_"),dev,0,0) + "\n"
                
        
        ## Create connections between dependent shapes
        for module in modules.keys():
            mod = modules[module]
            for dep in mod['depends']:
                if dep in modules.keys():
                    script = script + "\t" + ascript_new_connect(module.replace("-","_"),dep.replace("-","_")) + "\n"
                
    #    for dev in devices.keys():
    #        devtypes = devices[dev]
    #        for mod in devtypes:
    #            if mod in modules.keys():
    #                script = script + "\t" + ascript_new_connect(dev.replace("-","_"),mod.replace("-","_")) + "\n"
        
    
        script = script + "\tend tell\nend tell"

        f.write(script)
    
    except IOError:
        raise
        
    finally:
        f.close()

    output("AppleScript written to %s" % (script_file), "STATUS")
    return


################################################################################################
################################################################################################
if __name__ == '__main__':
    parser.add_option("-m",help="Display dependencies for given module name. Supports RegEx")
    parser.add_option("-s",help="Generate AppleScript for OmniGraffle and save to this file")
    parser.add_option("-a",help="Run a dependency audit",action="store_true",dest="show_audit",default=False)
    parser.add_option("-o",help="Path to Builder out directory")
    parser.add_option("-b",help="Path to Builder module directory")
    parser.add_option("-v",help="Verbose Ouput",action="store_true",dest="verbose",default=False)
    parser.add_option("-d",help="Limit parsing to specified device only")
    parser.add_option("-p",help="Save pickled version of dependency tree (for later loading)")
    parser.add_option("-u",help="Load and unpickle a previous version of the dependency tree")
    (options, args) = parser.parse_args()

    if (not (options.d or options.s or options.m or options.show_audit or options.verbose)):
        print "\nYou haven't asked me to do anything useful.\n"
        parser.print_help()
        exit(1)


    if (options.p and options.u):
        print "\nPickle and Unpickle are mutually exclusive.  Make up your mind and try again.\n"
        exit(1)
        
    if (options.u and options.d):
        print "\nI'm sorry, Dave, but I'm affraid you can't specify a device when loading a previous dependency tree\n"
        exit(1)
    
    
    
    try:

        if (options.u):
            output("Loading dependency tree from %s" % (options.u))
            modules = unpickle_module(options.u)
            if not modules:
                print "Failed to load dependency tree"
                exit(1)
                

        else:
            if (options.o):
                modpath = options.o

            if (options.b):
                polpath = options.b

            output("Looking in %s for builder modules" % (polpath))
            output("Looking in %s for builder output" % (modpath))

            if (options.d):
                get_mod_list(modpath,options.d)
            else:
                get_mod_list(modpath)
                get_policy_list(polpath)
            
            if (options.p):
                pickle_module(options.p)
            
        

        if (options.s):
            gen_module_ascript(options.s)

        if (options.m):
            check_depends(options.m)

        if (options.show_audit):
            audit_depends()

    except KeyboardInterrupt:
        print "\nGiving up so soon?  Fine. Be that way"
        exit(1)
    
    except:
        raise
        
