import { CellSetSelection, Cube, Tuple, MdxString, Mdx, Filter } from "@activeviam/activeui-sdk";
import { transformPositionToLocationInfo, transformMemberToMeasure, parsePayloadToFilter, parseAndMergeFilters, isExplicitMemberPayload, parseDefaultFilters } from "./impl/utils";
import { LocationInfo, MeasurePayload, Payload } from "./payloadUtils.types";

/**
 * Test if the selection is only on axis or not.
 * @param selection selection of the context menu.
 * @returns true if some of the selection is only on axis.
 */
export function isOnAxisOnly(selection: CellSetSelection): boolean {
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
export function parseSelectionToLocationInfo(
    selection: CellSetSelection | undefined, 
    widgetFilters: (MdxString | Mdx)[] | undefined, 
    pageFilters: ((MdxString | Mdx)[]) | undefined, 
    dashboardFilters: ((MdxString | Mdx)[]) | undefined, 
    cube: Cube
): LocationInfo[] {
    
    const filters: Map<string, Payload> = parseAndMergeFilters(
        dashboardFilters,
        pageFilters,
        widgetFilters,
        cube
    );
    if (selection && isOnAxisOnly(selection)) {
        const result: LocationInfo[] = [];
        (selection.axes ?? []).forEach((axisSelection: any) => 
            (axisSelection.positions ?? []).forEach(
                (position: Tuple) => result.push(transformPositionToLocationInfo(position, filters, cube))
            )
        );
        return result;
    }

    const result: LocationInfo[] = [];
    if (selection && selection.cells) {
        selection.cells.forEach((member:{
            tuple: Tuple,
            value?: number | string
        }) => {
            const measure: MeasurePayload | undefined = transformMemberToMeasure(member, cube);
            const locationInfo: LocationInfo = transformPositionToLocationInfo(member.tuple, filters, cube, measure);
            result.push(locationInfo);
        });
        return result;
    }

    if (filters.size == 0) {
        return [];
    }
    const defaultFiltersMap: Map<string, Payload> = parseDefaultFilters(cube);

    const defaults = Array.from(defaultFiltersMap)
        .filter((value: [string, Payload]) => 
            !Array.from(filters).some((filter: [string, Payload]) => `${filter[1].dimension.name}|${filter[1].hierarchy.name}|${filter[1].levels.length}` === value[0])
        )
        .map((value: [string, Payload]) => value[1]);
    
    return [
        {
            defaults: defaults,
            filters: Array.from(filters).map(([key, value]) => value)
        }
    ];
}

/**
 * Test if a dimension is present within the location infos.
 * @param locations locations of the selection.
 * @param dimensionName name of the dimension.
 * @returns true if the dimension is within at least one of the locations.
 */
export function isDimensionWithinLocationInfo(locations: LocationInfo[], dimensionName: string): boolean {
    return locations.some((loc: LocationInfo) => 
        (loc.defaults?.some((l: Payload) => isExplicitMemberPayload(l) && l.dimension.name === dimensionName)) || 
        (loc.locations?.some((l: Payload) => isExplicitMemberPayload(l) && l.dimension.name === dimensionName)) || 
        (loc.filters?.some((f: Payload) => isExplicitMemberPayload(f) && f.dimension.name === dimensionName))
    );
}

/**
 * Test if a hierarchy is present within the location infos.
 * @param locations locations of the selection.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @returns true if the hierarchy is within at least one of the locations.
 */
export function isHierarchyWithinLocationInfo(locations: LocationInfo[], dimensionName: string, hierarchyName: string): boolean {
    return locations.some((loc: LocationInfo) => 
        (loc.defaults?.some((l: Payload) => isExplicitMemberPayload(l) &&  (l.dimension.name === dimensionName) && (l.hierarchy.name === hierarchyName))) || 
        (loc.locations?.some((l: Payload) => isExplicitMemberPayload(l) &&  (l.dimension.name === dimensionName) && (l.hierarchy.name === hierarchyName))) || 
        (loc.filters?.some((f: Payload) => isExplicitMemberPayload(f) &&  (f.dimension.name === dimensionName) && (f.hierarchy.name === hierarchyName))) 
    );
}

/**
 * Test if a level is present within the location infos.
 * @param locations locations of the selection.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @param levelName name of the level.
 * @returns true if the level is within at least one of the locations.
 */
export function isLevelWithinLocationInfo(locations: LocationInfo[], dimensionName: string, hierarchyName: string, levelName: string): boolean {
    return locations.some((loc: LocationInfo) => 
        (loc.defaults?.some((l: Payload) => isExplicitMemberPayload(l) && (l.dimension.name === dimensionName) && (l.hierarchy.name === hierarchyName) && (l.levels.some(lvl => lvl.name === levelName)))) || 
        (loc.locations?.some((l: Payload) => isExplicitMemberPayload(l) && (l.dimension.name === dimensionName) && (l.hierarchy.name === hierarchyName) && (l.levels.some(lvl => lvl.name === levelName)))) || 
        (loc.filters?.some((f: Payload) => isExplicitMemberPayload(f) && (f.dimension.name === dimensionName) && (f.hierarchy.name === hierarchyName) && (f.levels.some(lvl => lvl.name === levelName))))
    );
}

/**
 * Retrieve all present members of the level passed.
 * @param locations locations from the selection parsed.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @param levelName name of the level.
 * @returns all the member for this level.
 */
export function retrieveMembersOfLevelFromLocationInfo(locations: LocationInfo[], dimensionName: string, hierarchyName: string, levelName: string): string[][] {
    const result:string[][] = [];
    locations.filter((loc: LocationInfo) => 
        (loc.defaults?.some(l => (l.dimension.name === dimensionName) && (l.hierarchy.name === hierarchyName) && (l.levels.some(lvl => lvl.name === levelName)))) || 
        (loc.locations?.some(l => (l.dimension.name === dimensionName) && (l.hierarchy.name === hierarchyName) && (l.levels.some(lvl => lvl.name === levelName)))) || 
        (loc.filters?.some(f => (f.dimension.name === dimensionName) && (f.hierarchy.name === hierarchyName) && (f.levels.some(lvl => lvl.name === levelName))))
    ).forEach((loc: LocationInfo) => {
        let added: boolean = false;
        (loc.locations ?? []).forEach(l => {
            if (isExplicitMemberPayload(l)) {
                    if (l.dimension.name === dimensionName && l.hierarchy.name === hierarchyName) {
                    const index = l.levels.findIndex(level => level.name === levelName);
                    if (index !== -1 && l.members !== undefined) {
                        added = true;
                        (l.members ?? []).forEach(m => result.push(m.slice(0, index + 1)))
                    }
                }
            }
        });
        if (!added) {
            (loc.filters ?? []).forEach(f => {
                if (isExplicitMemberPayload(f)) {
                    if (f.dimension.name === dimensionName && f.hierarchy.name === hierarchyName) {
                        const index = f.levels.findIndex(level => level.name === levelName);
                        if (index !== -1) {
                            if(!added) {
                                (f.members ?? []).forEach(m => result.push(m.slice(0, index + 1)))
                            }
                            added = true;
                        }
                    }
                }
            });
        }
        if (!added) {
            (loc.defaults ?? []).forEach(f => {
                if (isExplicitMemberPayload(f)) {
                    if (f.dimension.name === dimensionName && f.hierarchy.name === hierarchyName) {
                        const index = f.levels.findIndex(level => level.name === levelName);
                        if (index !== -1) {
                            if(!added) {
                                (f.members ?? []).forEach(m => result.push(m.slice(0, index + 1)))
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
export function getFiltersFromLocations(locations: LocationInfo[], fromSelection: boolean, fromFilters: boolean, cube: Cube): Filter[] {
    const result:Filter[] = [];
    const mergedLocationPayloads:{[locationKey: string]: Payload} = {};
    if (fromFilters) {
        locations.forEach((locationInfo: LocationInfo) => [...locationInfo.filters ?? []].forEach(locationPayload => {
            const key = `${locationPayload.dimension.name}|${locationPayload.hierarchy.name}|${locationPayload.levels[locationPayload.levels.length - 1].name}`;
            const mergedLocationPayload: Payload|undefined = mergedLocationPayloads[key];
            if (isExplicitMemberPayload(locationPayload)) {
                if (mergedLocationPayload !== undefined) {
                    if (isExplicitMemberPayload(mergedLocationPayload)) {
                        if (locationPayload.slicing) {
                            mergedLocationPayload!.members = locationPayload.members;
                        } else {
                            const newMembersToUpdate = [...mergedLocationPayload.members];
                            let newMembers = locationPayload.members;
                            newMembers.forEach(newMember => {
                                if (!newMembersToUpdate.some(member => JSON.stringify(member)==JSON.stringify(newMember))) {
                                    mergedLocationPayload!.members.push(newMember);
                                }
                            })   
                        }
                    }
                }
            }
            mergedLocationPayloads[key] = locationPayload;
        }));
    }
    if (fromSelection) {
        locations.forEach((locationInfo: LocationInfo) => locationInfo.locations?.forEach(locationPayload => {
            if (isExplicitMemberPayload(locationPayload)) {
                const key = `${locationPayload.dimension.name}|${locationPayload.hierarchy.name}|${locationPayload.levels[locationPayload.levels.length - 1].name}`;
                const mergedLocationPayload: Payload|undefined = mergedLocationPayloads[key];
                if (mergedLocationPayload !== undefined) {
                    if (isExplicitMemberPayload(mergedLocationPayload)) {
                        const newMembersToUpdate = [...mergedLocationPayload.members];
                        let newMembers = locationPayload.members;
                        newMembers.forEach(newMember => {
                            if (!newMembersToUpdate.some(member => JSON.stringify(member)==JSON.stringify(newMember))) {
                                mergedLocationPayload!.members.push(newMember);
                            }
                        })   
                        mergedLocationPayloads[key] = mergedLocationPayload;
                    } else {
                        mergedLocationPayloads[key] = locationPayload;
                    }
                } else {
                    mergedLocationPayloads[key] = locationPayload;
                }
            }
        }));
    }
    Object.entries(mergedLocationPayloads).forEach(val => result.push(parsePayloadToFilter(val[1], cube)));
    return result;
}