# AMA Donor and Surrogacy Agency Website

## Overview

This is a comprehensive website for AMA Donor and Surrogacy Agency, built on Django framework. The website provides information about surrogacy services, donor programs, and family-building solutions.

## Features

### Core Functionality
- **Homepage**: Hero slider, about section, services overview, success stories, testimonials, and FAQ preview
- **Services Page**: Detailed information about surrogacy and donor services
- **Programs Page**: Comprehensive overview of different surrogacy programs
- **Success Stories**: Real family stories and testimonials
- **FAQ Page**: Frequently asked questions organized by category
- **Contact Forms**: Inquiry forms and consultation requests
- **Admin Panel**: Full content management system

### Key Sections

#### 1. Surrogacy Services
- Traditional Surrogacy
- Gestational Surrogacy
- Donor Egg Programs
- Donor Sperm Programs
- Embryo Adoption
- IVF Services

#### 2. Donor Services
- Egg Donation
- Sperm Donation
- Comprehensive Screening
- Genetic Testing
- Legal Protection

#### 3. Support Services
- Initial Consultation
- Legal Guidance
- Medical Coordination
- Emotional Support
- 24/7 Assistance

## Technical Architecture

### Backend (Django)
- **Models**: Comprehensive data models for services, programs, testimonials, FAQs, and contact inquiries
- **Views**: RESTful API endpoints and page views
- **Admin**: Full Django admin interface for content management
- **Forms**: Contact forms and consultation requests

### Frontend
- **Responsive Design**: Mobile-first approach with modern CSS Grid and Flexbox
- **Animations**: AOS (Animate On Scroll) library for smooth animations
- **Icons**: Font Awesome icons for visual elements
- **Typography**: Clean, professional typography optimized for readability

### Database Models

#### SurrogacyService
- Service types (surrogacy, donor, IVF, consultation, legal)
- Features, pricing, duration
- Featured service flags

#### Testimonial
- Client stories and ratings
- Featured testimonial flags
- Client information

#### SurrogacyProgram
- Program types and descriptions
- Requirements and process steps
- Success rates and duration

#### FAQ
- Categorized questions and answers
- Frequently asked flags
- Ordering system

#### ContactInquiry
- Inquiry types and messages
- Contact preferences
- Urgency flags and status tracking

#### SuccessStory
- Family stories and outcomes
- Baby information
- Featured story flags

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 3.2+
- PostgreSQL or SQLite
- Virtual environment

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd amadsa
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_secret_key_here
DEBUG=True
DATABASE_URL=your_database_url
EMAIL_HOST=your_email_host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_password
```

## Content Management

### Admin Panel Access
- URL: `/danger/` (Django admin)
- Use your superuser credentials to access

### Adding Content

#### 1. Services
- Navigate to "Surrogacy Services" in admin
- Add service details, features, and pricing
- Mark as featured to display on homepage

#### 2. Programs
- Add surrogacy programs with requirements and process steps
- Include success rates and duration information

#### 3. Testimonials
- Add client testimonials with ratings
- Mark as featured for homepage display

#### 4. FAQs
- Organize questions by category
- Set order and mark as frequently asked

#### 5. Success Stories
- Add family success stories
- Include baby information and outcomes

## Customization

### Styling
- CSS is embedded in each template for easy customization
- Color scheme uses CSS variables for consistency
- Responsive breakpoints at 768px and below

### Content
- All content is managed through Django admin
- Templates include fallback content when no data exists
- Easy to update text, images, and information

### Images
- Image uploads handled through Django admin
- Automatic thumbnail generation
- Responsive image handling

## Deployment

### Production Considerations
- Set `DEBUG=False` in production
- Use production database (PostgreSQL recommended)
- Configure static file serving
- Set up email backend for contact forms
- Configure security headers

### Recommended Hosting
- **Platform**: Heroku, DigitalOcean, AWS
- **Database**: PostgreSQL
- **Static Files**: AWS S3, CloudFront
- **Email**: SendGrid, Mailgun

## SEO Features

- Meta titles and descriptions for all pages
- Structured data markup
- Clean URL structure
- Mobile-friendly design
- Fast loading times
- Semantic HTML

## Security Features

- CSRF protection on all forms
- SQL injection prevention
- XSS protection
- Secure admin access
- Input validation and sanitization

## Support & Maintenance

### Regular Tasks
- Update content through admin panel
- Monitor contact form submissions
- Backup database regularly
- Update dependencies
- Monitor performance metrics

### Troubleshooting
- Check Django logs for errors
- Verify database connections
- Test form submissions
- Check email configuration

## License

This project is proprietary software for AMA Donor and Surrogacy Agency.

## Contact

For technical support or questions about the website:
- Email: tech@amadonoragency.com
- Phone: +1 (555) 123-4567

---

**Note**: This website is designed specifically for surrogacy and donor services. Ensure all content complies with local regulations and medical guidelines in your jurisdiction.
