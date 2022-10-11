'use strict';

Object.defineProperty(exports, '__esModule', { value: true });

var activeuiSdk = require('@activeviam/activeui-sdk');
var dataModel = require('@activeviam/data-model');
var mdx = require('@activeviam/mdx');
var react = require('react');

function isExplicitMemberPayload(payload) {
  return payload.type === "explicit-members";
}
/**
 * Create a location payload from the arguments.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @param members members of the location (can be an empty list).
 * @param cube cube object from the props of the context menu.
 * @returns a locationPayload.
 */

function createExplicitMemberPayload(dimensionName, hierarchyName, members, slicing, cube) {
  const dimension = activeuiSdk.getDimension(dimensionName, cube);
  const hierarchy = activeuiSdk.getHierarchy({
    dimensionName,
    hierarchyName
  }, cube);
  const levelCoordinates = dataModel.getLevelCoordinates({
    dimension,
    hierarchy
  });
  const firstLevel = activeuiSdk.getLevel(levelCoordinates, cube);
  const childrenLevels = dataModel.getChildrenLevels(levelCoordinates, cube);

  if (members.length > 0) {
    const levels = [firstLevel];

    for (let i = 0; i < members.length - 1; i++) {
      levels.push(childrenLevels[i]);
    }

    return {
      dimension: dimension,
      hierarchy: hierarchy,
      levels: levels,
      members: [members],
      slicing: slicing,
      type: "explicit-members"
    };
  }

  return undefined;
}
/**
 * Parse the MdxCompoundIdentifier to a LocationPayload object.
 * @param mdx the mdxCompoundIdentifier containing an explicit filter.
 * @param cube cube object from the props of the context menu.
 * @returns the locationPayload parsed.
 */


function createLocationPayloadFromCompoundIdentifier(mdx, cube) {
  if (mdx.identifiers.length > 2) {
    const dimensionName = mdx.identifiers[0].value;
    const hierarchyName = mdx.identifiers[1].value;
    const members = [];
    let slicing = true;

    for (let i = 2; i < mdx.identifiers.length; i++) {
      const value = mdx.identifiers[i].value;

      if (value !== "AllMember" && value !== "ALL") {
        members.push(value);
      } else {
        slicing = false;
      }
    }

    return createExplicitMemberPayload(dimensionName, hierarchyName, members, slicing, cube);
  }

  return undefined;
}

function createMdxLocationPayload(mdx$1, cube) {
  if (mdx.isMdxFunction(mdx$1, "filter")) {
    const [membersNode] = mdx$1.arguments;

    if (mdx.isMdxFunction(membersNode, "members")) {
      const compoundIdentifier = membersNode.arguments[0];
      const specificCompoundIdentifier = mdx.getSpecificCompoundIdentifier(compoundIdentifier, {
        cube
      });

      if (specificCompoundIdentifier.type !== "level") {
        return undefined;
      }

      const {
        dimensionName,
        hierarchyName,
        levelName
      } = specificCompoundIdentifier;
      const dimension = activeuiSdk.getDimension(dimensionName, cube);
      const hierarchy = activeuiSdk.getHierarchy({
        dimensionName,
        hierarchyName
      }, cube);
      const levelCoordinates = dataModel.getLevelCoordinates({
        dimension,
        hierarchy
      });
      const firstLevel = activeuiSdk.getLevel(levelCoordinates, cube);
      const childrenLevels = dataModel.getChildrenLevels(levelCoordinates, cube);
      const levels = [firstLevel];

      if (firstLevel.name !== levelName) {
        for (let level of childrenLevels) {
          if (level.name !== levelName) {
            levels.push(level);
          } else {
            levels.push(level);
            break;
          }
        }
      }

      return {
        dimension,
        hierarchy,
        levels,
        slicing: false,
        mdx: mdx$1,
        type: "mdx"
      };
    }
  }

  if (mdx.isMdxFunction(mdx$1) && ["topcount", "topsum", "toppercent", "bottomcount", "bottomsum", "bottompercent"].includes(mdx$1.name.toLowerCase())) {
    const firstArgumentOfFilter = mdx$1.arguments[0].arguments[0];
    const scope = firstArgumentOfFilter.name.toLowerCase() === "children" ? "ofEachParent" : "overall";
    const hierarchyCompoundIdentifier = firstArgumentOfFilter.arguments[0].arguments[0];
    const [{
      dimensionName,
      hierarchyName
    }] = mdx.getHierarchies(hierarchyCompoundIdentifier, {
      cube
    });
    const levelIndex = scope === "overall" ? parseInt(firstArgumentOfFilter.arguments[0].arguments[1].value, 10) : 0;
    const dimension = activeuiSdk.getDimension(dimensionName, cube);
    const hierarchy = activeuiSdk.getHierarchy({
      dimensionName,
      hierarchyName
    }, cube);
    const levelCoordinates = dataModel.getLevelCoordinates({
      dimension,
      hierarchy
    });
    const firstLevel = activeuiSdk.getLevel(levelCoordinates, cube);
    const childrenLevels = dataModel.getChildrenLevels(levelCoordinates, cube);
    const levels = [firstLevel];

    for (let i = 1; i < levelIndex; i++) {
      levels.push(childrenLevels[i]);
    }

    return {
      dimension,
      hierarchy,
      levels,
      slicing: false,
      mdx: mdx$1,
      type: "mdx"
    };
  }

  return undefined;
}
/**
 * Retrieves the location payload of the default filters from the cube.
 * In case those filtesr are already within the widget filters, they won't be express here.
 * @param cube cube object from the props of the context menu.
 * @returns the default filters parsed.
 */


