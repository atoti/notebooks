import { WidgetPlugin, pluginWidgetKpi, pluginMenuItemRemoveWidget, pluginTitleBarButtonFullScreen, pluginTitleBarButtonToggleQueryMode, KpiWidgetState, CellSetSelection } from "@activeviam/activeui-sdk";
import { IconMatchup } from "./IconMatchup";

export const widgetKey = "matchup";

export const pluginWidgetMatchup: WidgetPlugin<KpiWidgetState, CellSetSelection> = {
  ...pluginWidgetKpi,
  Icon: IconMatchup,
  initialState: {
    ...pluginWidgetKpi.initialState,
    widgetKey
  },
  key: widgetKey,
  menuItems: [pluginMenuItemRemoveWidget.key],
  titleBarButtons: [
    pluginTitleBarButtonFullScreen.key,
    pluginTitleBarButtonToggleQueryMode.key,
  ],
  contextMenuItems: [],
  translations: {
    "en-US": {
      key: "Matchup",
      defaultName: "New Matchup"
    }
  },
}
