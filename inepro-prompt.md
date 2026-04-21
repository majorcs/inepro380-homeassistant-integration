I would like to implement a new Home Assistant integration for the inepro PRO380-Mod energy consumption meter, which provides modbus interface. Even the modbus registers could be read by HomeAssistant one-by-one, but they can not be groupped into a single device. This integration should represent a single device with all the provided registers as native homeassistant entities.

- This has to be a native Home Assistant integration
- This has to be installable from HACS, it should be deployed to git in a way, that HACS could use it natively
- build a skill for home assistant integration development based on its documentation: 
  - https://developers.home-assistant.io/docs/creating_component_index/
- build a skill for HACS to be able to publish the integration, based on its document:
  - https://www.hacs.xyz/docs/publish/
- build a skill for the device modbus interface management, the register map is in the file: #inepro-registers.csv
- the integration has to be configured on the HomeAssistant webUI without yaml. 
- it should support several devices to be used in parallel
- the main purpose of this implementation is to read the devices through Modbus TCP, optionally ModBUS RTU (serial communication)
- The configuration should ask for the protocol (TCP/Serial) and for the device info:
  - In case of TCP: IP/Port (default port 502)
  - In case of Serial: path to the serial port 
  - The slave ID (default: 1)
- All the readable values should be represented as a HomeAssistant entity with their corresponding state_class (measurement/total/total_increasing) and unit (if applicable, like W, kWh, var, A, etc).
- The serial number provided by the device could be included in the default name
- Writable registers should not be used at all, maybe in a later phase
- Maintain high automated test coverage

