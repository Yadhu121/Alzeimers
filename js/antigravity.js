// Google Antigravity Physics Effect
// Uses Matter.js

(function () {
    let engine, render, runner, mouseConstraint;
    let isPhysicsActive = false;

    window.toggleGravity = function () {
        if (isPhysicsActive) return; // Already active

        isPhysicsActive = true;

        // 1. Setup Matter.js
        const Engine = Matter.Engine,
            Render = Matter.Render,
            Runner = Matter.Runner,
            Bodies = Matter.Bodies,
            Composite = Matter.Composite,
            Mouse = Matter.Mouse,
            MouseConstraint = Matter.MouseConstraint;

        // Create engine
        engine = Engine.create();
        const world = engine.world;

        // 2. Identify Elements to "Physics-ify"
        // We will replace static DOM elements with physics bodies
        // For simplicity in this demo, we'll make the main containers fall

        const elements = [
            document.querySelector('.navbar'),
            document.querySelector('.hero-text h1'),
            document.querySelector('.hero-text p'),
            ...document.querySelectorAll('.btn-primary, .btn-secondary'),
            ...document.querySelectorAll('.feature-card'),
            document.querySelector('.upload-container'),
            document.querySelector('.footer')
        ].filter(el => el); // Filter out nulls

        const bodies = [];

        elements.forEach(el => {
            const rect = el.getBoundingClientRect();

            // Create a physics body matching the element's position and size
            const body = Bodies.rectangle(
                rect.left + rect.width / 2,
                rect.top + rect.height / 2 + window.scrollY,
                rect.width,
                rect.height,
                {
                    restitution: 0.8, // Bounciness
                    friction: 0.1,
                    render: { opacity: 0 } // Invisible body, we'll sync DOM to it
                }
            );

            bodies.push({ body, element: el });
            Composite.add(world, body);

            // Set element to absolute position to follow the body
            el.style.position = 'absolute';
            el.style.left = '0';
            el.style.top = '0';
            el.style.width = `${rect.width}px`;
            el.style.height = `${rect.height}px`;
            el.style.margin = '0';
            el.style.transformOrigin = 'center center';
            el.style.zIndex = '1000'; // Make sure they are on top
        });

        // 3. Add Boundaries (Floor, Walls)
        const floor = Bodies.rectangle(
            window.innerWidth / 2,
            document.body.scrollHeight + 50,
            window.innerWidth,
            100,
            { isStatic: true }
        );
        const wallLeft = Bodies.rectangle(
            -50,
            document.body.scrollHeight / 2,
            100,
            document.body.scrollHeight,
            { isStatic: true }
        );
        const wallRight = Bodies.rectangle(
            window.innerWidth + 50,
            document.body.scrollHeight / 2,
            100,
            document.body.scrollHeight,
            { isStatic: true }
        );

        Composite.add(world, [floor, wallLeft, wallRight]);

        // 4. Run the Engine
        runner = Runner.create();
        Runner.run(runner, engine);

        // 5. Mouse Interaction for Dragging
        // We need a canvas for mouse interaction even if we don't render bodies visually
        const canvas = document.createElement('canvas');
        canvas.width = window.innerWidth;
        canvas.height = document.body.scrollHeight;
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.pointerEvents = 'none'; // Let clicks pass through if needed, but we need it for mouse constraint...
        // Actually, for mouse constraint to work, we need to capture events.
        // But we want to drag the HTML elements. 
        // Matter.js MouseConstraint works on the canvas.
        // Let's rely on the visual effect primarily.

        // Sync Loop
        function update() {
            bodies.forEach(item => {
                const { x, y } = item.body.position;
                const angle = item.body.angle;

                item.element.style.transform = `translate(${x - item.element.offsetWidth / 2}px, ${y - item.element.offsetHeight / 2}px) rotate(${angle}rad)`;
            });
            requestAnimationFrame(update);
        }
        update();

        console.log("Gravity Activated!");
    };

    // Auto-init specific trigger if needed, or wait for button click
    // Add a specialized button to the navbar
    const nav = document.querySelector('.nav-links');
    if (nav) {
        const li = document.createElement('li');
        const btn = document.createElement('a');
        btn.innerText = 'Zero Gravity';
        btn.href = '#';
        btn.style.color = '#EA4335'; // Google Red
        btn.style.fontWeight = 'bold';
        btn.onclick = (e) => {
            e.preventDefault();
            window.toggleGravity();
        };
        li.appendChild(btn);
        nav.appendChild(li);
    }

})();
