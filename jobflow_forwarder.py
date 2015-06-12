import requests
import yaml
import os,sys,stat
import logging
import logging.config
import time
import glob

def readconfig(pathtoconfig):
    with open(pathtoconfig, 'r') as f:
        return yaml.load(f)

def save_a_file(directory,name,content):
    fullpath = os.path.join(directory,name)
    fo = open(fullpath, "wb")
    fo.write(content);
    fo.close()
    return fullpath

def perform_sending_content(url,content):
    try:
        r = requests.post(url, data=yaml.dump(content))
    except:
        log.exception('')
        return False
    return True

def find_output_to_forward(jobdirroot):
    dirs = glob.glob(os.path.join(jobdirroot,"*/F_*"))
    if dirs:
        return dirs[0]
    else:
        return False

def forward_outputs(jobdir):
    job_config = readconfig(os.path.join(jobdir,"config-job.yaml"))
    if not job_config.has_key("wfid"):
        log.error("Key \'wfid\' not found in config-job.yaml")
        return False
    wfid = job_config.get("wfid")

    app_config = readconfig(os.path.join(jobdir,"config-app.yaml"))
    if not app_config.has_key("outputs"):
        log.error("Key \'outputs\' not found in config-app.yaml")
        return False
    outputs = app_config.get("outputs")

    forward_success = True
    for ind, out in enumerate(outputs):
        log.debug("Checking output: \""+out.get("name")+"\"")
        if os.path.exists(os.path.join(jobdir,'output-forwarded-'+str(ind))):
            log.debug("Output \""+out.get("name")+"\" has already been forwarded as \""+out.get("targetname")+"\"")
            continue
       
        url = out.get("targeturl")
        if not os.path.exists(os.path.join(jobdir,'output-content-'+str(ind)+'.yaml')):
            job_dict = {}
            job_dict['wfid'] = wfid
            job_dict['inputs'] = []
            one_input = {}
            one_input['name'] = out.get("targetname")
            with open(os.path.join(jobdir,"sandbox",out.get("name")), 'r') as fo:
                out_content = fo.read()
            one_input['content'] = out_content
            job_dict['inputs'].append(one_input)
            content = yaml.dump(job_dict,default_flow_style=False)
            save_a_file(jobdir,'output-content-'+str(ind)+'.yaml',content)
            save_a_file(jobdir,'output-url-'+str(ind)+'.txt',url)
          
        log.info("Sending content for \""+out.get("targetname")+"\" to \""+url+"\"")
        content = readconfig(os.path.join(jobdir,'output-content-'+str(ind)+'.yaml'))
        success = perform_sending_content(url,content)
        if success:
            save_a_file(jobdir,'output-forwarded-'+str(ind),'done')
            log.info("Sending: SUCCESS.")
        else:
            log.info("Sending: FAILED. Will retry later.")
            forward_success = False
    if forward_success:
        save_a_file(jobdir,'output-forwarded','done')
        
    return True



def forward_one_output():
    log.info("Looking for an output to be forwarded at \""+jobdirroot+"\"")
    jobdir = find_output_to_forward(jobdirroot)
    if jobdir:
        log.info("Found output to forward at \""+jobdir+"\"")
        #forward_outputs(jobdir)
        log.info("Forward finished.")
        return False
    else:
        log.info("No output found to be forwarded.")
        return False


def loadconfig(sysconfpath):
    global confsys, jobdirroot, log
    confsys = readconfig(sysconfpath)
    jobdirroot = os.path.join(confsys['jobdirroot'])
    if not os.path.exists(jobdirroot): os.makedirs(jobdirroot)
    logging.config.dictConfig(confsys['logging'])
    log = logging.getLogger("jobflow.forwarder")


if len(sys.argv)==3 and sys.argv[1]=="-c":
    loadconfig(sys.argv[2])
else:
    loadconfig(os.path.join('/etc','jobflow-config-sys.yaml'))

while True:
    if forward_one_output()==False :
        time.sleep(confsys['sleepinterval'])

