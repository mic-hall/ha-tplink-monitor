import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from datetime import timedelta
from .const import DOMAIN, CONF_IP, CONF_USERNAME, CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_MTU
from .tplink_monitor import fetch_port_statistics

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up TP-Link sensors from a config entry."""
    config = hass.data[DOMAIN][entry.entry_id]

    ip = config[CONF_IP]
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]
    scan_interval = config.get(CONF_SCAN_INTERVAL, 15)  # Default to 15s
    mtu = config.get(CONF_MTU, 1500)  # Default MTU

    coordinator = TPLinkCoordinator(hass, ip, username, password, scan_interval, mtu)

    sensors = [TplinkPortSensor(coordinator, port) for port in range(1, 17)]
    async_add_entities(sensors, True)


class TPLinkCoordinator(DataUpdateCoordinator):
    """Fetch TP-Link switch data at a configured interval asynchronously."""

    def __init__(self, hass, ip, username, password, scan_interval, mtu):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="TP-Link Bandwidth Monitor",
            update_interval=timedelta(seconds=scan_interval),
        )
        self.hass = hass
        self.ip = ip
        self.username = username
        self.password = password
        self.mtu = mtu

    async def _async_update_data(self):
        """Fetch latest switch statistics asynchronously using `requests`."""
        return await self.hass.async_add_executor_job(
            fetch_port_statistics, self.ip, self.username, self.password
        )


class TplinkPortSensor(CoordinatorEntity, Entity):
    """Representation of a TP-Link Switch Port Sensor."""

    def __init__(self, coordinator, port):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._port = port
        self._attr_name = f"Port {port} Bandwidth"
        self._prev_rx_good = None
        self._prev_tx_good = None
        self._rx_mbps = 0
        self._tx_mbps = 0
        self._attr_unit_of_measurement = "Mbps"
        self._attr_device_class = "data_rate"
        self._attr_state_class = "measurement"


    @property
    def state(self):
        """Return the calculated bandwidth in Mbps."""
        data = self.coordinator.data
        if not data or self._port not in data:            
            return 0

        # Get current packet count
        rx_good = data[self._port]["rx_good"]
        tx_good = data[self._port]["tx_good"]

        # Get the polling interval directly
        time_diff = self.coordinator.update_interval.total_seconds()

        # Check if this is the first run (no previous data)
        if self._prev_rx_good is None or self._prev_tx_good is None:
            self._prev_rx_good = rx_good
            self._prev_tx_good = tx_good            
            return 0  # No bandwidth calculation yet

        # Calculate packet difference
        rx_diff = rx_good - self._prev_rx_good
        tx_diff = tx_good - self._prev_tx_good

        # Convert packets to Mbps using MTU and known scan interval
        mtu = self.coordinator.mtu
        self._rx_mbps = (rx_diff * mtu * 8) / (time_diff * 1e6)
        self._tx_mbps = (tx_diff * mtu * 8) / (time_diff * 1e6)

        # Update stored values for next calculation
        self._prev_rx_good = rx_good
        self._prev_tx_good = tx_good

        return round(self._rx_mbps + self._tx_mbps, 2)

    @property
    def extra_state_attributes(self):
        """Return additional switch statistics."""
        data = self.coordinator.data
        if not data or self._port not in data:            
            return {}

        return {
            "state": data[self._port]["state"],
            "link_status": data[self._port]["link_status"],
            "rx_good": data[self._port]["rx_good"],
            "tx_good": data[self._port]["tx_good"],
            "rx_bad": data[self._port]["rx_bad"],
            "tx_bad": data[self._port]["tx_bad"],
            "rx_mbps": round(self._rx_mbps, 2),
            "tx_mbps": round(self._tx_mbps, 2),
        }
