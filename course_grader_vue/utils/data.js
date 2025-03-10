import "regenerator-runtime/runtime";
import { useTokenStore } from "@/stores/token";

async function customFetch(url, options = {}) {
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
      if (response.status === 403) {  // Expired session
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

async function getSections(url) {
  return customFetch(url);
}

async function getSection(url) {
  return customFetch(url);
}

async function getSectionStatus(url) {
  return customFetch(url);
}

async function getGraderoster(url) {
  return customFetch(url);
}

async function getConversionScales(url) {
  return customFetch(url);
}

async function updateGraderoster(url, data) {
  return customFetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function submitGraderoster(url, data) {
  return customFetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function updateGrade(url, data) {
  return customFetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function createImport(url, data) {
  return customFetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function saveImportedGrades(url, data) {
  return customFetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function uploadGrades(url, file) {
  let formData = new FormData();
  formData.append("file", file);

  // Do not send a Content-Type header
  return customFetch(url, {
    method: "POST",
    body: formData,
  });
}

async function clearOverride(url) {
  return customFetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify({ clear_override: true }),
  });
}

export {
  getSections,
  getSection,
  getSectionStatus,
  getGraderoster,
  updateGraderoster,
  submitGraderoster,
  updateGrade,
  createImport,
  saveImportedGrades,
  uploadGrades,
  getConversionScales,
  clearOverride,
};
