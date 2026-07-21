(function () {
    const dataEl = document.getElementById("gallery-data");
    if (!dataEl) return;
    const items = JSON.parse(dataEl.textContent || "[]");
    if (!items.length) return;

    const lb = document.getElementById("lightbox");
    const media = document.getElementById("lb-media");
    const nameEl = document.getElementById("lb-name");
    const whoEl = document.getElementById("lb-who");
    const countEl = document.getElementById("lb-count");
    const dl = document.getElementById("lb-download");
    const prev = document.getElementById("lb-prev");
    const next = document.getElementById("lb-next");
    let i = 0;

    function render() {
        const it = items[i];
        media.innerHTML = "";
        let node;
        if (it.type === "video") {
            node = document.createElement("video");
            node.src = it.full;
            node.controls = true;
            node.autoplay = true;
            node.playsInline = true;
        } else {
            node = document.createElement("img");
            node.src = it.full;
            node.alt = it.name;
        }
        media.appendChild(node);
        nameEl.textContent = it.name;
        whoEl.textContent = it.who || "";
        countEl.textContent = (i + 1) + " / " + items.length;
        dl.href = it.download;
        const single = items.length < 2;
        prev.hidden = single;
        next.hidden = single;
    }

    function open(idx) {
        i = idx;
        lb.classList.add("open");
        lb.setAttribute("aria-hidden", "false");
        document.body.style.overflow = "hidden";
        render();
    }

    function close() {
        lb.classList.remove("open");
        lb.setAttribute("aria-hidden", "true");
        document.body.style.overflow = "";
        media.innerHTML = "";
    }

    function go(d) {
        i = (i + d + items.length) % items.length;
        render();
    }

    document.querySelectorAll("[data-index]").forEach(function (el) {
        el.addEventListener("click", function () {
            open(parseInt(el.getAttribute("data-index"), 10));
        });
    });

    document.getElementById("lb-close").addEventListener("click", close);
    prev.addEventListener("click", function () { go(-1); });
    next.addEventListener("click", function () { go(1); });
    lb.addEventListener("click", function (e) {
        if (e.target === lb || e.target.id === "lb-stage") close();
    });
    document.addEventListener("keydown", function (e) {
        if (!lb.classList.contains("open")) return;
        if (e.key === "Escape") close();
        else if (e.key === "ArrowLeft") go(-1);
        else if (e.key === "ArrowRight") go(1);
    });

    // swipe
    let sx = 0, sy = 0;
    const stage = document.getElementById("lb-stage");
    stage.addEventListener("touchstart", function (e) {
        sx = e.touches[0].clientX; sy = e.touches[0].clientY;
    }, { passive: true });
    stage.addEventListener("touchend", function (e) {
        const dx = e.changedTouches[0].clientX - sx;
        const dy = e.changedTouches[0].clientY - sy;
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) go(dx < 0 ? 1 : -1);
    }, { passive: true });
})();
