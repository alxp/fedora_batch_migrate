'''
Created on 2011-02-02

@author: aoneill
'''

import fcrepo.connection, fcrepo.client, ConfigParser, logging, os, time
from optparse import OptionParser
 
CONFIG_FILE_NAME = 'fedora_batch_migrate.cfg'
if __name__ == '__main__':
    config = ConfigParser.ConfigParser({'sourceurl': 'http://localhost:8080/fedora', 'sourceusername': 'fedoraAdmin', 'sourcepassword': 'fedoraAdmin',
                                                          'targeturl': 'http://localhost:8080/fedora', 'targetusername': 'fedoraAdmin', 'targetpassword': 'fedoraAdmin',
                                                          'log_file': 'fedora_batch_migrate.log', 'log_level': 'INFO'})

    if os.path.exists('/etc/%(conf)s' % {'conf': CONFIG_FILE_NAME}):
        config.read('/etc/%(conf)s' % {'conf': CONFIG_FILE_NAME})
    if os.path.exists(os.path.expanduser('~/.fedora_batch_migrate/%(conf)s' % {'conf': CONFIG_FILE_NAME})):
        config.read('/etc/%(conf)s' % {'conf': CONFIG_FILE_NAME})
    if os.path.exists(CONFIG_FILE_NAME):
        config.read(CONFIG_FILE_NAME)
        
    log_filename = config.get('Logging', 'log_file')
    levels = {'DEBUG':logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR':logging.ERROR, 'CRITICAL':logging.CRITICAL, 'FATAL':logging.FATAL}
    logging.basicConfig(filename = log_filename, level = levels[config.get('Logging', 'log_level')])
    parser = OptionParser()
    
    parser.add_option('-S', '--sourceurl', type = 'string', dest = 'sourceurl', default = config.get('SourceRepository', 'sourceurl'),
                      help = 'Source repository\'s URL. Defaults to http://localhost:8080/fedora if not specified.')
    parser.add_option('-T', '--targeturl', type = 'string', dest = 'targeturl', default = config.get('TargetRepository', 'targeturl'),
                      help = 'Target repository\'s URL. Defaults to http://localhost:8080/fedora if not specified.')
    parser.add_option('-U', '--sourceusername', type = 'string', dest = 'sourceusername', default = config.get('SourceRepository', 'sourceusername'),
                      help = 'Username to connect to the source repository as. Defaults to fedoraAdmin if not specified.')
    parser.add_option('-P', '--sourcepassword', type = 'string', dest = 'sourcepassword', default = config.get('SourceRepository', 'sourcepassword'),
                      help = 'Password to connect to the source repository with. Defaults to fedoraAdmin if not specified.')
    parser.add_option('-N', '--targetusername', type = 'string', dest = 'targetusername', default = config.get('TargetRepository', 'targetusername'),
                      help = 'Username to connect to the target repository as. Defaults to fedoraAdmin if not specified.')
    parser.add_option('-W', '--targetpassword', type = 'string', dest = 'targetpassword', default = config.get('TargetRepository', 'targetpassword'),
                      help = 'Password to connect to the target repository with. Defaults to fedoraAdmin if not specified.')
    parser.add_option('-F', '--pidsfile', type = 'string', dest = 'pidsfile', default = config.get('Input', 'pidsfile'),
                      help = 'File with list of pids to migrate.')
    
    (options, args) = parser.parse_args()
    f = open(options.pidsfile, 'r')
    sourceconn = fcrepo.connection.Connection(options.sourceurl, username = options.sourceusername, password = options.sourcepassword )
    sourceclient = fcrepo.client.FedoraClient(sourceconn)
    targetconn = fcrepo.connection.Connection(options.targeturl, username = options.targetusername, password = options.targetpassword )
    targetclient = fcrepo.client.FedoraClient(targetconn)
    lines = f.read().splitlines()
    for pid in lines:
        print pid
        try:
            request = sourceclient.api.getObjectExport(pid=pid, format='xml')
            response = request.submit()
            foxml = response.read()
            
            request2 = targetclient.api.createObject(pid=pid)
            request2.headers['Content-Type'] = 'text/xml; charset=utf-8'
            response2 = request2.submit(foxml[39:])
        except fcrepo.connection.FedoraConnectionException as e:
            logging.exception('FedoraConnectionException. ', e.value)
             
        foxml = None
        response2 = None
        response = None
        request2 = None
        request = None
        
