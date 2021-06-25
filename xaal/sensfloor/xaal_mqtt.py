from xaal.lib import Device,Engine,tools
import sys
import paho.mqtt.client as mqttClient
import logging
import platform

broker_address = "172.25.0.185"
port = 1883
PACKAGE_NAME="xaal.mqtt"
logger = logging.getLogger(PACKAGE_NAME)


def main():
	cfg = tools.load_cfg(PACKAGE_NAME)
	if cfg == None:
		print(cfg)
		logger.info('New  config file')
		cfg = tools.new_cfg(PACKAGE_NAME)
		cfg.write()
	dev= Device("xaal_mqtt.basic")
	dev.address=tools.str_to_uuid(cfg['config']['addr'])
	dev.product_id = 'xaal.mqtt'
	dev.info = "%s@%s" % (PACKAGE_NAME,platform.node())
	
	# attributes
	arrow = dev.new_attribute('Arrow')
	arrow.value = "init"
	dev.dump()
	
	# methods 
	def gauche(_topic):
                client = mqttClient.Client("Python")
                client.connect(broker_address, port=port)
                client.publish(str(_topic), "gauche")
                arrow.value = "gauche"
                print("%s gauche" % dev)
                client.disconnect()
		
	def droite(_topic) :
                client = mqttClient.Client("Python")
                client.connect(broker_address, port=port)
                client.publish(str(_topic), "droite")
                arrow.value = "droite"
                print("%s droite" % dev)
                client.disconnect()
		
	def plus(_topic) :
                print("topic : ",_topic)
                client = mqttClient.Client("Python")
                client.connect(broker_address, port=port)
                client.publish(str(_topic), "plus")
                arrow.value = "plus"
                print("%s plus" % dev)
                client.disconnect()
                
	def moins(_topic) :
                client = mqttClient.Client("Python")
                client.connect(broker_address, port=port)
                client.publish(str(_topic), "moins")
                arrow.value = "moins"
                print("%s moins" % dev)
                client.disconnect()
                
	def droit(_topic) :     
                client = mqttClient.Client("Python")
                client.connect(broker_address, port=port)
                client.publish(str(_topic), "droit")
                arrow.value = "eteint"
                print("%s eteint" % dev)
                client.disconnect()
	
	dev.add_method('gauche',gauche)
	dev.add_method('droite',droite)
	dev.add_method('plus',plus)
	dev.add_method('moins',moins)
	dev.add_method('droit',droit)
	
	eng = Engine()
	eng.add_device(dev)
	eng.run()


if __name__ =='__main__':
        main()

