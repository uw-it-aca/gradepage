import { ref } from "vue";
import { useTokenStore } from "@/stores/token";

export async function useCustomFetch(url, options = {}) {
  const tokenStore = useTokenStore();

  // Default headers
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
      const jsonResponse = await response.json();
      return jsonResponse;
    } else {
      if (response.status === 403) {
        // Expired session
        return alert(
          "Your session has expired. Refresh the page to start a new session."
        );
      }

      const errorResponse = await response.json();
      errorResponse.status = response.status;
      throw errorResponse;
    }
  } catch (error) {
    throw error;
  }
}
