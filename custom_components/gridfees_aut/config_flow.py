"""Configure a local tariff profile through the Home Assistant UI."""

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_EEG_TAX_EXEMPT,
    CONF_HOUSEHOLD,
    CONF_REGION,
    CONF_SNAP_ELIGIBLE,
    CONF_SUPPLY_TYPE,
    DOMAIN,
    REGIONS,
    SUPPLY_GRID,
    SUPPLY_LABELS,
    SUPPLY_TYPES,
)


class GridfeesAutConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Collect grid area, supply type and applicable tax assumptions."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the pending tariff profile."""
        self._profile: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select the tariff area and the energy allocation type."""
        if user_input is not None:
            self._profile = dict(user_input)
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
            profile = {**self._profile, **user_input}
            if profile[CONF_SUPPLY_TYPE] == SUPPLY_GRID:
                profile[CONF_EEG_TAX_EXEMPT] = False
            else:
                profile[CONF_SNAP_ELIGIBLE] = False

            if any(dict(entry.data) == profile for entry in self._async_current_entries()):
                return self.async_abort(reason="already_configured")

            return self.async_create_entry(
                title=(
                    f"{REGIONS[profile[CONF_REGION]]} · "
                    f"{SUPPLY_LABELS[profile[CONF_SUPPLY_TYPE]]}"
                ),
                data=profile,
            )

        fields: dict[Any, Any] = {
            vol.Required(CONF_HOUSEHOLD, default=True): selector.BooleanSelector(),
        }
        if self._profile[CONF_SUPPLY_TYPE] == SUPPLY_GRID:
            fields[vol.Required(CONF_SNAP_ELIGIBLE, default=True)] = (
                selector.BooleanSelector()
            )
        else:
            fields[vol.Required(CONF_EEG_TAX_EXEMPT, default=True)] = (
                selector.BooleanSelector()
            )

        return self.async_show_form(
            step_id="tariff", data_schema=vol.Schema(fields)
        )
