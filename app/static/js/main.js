/* --- Custom Cursor --- */
const cursor = document.getElementById("cursor");
const ring = document.getElementById("cursor-ring");
let mx = 0, my = 0, rx = 0, ry = 0;

if (cursor && ring) {
    document.addEventListener("mousemove", (e) => {
        mx = e.clientX;
        my = e.clientY;
    });
    function animCursor() {
        cursor.style.left = mx + "px";
        cursor.style.top = my + "px";
        rx += (mx - rx) * 0.12;
        ry += (my - ry) * 0.12;
        ring.style.left = rx + "px";
        ring.style.top = ry + "px";
        requestAnimationFrame(animCursor);
    }
    animCursor();
}

document.querySelectorAll("a, button, .portfolio-card, .blog-card, .testimonial-card, .why-item").forEach((el) => {
    el.addEventListener("mouseenter", () => {
        if (ring) {
            ring.style.width = "52px";
            ring.style.height = "52px";
            ring.style.opacity = "0.8";
        }
    });
    el.addEventListener("mouseleave", () => {
        if (ring) {
            ring.style.width = "36px";
            ring.style.height = "36px";
            ring.style.opacity = "0.5";
        }
    });
});

/* --- Navbar scroll --- */
const nav = document.getElementById("navbar");
if (nav) {
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            nav.classList.add("scrolled");
        } else {
            nav.classList.remove("scrolled");
        }
    });
}

/* --- Mobile Menu --- */
const hamburger = document.getElementById("hamburger");
const mobileMenu = document.getElementById("mobile-menu");
const mobileClose = document.getElementById("mobile-close");

if (hamburger && mobileMenu) {
    hamburger.onclick = () => mobileMenu.classList.add("open");
}
if (mobileClose && mobileMenu) {
    mobileClose.onclick = () => mobileMenu.classList.remove("open");
}

/* --- Scroll Reveal --- */
const reveals = document.querySelectorAll(".reveal");
if (reveals.length > 0) {
    const revealObs = new IntersectionObserver(
        (entries) => {
            entries.forEach((e) => {
                if (e.isIntersecting) {
                    e.target.classList.add("visible");
                }
            });
        },
        { threshold: 0.1, rootMargin: "0px 0px -40px 0px" },
    );
    reveals.forEach((el) => revealObs.observe(el));
}

/* --- Count Up --- */
function countUp(el) {
    const target = parseInt(el.dataset.target);
    const duration = 1800;
    const step = target / (duration / 16);
    let current = 0;
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = Math.floor(current);
    }, 16);
}

const countSection = document.querySelectorAll("#results, #hero .hero-stats");
if (countSection.length > 0) {
    const countObs = new IntersectionObserver(
        (entries) => {
            entries.forEach((e) => {
                if (e.isIntersecting) {
                    e.target.querySelectorAll(".count-up, [data-target]").forEach(countUp);
                    countObs.unobserve(e.target);
                }
            });
        },
        { threshold: 0.3 },
    );
    countSection.forEach((el) => countObs.observe(el));
}

/* --- Testimonials Slider --- */
const track = document.getElementById("testi-track");
const dots = document.querySelectorAll(".testi-dot");
const testiPrev = document.getElementById("testi-prev");
const testiNext = document.getElementById("testi-next");
const testiWrapper = document.querySelector(".testimonials-slider-wrapper");

if (track && dots.length > 0) {
    let currentTesti = 0;
    const totalTesti = dots.length;

    function goToSlide(n) {
        currentTesti = (n + totalTesti) % totalTesti;
        const w = window.innerWidth < 768 ? 100 : window.innerWidth < 1024 ? 50 : 33.333;
        track.style.transform = `translateX(-${currentTesti * w}%)`;
        dots.forEach((d, i) => d.classList.toggle("active", i === currentTesti));
    }

    if (testiPrev) testiPrev.onclick = () => goToSlide(currentTesti - 1);
    if (testiNext) testiNext.onclick = () => goToSlide(currentTesti + 1);
    dots.forEach((d, i) => (d.onclick = () => goToSlide(i)));

    let testiAuto = setInterval(() => goToSlide(currentTesti + 1), 4000);
    if (testiWrapper) {
        testiWrapper.addEventListener("mouseenter", () => clearInterval(testiAuto));
        testiWrapper.addEventListener("mouseleave", () => {
            testiAuto = setInterval(() => goToSlide(currentTesti + 1), 4000);
        });
    }

    track.addEventListener("touchstart", (e) => { track.touchStart = e.touches[0].clientX; });
    track.addEventListener("touchend", (e) => {
        const diff = track.touchStart - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) diff > 0 ? goToSlide(currentTesti + 1) : goToSlide(currentTesti - 1);
    });
}

/* --- Services Scroll Effect --- */
const serviceBlocks = document.querySelectorAll(".service-block");
if (serviceBlocks.length > 0) {
    window.addEventListener("scroll", () => {
        serviceBlocks.forEach((block) => {
            const rect = block.getBoundingClientRect();
            if (rect.top <= 250 && rect.top > 0) {
                const scale = 1 - (250 - rect.top) / 2000;
                block.style.transform = `scale(${scale})`;
            } else {
                block.style.transform = `scale(1)`;
            }
        });
    });
}