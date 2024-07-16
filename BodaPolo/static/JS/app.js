document.addEventListener('DOMContentLoaded', (event) => {
    const targetDate = new Date('November 23, 2024 15:30:00').getTime();

    const dias = document.getElementById('dias');
    
    const updateCountdown = () => {
        const now = new Date().getTime();
        const timeDifference = targetDate - now;

        const days = Math.floor(timeDifference / (1000 * 60 * 60 * 24));

        dias.innerHTML = `${days}`;

        if (timeDifference < 0) {
            clearInterval(interval);
            dias.innerHTML = "¡La fecha ha llegado!";
        }
    };

    const interval = setInterval(updateCountdown, 1000);
});
