import { WidgetPlugin } from "@activeviam/activeui-sdk";
import { IconOptimize } from "./IconOptimize";

import { Optimizer } from "./Optimizer";

const widgetKey = "optimizer";

export const pluginWidgetOptimizer: WidgetPlugin = {
    Component: Optimizer,
    Icon: IconOptimize,
    initialState: {
        widgetKey,
    },
    key: widgetKey,
    translations: {
        "en-US": {
            key: "Optimizer",
            defaultName: "Portfolio Optimizer"
        }
    }
};