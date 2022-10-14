import { WidgetPlugin } from "@activeviam/activeui-sdk";
import { IconPortfolioUploader } from "./IconPortfolioUploader";

import { PortfolioUploader } from "./PortfolioUploader";

const widgetKey = "portfolioUploader";

export const pluginWidgetUploader: WidgetPlugin = {
    Component: PortfolioUploader,
    Icon: IconPortfolioUploader,
    initialState: {
        widgetKey,
    },
    key: widgetKey,
    translations: {
        "en-US": {
            key: "PortfolioUploader",
            defaultName: "Upload portfolio",
        }
    }
};