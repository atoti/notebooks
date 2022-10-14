import { Dimension, Hierarchy, Level, Mdx, Measure } from "@activeviam/activeui-sdk";

/**
 * A payload is either an mdx or an explicit members.
 * From the explicit members you can retrieve the explicit members expressed from the filter or the selection done by the user.
 */
 export interface LocationInfo {
    defaults?: Payload[],
    locations?: Payload[],
    filters?: Payload[],
    measure?: MeasurePayload
}

interface LocationPayload {
    dimension: Dimension,
    hierarchy: Hierarchy,
    levels: Level[],
    slicing: boolean,
    type: LocationPayloadType
}

type LocationPayloadType = "explicit-members"|"mdx"


export interface ExplicitMemberPayload extends LocationPayload {
    members: string[][],
    type: "explicit-members"
}

// export interface DefaultMemberPayload extends LocationPayload {
//     members: string[][],
//     type: "default"
// }


export interface MdxPayload extends LocationPayload {
    mdx: Mdx,
    type: "mdx"
}

export declare type Payload = MdxPayload|ExplicitMemberPayload;

export interface MeasurePayload {
    measure: Measure,
    value: number | string
}