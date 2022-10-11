import { createFilter, Cube, Dimension, Filter, FilterOnMembers, getDimension, getHierarchy, getLevel, getMeasure, Hierarchy, Level, Mdx, MdxCompoundIdentifier, MdxExpression, MdxString, Measure, Member, TopBottomMode, Tuple } from "@activeviam/activeui-sdk";
import { DefaultMember, DimensionName, getChildrenLevels, getLevelCoordinates, HierarchyCoordinates, HierarchyName } from "@activeviam/data-model";
import { getHierarchies, getSpecificCompoundIdentifier, isMdxFunction, MdxFunction, MdxLiteral, MdxMeasureCompoundIdentifier, MdxUnknownCompoundIdentifier } from "@activeviam/mdx";
import { ExplicitMemberPayload, LocationInfo, MdxPayload, MeasurePayload, Payload } from "../payloadUtils.types";

type MdxTopBottomFunction = MdxFunction & {
    name: TopBottomMode;
    arguments: [
      MdxFunction & {
        arguments: [
          MdxFunction & {
            arguments: [
              MdxFunction & { arguments: [MdxCompoundIdentifier, MdxLiteral] },
            ];
          },
        ];
      },
      MdxLiteral,
      MdxUnknownCompoundIdentifier | MdxMeasureCompoundIdentifier,
    ];
  };

export function isExplicitMemberPayload(payload: Payload): payload is ExplicitMemberPayload {
    return payload.type === "explicit-members";
}

export function isMdxPayload(payload: Payload): payload is MdxPayload {
    return payload.type === "mdx";
}

/**
 * Create a location payload from the arguments.
 * @param dimensionName name of the dimension.
 * @param hierarchyName name of the hierarchy.
 * @param members members of the location (can be an empty list).
 * @param cube cube object from the props of the context menu.
 * @returns a locationPayload.
 */
