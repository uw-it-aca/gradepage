import "regenerator-runtime/runtime";
import { useCustomFetch } from "@/composables/customFetch";

async function getSections(url) {
  return useCustomFetch(url);
}

async function getSection(url) {
  return useCustomFetch(url);
}

async function getSectionStatus(url) {
  return useCustomFetch(url);
}

async function getGraderoster(url) {
  return useCustomFetch(url);
}

async function getConversionScales(url) {
  return useCustomFetch(url);
}

async function updateGraderoster(url, data) {
  return useCustomFetch(url, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function submitGraderoster(url, data) {
  return useCustomFetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function updateGrade(url, data) {
  return useCustomFetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function clearSavedGrades(url) {
  return useCustomFetch(url, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
      body: JSON.stringify({ clear_grades: true }),
  });
}

async function createImport(url, data) {
  return useCustomFetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    body: JSON.stringify(data),
  });
}

async function saveImportedGrades(url, data) {
  return useCustomFetch(url, {
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
  return useCustomFetch(url, {
    method: "POST",
    body: formData,
  });
}

async function clearOverride(url) {
  return useCustomFetch(url, {
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
  clearSavedGrades,
  createImport,
  saveImportedGrades,
  uploadGrades,
  getConversionScales,
  clearOverride,
};
