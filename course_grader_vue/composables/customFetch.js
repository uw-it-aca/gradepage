import { useTokenStore } from "@/stores/token";

export async function useCustomFetch(url, options = {}) {
  const tokenStore = useTokenStore();

  // set default headers
  const defaultHeaders = {
    "Access-Control-Allow-Origin": "*",
    "X-CSRFToken": tokenStore.csrfToken,
    "X-Requested-With": "XMLHttpRequest",
  };

  // Merge default headers with any provided in options
  options.headers = {
    ...defaultHeaders,
    ...options.headers,
  };

  try {
    const response = await fetch(url, options);

    if (response.ok) {
      return response.text().then(text => {
        try {
          const json = JSON.parse(text);
          return json;
        } catch (error) {
          throw new Error(`Failed to parse response as JSON:, ${error}`);
        }
      });
    } else {
      if (response.status === 403) {
        alert(
          "Your session has expired. Refresh the page to start a new session."
        );
        return;
      } else {
        return response.text().then(text => {
          throw new Error(text);
        });
      }
    }
  } catch (error) {
    throw error;
  }
}
