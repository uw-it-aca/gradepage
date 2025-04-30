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

    // Check if response is ok (status 2xx)
    if (!response.ok) {
      // Handle expired session (403 status)
      if (response.status === 403) {
        alert(
          "Your session has expired. Refresh the page to start a new session."
        );
        return;
      } else {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
    }

    // 204 No Content responses have no body
    if (response.status !== 204) {
      return response.text().then(text => {
        try {
          // Attempt to parse the response as JSON
          const json = JSON.parse(text);
          return json;
        } catch (error) {
          // Handle JSON parsing errors
          throw new Error(`Failed to parse response as JSON:, ${error}`);
        }
      });
    }
  } catch (error) {
    console.error("Fetch error:", error);
    throw error;
  }
}
