const TOKEN_STORAGE_KEY = "activeui-token" as const;

const getToken = (): string | null => {
  const { localStorage } = window;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
};

export default getToken;