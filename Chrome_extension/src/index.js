import axios from "axios";
const errors = document.querySelector(".errors");
const links = document.querySelector(".Links");
errors.textContent = "";

const form = document.querySelector(".form-data");

var activeTabId;

chrome.tabs.onActivated.addListener(function (activeInfo) {
    activeTabId = activeInfo.tabId;
});

const searchForCountry = async () => {
    chrome.tabs.query({ currentWindow: true, active: true }, async function (tabs) {
        var url = tabs[0].url;
        if (url) {
            errors.textContent = "";
            var api = `http://127.0.0.1:5000/api/summarize?youtube_url=${url}`;
            try {
                
                var win = window.open(api);
                
            } catch (error) {
                errors.textContent = "Error occured";
            }
        }
    }); 
};
const handleSubmit = async e => {
    e.preventDefault();
    searchForCountry();
};
form.addEventListener("submit", e => handleSubmit(e));
