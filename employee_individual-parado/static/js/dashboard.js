// Search functionality
document.querySelector('.search-input').addEventListener('input', function(e) {
    const searchTerm = e.target.value.toLowerCase();
    const cards = document.querySelectorAll('.student-card');
    
    cards.forEach(card => {
        const name = card.querySelector('.student-name').textContent.toLowerCase();
        const id = card.querySelector('.student-id').textContent.toLowerCase();
        const email = card.querySelector('.student-detail:nth-of-type(1) span').textContent.toLowerCase();
        const course = card.querySelector('.student-detail:nth-of-type(2) span').textContent.toLowerCase();
        
        if (name.includes(searchTerm) || id.includes(searchTerm) || 
            email.includes(searchTerm) || course.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});

// Filter buttons
document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const filter = this.textContent.toLowerCase();
        const cards = document.querySelectorAll('.student-card');
        
        if (filter === 'all') {
            cards.forEach(card => card.style.display = 'block');
            return;
        }
        
        cards.forEach(card => {
            const year = card.querySelector('.student-detail:nth-of-type(3) span').textContent.toLowerCase();
            if (year.includes(filter)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
});