import { useMemo } from "react";
import getToken from "./localStorageUtils";

export const useSecurityRequestOptions = (): RequestInit => {
  const token = getToken();

  const requestOptions: RequestInit = useMemo(() => {
    return !token ? {} : { headers: { authorization: `Jwt ${token}` } };
  }, [token]);

  return requestOptions;
};

const DefaultHeaders: HeadersInit = {
  "Content-Type": "application/json",
  Accept: "application/json",
};

export type RestQuerierType = {
  getRequest: (serviceUrl: string) => Promise<Response>;
  deleteRequest: (serviceUrl: string) => Promise<Response>;
  postJSONRequest: (
    serviceUrl: string,
    body?: unknown,
    headers?: HeadersInit
  ) => Promise<Response>;
  postRawRequest: (
    serviceUrl: string,
    body?: BodyInit,
    headers?: HeadersInit
  ) => Promise<Response>;
  putJSONRequest: (
    serviceUrl: string,
    body?: unknown,
    headers?: HeadersInit
  ) => Promise<Response>;
  putRawRequest: (
    serviceUrl: string,
    body?: BodyInit,
    headers?: HeadersInit
  ) => Promise<Response>;
};

export const createSecureRestQuerierFrom = (
  requestOptions: RequestInit
): RestQuerierType => {
  const mergedHeaders = (headers?: HeadersInit) => {
    let mutatingHeaders = headers;

    if (requestOptions) {
      mutatingHeaders = { ...headers, ...requestOptions.headers };
    }
    return mutatingHeaders;
  };

  return {
    getRequest: (url: string) => {
      return fetch(url, requestOptions);
    },
    deleteRequest: (url: string) => {
      const requestionOptions: RequestInit = {
        ...requestOptions,
        method: "DELETE",
      };

      return fetch(url, requestionOptions);
    },
    postJSONRequest: (
      url: string,
      body?: unknown,
      headers = DefaultHeaders
    ) => {
      const requestionOptions: RequestInit = {
        ...requestOptions,
        headers: mergedHeaders(headers),
        method: "POST",
        body: JSON.stringify(body),
      };
      return fetch(url, requestionOptions);
    },

    putJSONRequest: (url: string, body?: unknown, headers = DefaultHeaders) => {
      const requestionOptions: RequestInit = {
        ...requestOptions,
        headers: mergedHeaders(headers),
        method: "PUT",
        body: JSON.stringify(body),
      };
      return fetch(url, requestionOptions);
    },
    postRawRequest: (url: string, body?: BodyInit, headers?: HeadersInit) =>
      fetch(url, {
        ...requestOptions,
        headers: mergedHeaders(headers),
        method: "POST",
        body,
      }),
    putRawRequest: (url: string, body?: BodyInit, headers?: HeadersInit) =>
      fetch(url, {
        ...requestOptions,
        headers: mergedHeaders(headers),
        method: "PUT",
        body,
      }),
  };
};

/**
 * React Hook returning a service for querying rest endpoints on the server.
 */
export const useSecureRestQuerier = (): RestQuerierType => {
  const requestInit = useSecurityRequestOptions();

  return useMemo(() => createSecureRestQuerierFrom(requestInit), [requestInit]);
};