function parseDefaultFilters(cube) {
  //@ts-ignore
  const mapResult = new Map();
  const defaultFilters = cube.defaultMembers;

  if (!defaultFilters) {
    return mapResult;
  }

  defaultFilters.filter(value => value.dimension !== "Measures").forEach(value => {
    const dimensionName = value.dimension;
    const hierarchyName = value.hierarchy;
    const members = value.path.filter(val => val !== "AllMember" && val !== "ALL");
    const slicing = !value.path.some(val => val === "AllMember" || val === "ALL");
    const locationPayload = createExplicitMemberPayload(dimensionName, hierarchyName, members, slicing, cube);

    if (locationPayload) {
      if (members.length > 0) {
        const key = dimensionName + "|" + hierarchyName + "|" + locationPayload.levels.length; // Do not take the default filters that has been override by the widget filters

        const oldResult = mapResult.get(key);

        if (oldResult !== undefined) {
          if (isExplicitMemberPayload(oldResult)) {
            oldResult.members.forEach(m => locationPayload.members.push(m));
          }
        }

        mapResult.set(key, locationPayload);
      }
    }
  });
  return mapResult;
}

function transformFilters(filters, cube) {
  if (!filters) {
    return new Map();
  }

  const mapResult = new Map();
  filters.filter(mdx => !(typeof mdx === 'string')) //@ts-ignore
  .forEach(mdx => {
    let added = false;

    if (mdx.elementType === "CompoundIdentifier") {
      const locationPayload = createLocationPayloadFromCompoundIdentifier(mdx, cube);

      if (locationPayload) {
        const key = locationPayload.dimension.name + "|" + locationPayload.hierarchy.name + "|" + locationPayload.levels.length;
        const oldResult = mapResult.get(key);

        if (oldResult !== undefined) {
          if (isExplicitMemberPayload(oldResult)) {
            oldResult.members.forEach(m => locationPayload.members.push(m));
          }
        }

        mapResult.set(key, locationPayload);
        added = true;
      }
    }

    if (mdx.elementType === "Function") {
      mdx.arguments.forEach(arg => {
        if (arg.elementType === "CompoundIdentifier") {
          const locationPayload = createLocationPayloadFromCompoundIdentifier(arg, cube); // case multiple compound identifier for one level, aka multiple members filtered for one level.

          if (locationPayload !== undefined) {
            const key = locationPayload.dimension.name + "|" + locationPayload.hierarchy.name + "|" + locationPayload.levels.length;
            const oldResult = mapResult.get(key);

            if (oldResult) {
              if (isExplicitMemberPayload(oldResult)) {
                oldResult.members.forEach(m => locationPayload.members.push(m));
              }
            }

            mapResult.set(key, locationPayload);
            added = true;
          }
        }
      });
    }

    if (!added) {
      const locationPayload = createMdxLocationPayload(mdx, cube);

      if (locationPayload) {
        const key = locationPayload.dimension.name + "|" + locationPayload.hierarchy.name + "|" + locationPayload.levels.length;
        mapResult.set(key, locationPayload);
        added = true;
      }
    }
  });
  return mapResult;
}

