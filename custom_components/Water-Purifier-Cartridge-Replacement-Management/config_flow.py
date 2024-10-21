"""Config flow for Water Purifier Data integration."""

from __future__ import annotations

import logging

from typing import Any
from datetime import datetime
import datetime
import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_CUSTOMER_ID,
    CONF_LS_TOTAL,
    CONF_DATE_START,
    CONF_LIFE_CYCLE,
    DOMAIN, 
)

_LOGGER = logging.getLogger(__name__)

time_obj = datetime.datetime.now()
nDate = datetime.datetime.strptime(str(time_obj.date()), '%Y-%m-%d').strftime('%d/%m/%Y')

def Date(fmt='%Y-%m-%d'):
    return lambda v: datetime.strptime(v, fmt)

NAME_FIELD = vol.Schema(
    {
        vol.Required(CONF_CUSTOMER_ID): str,    
    }
)

LS_TOTAL_FIELD = vol.Schema(
    {
        vol.Required(CONF_LS_TOTAL): int,   
    }
)

DATE_START_FIELD = vol.Schema(    
    {       
        vol.Optional(field, default=""): str
        for field in CONF_DATE_START                   
    },  
)

LIFE_CYCLE_FIELD = vol.Schema(
    {
        vol.Required(field, default=0): vol.All(int, vol.Range(min=0, max=1000))
        for field in CONF_LIFE_CYCLE
    }
)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Config Flow for setting up this Integration."""

    VERSION = 1

    def __init__(self):
        self._user_data = {}
        self._errors = {}

    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        return await self.async_step_name_start()
    

    
    async def async_step_name_start(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle customer-id config flow by the user."""

        if user_input is not None:
            self._user_data[CONF_CUSTOMER_ID] = user_input[CONF_CUSTOMER_ID]
            return await self.async_step_date_start()
                           
        return self.async_show_form(
            step_id="name_start",
            data_schema=NAME_FIELD,
            errors=self._errors
        )
    
    async def async_step_date_start(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle date_start config flow by the user."""
        self._errors = {}
        
        if user_input is not None:
            for field in CONF_DATE_START:
                self._user_data[field] = user_input.get(field, None)              
            return await self.async_step_life_cycle()
                                                                                                           
        return self.async_show_form(
            step_id="date_start",
            data_schema=DATE_START_FIELD,
            errors=self._errors
        )    
    
    async def async_step_life_cycle(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle life_cycle config flow by the user."""

        if user_input is not None:
            for field in CONF_LIFE_CYCLE:
                self._user_data[field] = user_input.get(field, None)               
            await self.async_set_unique_id(self._user_data[CONF_CUSTOMER_ID])
            self._abort_if_unique_id_configured()         
            return self.async_create_entry(
                        title=self._user_data[CONF_CUSTOMER_ID], data=self._user_data
                    )

        return self.async_show_form(
            step_id="life_cycle",
            data_schema=LIFE_CYCLE_FIELD,
            errors=self._errors
        )    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(OptionsFlow):
    """HACS config flow options handler."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self._user_data = {}
        self._errors = {}
    
    async def async_step_init(
        self,
        user_input: dict[str, str] | None = None,
    ) -> ConfigFlowResult:
        """Manage the options."""
        return await self.async_step_date_start()
    
    async def async_step_date_start(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle date_start OptionsFlow config flow by the user."""

        if user_input is not None:
            for field in CONF_DATE_START:
                self._user_data[field] = user_input.get(field, None)                     
            return await self.async_step_life_cycle()
                
        schema_date_start = {
        vol.Optional(field, default=self.config_entry.data.get(field)): str
        for field in CONF_DATE_START
        }
              
        return self.async_show_form(
            step_id="date_start",
            data_schema=vol.Schema(schema_date_start),
            errors=self._errors
        )    
    
    async def async_step_life_cycle(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle life_cycle OptionsFlow config flow by the user."""
        self._user_data[CONF_CUSTOMER_ID] = self.config_entry.data.get(CONF_CUSTOMER_ID)
        if user_input is not None:
            for field in CONF_LIFE_CYCLE:
                self._user_data[field] = user_input.get(field, None)          
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=self._user_data              
            )   
            
            return self.async_create_entry(
                title=self.config_entry.title, data=self._user_data
            )
        
        schema_life_cycle = {
        vol.Optional(field, default=self.config_entry.data.get(field)): vol.All(int, vol.Range(min=0, max=1000))
        for field in CONF_LIFE_CYCLE
        }

        return self.async_show_form(
            step_id="life_cycle",
            data_schema=vol.Schema(schema_life_cycle),
            errors=self._errors
        )      
    
    

       
