document.addEventListener("DOMContentLoaded", function () {
    // Navbar shrink on scroll
    window.addEventListener("scroll", function () {
        let navbar = document.querySelector(".navbar");
        if (window.scrollY > 50) {
            navbar.classList.add("scrolled");
        } else {
            navbar.classList.remove("scrolled");
        }
    });

    // Section Fade-in on Scroll
    const sections = document.querySelectorAll(".main_heading");
    const options = { threshold: 0.2 };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
            }
        });
    }, options);
    sections.forEach(section => observer.observe(section));

    // Back to Top Button
    let backToTop = document.createElement("button");
    backToTop.id = "backToTop";
    backToTop.innerHTML = "⬆";
    document.body.appendChild(backToTop);

    backToTop.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    window.addEventListener("scroll", function () {
        if (window.scrollY > 200) {
            backToTop.style.display = "block";
        } else {
            backToTop.style.display = "none";
        }
    });

    // Carousel Auto Play and Pause on Hover
    let carousel = document.querySelector("#carouselExampleCaptions");
    carousel.addEventListener("mouseenter", () => {
        bootstrap.Carousel.getInstance(carousel).pause();
    });
    carousel.addEventListener("mouseleave", () => {
        bootstrap.Carousel.getInstance(carousel).cycle();
    });
});
document.addEventListener("DOMContentLoaded", function () {
    // Fade-in Effect for Sections
    const sections = document.querySelectorAll(".section");
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                }
            });
        },
        { threshold: 0.2 }
    );
    sections.forEach((section) => observer.observe(section));
});
