import { useTokenStore } from "@/stores/token";

function parseError(str) {
  try {
    return JSON.parse(str);
  } catch (error) {
    try {
      // nginx error html?
      var parser = new DOMParser(),
        errorDoc = parser.parseFromString(str, "text/html"),
        title = errorDoc.title;
      return {
        status: parseInt(title.substring(0, title.indexOf(" "))),
        error: title.substring(title.indexOf(" ") + 1),
      };
    } catch (error) {
      return { status: null, error: str };
    }
  }
}

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
      return response.text().then((text) => {
        try {
          const json = text.length ? JSON.parse(text) : {};
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
        return response.text().then((text) => {
          const error = new Error("Error");
          error.data = parseError(text);
          throw error;
        });
      }
    }
  } catch (error) {
    error.data = parseError(error.message);
    throw error;
  }
}
