"""MLN sensor setup"""

import logging
from typing import Any
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from . import MLN
from homeassistant.components.sensor import (
    DOMAIN as ENTITY_DOMAIN,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
CONF_LS = "LS"
from .const import (
CONF_DEVICE_MANUFACTURER,
CONF_DEVICE_NAME,
CONF_DEVICE_SW_VERSION,    
CONF_DEVICE_NAME,
CONF_CUSTOMER_ID,
DEFAULT_SCAN_INTERVAL,
CONF_DATE_START,
CONF_LIFE_CYCLE,
DOMAIN,
)
from .types import MLN_SENSORS, MLNSensorEntityDescription
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
):
    """Setup sensors from a config entry created in the integrations UI."""
    config = hass.data[DOMAIN][entry.entry_id]
    mln_c = MLN.MLNc(hass)
    mln_device = WaterFilterDevice(config,mln_c)
    await mln_device.async_create_coordinator(hass)
    entities = []
    entities = [WaterFilterSensor(mln_device, description, hass) for description in MLN_SENSORS]
    async_add_entities(entities)


class WaterFilterDevice:
    def __init__(self, dataset, mln: MLN.MLNc) -> None:
         self._name = f"{CONF_DEVICE_NAME}: {dataset[CONF_CUSTOMER_ID]}"
         self._coordinator: DataUpdateCoordinator = None
         self._customer_id = dataset.get(CONF_CUSTOMER_ID) 
         # Lưu trữ ngày bắt đầu và vòng đời trong danh sách từ CONF_DATE_START và CONF_LIFE_CYCLE
         self.ls_dates = [dataset.get(CONF_DATE_START[i]) for i in range(12)]
         self.ls_life_cycles = [dataset.get(CONF_LIFE_CYCLE[i]) for i in range(12)]
         self._config_info = ""
         self._mln = mln  
         self._data = {}

    async def update(self) -> dict[str, Any]:
        """Calculate time when Cartridges has expired."""
        
        # Tạo danh sách các tham số để truyền vào hàm request_update
        params = [self._name]
        for date, life_cycle in zip(self.ls_dates, self.ls_life_cycles):
            params.extend([date, life_cycle])
        
        # Truyền tham số vào request_update bằng cách sử dụng *args
        self._data = await self._mln.request_update(*params)
        return self._data

    
    async def _async_update(self):
        """Fetch the latest data from MLN."""
        await self.update()     
    
    
    async def async_create_coordinator(self, hass: HomeAssistant) -> None:
        """Create the coordinator for this specific device."""
        #if self._coordinator:
         #   return

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{self._name}",
            update_method=self._async_update,
            update_interval=DEFAULT_SCAN_INTERVAL,         
        )  
        await coordinator.async_config_entry_first_refresh()
        self._coordinator = coordinator

    @property
    def info(self) -> DeviceInfo:
        """Return device description for device registry."""

        return DeviceInfo(
            name=self._name,
            identifiers={(DOMAIN, self._customer_id)},
            manufacturer=CONF_DEVICE_MANUFACTURER,
            sw_version=CONF_DEVICE_SW_VERSION,           
        )   
      
    @property
    def coordinator(self) -> DataUpdateCoordinator or None:
        """Return coordinator associated."""
        return self._coordinator
    

class WaterFilterSensor(CoordinatorEntity, SensorEntity):
    """Implementation of the MLN sensor."""

    def __init__(self, device: WaterFilterDevice, description: MLNSensorEntityDescription, hass):
        """Initialize the sensor."""
        super().__init__(device.coordinator)
        self._device = device
        self._attr_name = f"{device._name} {description.name}"
        self._unique_id = str(f"{device._customer_id}_{description.key}").lower()
        self._default_name = description.name
        self.entity_id = (
            f"{ENTITY_DOMAIN}.{device._customer_id}_{description.key}".lower()
        )
        self.entity_description = description
           
    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._unique_id
    
    @property
    def native_value(self):
        """Return the state of the sensor."""
        data = self.entity_description.value_fn(self._device._data)

        if self.entity_description.dynamic_name:
            self._attr_name = f"{self._default_name} {data.get('info')}"

        if self.entity_description.dynamic_icon:
            self._attr_icon = data.get("info")

        return data.get("value")

    @property
    def device_info(self):
        """Return a device description for device registry."""
        return self._device.info    

    

    


        