function parseAndMergeFilters(dashboardFilters, pageFilters, widgetFilters, cube) {
  // const defaultFilters: DefaultMember[] | undefined = cube.defaultMembers;
  const result = new Map(); //parseDefaultFilters(defaultFilters, cube);

  const dashboardFiltersParsed = transformFilters(dashboardFilters, cube);
  const pageFiltersParsed = transformFilters(pageFilters, cube);
  const widgetFiltersParsed = transformFilters(widgetFilters, cube);
  dashboardFiltersParsed.forEach((val, key) => result.set(key, val));
  pageFiltersParsed.forEach((val, key) => result.set(key, val));
  widgetFiltersParsed.forEach((val, key) => result.set(key, val));
  return result;
}
/**
 * Retrieve the measures parsed from the member cell location.
 * @param member member of the cell location.
 * @param cube cube of widget.
 * @returns the measures parsed from the member cell location.
 */

function transformMemberToMeasure(member, cube) {
  const measures = member.tuple.filter(value => value.dimensionName == "Measures").map(value => activeuiSdk.getMeasure(value.captionPath[0], cube));

  if (!measures || measures.length === 0 || measures[0] === undefined || !member.value && member.value !== 0) {
    return undefined;
  }

  return {
    measure: measures[0],
    value: member.value
  };
}
/**
 * Take a position from the selection and create a location info.
 * It add the default filters and widget filter that have been updated so that if a point is present within the position, 
 * this point won't be duplicated on the filters neither on default filters. 
 * @param position The position from the selection.
 * @param filtersMap list of filters from the widget state.
 * @param cube cube of the widget.
 * @param measure measure and its value for this position.
 * @returns a location info.
 */

function transformPositionToLocationInfo(position, filtersMap, cube, measure) {
  const locations = [];
  position.forEach(tuple => {
    if (tuple.dimensionName != "Measures") {
      const dimensionName = tuple.dimensionName;
      const hierarchyName = tuple.hierarchyName;
      const members = tuple.captionPath.filter(member => member !== "AllMember" && member !== "ALL");
      const slicing = !tuple.captionPath.some(val => val === "AllMember" || val === "ALL");
      const locationPayload = createExplicitMemberPayload(dimensionName, hierarchyName, members, slicing, cube);

      if (locationPayload && members.length > 0) {
        // const key:string = dimensionName + "|" + hierarchyName + "|" + locationPayload.levels.length;
        // filtersMap.delete(key);
        locations.push(locationPayload);
      }
    }
  });
  const filters = Array.from(filtersMap).map(([key, value]) => value);
  const defaultFiltersMap = parseDefaultFilters(cube);
  const defaults = Array.from(defaultFiltersMap).filter(value => !filters.some(filter => `${filter.dimension.name}|${filter.hierarchy.name}|${filter.levels.length}` === value[0]) && !locations.some(filter => `${filter.dimension.name}|${filter.hierarchy.name}|${filter.levels.length}` === value[0])).map(value => value[1]);
  return {
    defaults: defaults,
    locations: locations,
    filters: filters,
    measure: measure
  };
}
/**
 * Parse a location Payload to a filter on member object.
 * @param locationPayload a location payload.
 * @returns the location payload parsed to a filter on member.
 */

function parsePayloadToFilter(locationPayload, cube) {
  return isExplicitMemberPayload(locationPayload) ? {
    dimensionName: locationPayload.dimension.name,
    hierarchyName: locationPayload.hierarchy.name,
    members: locationPayload.members.map(m => locationPayload.slicing ? m : ["AllMember", ...m]),
    type: "members"
  } : activeuiSdk.createFilter(locationPayload.mdx, cube);
}

/**
 * Test if the selection is only on axis or not.
 * @param selection selection of the context menu.
 * @returns true if some of the selection is only on axis.
 */
function isOnAxisOnly(selection) {
  return selection.cells === undefined || selection.cells.length === 0;
}
/**
 * Parse the selection into a list of location info.
 * @param selection selection of the context menu.
 * @param widgetFilters widget filters or undefined.
 * @param pageFilters page filters or undefined.
 * @param dashboardFilters dashboard filters or undefined.
 * @param cube cube of the widget selected.
 * @returns a list of location info.
 */

