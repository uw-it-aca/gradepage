import "regenerator-runtime/runtime";
//import axios from "axios";
import { useTokenStore } from "@/stores/token";

// request interceptor
/*
axios.interceptors.request.use(
  function (config) {
    const tokenStore = useTokenStore();

    config.headers["Content-Type"] = "application/json;charset=UTF-8";
    config.headers["Access-Control-Allow-Origin"] = "*";
    config.headers["X-CSRFToken"] = tokenStore.csrfToken;
    config.headers["X-Requested-With"] = "XMLHttpRequest";
    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);

// methods
function _handleError(error) {
  if (error.response) {
    if (error.response.status === 403) {
      // Expired Session
      return alert(
        "Your session has expired. Refresh the page to start a new session."
      );
    }
    throw error;
  }
}
*/

// Fetch wrapper with headers and error handling
async function customFetch(url, options = {}) {
  const tokenStore = useTokenStore();

  // Set default headers
  const defaultHeaders = {
    "Content-Type": "application/json;charset=UTF-8",
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

    // Handle expired session (403 status)
    if (response.status === 403) {
      alert(
        "Your session has expired. Refresh the page to start a new session."
      );
      return;
    }

    // Check if response is ok (status 2xx)
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Parse and return JSON response
    return response.json();
  } catch (error) {
    console.error("Fetch error:", error);
    throw error;
  }
}

//async function getSections(url) {
//  return axios.get(url).catch(_handleError);
//}

// Method to get sections
async function getSections(url) {
  return customFetch(url);
}

//async function getSection(url) {
// return axios.get(url).catch(_handleError);
//}
async function getSection(url) {
  return customFetch(url);
}

//async function getSectionStatus(url) {
//  return axios.get(url);
//}
async function getSectionStatus(url) {
  return customFetch(url);
}

//async function getGraderoster(url) {
//  return axios.get(url).catch(_handleError);
//}
async function getGraderoster(url) {
  return customFetch(url);
}

//async function updateGraderoster(url, data) {
//  return axios.put(url, data).catch(_handleError);
//}
async function updateGraderoster(url, data) {
  return customFetch(url, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

//async function submitGraderoster(url, data) {
//  return axios.post(url, data).catch(_handleError);
//}
async function submitGraderoster(url, data) {
  return customFetch(url, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

//async function updateGrade(url, data) {
//  return axios.patch(url, data);
//}
async function updateGrade(url, data) {
  return customFetch(url, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

//async function createImport(url, data) {
//  return axios.post(url, data).catch(_handleError);
//}
async function createImport(url, data) {
  return customFetch(url, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

//async function saveImportedGrades(url, data) {
//  return axios.put(url, data).catch(_handleError);
//}
async function saveImportedGrades(url, data) {
  return customFetch(url, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

/*
async function uploadGrades(url, file) {
  var formData = new FormData();
  formData.append("file", file);

  return axios
    .post(url, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      // MARK: the following added as a fix for axios 1.7.9
      transformRequest: (formData) => formData,
    })
    .catch(_handleError);
}
*/

async function uploadGrades(url, file) {
  const formData = new FormData();
  formData.append("file", file);

  return customFetch(url, {
    method: "POST",
    body: formData,
  });
}

//async function getConversionScales(url) {
//  return axios.get(url).catch(_handleError);
//}
async function getConversionScales(url) {
  return customFetch(url);
}

//async function clearOverride(url) {
//  return axios.post(url, { clear_override: true });
//}
async function clearOverride(url) {
  return customFetch(url, {
    method: "POST",
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
