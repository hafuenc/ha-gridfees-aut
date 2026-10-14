"""Configure a local tariff profile through the Home Assistant UI."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .calculator import TariffProfile
from .const import (
    CONF_HOUSEHOLD,
    CONF_REGION,
    CONF_SNAP_ELIGIBLE,
    CONF_SUPPLY_TYPE,
    DOMAIN,
    REGIONS,
    SUPPLY_GRID,
    SUPPLY_TYPES,
    profile_title,
)


class GridfeesAutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Collect grid area, supply type and applicable tax assumptions."""

    VERSION = 1
    MINOR_VERSION = 2

    def __init__(self) -> None:
        """Initialize the pending tariff profile."""
        self._profile: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select the tariff area and the energy allocation type."""
        if user_input is not None:
            self._profile = dict(user_input)
            if self._profile[CONF_SUPPLY_TYPE] != SUPPLY_GRID:
                return self._create_profile()
            return await self.async_step_tariff()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_REGION): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                {"value": code, "label": name}
                                for code, name in REGIONS.items()
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_SUPPLY_TYPE, default=SUPPLY_GRID): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=list(SUPPLY_TYPES),
                            translation_key="supply_type",
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_tariff(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Ask only for assumptions that apply to this supply type."""
        if user_input is not None:
            return self._create_profile(user_input)

        fields: dict[Any, Any] = {
            vol.Required(CONF_HOUSEHOLD, default=True): selector.BooleanSelector(),
        }
        fields[vol.Required(CONF_SNAP_ELIGIBLE, default=True)] = (
            selector.BooleanSelector()
        )

        return self.async_show_form(
            step_id="tariff",
            data_schema=vol.Schema(fields),
            description_placeholders={
                "elabgg_url": "https://ris.bka.gv.at/eli/bgbl/1996/201/P7/NOR40273847",
                "stromkostenzuschuss_url": "https://www.ris.bka.gv.at/eli/bgbl/i/2022/156/P4/NOR40250760",
            },
        )

    def _create_profile(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Create a normalized profile and reject equivalent legacy profiles."""
        profile = TariffProfile.from_config({**self._profile, **(user_input or {})})
        if any(
            TariffProfile.from_config(entry.data) == profile
            for entry in self._async_current_entries()
        ):
            return self.async_abort(reason="already_configured")
        return self.async_create_entry(
            title=profile_title(profile.region, profile.supply_type),
            data=profile.as_config(),
        )
