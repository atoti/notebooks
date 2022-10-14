import _ from "lodash";

const getUrlFrom = (serverKey: string): string => {
  return _.get(window, ["env", "activePivotServers", serverKey, "url"], "");
};

export default getUrlFrom;