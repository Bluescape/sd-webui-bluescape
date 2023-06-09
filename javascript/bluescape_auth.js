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
function bluescape_registration() {
    window.open("/bluescape/registration", "_blank");
}

function bluescape_logout() {
    window.location = "/bluescape/logout";
}

function bluescape_update_status(input) {
    const statuses = input.split("\n")
    const txt2imgStatusLabel = document.getElementById("bluescape-status-txt2img");
    const img2imgStatusLabel = document.getElementById("bluescape-status-img2img");

    // This is a bit error prone and should be cleaned up
    if (statuses[0] && txt2imgStatusLabel) {
        txt2imgStatusLabel.innerHTML = statuses[0]
    }
    if (statuses[1] && img2imgStatusLabel) {
        img2imgStatusLabel.innerHTML = statuses[1]
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