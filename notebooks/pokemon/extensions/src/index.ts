import { ExtensionModule } from "@activeviam/activeui-sdk";
import { pluginWidgetBattle } from "./battle/pluginWidgetBattle";
import { pluginWidgetHistory } from "./history/pluginWidgetHistory";
import { pluginWidgetMatchup } from "./matchup/pluginWidgetMatchup";

const extension: ExtensionModule = {
  async activate(configuration) {
    
    configuration.pluginRegistry.widget![pluginWidgetBattle.key] = pluginWidgetBattle;
    configuration.pluginRegistry.widget![pluginWidgetHistory.key] = pluginWidgetHistory;
    configuration.pluginRegistry.widget![pluginWidgetMatchup.key] = pluginWidgetMatchup;
  },
};

// ActiveUI expects a default export.
// eslint-disable-next-line import/no-default-export
export default extension;
