import {
    FilterOnMembers,
    HierarchyCoordinates,
} from "@activeviam/activeui-sdk";

/**
 * Returns  a {@link FilterOnMembers}.
 */
export function createFilterOnMembers(
    key: string,
    value: any
): FilterOnMembers {

    const hierarchy: HierarchyCoordinates = {
        dimensionName: key,
        hierarchyName: key,
    };
    const members = [
        ["AllMember", value]
    ];

    return {
        ...hierarchy,
        members,
        type: "members",
    };
}
