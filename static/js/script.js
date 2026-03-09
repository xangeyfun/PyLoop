document.querySelectorAll(".notification").forEach(el => {
    setTimeout(() => {
        el.style.opacity = "0";
        setTimeout(() => el.remove(), 300);
    }, 4000);
});

const observerOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px"
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
        }
    });
}, observerOptions);

document.querySelectorAll(".features h2, .feature-card, .how-to-play h2, .step, .cta").forEach(el => {
    observer.observe(el);
});