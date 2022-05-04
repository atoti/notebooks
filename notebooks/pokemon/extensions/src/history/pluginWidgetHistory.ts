import { pluginMenuItemRemoveWidget, pluginTitleBarButtonFullScreen, WidgetPlugin } from "@activeviam/activeui-sdk";
import { History } from "./History";
import { IconHistory } from "./IconHistory";

const widgetKey = "history";

export const pluginWidgetHistory: WidgetPlugin = {
  Component: History,
  Icon: IconHistory,
  initialState: {
    widgetKey
  },
  key: widgetKey,
  menuItems: [pluginMenuItemRemoveWidget.key],
  titleBarButtons: [pluginTitleBarButtonFullScreen.key],
  contextMenuItems: [],
  translations: {
    "en-US": {
      key: "History",
      defaultName: "New History"
    }
  },
}
