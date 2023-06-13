import _keyBy from "lodash/keyBy";
import _merge from "lodash/merge";
import {
  PluginRegistry,
  WidgetPlugin,
} from "@activeviam/activeui-sdk";
import { pluginWidgetBattle } from "./battle/pluginWidgetBattle";
import { pluginWidgetHistory } from "./history/pluginWidgetHistory";
import { pluginWidgetMatchup } from "./matchup/pluginWidgetMatchup";


// Order matters: it controls the order of the icons in the widget ribbons.
const widgetPlugins: Array<WidgetPlugin<any, any>> = [
  pluginWidgetBattle,
  pluginWidgetHistory,
  pluginWidgetMatchup
];


const plugins: PluginRegistry = {
  widget: _keyBy(widgetPlugins, "key"),
};


export const registerPlugins = (pluginRegistry: PluginRegistry): void => {
  _merge(pluginRegistry.widget, plugins.widget);
}