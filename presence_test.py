from gevent import monkey; monkey.patch_all()

from xaal.lib import tools,Device
from xaal.lib.asyncio import Engine
import time
import socketio
import asyncio
import inspect
import atexit
import logging

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)

PACKAGE_NAME = 'xaal.SensFloor'
logger = logging.getLogger(PACKAGE_NAME)
FUNCTION_PRESENCE = 'Presence'
FUNCTION_FALL = 'Fall'
ip_addr = 'http://172.25.0.178:8000'
#ip_addr = 'http://192.168.5.5:8000'


class Socketio_class(object):

# ---------- Partie socketio ---------- #
    
    def __init__(self):
        self.project_installation = False
        self.device_installation = False
        self.sio = socketio.AsyncClient()
        self.config()
        self.data_areas = {} # Contient l'id de l'application ainsi que son nom
        self.functs = {} # Contient l'id de l'application ainsi que sa fonction
        self.zones_presence = {} # Contient toutes les zones appartenant au type Presence (cle : id / valeur : nom de zone)
        self.zones_fall = {} # Contient toutes les zones appartenant au type Fall (cle : id / valeur : nom de zone)
        self.l = {} # Contient l'id de l'application et le device
        self.sio.on('connect', self.connect)    
        self.sio.on('funcresult-update', self.etat_app)
        self.sio.on('project', self.project)
        self.eng = Engine()
        self.devices = {}
        atexit.register(self._exit)

    async def connect(self):
        print("\nConnexion au socket : SUCCES\n")

    async def project(self,msg):
        for cle, objet in msg['project']['areas'].items():
            self.data_areas[cle]=objet['name']
        for cle, objet in msg['project']['functs'].items():
            self.functs[cle]=objet['name']
        for cle in self.data_areas.keys():
            if (self.functs[cle]==FUNCTION_PRESENCE and not(self.data_areas[cle] in self.zones_presence)):
                self.zones_presence[cle]=self.data_areas[cle]
            if (self.functs[cle]==FUNCTION_FALL and not(self.data_areas[cle] in self.zones_fall)):
                self.zones_fall[cle]=self.data_areas[cle]
        self.project_installation = True

    async def etat_app(self,msg):
        if self.device_installation == True :
            self.treatment_msg(msg)
            
    def treatment_msg(self,message):
        if not(len(self.l)==0):
            if (self.functs[message["uid"]]==FUNCTION_PRESENCE or self.functs[message["uid"]]==FUNCTION_FALL):
                dev=self.l[message["uid"]]
                result=message['result']
                self.update_attribute(dev,message['uid'],result)

    async def run_sio(self):
        print("\nConnexion au socket : ATTENTE\n")
        await self.sio.connect(ip_addr)
        await self.sio.wait()

# ---------- Partie xAAL ---------- #
    
    def config(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if not cfg:
            cfg= tools.new_cfg(PACKAGE_NAME)
            cfg['devices Fall'] = {}
            cfg['devices Presence'] = {}
            logger.warn("Created an empty config file")
            cfg.write()
        self.cfg = cfg          

                    
    async def add_applications(self):
        addr_list = []
        i=0
        while(self.project_installation==False):
            print("Attente de connexion et des infos de configuration du SensFloor")
            await asyncio.sleep(1)
        if (len(self.zones_fall)!=0):
            for id,name in self.zones_fall.items():
                name_basic="fall.basic"
                dev= Device(name_basic)
                check = "base_addr"+str(i)
                dev.info = "SensFloor Fall Detection : %s" %name
                liste_section = list(self.cfg['devices Fall'].keys())
                if len(liste_section)==0 :
                    #Liste vide
                    base_addr = tools.get_random_base_uuid()
                    self.cfg['devices Fall'][check]=str(base_addr)
                    dev.address=base_addr
                else : 
                    # Liste non vide
                    if(check in liste_section):
                        base_addr = tools.str_to_uuid(self.cfg['devices Fall'][check])
                        dev.address=base_addr

                    else:   #pas present dans la liste
                        base_addr = tools.get_random_base_uuid()
                        self.cfg['devices Fall'][check]=str(base_addr)
                        dev.address=base_addr

                fall = dev.new_attribute('Fall')
                fall.value = "init"
                dev.dump()
                self.l[id]=dev
                addr_list.append(dev.address)
                self.eng.add_device(dev)
                i=i+1


        if (len(self.zones_presence)!=0):   
            for id,name in self.zones_presence.items():
                name_basic="presence.basic"
                dev= Device(name_basic)
                check = "base_addr"+str(i)
                dev.info = "SensFloor Presence Detection : %s" %name
                liste_section = list(self.cfg['devices Presence'].keys())
                if len(liste_section)==0 :
                    #Liste vide
                    base_addr = tools.get_random_base_uuid()
                    self.cfg['devices Presence'][check]=str(base_addr)
                    dev.address=base_addr
                else : 
                    # Liste non vide
                    if(check in liste_section):
                        base_addr = tools.str_to_uuid(self.cfg['devices Presence'][check])
                        dev.address=base_addr

                    else:   #pas present dans la liste
                        base_addr = tools.get_random_base_uuid()
                        self.cfg['devices Presence'][check]=str(base_addr)
                        dev.address=base_addr

                presence = dev.new_attribute('Presence')
                presence.value = "init"
                dev.dump()
                self.l[id]=dev
                addr_list.append(dev.address)
                self.eng.add_device(dev)
                i=i+1
        self.device_installation = True
        await self.eng.run()

    def update_attribute(self,dev,id,result):
        if (id in self.zones_presence):
            attr=dev.get_attribute(FUNCTION_PRESENCE)
            attr.value=result
        if (id in self.zones_fall):
            attr=dev.get_attribute(FUNCTION_FALL)
            attr.value=result
       
    def _exit(self):
        cfg = tools.load_cfg(PACKAGE_NAME)
        if cfg != self.cfg:
            logger.info('Saving configuration file')
            self.cfg.write()

if __name__ == '__main__':
    logger.info('Starting %s' % PACKAGE_NAME)
    sock=Socketio_class()
    tasks = [asyncio.ensure_future(sock.run_sio()),asyncio.ensure_future(sock.add_applications())]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))

def setup(eng):
    logger.info('Starting %s' % PACKAGE_NAME)
    sock=Socketio_class(eng)
    tasks = [asyncio.ensure_future(sock.run_sio()),asyncio.ensure_future(sock.add_applications())]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
