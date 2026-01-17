/* Global Game Icons Background Animation */
function createGameParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;

    // Clear existing particles if any
    particlesContainer.innerHTML = '';

    // Inject animation keyframes if not present (fallback for cached CSS)
    if (!document.getElementById('particle-keyframes')) {
        const style = document.createElement('style');
        style.id = 'particle-keyframes';
        style.innerHTML = `
            @keyframes floatIcon {
                0% { transform: translateY(0) rotate(0deg); opacity: 0; }
                10% { opacity: 0.4; }
                90% { opacity: 0.4; }
                100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }

    const icons = [
        'fa-gamepad', 'fa-ghost', 'fa-dragon', 'fa-dice-d20',
        'fa-trophy', 'fa-rocket', 'fa-puzzle-piece', 'fa-headset',
        'fa-crosshairs', 'fa-chess-knight', 'fa-dungeon', 'fa-space-shuttle'
    ];

    const particleCount = 30; // Increased density

    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('i');
        const randomIcon = icons[Math.floor(Math.random() * icons.length)];

        particle.className = `fas ${randomIcon} game-particle`;
        particle.style.position = 'absolute'; // Ensure positioning works even if CSS fails

        // Random positioning
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';

        // Random animation properties
        particle.style.animationDelay = (Math.random() * 5) + 's';
        particle.style.animationDuration = (15 + Math.random() * 20) + 's'; // Slower float

        // Random size
        const size = 1.5 + Math.random() * 3; // Larger icons (1.5rem to 4.5rem)
        particle.style.fontSize = `${size}rem`;
        particle.style.opacity = 0.25 + Math.random() * 0.3; // More visible (0.25 - 0.55)

        // Random rotation
        particle.style.transform = `rotate(${Math.random() * 360}deg)`;

        particlesContainer.appendChild(particle);
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    createGameParticles();
});
