// Floating Particles Effect - High Visibility Rainbow Pattern

(function () {
    console.log("Initializing Rainbow Particles...");

    const particles = [];
    const numParticles = 600;

    // Mouse tracking
    let mouseX = -1000;
    let mouseY = -1000;
    const mouseRadius = 200;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Container setup - HIGH Z-INDEX to ensure it's on top of everything but below cursor
    const container = document.createElement('div');
    container.id = 'particles-container';
    container.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1; 
        overflow: hidden;
        background: transparent;
    `;
    document.body.appendChild(container); // Append to body end

    const centerX = window.innerWidth / 2;
    const centerY = window.innerHeight / 2;

    for (let i = 0; i < numParticles; i++) {
        const particle = document.createElement('div');

        // Random angle
        const angle = Math.random() * Math.PI * 2;

        // Distance
        const minRadius = 150;
        const maxRadius = Math.max(window.innerWidth, window.innerHeight) * 0.9;
        const radius = minRadius + Math.pow(Math.random(), 1.5) * (maxRadius - minRadius);

        // Position
        const startX = centerX + Math.cos(angle) * radius;
        const startY = centerY + Math.sin(angle) * radius;

        // Color based on ANGLE (Rainbow Wheel)
        const hue = (angle * 180 / Math.PI) + 180;
        const color = `hsl(${hue}, 80%, 55%)`; // Vivid colors

        // Shape - LARGER for visibility
        const size = Math.random() * 5 + 3; // 3-8px
        const isDash = Math.random() > 0.5;

        particle.style.cssText = `
            position: absolute;
            background: ${color};
            opacity: ${Math.random() * 0.5 + 0.5}; /* High opacity */
            transform: translate3d(0,0,0);
        `;

        if (isDash) {
            particle.style.width = `${size * 3}px`;
            particle.style.height = `${size}px`;
            particle.style.transform = `rotate(${angle * 57.2958}deg)`;
            particle.style.borderRadius = '2px';
        } else {
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;
            particle.style.borderRadius = '50%';
        }

        // Set initial position relative to center for the new transform logic
        particle.style.left = '50%';
        particle.style.top = '50%';

        container.appendChild(particle);

        particles.push({
            el: particle,
            x: startX,
            y: startY,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
            baseX: startX,
            radius: radius, // Added for pulsing effect
            angle: angle,
            rotation: isDash ? angle * 57.2958 : 0
        });
    }

    let time = 0;

    function animate() {
        time += 0.005; // pulsation speed

        // Calculate pulse factor (sine wave)
        // Moves between -1 and 1, we map it to a scale factor e.g. 0.9 to 1.1
        const pulseScale = 1 + Math.sin(time) * 0.15; // +/- 15% size change

        particles.forEach(p => {
            // Mouse Interaction (Push)
            const dx = p.x - mouseX;
            const dy = p.y - mouseY;
            const dist = Math.sqrt(dx * dx + dy * dy);

            let pushX = 0;
            let pushY = 0;

            if (dist < mouseRadius) {
                const force = (mouseRadius - dist) / mouseRadius;
                const pushAngle = Math.atan2(dy, dx);
                pushX = Math.cos(pushAngle) * force * 50; // stronger momentary push
                pushY = Math.sin(pushAngle) * force * 50;
            }

            // Current Target Position based on PULSE
            // We calculate where the particle should be in the "breathing" cycle
            const currentRadius = p.radius * pulseScale;
            const targetX = centerX + Math.cos(p.angle) * currentRadius;
            const targetY = centerY + Math.sin(p.angle) * currentRadius;

            // Smoothly move towards the target pulsed position + incidental drift
            // Ease mechanism: x += (target - x) * easing
            p.x += (targetX + pushX - p.x) * 0.05;
            p.y += (targetY + pushY - p.y) * 0.05;

            // Add tiny noise so it's not too rigid
            p.x += (Math.random() - 0.5) * 0.5;
            p.y += (Math.random() - 0.5) * 0.5;

            p.el.style.transform = `translate(${p.x - centerX}px, ${p.y - centerY}px) rotate(${p.rotation}deg)`;

            // Update rotation for dashes
            if (p.rotation !== 0) {
                p.rotation += 0.1;
            }
        });

        requestAnimationFrame(animate);
    }

    animate();

})();