function createExplicitMemberPayload(dimensionName: DimensionName, hierarchyName: HierarchyName, members: string[], slicing: boolean, cube: Cube): ExplicitMemberPayload | undefined {
    const dimension:Dimension = getDimension(dimensionName, cube);
    const hierarchy:Hierarchy = getHierarchy({dimensionName, hierarchyName}, cube);
    const levelCoordinates = getLevelCoordinates(
        {
            dimension,
            hierarchy
        }
    );
    const firstLevel: Level = getLevel(
        levelCoordinates,
        cube
    );
    const childrenLevels: Level[] = getChildrenLevels(
        levelCoordinates,
        cube
    );
    if (members.length > 0) {
        const levels: Level[] = [firstLevel];
        for (let i = 0; i < members.length - 1; i ++) {
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
function createLocationPayloadFromCompoundIdentifier(
    mdx:MdxCompoundIdentifier, 
    cube: Cube): ExplicitMemberPayload | undefined {
    if (mdx.identifiers.length > 2) {
        const dimensionName: DimensionName = mdx.identifiers[0].value;
        const hierarchyName: HierarchyName = mdx.identifiers[1].value;
        const members:string[] = [];
        let slicing = true;
        for (let i=2; i < mdx.identifiers.length; i++) {
            const value = mdx.identifiers[i].value;
            if ((value !== "AllMember") && (value !== "ALL")) {
                members.push(value);
            } else {
                slicing = false;
            }
        }
        return createExplicitMemberPayload(dimensionName, hierarchyName, members, slicing, cube);
    }
    return undefined;
}

function createMdxLocationPayload(mdx: Mdx, cube: Cube): MdxPayload|undefined {
    if (isMdxFunction(mdx, "filter")) {
        const [membersNode] = mdx.arguments;
        if (isMdxFunction(membersNode, "members")) {
            const compoundIdentifier = membersNode.arguments[0] as MdxCompoundIdentifier;
            const specificCompoundIdentifier = getSpecificCompoundIdentifier(compoundIdentifier, {cube, });
            if (specificCompoundIdentifier.type !== "level") {
                return undefined;
            }
            const {
                dimensionName,
                hierarchyName,
                levelName,
            } = specificCompoundIdentifier;
            const dimension:Dimension = getDimension(dimensionName, cube);
            const hierarchy:Hierarchy = getHierarchy({dimensionName, hierarchyName}, cube);
            const levelCoordinates = getLevelCoordinates(
                {
                    dimension,
                    hierarchy
                }
            );
            const firstLevel: Level = getLevel(
                levelCoordinates,
                cube
            );
            const childrenLevels: Level[] = getChildrenLevels(
                levelCoordinates,
                cube
            );       
            const levels: Level[] = [firstLevel];
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
                mdx,
                type: "mdx"
            }
        }
    } 
    if (isMdxFunction(mdx) && [
      "topcount",
      "topsum",
      "toppercent",
      "bottomcount",
      "bottomsum",
      "bottompercent",
    ].includes(mdx.name.toLowerCase())) {
        const firstArgumentOfFilter = (mdx as MdxTopBottomFunction).arguments[0].arguments[0];
        const scope =
        firstArgumentOfFilter.name.toLowerCase() === "children"
          ? "ofEachParent"
          : "overall";
        const hierarchyCompoundIdentifier = firstArgumentOfFilter.arguments[0].arguments[0];
        const [{ dimensionName, hierarchyName },] = getHierarchies(hierarchyCompoundIdentifier, { cube });
        const levelIndex = scope === "overall" ? parseInt(firstArgumentOfFilter.arguments[0].arguments[1].value, 10) : 0;
        const dimension:Dimension = getDimension(dimensionName, cube);
        const hierarchy:Hierarchy = getHierarchy({dimensionName, hierarchyName}, cube);
        const levelCoordinates = getLevelCoordinates(
            {
                dimension,
                hierarchy
            }
        );
        const firstLevel: Level = getLevel(
            levelCoordinates,
            cube
        );
        const childrenLevels: Level[] = getChildrenLevels(
            levelCoordinates,
            cube
        );       
        const levels: Level[] = [firstLevel];
        for (let i = 1; i < levelIndex; i++) {
            levels.push(childrenLevels[i]);
        } 
        return {
            dimension,
            hierarchy,
            levels,
            slicing: false,
            mdx,
            type: "mdx"
        }
    }
    return undefined;
}

/**
 * Retrieves the location payload of the default filters from the cube.
 * In case those filtesr are already within the widget filters, they won't be express here.
 * @param cube cube object from the props of the context menu.
 * @returns the default filters parsed.
 */
export function parseDefaultFilters(cube: Cube): Map<string, Payload> {
    //@ts-ignore
    const mapResult:Map<string, Payload> = new Map();
    const defaultFilters: DefaultMember[] | undefined = cube.defaultMembers;
    if (!defaultFilters) {
        return mapResult;
    }
    defaultFilters.filter((value: DefaultMember) => value.dimension !== "Measures")
        .forEach((value: DefaultMember) => {
            const dimensionName: DimensionName = value.dimension;
            const hierarchyName: HierarchyName = value.hierarchy;
            const members:string[] = value.path.filter(val => (val !== "AllMember") && (val !== "ALL"));
            const slicing: boolean = !value.path.some(val => (val === "AllMember") || (val === "ALL"));
            const locationPayload = createExplicitMemberPayload(dimensionName, hierarchyName, members, slicing, cube);
            if (locationPayload) {
                if (members.length > 0) {
                    const key:string = dimensionName + "|" + hierarchyName + "|" + locationPayload.levels.length;
                    // Do not take the default filters that has been override by the widget filters
                    const oldResult: Payload | undefined = mapResult.get(key);
                    if (oldResult !== undefined) {
                        if (isExplicitMemberPayload(oldResult)) {
                            oldResult.members.forEach((m: string[]) => locationPayload.members.push(m));
                        }
                    }
                    mapResult.set(key, locationPayload);
                }
            }
        });
    return mapResult;
}

function transformFilters(filters: ((MdxString | Mdx)[]) | undefined, cube: Cube): Map<string, Payload> {
    if (!filters) {
        return new Map();
    }
    const mapResult:Map<string, Payload> = new Map();
    filters
        .filter((mdx:(Mdx|MdxString)) => !(typeof mdx === 'string'))
        //@ts-ignore
        .forEach((mdx:Mdx) => {
        let added = false;
        if (mdx.elementType === "CompoundIdentifier") {
            const locationPayload = createLocationPayloadFromCompoundIdentifier(mdx, cube);
            if (locationPayload) {
                const key:string = locationPayload.dimension.name + "|" + locationPayload.hierarchy.name + "|" + locationPayload.levels.length;
                const oldResult: Payload | undefined = mapResult.get(key);
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
            mdx.arguments.forEach((arg: MdxExpression) => {
                if (arg.elementType === "CompoundIdentifier") {
                    const locationPayload: ExplicitMemberPayload|undefined = createLocationPayloadFromCompoundIdentifier(arg, cube);
                    // case multiple compound identifier for one level, aka multiple members filtered for one level.
                    if (locationPayload !== undefined) {
                        const key:string = locationPayload.dimension.name + "|" + locationPayload.hierarchy.name + "|" + locationPayload.levels.length;
                        const oldResult: Payload | undefined = mapResult.get(key);
                        if (oldResult){
                            if (isExplicitMemberPayload(oldResult)) {
                                oldResult.members.forEach(m => locationPayload.members.push(m));
                            } 
                        }
                        mapResult.set(key, locationPayload); 
                        added = true;   
                     }
                }
            })
        }
        if (!added) {
            const locationPayload: MdxPayload|undefined = createMdxLocationPayload(mdx, cube);
            if (locationPayload) {
                const key:string = locationPayload.dimension.name + "|" + locationPayload.hierarchy.name + "|" + locationPayload.levels.length;
                mapResult.set(key, locationPayload);
                added = true;
            }
        }
    });
    return mapResult;
}

export function parseAndMergeFilters(
    dashboardFilters: ((MdxString | Mdx)[]) | undefined, 
    pageFilters: ((MdxString | Mdx)[]) | undefined, 
    widgetFilters: ((MdxString | Mdx)[]) | undefined, 
    cube: Cube
    ): Map<string, Payload> {
    // const defaultFilters: DefaultMember[] | undefined = cube.defaultMembers;
    const result: Map<string, Payload> = new Map();//parseDefaultFilters(defaultFilters, cube);
    const dashboardFiltersParsed:Map<string, Payload> = transformFilters(dashboardFilters, cube);
    const pageFiltersParsed:Map<string, Payload> =  transformFilters(pageFilters, cube);
    const widgetFiltersParsed:Map<string, Payload> =  transformFilters(widgetFilters, cube);

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
export function transformMemberToMeasure(member: { tuple: Tuple; value?: string | number | undefined; }, cube: Cube): MeasurePayload | undefined {
    const measures: (Measure | undefined)[] = member.tuple.filter(value => value.dimensionName == "Measures").map(value => getMeasure(value.captionPath[0], cube));
    if (!measures || measures.length === 0 || measures[0] === undefined || ((!member.value) && (member.value !== 0))) {
        return undefined
    }
    return {
        measure: measures[0],
        value: member.value
    }
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
export function transformPositionToLocationInfo(
    position: Tuple, 
    filtersMap: Map<string, Payload>, 
    cube: Cube,
    measure?: MeasurePayload
    ): LocationInfo {
    const locations : Payload[] = [];
    position.forEach((tuple: (HierarchyCoordinates & Member)) => { 
        if (tuple.dimensionName != "Measures") {
            const dimensionName:DimensionName = tuple.dimensionName;
            const hierarchyName:HierarchyName = tuple.hierarchyName;
            const members: string[] = tuple.captionPath.filter(member => (member !== "AllMember") && (member !== "ALL"));
            const slicing: boolean = !tuple.captionPath.some(val => (val === "AllMember") || (val === "ALL"));
            const locationPayload:ExplicitMemberPayload|undefined = createExplicitMemberPayload(dimensionName, hierarchyName, members, slicing, cube);
            if (locationPayload && members.length > 0) {
                // const key:string = dimensionName + "|" + hierarchyName + "|" + locationPayload.levels.length;
                // filtersMap.delete(key);
                locations.push(locationPayload);
            }
        }
    });
    const filters: Payload[] = Array.from(filtersMap).map(([key, value]) => value);
    const defaultFiltersMap: Map<string, Payload> = parseDefaultFilters(cube);

    const defaults = Array.from(defaultFiltersMap)
        .filter((value: [string, Payload]) => 
            !filters.some(filter => `${filter.dimension.name}|${filter.hierarchy.name}|${filter.levels.length}` === value[0]) 
                && !locations.some(filter => `${filter.dimension.name}|${filter.hierarchy.name}|${filter.levels.length}` === value[0]))
        .map((value: [string, Payload]) => value[1]);
    return {
        defaults: defaults,
        locations: locations,
        filters: filters, 
        measure: measure
    }
}

/**
 * Return true if at least one of the member to find is within the member from the location.
 * @param memberFromLocation member from the location.
 * @param memberToFind member to find within member from the location.
 * @returns true if at least one of the member to find is within the member from the location.
 */
 export function testIncludeMembers(memberFromLocation: string[][], memberToFind: string[][]): boolean {
    for (const memberF of memberFromLocation) {
        for (const memberT of memberToFind) {
            if (memberF.length === memberT.length) {
                let result = true;
                for (let i = 0; i<memberF.length; i++) {
                    if (memberF[i] !== memberT[i]) {
                        result = false;
                        break;
                    }
                }
                if (result) {
                    return true;
                }
            }
        }
    }
    return false;
}

/**
 * Parse a location Payload to a filter on member object.
 * @param locationPayload a location payload.
 * @returns the location payload parsed to a filter on member.
 */
export function parsePayloadToFilter(locationPayload: Payload, cube: Cube): Filter {
    return isExplicitMemberPayload(locationPayload) ? {
        dimensionName: locationPayload.dimension.name,
        hierarchyName: locationPayload.hierarchy.name,
        members:  locationPayload.members.map(m => locationPayload.slicing ? m : ["AllMember", ...m]),
        type: "members"
    } as FilterOnMembers : createFilter(locationPayload.mdx, cube)
}