function parseSelectionToLocationInfo(selection, widgetFilters, pageFilters, dashboardFilters, cube) {
  const filters = parseAndMergeFilters(dashboardFilters, pageFilters, widgetFilters, cube);

  if (selection && isOnAxisOnly(selection)) {
    var _selection$axes;

    const result = [];
    ((_selection$axes = selection.axes) !== null && _selection$axes !== void 0 ? _selection$axes : []).forEach(axisSelection => {
      var _axisSelection$positi;

      return ((_axisSelection$positi = axisSelection.positions) !== null && _axisSelection$positi !== void 0 ? _axisSelection$positi : []).forEach(position => result.push(transformPositionToLocationInfo(position, filters, cube)));
    });
    return result;
  }

  const result = [];

  if (selection && selection.cells) {
    selection.cells.forEach(member => {
      const measure = transformMemberToMeasure(member, cube);
      const locationInfo = transformPositionToLocationInfo(member.tuple, filters, cube, measure);
      result.push(locationInfo);
    });
    return result;
  }

  if (filters.size == 0) {
    return [];
  }

  const defaultFiltersMap = parseDefaultFilters(cube);
  const defaults = Array.from(defaultFiltersMap).filter(value => !Array.from(filters).some(filter => `${filter[1].dimension.name}|${filter[1].hierarchy.name}|${filter[1].levels.length}` === value[0])).map(value => value[1]);
  return [{
    defaults: defaults,
    filters: Array.from(filters).map(([key, value]) => value)
  }];
}
/**
 * Test if a dimension is present within the location infos.
 * @param locations locations of the selection.
 * @param dimensionName name of the dimension.
 * @returns true if the dimension is within at least one of the locations.
 */

function isDimensionWithinLocationInfo(locations, dimensionName) {
  return locations.some(loc => {
    var _loc$defaults, _loc$locations, _loc$filters;

    return ((_loc$defaults = loc.defaults) === null || _loc$defaults === void 0 ? void 0 : _loc$defaults.some(l => isExplicitMemberPayload(l) && l.dimension.name === dimensionName)) || ((_loc$locations = loc.locations) === null || _loc$locations === void 0 ? void 0 : _loc$locations.some(l => isExplicitMemberPayload(l) && l.dimension.name === dimensionName)) || ((_loc$filters = loc.filters) === null || _loc$filters === void 0 ? void 0 : _loc$filters.some(f => isExplicitMemberPayload(f) && f.dimension.name === dimensionName));
  });
}
/**
 * Test if a hierarchy is present within the location infos.
 * @param locations locations of the selection.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @returns true if the hierarchy is within at least one of the locations.
 */

function isHierarchyWithinLocationInfo(locations, dimensionName, hierarchyName) {
  return locations.some(loc => {
    var _loc$defaults2, _loc$locations2, _loc$filters2;

    return ((_loc$defaults2 = loc.defaults) === null || _loc$defaults2 === void 0 ? void 0 : _loc$defaults2.some(l => isExplicitMemberPayload(l) && l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName)) || ((_loc$locations2 = loc.locations) === null || _loc$locations2 === void 0 ? void 0 : _loc$locations2.some(l => isExplicitMemberPayload(l) && l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName)) || ((_loc$filters2 = loc.filters) === null || _loc$filters2 === void 0 ? void 0 : _loc$filters2.some(f => isExplicitMemberPayload(f) && f.dimension.name === dimensionName && f.hierarchy.name === hierarchyName));
  });
}
/**
 * Test if a level is present within the location infos.
 * @param locations locations of the selection.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @param levelName name of the level.
 * @returns true if the level is within at least one of the locations.
 */

function isLevelWithinLocationInfo(locations, dimensionName, hierarchyName, levelName) {
  return locations.some(loc => {
    var _loc$defaults3, _loc$locations3, _loc$filters3;

    return ((_loc$defaults3 = loc.defaults) === null || _loc$defaults3 === void 0 ? void 0 : _loc$defaults3.some(l => isExplicitMemberPayload(l) && l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName && l.levels.some(lvl => lvl.name === levelName))) || ((_loc$locations3 = loc.locations) === null || _loc$locations3 === void 0 ? void 0 : _loc$locations3.some(l => isExplicitMemberPayload(l) && l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName && l.levels.some(lvl => lvl.name === levelName))) || ((_loc$filters3 = loc.filters) === null || _loc$filters3 === void 0 ? void 0 : _loc$filters3.some(f => isExplicitMemberPayload(f) && f.dimension.name === dimensionName && f.hierarchy.name === hierarchyName && f.levels.some(lvl => lvl.name === levelName)));
  });
}
/**
 * Retrieve all present members of the level passed.
 * @param locations locations from the selection parsed.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @param levelName name of the level.
 * @returns all the member for this level.
 */

