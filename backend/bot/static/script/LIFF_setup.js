let userId = null;
let userName = null;
let liffId = "{{ liff_id }}"; // Get LIFF ID from Django context

function initializeLiff() {
  liff
    .init({ liffId: liffId })
    .then(() => {
      document.getElementById("scanButton").disabled = false;
      if (liff.isLoggedIn()) {
        getUserProfile(1);
      } else {
        liff.login();
      }
    })
    .catch((err) => {
      console.error("LIFF Initialization failed", err);
    });
}

function getUserProfile(scan) {
  liff
    .getProfile()
    .then((profile) => {
      userId = profile.userId;
      userName = profile.displayName;
      console.log("User ID: " + userId);
      console.log("User Name: " + userName);
    })
    .catch((err) => {
      console.error("Error getting user profile", err);
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function closeWindow() {
  liff.closeWindow();
}

window.onload = initializeLiff;
