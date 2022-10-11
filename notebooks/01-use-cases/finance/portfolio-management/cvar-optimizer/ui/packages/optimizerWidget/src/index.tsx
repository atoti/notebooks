import {
  ExtensionModule,
} from "@activeviam/activeui-sdk";
import { registerPlugins } from "./plugins";

const extension: ExtensionModule = {
  async activate(configuration) {
      registerPlugins(configuration.pluginRegistry);
  },
};

// ActiveUI expects a default export.
// eslint-disable-next-line import/no-default-export
export default extension;