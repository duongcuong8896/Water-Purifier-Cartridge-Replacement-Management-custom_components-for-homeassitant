"""Setup and manage the MLN."""

from datetime import datetime
import logging
from typing import Any
import datetime
from homeassistant.components import persistent_notification
from homeassistant.core import HomeAssistant
from .const import (
ID_REMAIN_TIMES,
)

_LOGGER = logging.getLogger(__name__)

class MLNc:
    def __init__(self, hass: HomeAssistant):     
        self.hass = hass  
        self._notify_bufer = ""
       
        """Construct MLN wrapper."""
    async def request_update(self, name_device, *args) -> dict[str, Any]:
        fetch_data = {}
        self._notify_buffer = ""

        # Duyệt qua từng cartridge
        for index in range(12):
            date_start = args[index * 2]  # Lấy date_start
            life_cycle = args[index * 2 + 1]  # Lấy life_cycle

            # Tính toán thời gian còn lại
            str_remain_date, month_remain = calculator_date_remain(date_start, life_cycle)

            # Cập nhật dữ liệu vào fetch_data
            fetch_data[ID_REMAIN_TIMES[index]] = {
                "value": str_remain_date,
                "info": check_value_info(date_start),
            }

            # Kiểm tra xem cartridge đã hết hạn chưa
            if month_remain < 0:
                self._notify_buffer += (
                    f"Water Purifier Cartridge {index + 1} which was replaced on {date_start} has expired. Please replace it!\n"
                )

        # Gửi thông báo nếu có cartridge đã hết hạn
        if self._notify_buffer:
            notify_delivered(self.hass, name_device, self._notify_buffer)

        return fetch_data   
   
def check_value_info(date_start):
        start_date = ""
        if date_start != '':
             start_date = date_start
        else:
             start_date = "None"     
        return start_date         
    
def calculator_date_remain(date_start, life_cycle):  
        str_remain_date = ""
        days = 0
        month_remain = 0
        if date_start != '':
            try:
                nDate = datetime.datetime.strptime(date_start, '%Y-%m-%d')
                days = ( datetime.datetime.now() - nDate)

                remain_days  = days.days
                days_cycle = life_cycle * 30
                days_remain_cycle = days_cycle - remain_days
                month_remain = days_remain_cycle // 30
                days_remain = days_remain_cycle - (month_remain * 30)
                 
                str_remain_date = str(month_remain) + " month " + str(days_remain) + " days "
            except Exception as e: 
                 str_remain_date = "Error Date Input"  
                 month_remain = 0  
        else:
             str_remain_date = "None"            
        return str_remain_date, month_remain

def notify_delivered(hass: HomeAssistant, name_device: str, message: str):
    """Notify when Cartridges has expired."""
    message = message
    title = name_device
    notification_id = name_device

    persistent_notification.create(
        hass, message, title=title, notification_id=notification_id
    )
