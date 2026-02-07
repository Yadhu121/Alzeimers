// Cursor Effect - Circle follows mouse and changes state
(function () {
    // Create cursor elements
    const cursorDot = document.createElement('div');
    const cursorCircle = document.createElement('div');

    // Dot styles (The actual pointer position)
    cursorDot.style.cssText = `
        width: 8px;
        height: 8px;
        background-color: black;
        border-radius: 50%;
        position: fixed;
        pointer-events: none;
        z-index: 9999;
        transform: translate(-50%, -50%);
        transition: opacity 0.3s ease;
    `;

    // Circle styles (The trailing circle)
    cursorCircle.style.cssText = `
        width: 40px;
        height: 40px;
        border: 1px solid rgba(0, 0, 0, 0.5);
        border-radius: 50%;
        position: fixed;
        pointer-events: none;
        z-index: 9998;
        transform: translate(-50%, -50%);
        transition: width 0.3s ease, height 0.3s ease, background-color 0.3s ease, border-color 0.3s ease;
    `;

    document.body.appendChild(cursorDot);
    document.body.appendChild(cursorCircle);

    // Mouse movement
    let mouseX = 0;
    let mouseY = 0;
    let circleX = 0;
    let circleY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;

        // Dot moves instantly
        cursorDot.style.left = mouseX + 'px';
        cursorDot.style.top = mouseY + 'px';
    });

    // Animation loop for smooth circle trailing
    function animate() {
        // Smooth follow
        circleX += (mouseX - circleX) * 0.15;
        circleY += (mouseY - circleY) * 0.15;

        cursorCircle.style.left = circleX + 'px';
        cursorCircle.style.top = circleY + 'px';

        requestAnimationFrame(animate);
    }
    animate();

    // Hover effects on interactive elements
    const interactiveElements = document.querySelectorAll('a, button, input, select, textarea, .upload-area, .feature-card, .logo, .stat-card');

    interactiveElements.forEach(el => {
        el.addEventListener('mouseenter', () => {
            // Scale up circle and make it slightly opaque/colorful
            cursorCircle.style.width = '60px';
            cursorCircle.style.height = '60px';
            cursorCircle.style.backgroundColor = 'rgba(0, 0, 0, 0.05)';
            cursorCircle.style.borderColor = 'transparent';
            cursorDot.style.opacity = '0.5';
        });

        el.addEventListener('mouseleave', () => {
            // Reset
            cursorCircle.style.width = '40px';
            cursorCircle.style.height = '40px';
            cursorCircle.style.backgroundColor = 'transparent';
            cursorCircle.style.borderColor = 'rgba(0, 0, 0, 0.5)';
            cursorDot.style.opacity = '1';
        });
    });

    // Hide default cursor
    const style = document.createElement('style');
    style.textContent = `
        *, *::before, *::after {
            cursor: none !important;
        }
    `;
    document.head.appendChild(style);
})();
