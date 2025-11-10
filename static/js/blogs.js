
// Enhanced navbar scroll effect
// window.addEventListener('scroll', function() {
//     const navbar = document.getElementById('navbar');

//     if (window.scrollY > 100) {
//         navbar.classList.add('scrolled');
//     } else {
//         navbar.classList.remove('scrolled');
//     }
// });

// Blog post click handler
function readPost(postId) {
    const posts = {
        'off-plan-guide': 'Complete Guide to Off-Plan Properties in Dubai 2025',
        'luxury-villas': 'Palm Jumeirah vs Palm Jebel Ali: Which Luxury Villa Investment Wins?',
        'downtown-apartments': 'Downtown Dubai Apartments: ROI Analysis and Investment Potential',
        'dubai-south': 'Dubai South: The Next Investment Hotspot Near Al Maktoum Airport',
        'property-management': 'Maximizing Rental Returns: Property Management Tips for Dubai Investors',
        'jvc-townhouses': 'JVC Townhouses: Affordable Luxury Investment Option',
        'marina-penthouses': 'Dubai Marina Penthouses: Ultimate Waterfront Living',
        'business-bay': 'Business Bay Commercial Properties: Investment Potential'
    };

    const postTitle = posts[postId] || 'Blog Post';
    alert(`Opening: "${postTitle}"\n\nThis would redirect to the full blog post page with detailed content, images, and related articles.`);
}

// Search functionality
// document.querySelector('.search-btn').addEventListener('click', function () {
//     const searchInput = document.querySelector('.search-input');
//     const searchTerm = searchInput.value.trim();

//     if (searchTerm) {
//         alert(`Searching for: "${searchTerm}"\n\nThis would show filtered blog posts related to your search term.`);
//     } else {
//         alert('Please enter a search term');
//     }
// });

// Newsletter subscription
// document.querySelector('.newsletter-form').addEventListener('submit', function (e) {
//     e.preventDefault();
//     const email = this.querySelector('.newsletter-input').value;

//     if (email) {
//         alert(`Thank you for subscribing with: ${email}\n\nYou'll receive weekly Dubai real estate insights and market updates.`);
//         this.querySelector('.newsletter-input').value = '';
//     }
// });

// Category and tag clicks
// document.querySelectorAll('.categories-list a, .tag').forEach(link => {
//     link.addEventListener('click', function (e) {
//         e.preventDefault();
//         const category = this.textContent.trim();
//         alert(`Viewing posts in category: "${category}"\n\nThis would show filtered blog posts for this category.`);
//     });
// });

// Intersection Observer for animations
// const observerOptions = {
//     threshold: 0.1,
//     rootMargin: '0px 0px -50px 0px'
// };

// const observer = new IntersectionObserver(function(entries) {
//     entries.forEach(entry => {
//         if (entry.isIntersecting) {
//             entry.target.style.opacity = '1';
//             entry.target.style.transform = 'translateY(0)';
//         }
//     });
// }, observerOptions);

// Observe blog posts and sidebar widgets
// document.querySelectorAll('.blog-post, .sidebar-widget, .featured-post').forEach(element => {
//     element.style.opacity = '0';
//     element.style.transform = 'translateY(30px)';
//     element.style.transition = 'all 0.8s ease';
//     observer.observe(element);
// });

// Enhanced hover effects
document.querySelectorAll('.blog-post').forEach(post => {
    post.addEventListener('mouseenter', function () {
        this.querySelector('.post-image').style.transform = 'scale(1.05)';
        this.querySelector('.post-image').style.transition = 'transform 0.3s ease';
    });

    post.addEventListener('mouseleave', function () {
        this.querySelector('.post-image').style.transform = 'scale(1)';
    });
});

// Parallax effect
window.addEventListener('scroll', function () {
    const scrolled = window.pageYOffset;
    const header = document.querySelector('.page-header');
    const rate = scrolled * -0.5;

    if (header && scrolled < header.offsetHeight) {
        header.style.transform = `translateY(${rate}px)`;
    }
});

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    // Add loading animation
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in-out';

    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);

    // Staggered animation for blog posts
    const blogPosts = document.querySelectorAll('.blog-post');
    blogPosts.forEach((post, index) => {
        setTimeout(() => {
            post.style.opacity = '1';
            post.style.transform = 'translateY(0)';
        }, 300 + (index * 150));
    });

    // Animate sidebar widgets
    const sidebarWidgets = document.querySelectorAll('.sidebar-widget');
    sidebarWidgets.forEach((widget, index) => {
        setTimeout(() => {
            widget.style.opacity = '1';
            widget.style.transform = 'translateY(0)';
        }, 500 + (index * 100));
    });
});

// Pagination handling
document.querySelectorAll('.pagination a').forEach(link => {
    link.addEventListener('click', function (e) {
        e.preventDefault();

        // Remove active class from all links
        document.querySelectorAll('.pagination a').forEach(a => a.classList.remove('active'));

        // Add active class to clicked link (if it's not an arrow)
        if (!this.innerHTML.includes('arrow')) {
            this.classList.add('active');
        }

        const pageNum = this.textContent || 'next';
        // alert(`Loading page ${pageNum}...\n\nThis would load more blog posts.`);
    });
});





// Search on Enter key
document.querySelector('.search-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        document.querySelector('.search-btn').click();
    }
});




