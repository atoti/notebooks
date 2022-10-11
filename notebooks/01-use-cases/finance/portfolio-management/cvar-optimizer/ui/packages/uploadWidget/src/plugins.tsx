import _keyBy from "lodash/keyBy";
import _merge from "lodash/merge";
import {
    PluginRegistry,
    WidgetPlugin,
  } from "@activeviam/activeui-sdk";
import { pluginWidgetUploader } from "./pluginUploadWidget/pluginPortfolioUploader";

const pluginWidgetTextEditorExtended = {
  ...pluginWidgetUploader,
  menuItems: ["remove-widget"]
};


// Order matters: it controls the order of the icons in the widget ribbons.
const widgetPlugins: Array<WidgetPlugin<any, any>> = [
  pluginWidgetTextEditorExtended
];


const plugins: PluginRegistry = {
  widget: _keyBy(widgetPlugins, "key"),
};


export const registerPlugins = (pluginRegistry:PluginRegistry): void => {
  _merge(pluginRegistry.widget, plugins.widget);
}