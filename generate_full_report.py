import sys
sys.path.append("util")
import json
import numpy as np  
import matplotlib.mlab as mlab  
import matplotlib.pyplot as plt 
from find_cert import *
from count_cert import *
from count_domain_ip import *
from parse_csv import *
import os



def get_report(domain):
    with open("report/test_https/"+domain+".json") as f:
        https_test = json.load(f)
    out_map = {'https_overall':{'http_default':len(https_test['http_default']),"http_only":len(https_test['http_only']),"https_reachable":len(https_test['https_reachable']),"https_default":len(https_test['https_default']),"https_only":len(https_test['https_only']),"https_error":len(https_test['https_error']),"unreachable":len(https_test['unreachable'])}}
    return (https_test,out_map)

def get_error_map(https_error):
    err_map = {}
    labels = []

    for i in https_error:
        item = i.split(' (')
        d = item[0]
        error = item[1].strip(')')
        if error not in err_map:
            err_map[error] = set([d])
            labels.append(error)
        else:
            err_map[error].add(d)
    with open("report/error_domain/"+domain+"_err_reason_map.txt","w") as f:
        for k in err_map:
            f.write(k+":\n")
            f.write('\t'+str(err_map[k])+'\n')
    return err_map

def draw_overall_pie(https_test,domain):        
    #画饼图
    del https_test['http_default']
    labels = https_test.keys()
    X = [len(v) for v in https_test.values()]
    fig = plt.figure(figsize=(8,8))
    plt.pie(X,labels=labels,autopct='%1.2f%%',pctdistance=0.8,labeldistance=1.1,rotatelabels=10,radius=0.8) 
    plt.legend(loc='upper left',bbox_to_anchor=(-0.15,1))
    plt.title("overall https analysis for "+domain)
    plt.show() 
    if not os.path.exists('report/pic/'+domain):
        os.mkdir('report/pic/'+domain)
    plt.savefig("report/pic/"+domain+"/"+domain+"https_overall_result.png")
    

def init_dir():
    if not os.path.exists('util/log'):
        os.mkdir('util/log')
    if not os.path.exists('report/cert'):
        os.mkdir('report/cert')
        os.mkdir('report/cert/cert_ct')
        os.mkdir('report/cert/cert_from_domain')
        os.mkdir('report/cert/cert_from_ip')
        os.mkdir('report/cert/shared_cert')
    if not os.path.exists('report/pic'):
        os.mkdir('report/pic')
    if not os.path.exists('report/domain_ip'):
        os.mkdir('report/domain_ip')

def init_pic_path(domain):
    if not os.path.exists('report/pic/'+domain):
        os.mkdir('report/pic/'+domain)

if __name__=='__main__':
    init_dir()
    domains = sys.argv[1:]
    for domain in domains:
        #init the picture saving path for specific domain
        init_pic_path(domain)

        #draw the overall https test result
        (https_test,out_map) = get_report(domain)
        draw_overall_pie(https_test,domain)

        ##parse the report from ssllab and draw piechar
        #dlist = read_csv("report/ssllab/"+domain+"_error.csv")
        ##draw the piechar of error domain's ip
        #draw_ip_map(dlist,domain)
        ##draw the most common HTTPS error reasons reported
        #draw_error_reason(dlist,domain)
        ##draw the common names of error certs
        #draw_error_cert(dlist,domain)

        #count the relationships between domain and ip
        out_map['ip_DNS_map'] = count_domains_ip_fromDNS(domain)
        #try to connect each domain's 443 port (use tls sni extension)
        get_cert_from_domains(domain, read_domains("domain/resolved_domain/"+domain+".txt"))
        certfd = count_cert_fd(domain)
        #find shared cert between different domains
        out_map['shared_cert_map'] = find_shared_cert(domain,certfd)
        #draw the piechar for certs' CA map
        out_map['ca_map'] = find_CA(domain,certfd,'fd')
        #search if the certificate was logged in CT
        search_cert_in_ct(certfd,domain)
        #count the number of logged certs in CT, write down the not logged ones
        out_map['ct_map'] = count_cert_in_ct(domain,certfd)

        #output the final result in json
        print(json.dumps(out_map))
        with open('report/chart/'+domain+".json","w") as f:
            json.dump(out_map,f)