function retrieveMembersOfLevelFromLocationInfo(locations, dimensionName, hierarchyName, levelName) {
  const result = [];
  locations.filter(loc => {
    var _loc$defaults4, _loc$locations4, _loc$filters4;

    return ((_loc$defaults4 = loc.defaults) === null || _loc$defaults4 === void 0 ? void 0 : _loc$defaults4.some(l => l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName && l.levels.some(lvl => lvl.name === levelName))) || ((_loc$locations4 = loc.locations) === null || _loc$locations4 === void 0 ? void 0 : _loc$locations4.some(l => l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName && l.levels.some(lvl => lvl.name === levelName))) || ((_loc$filters4 = loc.filters) === null || _loc$filters4 === void 0 ? void 0 : _loc$filters4.some(f => f.dimension.name === dimensionName && f.hierarchy.name === hierarchyName && f.levels.some(lvl => lvl.name === levelName)));
  }).forEach(loc => {
    var _loc$locations5;

    let added = false;
    ((_loc$locations5 = loc.locations) !== null && _loc$locations5 !== void 0 ? _loc$locations5 : []).forEach(l => {
      if (isExplicitMemberPayload(l)) {
        if (l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName) {
          const index = l.levels.findIndex(level => level.name === levelName);

          if (index !== -1 && l.members !== undefined) {
            var _l$members;

            added = true;
            ((_l$members = l.members) !== null && _l$members !== void 0 ? _l$members : []).forEach(m => result.push(m.slice(0, index + 1)));
          }
        }
      }
    });

    if (!added) {
      var _loc$filters5;

      ((_loc$filters5 = loc.filters) !== null && _loc$filters5 !== void 0 ? _loc$filters5 : []).forEach(f => {
        if (isExplicitMemberPayload(f)) {
          if (f.dimension.name === dimensionName && f.hierarchy.name === hierarchyName) {
            const index = f.levels.findIndex(level => level.name === levelName);

            if (index !== -1) {
              if (!added) {
                var _f$members;

                ((_f$members = f.members) !== null && _f$members !== void 0 ? _f$members : []).forEach(m => result.push(m.slice(0, index + 1)));
              }

              added = true;
            }
          }
        }
      });
    }

    if (!added) {
      var _loc$defaults5;

      ((_loc$defaults5 = loc.defaults) !== null && _loc$defaults5 !== void 0 ? _loc$defaults5 : []).forEach(f => {
        if (isExplicitMemberPayload(f)) {
          if (f.dimension.name === dimensionName && f.hierarchy.name === hierarchyName) {
            const index = f.levels.findIndex(level => level.name === levelName);

            if (index !== -1) {
              if (!added) {
                var _f$members2;

                ((_f$members2 = f.members) !== null && _f$members2 !== void 0 ? _f$members2 : []).forEach(m => result.push(m.slice(0, index + 1)));
              }

              added = true;
            }
          }
        }
      });
    }
  });
  return result;
}
/**
 * Retrieve filter member from location and/or mdx filters accordingly to the parameters passed.
 * Method used for the story telling action.
 * @param locations location info parsed from the payload.
 * @param fromSelection if selection locations will be put within this result.
 * @param fromFilters if widget filter will be put within this result.
 * @param cube cube of the selection.
 * @returns the list of filter members and mdx filters parsed.
 */

