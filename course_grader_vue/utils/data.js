import "regenerator-runtime/runtime";
import axios from "axios";
import { useTokenStore } from "@/stores/token";

// request interceptor
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

async function getSections(url) {
  return axios.get(url).catch(_handleError);
}

async function getSectionStatus(url) {
  return axios.get(url);
}

async function getGraderoster(url) {
  return axios.get(url).catch(_handleError);
}

async function updateGraderoster(url, data) {
  return axios.put(url, data).catch(_handleError);
}

async function submitGraderoster(url, data) {
  return axios.post(url, data).catch(_handleError);
}

async function updateGrade(url, data) {
  return axios.patch(url, data);
}

async function createImport(url, data) {
  return axios.post(url, data).catch(_handleError);
}

async function saveImportedGrades(url, data) {
  return axios.put(url, data).catch(_handleError);
}

async function uploadGrades(url, data) {
  return axios.post(url, data).catch(_handleError);
}

async function getConversionScales(url) {
  return axios.get(url).catch(_handleError);
}
async function clearOverride() {
  return axios.post("/api/internal/support/", { clear_override: true });
}

export {
  getSections,
  getSectionStatus,
  getGraderoster,
  updateGraderoster,
  submitGraderoster,
  updateGrade,
  createImport,
  saveImportedGrades,
  uploadGrades,
  getConversionScales,
  clearOverride
};