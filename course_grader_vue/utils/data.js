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

export {

};
