var isScrolling;
window.addEventListener('scroll', function() {
    clearTimeout(isScrolling);
    isScrolling = setTimeout(function() {
        var scrollPosition = window.scrollY;
        var viewportHeight = window.innerHeight;
        var sectionIndex = Math.round(scrollPosition / viewportHeight);
        var targetScroll = sectionIndex * viewportHeight;
        window.scrollTo({
            top: targetScroll,
            behavior: 'smooth'
        });
    }, 200); 
});
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}
