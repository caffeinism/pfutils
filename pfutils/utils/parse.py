import re
from iictl.utils.exception import ParseError, PortError

def parse_envs(env_list):
    env_format = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)=(.*)$')
    
    envs = []
    for env in env_list:
        match = env_format.match(env)
        if match is None:
            raise ParseError(env, 'environment variable')
            
        name = match.group(1)
        value = match.group(2)
        
        envs.append((name, value))
    
    return envs
    
    #name:path:ro
def parse_volumes(volume_list):
    volume_format = re.compile(r'^([a-z-.]+):(/|(?:/[\w-]+)+)(:r[wo])?$')
    
    volumes = []
    for volume in volume_list:
        match = volume_format.match(volume)
        if match is None:
            raise ParseError(volume, 'volume')
            
        name = match.group(1)
        path = match.group(2)
        ro = match.group(3)
        
        if ro is None or ro == ":rw":
            ro = False
        else:
            ro = True
        
        volumes.append((name, path, ro))
    
    return volumes

def parse_domains(domain_list):
    domain_format = re.compile(r'^([0-9]{0,5}):([a-z0-9-_]+(?:\.[a-z0-9-_]+)+)$')
    
    domains = []
    for domain in domain_list:
        match = domain_format.match(domain)
        if match is None:
            raise ParseError(domain, 'domain')
            
        port = int(match.group(1))
        if port > 65535:
            raise PortError(port)
        
        domain = match.group(2)
                
        domains.append((port, domain))
    
    return domains

def is_valid_object_name(object_name):
    object_name_format = re.compile(r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$')
    
    return object_name_format.match(object_name) is not None