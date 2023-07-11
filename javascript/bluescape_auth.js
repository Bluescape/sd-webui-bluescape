/*
 * MIT License
 *
 * Copyright (c) 2023 Thought Stream, LLC dba Bluescape.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

var styles = `.bluescape-tab-active { background-color: #ef4444 !important; color: #2e363d !important; }`;

var styleSheet = document.createElement("style");
styleSheet.innerText = styles;
document.head.appendChild(styleSheet);

const tokenExpiredMessage = "<span style='color:red;'>Access to Bluescape has expired. Please login in the Bluescape tab.</span>";

function bluescape_registration() {
    window.open("/bluescape/registration", "_blank");
}

function bluescape_logout() {
    window.location = "/bluescape/logout";
}

function bluescape_update_status(input) {
    const statuses = input.split("\n");
    const tokenExpired = statuses[3] === "True";
    const txt2imgStatusLabel = document.getElementById("bluescape-status-txt2img");
    const img2imgStatusLabel = document.getElementById("bluescape-status-img2img");
    const selectedWorkspaceLabel = document.getElementById("selected-workspace-label");

    HighlightBluescapeTab(tokenExpired)

    // This is a bit error prone and should be cleaned up
    if (txt2imgStatusLabel) {
        txt2imgStatusLabel.innerHTML = tokenExpired ? tokenExpiredMessage : statuses[0];
    }
    if (img2imgStatusLabel) {
        img2imgStatusLabel.innerHTML = tokenExpired ? tokenExpiredMessage : statuses[1];
    }
    if (selectedWorkspaceLabel) {
        selectedWorkspaceLabel.innerHTML = statuses[2];
    }
}

document.addEventListener("DOMContentLoaded", function () {

    const bsAuthSuccess = localStorage.getItem("bluescapeRefreshUI");
    if (bsAuthSuccess) {
        localStorage.removeItem("bluescapeRefreshUI");
        RetryCallback(ClickOnBluescapeTab, 500, 6);
    }

    // Status polling
    statusInterval = setInterval(async () => {
        try {
            const response = await fetch("/bluescape/status");
            bluescape_update_status(await response.text());
        }
        catch (error) {
            // Do nothing
        }
    }, 2000);
});

function RetryCallback(callback, delay, tries) {
    if (tries && callback() !== true) {
        setTimeout(RetryCallback.bind(this, callback, delay, tries - 1), delay);
    }
}

function ClickOnBluescapeTab() {
    const links = Array.from(document.querySelectorAll('#tabs .tab-nav button'));
    let clicked = false;
    links.forEach((link) => {
        if (link.textContent === "Bluescape ") {
            link.click();
            clicked = true;
        }
    });

    return clicked;
}

function HighlightBluescapeTab(expired) {
    if (expired){
        document.getElementById("bs-token-expired-tip").style.display = "block";
    } else{
        document.getElementById("bs-token-expired-tip").style.display = "none";
    }

    // Note, for now disabling this as it can be annoying if you don't use Bluescape
    // upload most of the time.
    // Array.from(document.querySelectorAll('#tabs .tab-nav button')).forEach((link) => {
    //     if (link.textContent === "Bluescape ") {
    //         if (expired){
    //             link.classList.add('bluescape-tab-active');
    //         } else{
    //             link.classList.remove('bluescape-tab-active');
    //         }
    //     }
    // });
}