function getFiltersFromLocations(locations, fromSelection, fromFilters, cube) {
  const result = [];
  const mergedLocationPayloads = {};

  if (fromFilters) {
    locations.forEach(locationInfo => {
      var _locationInfo$filters;

      return [...((_locationInfo$filters = locationInfo.filters) !== null && _locationInfo$filters !== void 0 ? _locationInfo$filters : [])].forEach(locationPayload => {
        const key = `${locationPayload.dimension.name}|${locationPayload.hierarchy.name}|${locationPayload.levels[locationPayload.levels.length - 1].name}`;
        const mergedLocationPayload = mergedLocationPayloads[key];

        if (isExplicitMemberPayload(locationPayload)) {
          if (mergedLocationPayload !== undefined) {
            if (isExplicitMemberPayload(mergedLocationPayload)) {
              if (locationPayload.slicing) {
                mergedLocationPayload.members = locationPayload.members;
              } else {
                const newMembersToUpdate = [...mergedLocationPayload.members];
                let newMembers = locationPayload.members;
                newMembers.forEach(newMember => {
                  if (!newMembersToUpdate.some(member => JSON.stringify(member) == JSON.stringify(newMember))) {
                    mergedLocationPayload.members.push(newMember);
                  }
                });
              }
            }
          }
        }

        mergedLocationPayloads[key] = locationPayload;
      });
    });
  }

  if (fromSelection) {
    locations.forEach(locationInfo => {
      var _locationInfo$locatio;

      return (_locationInfo$locatio = locationInfo.locations) === null || _locationInfo$locatio === void 0 ? void 0 : _locationInfo$locatio.forEach(locationPayload => {
        if (isExplicitMemberPayload(locationPayload)) {
          const key = `${locationPayload.dimension.name}|${locationPayload.hierarchy.name}|${locationPayload.levels[locationPayload.levels.length - 1].name}`;
          const mergedLocationPayload = mergedLocationPayloads[key];

          if (mergedLocationPayload !== undefined) {
            if (isExplicitMemberPayload(mergedLocationPayload)) {
              const newMembersToUpdate = [...mergedLocationPayload.members];
              let newMembers = locationPayload.members;
              newMembers.forEach(newMember => {
                if (!newMembersToUpdate.some(member => JSON.stringify(member) == JSON.stringify(newMember))) {
                  mergedLocationPayload.members.push(newMember);
                }
              });
              mergedLocationPayloads[key] = mergedLocationPayload;
            } else {
              mergedLocationPayloads[key] = locationPayload;
            }
          } else {
            mergedLocationPayloads[key] = locationPayload;
          }
        }
      });
    });
  }

  Object.entries(mergedLocationPayloads).forEach(val => result.push(parsePayloadToFilter(val[1], cube)));
  return result;
}

const TOKEN_STORAGE_KEY = "activeui-token";

const getToken = () => {
  const {
    localStorage
  } = window;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
};

const useSecurityRequestOptions = () => {
  const token = getToken();
  const requestOptions = react.useMemo(() => {
    return !token ? {} : {
      headers: {
        authorization: `Jwt ${token}`
      }
    };
  }, [token]);
  return requestOptions;
};
const DefaultHeaders = {
  "Content-Type": "application/json",
  Accept: "application/json"
};
const createSecureRestQuerierFrom = requestOptions => {
  const mergedHeaders = headers => {
    let mutatingHeaders = headers;

    if (requestOptions) {
      mutatingHeaders = { ...headers,
        ...requestOptions.headers
      };
    }

    return mutatingHeaders;
  };

  return {
    getRequest: url => {
      return fetch(url, requestOptions);
    },
    deleteRequest: url => {
      const requestionOptions = { ...requestOptions,
        method: "DELETE"
      };
      return fetch(url, requestionOptions);
    },
    postJSONRequest: (url, body, headers = DefaultHeaders) => {
      const requestionOptions = { ...requestOptions,
        headers: mergedHeaders(headers),
        method: "POST",
        body: JSON.stringify(body)
      };
      return fetch(url, requestionOptions);
    },
    putJSONRequest: (url, body, headers = DefaultHeaders) => {
      const requestionOptions = { ...requestOptions,
        headers: mergedHeaders(headers),
        method: "PUT",
        body: JSON.stringify(body)
      };
      return fetch(url, requestionOptions);
    },
    postRawRequest: (url, body, headers) => fetch(url, { ...requestOptions,
      headers: mergedHeaders(headers),
      method: "POST",
      body
    }),
    putRawRequest: (url, body, headers) => fetch(url, { ...requestOptions,
      headers: mergedHeaders(headers),
      method: "PUT",
      body
    })
  };
};
/**
 * React Hook returning a service for querying rest endpoints on the server.
 */

const useSecureRestQuerier = () => {
  const requestInit = useSecurityRequestOptions();
  return react.useMemo(() => createSecureRestQuerierFrom(requestInit), [requestInit]);
};

exports.createSecureRestQuerierFrom = createSecureRestQuerierFrom;
exports.getFiltersFromLocations = getFiltersFromLocations;
exports.isDimensionWithinLocationInfo = isDimensionWithinLocationInfo;
exports.isHierarchyWithinLocationInfo = isHierarchyWithinLocationInfo;
exports.isLevelWithinLocationInfo = isLevelWithinLocationInfo;
exports.isOnAxisOnly = isOnAxisOnly;
exports.parseSelectionToLocationInfo = parseSelectionToLocationInfo;
exports.retrieveMembersOfLevelFromLocationInfo = retrieveMembersOfLevelFromLocationInfo;
exports.useSecureRestQuerier = useSecureRestQuerier;
exports.useSecurityRequestOptions = useSecurityRequestOptions;
