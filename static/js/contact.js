
        // Enhanced navbar scroll effect
        window.addEventListener('scroll', function() {
            const navbar = document.getElementById('navbar');
            
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });

        // Form handling
        document.getElementById('contactForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Collect form data
            const formData = new FormData(this);
            const data = {};
            
            // Handle regular form fields
            for (let [key, value] of formData.entries()) {
                if (key === 'propertyInterest') {
                    if (!data[key]) data[key] = [];
                    data[key].push(value);
                } else {
                    data[key] = value;
                }
            }
            
            // Simulate form submission
            const submitBtn = this.querySelector('.submit-btn');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            submitBtn.disabled = true;
            
            setTimeout(() => {
                alert('Thank you for your inquiry! Our Dubai real estate experts will contact you within 24 hours to discuss your investment opportunities.');
                this.reset();
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });

        // FAQ Accordion
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', function() {
                const faqItem = this.parentElement;
                const isActive = faqItem.classList.contains('active');
                
                // Close all FAQ items
                document.querySelectorAll('.faq-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Open clicked item if it wasn't active
                if (!isActive) {
                    faqItem.classList.add('active');
                }
            });
        });

        // Enhanced form interactions
        document.querySelectorAll('.form-group input, .form-group select, .form-group textarea').forEach(field => {
            field.addEventListener('focus', function() {
                this.parentElement.style.transform = 'scale(1.02)';
                this.parentElement.style.transition = 'transform 0.3s ease';
            });
            
            field.addEventListener('blur', function() {
                this.parentElement.style.transform = 'scale(1)';
            });
        });

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

        // Observe contact items and form
        // document.querySelectorAll('.contact-item, .contact-form, .faq-item').forEach(element => {
        //     element.style.opacity = '0';
        //     element.style.transform = 'translateY(30px)';
        //     element.style.transition = 'all 0.8s ease';
        //     observer.observe(element);
        // });

        // Parallax effect
        window.addEventListener('scroll', function() {
            const scrolled = window.pageYOffset;
            const header = document.querySelector('.page-header');
            const rate = scrolled * -0.5;
            
            if (header && scrolled < header.offsetHeight) {
                header.style.transform = `translateY(${rate}px)`;
            }
        });

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            // Add loading animation
            document.body.style.opacity = '0';
            document.body.style.transition = 'opacity 0.5s ease-in-out';
            
            setTimeout(() => {
                document.body.style.opacity = '1';
            }, 100);

            // Staggered animation for contact items
            const contactItems = document.querySelectorAll('.contact-item');
            contactItems.forEach((item, index) => {
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateY(0)';
                }, 300 + (index * 200));
            });
        });

        // Real-time form validation
        document.querySelectorAll('input[required], select[required]').forEach(field => {
            field.addEventListener('blur', function() {
                if (this.value.trim() === '') {
                    this.style.borderColor = '#ff6b6b';
                } else {
                    this.style.borderColor = '#4ecdc4';
                }
            });
        });

        // Phone number formatting
        document.getElementById('phone').addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value.startsWith('971')) {
                    this.value = '+' + value;
                } else if (value.startsWith('0')) {
                    this.value = '+971' + value.substring(1);
                } else if (!value.startsWith('971')) {
                    this.value = '+971' + value;
                }
            }
        });