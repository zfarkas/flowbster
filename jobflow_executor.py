import yaml
import os,sys,stat
import subprocess

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

sysconfpath = os.path.join('config-sys.yaml')
confsys = dict(readconfig(sysconfpath))
jobdirroot = confsys['jobdirroot']

def perform_exec(sandboxdir,exename,arguments):
    os.chdir(sandboxdir)
    status = subprocess.call('./'+exename+' '+arguments+'>../stdout 2>../stderr',shell=True)
    save_a_file('..','retcode',str(status))

def find_job_to_run(jobdirroot):
    dirs = os.listdir(jobdirroot)
    for name in dirs:
        found = True
        confapppath = os.path.join(jobdirroot,name,'config-app.yaml')
        if not os.path.exists(confapppath):
            continue

        if os.path.exists(os.path.join(jobdirroot,name,'retcode')):
            continue

        confapp = dict(readconfig(confapppath))
        inputlist = confapp['inputs']
        for k in inputlist:
            inputfilepath = os.path.join(jobdirroot,name,"sandbox",k['name'])
            if not os.path.exists(inputfilepath):
                found = False

        if found:
            exename = confapp['executable']['filename']
            arguments = confapp['arguments']
            return (os.path.join(jobdirroot,name),exename,arguments)
    return (False,False,False)

def exec_one_job():
    print "Looking for a job to be executed at \""+jobdirroot+"\""
    (jobdir,exename,arguments) = find_job_to_run(jobdirroot)
    if jobdir:
        print "Found job to execute at \""+jobdir+"\""
        sandboxdir = os.path.join(jobdir,'sandbox')
        perform_exec(sandboxdir,exename,arguments)
        print "Execution done."
        return jobdir
    else:
        print "No job found to be executed."
        return False

exec_one_job()










